from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QCheckBox, QHBoxLayout, QListWidget, QTextEdit, QMessageBox,
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
        self.setGeometry(100, 100, 900, 1200)
        self.initUI()
        keyboard.on_press_key("tab", lambda _: self.procesar_codigo_barras())
        self.cargar_datos_flujo()  # Cargar los datos del flujo

    def initUI(self):
        main_layout = QHBoxLayout()

        # **Lado izquierdo: Información y validación de facturas**
        left_layout = QVBoxLayout()

        # **Ingreso del número de factura**
        self.factura_label = QLabel("Número de Factura:")
        self.factura_input = QLineEdit()
        self.buscar_button = QPushButton("Buscar")
        self.buscar_button.clicked.connect(self.buscar_factura)

        factura_layout = QHBoxLayout()
        factura_layout.addWidget(self.factura_label)
        factura_layout.addWidget(self.factura_input)
        factura_layout.addWidget(self.buscar_button)
        left_layout.addLayout(factura_layout)

        # **Título dinámico del flujo**
        self.titulo_flujo = QLabel("")
        self.titulo_flujo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo_flujo.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(self.titulo_flujo)

        # **Información dinámica del flujo**
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
        self.total_cajas = QLabel("Total cajas:")

        self.labels_despacho = [
            self.info_validador, self.info_conductor, self.info_peoneta, self.info_vehiculo, self.info_patente
        ]
        self.labels_retiro = [
            self.info_validador, self.info_quien_retira, self.info_patente, self.info_refrigerado
        ]

        for label in self.labels_despacho + self.labels_retiro + [
            self.info_cliente ,self.info_rut, self.info_facturador, self.info_kilos, self.total_cajas
        ]:
            left_layout.addWidget(label)

        # **Título "Detalle de Factura" en negrita y más grande**
        self.detalle_label = QLabel("<b><font size=4>Detalle de Factura</font></b>")
        left_layout.addWidget(self.detalle_label)

        # **Tabla de etiquetas**
        self.tabla_etiquetas = QTableWidget()
        self.tabla_etiquetas.setColumnCount(5)
        self.tabla_etiquetas.setHorizontalHeaderLabels(["N° Etiqueta", "Corte", "Marca", "Kilos", "Validar"])
        left_layout.addWidget(self.tabla_etiquetas)

        # **Barra de entrada para la pistola**
        self.barra_entrada_pistola = QLineEdit(self)
        self.barra_entrada_pistola.setPlaceholderText("Escanea un código de barras aquí...")
        self.barra_entrada_pistola.setMaxLength(50)
        self.barra_entrada_pistola.returnPressed.connect(self.procesar_codigo_barras)
        left_layout.addWidget(self.barra_entrada_pistola)

        # **Botón de Volver**
        self.volver_button = QPushButton("Volver")
        self.volver_button.clicked.connect(self.volver_a_flujo)
        left_layout.addWidget(self.volver_button)

        # **Botón de validación**
        self.validar_button = QPushButton("Factura Validada")
        self.validar_button.clicked.connect(self.factura_validada)

        # **Botón de finalizar validación**
        self.finalizar_button = QPushButton("Finalizar Validación")
        self.finalizar_button.clicked.connect(self.finalizar_validacion)

        left_layout.addWidget(self.validar_button)
        left_layout.addWidget(self.finalizar_button)
        main_layout.addLayout(left_layout)

        # **Lado derecho: Registro de validaciones**
        right_layout = QVBoxLayout()

        # **Título "Facturas Validadas" en negrita y más grande**
        self.registro_label = QLabel("<b><font size=4>Facturas Validadas</font></b>")
        right_layout.addWidget(self.registro_label)

        

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
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            self.info_cliente.setText(f"Cliente: {data['cliente']}")
            self.info_rut.setText(f"Rut: {data['rut']}")
            self.info_facturador.setText(f"Facturador: {data['facturador']}")
            self.info_kilos.setText(f"Total Kilos: {data['total kilos']}")
            self.total_cajas.setText(f"Total cajas: {data['total Cajas']}")
            

            detalles_url = f"http://127.0.0.1:5000/api/factura/{nro_factura}/detalles"
            detalles_response = requests.get(detalles_url)
            if detalles_response.status_code == 200:
                detalles = detalles_response.json()
                self.llenar_tabla(detalles)
            else:
                QMessageBox.warning(self, "Error", "No se encontraron detalles para la factura")
        else:
            QMessageBox.warning(self, "Error", "Factura no encontrada")
    
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
        """ Elimina facturas seleccionadas """
        filas_a_eliminar = [
            row for row in range(self.registro_validaciones.rowCount())
            if self.registro_validaciones.cellWidget(row, 0).isChecked()
        ]

        for row in reversed(filas_a_eliminar):  # Eliminar de atrás hacia adelante
            self.registro_validaciones.removeRow(row)

        self.eliminar_button.setVisible(False)  # Ocultar botón si ya no hay seleccionadas
        

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

            # ✅ Obtener etiquetas desde `self.etiquetas_por_factura`
            etiquetas = self.etiquetas_por_factura.get(nro_factura, {"validadas": [], "no_encontradas": []})

            cliente_rut = self.info_rut.text().replace("Rut: ", "").strip()
            cliente_nombre = self.info_cliente.text().replace("Cliente: ", "").strip()

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
        