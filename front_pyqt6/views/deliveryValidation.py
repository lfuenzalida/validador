from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QCheckBox, QHBoxLayout, QListWidget, QTextEdit, QMessageBox, QGridLayout,QSpacerItem,QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
import requests
import json
from datetime import date
import re
import keyboard

class DeliveryValidationScreen(QWidget):
    def __init__(self, main_app, flujo, datos_generales):
        super().__init__()
        self.etiquetas_por_factura = {}
        self.clientes_por_factura = {} 
        self.total_etiquetas_validadas = 0  # Contador de etiquetas validadas
        self.total_etiquetas_factura_actual = 0  # Contador de etiquetas de la factura actual
        self.etiquetas_validadas_factura_actual = 0  # Contador de etiquetas validadas de la factura actual
        self.main_app = main_app
        self.flujo = flujo
        self.datos_generales = datos_generales or {
            "validador": "No definido",
            "conductor": "",
            "peoneta": "",
            "vehiculo": "",
            "patente": "",
            "quien_retira": "",
            "refrigerado": False
        }
        self.setWindowTitle("Validación de Facturas")
        self.showMaximized()
        self.initUI()
        
        keyboard.on_press_key("tab", lambda _: self.procesar_codigo_barras())
        self.cargar_datos_flujo()  # Cargar los datos del flujo

    

    def initUI(self):
        main_layout = QHBoxLayout()


        # **📌 Lado izquierdo: Información y validación de facturas**
        left_layout = QVBoxLayout()

        # **📌 Ingreso del número de factura**
        self.factura_label = QLabel("Número de Factura:")
        self.factura_input = QLineEdit()
        self.buscar_button = QPushButton("Buscar")
        self.buscar_button.clicked.connect(self.buscar_factura)
        self.factura_input.returnPressed.connect(self.buscar_factura)

        factura_layout = QHBoxLayout()
        factura_layout.addWidget(self.factura_label)
        factura_layout.addWidget(self.factura_input)
        factura_layout.addWidget(self.buscar_button)
        left_layout.addLayout(factura_layout)

        # **📌 Título dinámico del flujo**
        self.titulo_flujo = QLabel("")
        self.titulo_flujo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo_flujo.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(self.titulo_flujo)

        # **📌 Información dinámica del flujo**
        self.info_validador = QLabel("Validador: ")
        self.info_conductor = QLabel("Conductor: ")
        self.info_peoneta = QLabel("Peoneta: ")
        self.info_vehiculo = QLabel("Vehículo: ")
        self.info_patente = QLabel("Patente: ")
        self.info_quien_retira = QLabel("Quien Retira: ")
        self.info_refrigerado = QLabel("Vehículo Refrigerado: ")
        
        self.info_cliente = QLabel("Cliente: ")
        self.info_rut = QLabel("Rut: ")
        self.info_facturador = QLabel("Facturador: ")
        self.info_kilos = QLabel("Total Kilos: ")

        self.labels_despacho = [
            self.info_validador, self.info_conductor, self.info_peoneta, self.info_vehiculo, self.info_patente
        ]
        self.labels_retiro = [
            self.info_validador, self.info_quien_retira, self.info_patente, self.info_refrigerado
        ]

        for label in self.labels_despacho + self.labels_retiro + [
            self.info_cliente, self.info_rut, self.info_facturador, self.info_kilos
        ]:
            left_layout.addWidget(label)

        # **📌 Título "Detalle de Factura" en negrita y más grande**
        self.detalle_label = QLabel("<b><font size=4>Detalle de Factura</font></b>")
        self.detalle_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        left_layout.addWidget(self.detalle_label)

        # **📌 Tabla de etiquetas (más pegada al título)**
        self.tabla_etiquetas = QTableWidget()
        self.tabla_etiquetas.setColumnCount(5)
        self.tabla_etiquetas.setHorizontalHeaderLabels(["N° Etiqueta", "Corte", "Marca", "Kilos", "Validar"])
        self.tabla_etiquetas.setStyleSheet("margin-top: -5px;")
        left_layout.addWidget(self.tabla_etiquetas, 1)  # 🔹 Factor 1: La tabla se expande ocupando todo el espacio disponible

        # **📌 Espaciador para empujar el contenedor final hacia abajo**
        # left_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # **📌 Layout horizontal para agrupar lector de código y contador**
        self.contador_lector_layout = QHBoxLayout()
        self.contador_lector_layout.setContentsMargins(0, 0, 0, 0)

        # **📌 Layout vertical para lector de código + botones**
        self.lector_botones_layout = QVBoxLayout()

        # **📌 Barra de entrada para la pistola**
        self.barra_entrada_pistola = QLineEdit()
        self.barra_entrada_pistola.setPlaceholderText("Escanea un código de barras aquí...")
        self.barra_entrada_pistola.setMaxLength(50)
        self.barra_entrada_pistola.returnPressed.connect(self.procesar_codigo_barras)

        # **📌 Ajustar tamaño del lector**
        self.barra_entrada_pistola.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.barra_entrada_pistola.setMinimumHeight(40)
        self.barra_entrada_pistola.setStyleSheet("font-size: 18px; padding: 5px;")

        # **📌 Contador TOTAL y C° Validadas**
        self.contador_container = QWidget()
        self.contador_container.setStyleSheet("background-color: black; border-radius: 8px; padding: 5px;")
        self.contador_container.setFixedHeight(150)

        self.contador_layout = QGridLayout(self.contador_container)

        # **📌 Etiquetas para los valores**
        self.total_etiquetas_label = QLabel("TOTAL")
        self.validadas_etiquetas_label = QLabel("C° Validadas")

        self.total_cajas = QLabel("0")
        self.validadas_etiquetas_factura_label = QLabel("0")

        # **📌 Aplicar estilos**
        for label in [self.total_etiquetas_label, self.validadas_etiquetas_label]:
            label.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")

        for label in [self.total_cajas, self.validadas_etiquetas_factura_label]:  
            label.setStyleSheet("font-size: 40px; font-weight: bold; color: white; padding: 5px;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # **📌 Agregar etiquetas al layout del contador**
        self.contador_layout.addWidget(self.total_etiquetas_label, 0, 0)
        self.contador_layout.addWidget(self.validadas_etiquetas_label, 0, 1)
        self.contador_layout.addWidget(self.total_cajas, 1, 0)
        self.contador_layout.addWidget(self.validadas_etiquetas_factura_label, 1, 1)

        # **📌 Botones debajo del lector de código**
        self.volver_button = QPushButton("Volver")
        self.volver_button.clicked.connect(self.volver_a_flujo)

        self.validar_button = QPushButton("Factura Validada")
        self.validar_button.clicked.connect(self.factura_validada)

        self.finalizar_button = QPushButton("Finalizar Validación")
        self.finalizar_button.clicked.connect(self.finalizar_validacion)

        # **📌 Agregar lector y botones al layout vertical**
        self.lector_botones_layout.addWidget(self.barra_entrada_pistola)  
        self.lector_botones_layout.addWidget(self.volver_button)  
        self.lector_botones_layout.addWidget(self.validar_button)  
        self.lector_botones_layout.addWidget(self.finalizar_button)  
        self.lector_botones_layout.addStretch()  

        # **📌 Añadir lector + botones a la izquierda y contador a la derecha**
        self.contador_lector_layout.addLayout(self.lector_botones_layout, 2)  
        self.contador_lector_layout.addStretch()  
        self.contador_lector_layout.addWidget(self.contador_container, 1)  

        # **📌 Agregar el nuevo layout al fondo del diseño**
        left_layout.addLayout(self.contador_lector_layout)  

        # **📌 Agregar el layout izquierdo al principal**
        main_layout.addLayout(left_layout)


        # **Lado derecho: Registro de validaciones**
        right_layout = QVBoxLayout()
        header_layout = QHBoxLayout()

        # **Título "Facturas Validadas" en negrita y más grande**
        self.registro_label = QLabel("<b><font size=4>Facturas Validadas</font></b>")
        self.contador_etiquetas_label = QLabel("N° Cajas: 0")
        self.contador_etiquetas_label.setStyleSheet("background-color: black; border: 2px solid black; padding: 5px; font-weight: bold;""font-size: 28px;")
        right_layout.addWidget(self.registro_label)
        header_layout.addStretch()
        header_layout.addWidget(self.contador_etiquetas_label)
        right_layout.addLayout(header_layout)
        

        self.registro_validaciones = QTableWidget()
        self.registro_validaciones.setColumnCount(5)
        self.registro_validaciones.setHorizontalHeaderLabels(["✓", "N° Factura", "Cliente", "Estado", "Detalle"])
        right_layout.addWidget(self.registro_validaciones)

        self.eliminar_button = QPushButton("Eliminar Facturas Seleccionadas")
        self.eliminar_button.setVisible(False)
        self.eliminar_button.clicked.connect(self.eliminar_facturas)
        right_layout.addWidget(self.eliminar_button)

        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def showEvent(self, event):
        """Se ejecuta cada vez que la ventana es mostrada para asegurarse de que se maximice."""
        self.showMaximized()  # 🔹 Asegurar que se maximice cada vez que se muestra
        super().showEvent(event)  # 🔹 Mantiene el comportamiento original del evento


    def volver_a_flujo(self):
        """Regresa a la pantalla del flujo correspondiente (despacho o retiro)."""
        if self.flujo == "despacho":
            self.main_app.cambiar_a_delivery()
        elif self.flujo == "retiro":
            self.main_app.cambiar_a_withdrawal()
        else:
            QMessageBox.warning(self, "Error", f"Flujo desconocido: {self.flujo}.")

    def cargar_datos_flujo(self):
        """Cargar los datos del flujo en la interfaz."""
        if self.flujo == "despacho":
            self.titulo_flujo.setText("Flujo: Despacho")
            self.info_validador.setText(f"Validador: {self.datos_generales.get('validador', 'No definido')}")
            self.info_conductor.setText(f"Conductor: {self.datos_generales.get('conductor', 'No definido')}")
            self.info_peoneta.setText(f"Peoneta: {self.datos_generales.get('peoneta', 'No definido')}")
            self.info_vehiculo.setText(f"Vehículo: {self.datos_generales.get('vehiculo', 'No definido')}")
            self.info_patente.setText(f"Patente: {self.datos_generales.get('patente', 'No definido')}")

            # Ocultar campos específicos de retiro
            self.info_quien_retira.hide()
            self.info_refrigerado.hide()
        elif self.flujo == "retiro":
            self.titulo_flujo.setText("Flujo: Retiro")
            self.info_validador.setText(f"Validador: {self.datos_generales.get('validador', 'No definido')}")
            self.info_quien_retira.setText(f"Quien Retira: {self.datos_generales.get('quien_retira', 'No definido')}")
            self.info_patente.setText(f"Patente: {self.datos_generales.get('patente', 'No definido')}")
            refrigerado = "Sí" if self.datos_generales.get('refrigerado', False) else "No"
            self.info_refrigerado.setText(f"Vehículo Refrigerado: {refrigerado}")

            # Ocultar campos específicos de despacho
            self.info_conductor.hide()
            self.info_peoneta.hide()
            self.info_vehiculo.hide()
        else:
            QMessageBox.warning(self, "Error", f"Flujo desconocido: {self.flujo}.")


    def buscar_factura(self):
        nro_factura = self.factura_input.text().strip()
        if not nro_factura:
            QMessageBox.warning(self, "Error", "Ingrese un número de factura")
            return
        
        if self.factura_ya_validada(nro_factura):
            QMessageBox.warning(self, "Advertencia", f"La factura {nro_factura} ya ha sido validada.")
            return

        url = f"http://127.0.0.1:5000/api/factura/{nro_factura}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # 🔹 Lanza una excepción si hay error en la solicitud
            
            data = response.json()

            # ✅ Guardar cliente en `self.clientes_por_factura`
            cliente_rut = data.get("rut", "").strip()
            cliente_nombre = data.get("cliente", "").strip()

            self.clientes_por_factura[nro_factura] = {
                "rut": cliente_rut,
                "nombre": cliente_nombre
            }

            print(f"✅ Cliente Guardado para Factura {nro_factura}: {cliente_nombre} - {cliente_rut}")

            # ✅ Mostrar en la interfaz
            self.info_cliente.setText(f"Cliente: {cliente_nombre}")
            self.info_rut.setText(f"Rut: {cliente_rut}")
            self.info_facturador.setText(f"Facturador: {data.get('facturador', '')}")
            self.info_kilos.setText(f"Total Kilos: {data.get('total kilos', '')}")
            self.total_cajas.setText(f"{data.get('total Cajas', '')}")

            # 🔹 Obtener detalles de la factura
            detalles_url = f"http://127.0.0.1:5000/api/factura/{nro_factura}/detalles"
            detalles_response = requests.get(detalles_url)
            detalles_response.raise_for_status()  # 🔹 Lanza una excepción si hay error
            
            detalles = detalles_response.json()
            self.llenar_tabla(detalles)

            self.barra_entrada_pistola.setFocus()

        except requests.exceptions.HTTPError as http_err:
            QMessageBox.warning(self, "Error", f"HTTP error al buscar la factura: {http_err}")
        except requests.exceptions.ConnectionError:
            QMessageBox.warning(self, "Error", "Error de conexión con el servidor")
        except requests.exceptions.Timeout:
            QMessageBox.warning(self, "Error", "El servidor tardó demasiado en responder")
        except requests.exceptions.RequestException as err:
            QMessageBox.warning(self, "Error", f"Error inesperado: {err}")

    
    def factura_ya_validada(self, nro_factura):
        """ Verifica si una factura ya ha sido validada """
        for row in range(self.registro_validaciones.rowCount()):
            if self.registro_validaciones.item(row, 1).text() == nro_factura:
                return True
        return False

    def procesar_codigo_barras(self):
        """ Procesa el código ingresado por la pistola, busca en la tabla y marca el checkbox. """
        QTimer.singleShot(0, self._procesar_codigo_barras)  # Ejecutar en el hilo principal

    def _procesar_codigo_barras(self):
        """Lógica real de procesamiento del código."""
        codigo_ingresado = self.barra_entrada_pistola.text().strip()

        if not codigo_ingresado:
            return

        # Extraer solo el número del código después de ' o -
        match = re.search(r"[-'](\d+)", codigo_ingresado)
        if match:
            codigo_final = match.group(1).strip()
        else:
            codigo_final = codigo_ingresado  # Si no hay separador, usar el código completo

        encontrado = False  # Para saber si se encontró el código en la tabla
        alerta_mostrada = False  # Controla si se mostró una alerta

        # Recorrer la tabla y buscar el código en la columna 0
        for row in range(self.tabla_etiquetas.rowCount()):
            item = self.tabla_etiquetas.item(row, 0)  # Columna del número de etiqueta
            if item and item.text() == codigo_final:
                encontrado = True
                checkbox = self.tabla_etiquetas.cellWidget(row, 4)
                if isinstance(checkbox, QCheckBox):  # Verificar si es un checkbox
                    if checkbox.isChecked():
                        QMessageBox.warning(self, "Código Escaneado", f"El código {codigo_final} ya está escaneado.")
                        alerta_mostrada = True
                    else:
                        checkbox.setChecked(True)
                        self.etiquetas_validadas_factura_actual += 1
                        self.actualizar_contador_factura_actual()
                        
                break  # Salir del bucle tras encontrar el código

        if not encontrado:
            QMessageBox.warning(self, "Etiqueta No Encontrada", f"El código {codigo_final} no pertenece a esta factura.")
            alerta_mostrada = True

        # Limpiar la barra de entrada para la siguiente lectura
        self.barra_entrada_pistola.clear()

        # Solo restablecer el foco si NO se mostró una alerta (para evitar problemas con QMessageBox)
        if not alerta_mostrada:
            QTimer.singleShot(100, self.barra_entrada_pistola.setFocus)  # Espera 100ms y devuelve el foco


    def llenar_tabla(self, detalles):
        """ Llena la tabla de etiquetas con datos. """
        self.tabla_etiquetas.setRowCount(len(detalles))
    
        for row, item in enumerate(detalles):
            # Crear elementos no editables para las columnas de datos
            nro_etiqueta_item = QTableWidgetItem(str(item['nro_etiqueta']))
            nro_etiqueta_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Solo seleccionable
            self.tabla_etiquetas.setItem(row, 0, nro_etiqueta_item)

            corte_item = QTableWidgetItem(item['corte'])
            corte_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Solo seleccionable
            self.tabla_etiquetas.setItem(row, 1, corte_item)

            marca_item = QTableWidgetItem(item['marca'])
            marca_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Solo seleccionable
            self.tabla_etiquetas.setItem(row, 2, marca_item)

            kilos_item = QTableWidgetItem(str(item['kilos']))
            kilos_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)  # Solo seleccionable
            self.tabla_etiquetas.setItem(row, 3, kilos_item)

            # Crear checkbox para validar
            checkbox = QCheckBox()
            checkbox.setEnabled(False)
            self.tabla_etiquetas.setCellWidget(row, 4, checkbox)

    def cargar_datos_factura(self, total_cajas):
        """Carga el total de etiquetas desde la cabecera y lo mantiene hasta la validación."""
        if self.total_etiquetas_factura_actual == 0:  # Solo se asigna al buscar la factura
            self.total_etiquetas_factura_actual = total_cajas  
            self.total_cajas.setText(f"{self.total_etiquetas_factura_actual}")  # ✅ Se mantiene fijo
        self.actualizar_contador_factura_actual()

    def actualizar_contador_etiquetas(self):
        """Actualiza el contador de etiquetas validadas en la interfaz."""
        self.contador_etiquetas_label.setText(f"N° Cajas: {self.total_etiquetas_validadas}")

    def actualizar_contador_factura_actual(self):
        """Solo actualiza el número de etiquetas validadas sin afectar el total."""
        self.validadas_etiquetas_factura_label.setText(f"{self.etiquetas_validadas_factura_actual}")  # ✅ Se actualiza dinámicamente

    def actualizar_contador_cajas(self):
        """Recalcula el número total de etiquetas validadas y actualiza el contador."""
        total_cajas = 0
        for row in range(self.registro_validaciones.rowCount()):
            nro_factura = self.registro_validaciones.item(row, 1).text() or ""
            if nro_factura in self.etiquetas_por_factura:
                total_cajas += len(self.etiquetas_por_factura[nro_factura]["validadas"])

        self.contador_etiquetas_label.setText(f"N° Cajas: {total_cajas}")

    def factura_validada(self):
        nro_factura = self.factura_input.text()
        if not nro_factura:
            QMessageBox.warning(self, "Error", "Debe ingresar un número de factura")
            return

        # Verificar si la factura ya fue registrada
        for row in range(self.registro_validaciones.rowCount()):
            item = self.registro_validaciones.item(row, 1)  # Columna "N° Factura"
            if item and item.text() == nro_factura:
                QMessageBox.warning(self, "Advertencia", f"La factura {nro_factura} ya ha sido validada.")
                return  # Evitar duplicados

        # ✅ Guardamos etiquetas en `self.etiquetas_por_factura`
        self.etiquetas_por_factura[nro_factura] = {
            "validadas": self.obtener_etiquetas_validadas(),
            "no_encontradas": self.obtener_etiquetas_no_encontradas()
        }

        etiquetas_faltantes = [
            self.tabla_etiquetas.item(row, 0).text()
            for row in range(self.tabla_etiquetas.rowCount())
            if not self.tabla_etiquetas.cellWidget(row, 4).isChecked()
        ]

        if etiquetas_faltantes:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Advertencia")
            msg_box.setText(f"Está validando una factura con etiquetas faltantes:\n{', '.join(etiquetas_faltantes)}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Cancel)
            respuesta = msg_box.exec()

            if respuesta == QMessageBox.StandardButton.Cancel:
                return  # No se guarda la validación y el usuario puede seguir validando

            estado = "Validada (con detalles)"
            detalle = f"{', '.join(etiquetas_faltantes)}"
        else:
            estado = "Validada"
            detalle = "OK"

        # 🔍 Debugging para verificar almacenamiento
        print(f"📌 Factura: {nro_factura}")
        print(f"✅ Etiquetas Validadas Guardadas: {self.etiquetas_por_factura[nro_factura]['validadas']}")
        print(f"⚠️ Etiquetas No Encontradas Guardadas: {self.etiquetas_por_factura[nro_factura]['no_encontradas']}")

        etiquetas_faltantes = [
            self.tabla_etiquetas.item(row, 0).text()
            for row in range(self.tabla_etiquetas.rowCount())
            if not self.tabla_etiquetas.cellWidget(row, 4).isChecked()
        ]

        estado = "Validada (con detalles)" if etiquetas_faltantes else "Validada"
        detalle = ", ".join(etiquetas_faltantes) if etiquetas_faltantes else "OK"

        cliente = self.info_cliente.text().replace("Cliente: ", "").strip()  # ✅ Extraer correctamente el nombre del cliente

        row_count = self.registro_validaciones.rowCount()
        self.registro_validaciones.insertRow(row_count)

        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.mostrar_boton_eliminar)

        self.registro_validaciones.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.registro_validaciones.setCellWidget(row_count, 0, checkbox)
        self.registro_validaciones.setItem(row_count, 1, QTableWidgetItem(nro_factura))
        self.registro_validaciones.setItem(row_count, 2, QTableWidgetItem(cliente))
        self.registro_validaciones.setItem(row_count, 3, QTableWidgetItem(estado))
        self.registro_validaciones.setItem(row_count, 4, QTableWidgetItem(detalle))

        print(f"📌 Cliente Registrado: {cliente}")

        # Incrementar el contador de etiquetas validadas
        self.total_etiquetas_validadas += len(self.etiquetas_por_factura[nro_factura]["validadas"])
        self.actualizar_contador_etiquetas()

        self.total_etiquetas_factura_actual = 0  # ✅ Se restablece el total solo cuando la factura es validada
        self.etiquetas_validadas_factura_actual = 0
        self.total_cajas.setText("0")  # ✅ Ahora sí se resetea
        self.validadas_etiquetas_factura_label.setText("0")

        # Limpiar la tabla de etiquetas, pero no perder las etiquetas guardadas
        self.tabla_etiquetas.setRowCount(0)
        self.factura_input.clear()
        self.eliminar_button.setVisible(True)


    def mostrar_boton_eliminar(self):
        """ Muestra el botón de eliminar si hay facturas seleccionadas """
        hay_seleccionadas = any(
            self.registro_validaciones.cellWidget(row, 0).isChecked()
            for row in range(self.registro_validaciones.rowCount())
        )
        self.eliminar_button.setVisible(hay_seleccionadas)

    def eliminar_facturas(self):
        """ Elimina las facturas seleccionadas y actualiza el contador de cajas. """
        
        filas_a_eliminar = []
        
        for row in range(self.registro_validaciones.rowCount()):
            checkbox = self.registro_validaciones.cellWidget(row, 0)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                filas_a_eliminar.append(row)

        if not filas_a_eliminar:
            QMessageBox.warning(self, "Advertencia", "Seleccione al menos una factura para eliminar.")
            return

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("Confirmación")
        msg_box.setText("¿Está seguro de eliminar las facturas seleccionadas?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        respuesta = msg_box.exec()

        if respuesta == QMessageBox.StandardButton.No:
            return

        # **Eliminar facturas seleccionadas de la tabla**
        for row in reversed(filas_a_eliminar):  # 🔹 Recorrer de atrás hacia adelante para evitar errores de indexación
            nro_factura = self.registro_validaciones.item(row, 1).text() or ""

            # **Eliminar la factura de la estructura etiquetas_por_factura**
            if nro_factura in self.etiquetas_por_factura:
                del self.etiquetas_por_factura[nro_factura]

            self.registro_validaciones.removeRow(row)

        # **Actualizar contador de cajas después de eliminar**
        self.actualizar_contador_cajas()

        # **Ocultar botón si ya no hay facturas seleccionadas**
        self.eliminar_button.setVisible(False)


    def limpiar_datos_cliente(self):
        """Limpia los datos del cliente en la interfaz."""
        self.info_cliente.setText("Cliente: ")
        self.info_facturador.setText("Facturador: ")
        self.info_kilos.setText("Total Kilos: ")
        self.tabla_etiquetas.setRowCount(0)

        # Forzar refresco de la interfaz
        self.info_cliente.update()
        self.info_rut.update()
        self.info_facturador.update()
        self.info_kilos.update()
        self.factura_input.update()
        self.tabla_etiquetas.update()


    def finalizar_validacion(self):
        """ Finaliza la validación enviando los registros al backend con etiquetas guardadas. """
        if not self.datos_generales:
            QMessageBox.warning(self, "Error", "No hay datos generales disponibles para validar.")
            return

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("Confirmación")
        msg_box.setText("¿Está seguro de finalizar la validación?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        respuesta = msg_box.exec()

        if respuesta == QMessageBox.StandardButton.No:
            return

        registros = []
        for row in range(self.registro_validaciones.rowCount()):
            nro_factura = self.registro_validaciones.item(row, 1).text() or ""
            estado = self.registro_validaciones.item(row, 3).text() or ""

            # ✅ Obtener cliente correcto desde `self.clientes_por_factura`
            cliente_data = self.clientes_por_factura.get(nro_factura, {"rut": "N/A", "nombre": "Desconocido"})
            cliente_rut = cliente_data["rut"]
            cliente_nombre = cliente_data["nombre"]

            # ✅ Obtener etiquetas desde `self.etiquetas_por_factura`
            etiquetas = self.etiquetas_por_factura.get(nro_factura, {"validadas": [], "no_encontradas": []})

            print(f"📌 Factura: {nro_factura}")
            print(f"📌 Cliente: {cliente_nombre} - RUT: {cliente_rut}")
            print(f"✅ Etiquetas Validadas a enviar: {etiquetas['validadas']}")
            print(f"⚠️ Etiquetas No Encontradas a enviar: {etiquetas['no_encontradas']}")

            registro = {
                "nombre_validador": self.datos_generales.get("validador", "No definido"),
                "nro_factura": nro_factura.strip(),
                "cliente_rut": cliente_rut if cliente_rut.isdigit() else "",
                "cliente_nombre": cliente_nombre,  
                "estado": estado,
                "etiquetas_validadas": etiquetas["validadas"],
                "etiquetas_no_encontradas": etiquetas["no_encontradas"]
            }

            if self.flujo == "despacho":
                registro.update({
                    "conductor": self.datos_generales.get("conductor", ""),
                    "peoneta": self.datos_generales.get("peoneta", ""),
                    "vehiculo": self.datos_generales.get("vehiculo", ""),
                    "patente": self.datos_generales.get("patente", ""),
                })
            elif self.flujo == "retiro":
                registro.update({
                    "quien_retira": self.datos_generales.get("quien_retira", ""),
                    "refrigerado": self.datos_generales.get("refrigerado", ""),
                    "patente": self.datos_generales.get("patente", ""),
                })

            registros.append(registro)

        payload = {"registros": registros}

        print(f"\n📤 Enviando payload al backend: {payload}")

        endpoint = "http://127.0.0.1:5000/api/despacho" if self.flujo == "despacho" else "http://127.0.0.1:5000/api/retiro"

        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            QMessageBox.information(self, "Validación Exitosa", "Todos los datos fueron enviados correctamente.")
            self.main_app.regresar_a_home()
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "Error", f"Error al enviar datos al backend: {e}")

        self.registro_validaciones.setRowCount(0)
        self.main_app.regresar_a_home()


    def obtener_etiquetas_validadas(self):
        """Obtiene el listado de etiquetas validadas."""
        etiquetas_validadas = []
        for row in range(self.tabla_etiquetas.rowCount()):
            checkbox = self.tabla_etiquetas.cellWidget(row, 4)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                etiqueta = self.tabla_etiquetas.item(row, 0).text()
                etiquetas_validadas.append(etiqueta)
        return etiquetas_validadas

    def obtener_etiquetas_no_encontradas(self):
        """Obtiene el listado de etiquetas no encontradas."""
        etiquetas_no_encontradas = []
        for row in range(self.tabla_etiquetas.rowCount()):
            checkbox = self.tabla_etiquetas.cellWidget(row, 4)
            if isinstance(checkbox, QCheckBox) and not checkbox.isChecked():
                etiqueta = self.tabla_etiquetas.item(row, 0).text()
                etiquetas_no_encontradas.append(etiqueta)
        return etiquetas_no_encontradas
        