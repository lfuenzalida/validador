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


class ValidationScreen(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle("Validación de Facturas")
        self.setGeometry(100, 100, 900, 1200)
        self.initUI()
        keyboard.on_press_key("tab", lambda _: self.procesar_codigo_barras())
        

    def initUI(self):
        main_layout = QHBoxLayout()  # Cambio a diseño horizontal para dividir en dos partes

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

        # **Información del validador y datos de la factura**
        self.info_validador = QLabel("Validador: ")
        self.info_conductor = QLabel("Conductor: ")
        self.info_peoneta = QLabel("Peoneta: ")
        self.info_vehiculo = QLabel("Vehículo: ")
        self.info_patente = QLabel("Patente: ")

        self.info_cliente = QLabel("Cliente: ")
        self.info_facturador = QLabel("Facturador: ")
        self.info_kilos = QLabel("Total Kilos: ")

        for label in [
            self.info_validador, self.info_conductor, self.info_peoneta, self.info_vehiculo, self.info_patente,
            self.info_cliente, self.info_facturador, self.info_kilos
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
        self.barra_entrada_pistola.setMaxLength(50)  # Limitar caracteres por seguridad
        self.barra_entrada_pistola.returnPressed.connect(self.procesar_codigo_barras)
        left_layout.addWidget(self.barra_entrada_pistola)


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
        self.eliminar_button.setVisible(False)  # Inicialmente oculto
        self.eliminar_button.clicked.connect(self.eliminar_facturas)
        right_layout.addWidget(self.eliminar_button)

        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def cargar_datos_validacion(self, datos):
        """Carga los datos del validador al cambiar de pantalla."""
        self.info_validador.setText(f"Validador: {datos['validador']}")
        self.info_conductor.setText(f"Conductor: {datos['conductor']}")
        self.info_peoneta.setText(f"Peoneta: {datos['peoneta']}")
        self.info_vehiculo.setText(f"Vehículo: {datos['vehiculo']}")
        self.info_patente.setText(f"Patente: {datos['patente']}")

    def buscar_factura(self):
        nro_factura = self.factura_input.text().strip()
        if not nro_factura:
            QMessageBox.warning(self, "Error", "Ingrese un número de factura")
            return
        
        if self.factura_ya_validada(nro_factura):
            QMessageBox.warning(self, "Advertencia", f"La factura {nro_factura} ya ha sido validada.")
            return

        url = f"http://127.0.0.1:8000/api/factura/{nro_factura}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            self.info_cliente.setText(f"Cliente: {data['cliente']}")
            self.info_facturador.setText(f"Facturador: {data['facturador']}")
            self.info_kilos.setText(f"Total Kilos: {data['total kilos']}")

            detalles_url = f"http://127.0.0.1:8000/api/factura/{nro_factura}/detalles"
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
            self.tabla_etiquetas.setItem(row, 0, QTableWidgetItem(str(item['nro_etiqueta'])))
            self.tabla_etiquetas.setItem(row, 1, QTableWidgetItem(item['corte']))
            self.tabla_etiquetas.setItem(row, 2, QTableWidgetItem(item['marca']))
            self.tabla_etiquetas.setItem(row, 3, QTableWidgetItem(str(item['kilos'])))

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

        cliente = self.info_cliente.text().replace("Cliente: ", "")

        row_count = self.registro_validaciones.rowCount()
        self.registro_validaciones.insertRow(row_count)

        checkbox = QCheckBox()
        checkbox.stateChanged.connect(self.mostrar_boton_eliminar)

        self.registro_validaciones.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.registro_validaciones.setCellWidget(row_count, 0, checkbox)  # Checkbox en la primera columna
        self.registro_validaciones.setItem(row_count, 1, QTableWidgetItem(nro_factura))  # Número de factura
        self.registro_validaciones.setItem(row_count, 2, QTableWidgetItem(cliente))  # Cliente
        self.registro_validaciones.setItem(row_count, 3, QTableWidgetItem(estado))  # Estado de la validación
        self.registro_validaciones.setItem(row_count, 4, QTableWidgetItem(detalle))  # Detalles

        # Limpiar la tabla de detalles de la factura después de registrar la validación
        self.tabla_etiquetas.setRowCount(0)
        self.factura_input.clear()

        # Mostrar botón de eliminar si hay registros
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
        
    def mostrar_pantalla_login(self):
        """ Cambia a la pantalla de inicio de sesión después de finalizar la validación. """
        self.validation_screen.hide()
        self.login.show()


    def finalizar_validacion(self):
        """ Pregunta al usuario si desea finalizar la validación y envía los datos al backend si confirma. """

        # Mostrar cuadro de diálogo de confirmación
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle("Confirmación")
        msg_box.setText("¿Está seguro de finalizar la validación?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        respuesta = msg_box.exec()

        # Si el usuario elige "No", cancelar la operación
        if respuesta == QMessageBox.StandardButton.No:
            return

        # Si el usuario elige "Sí", proceder con la validación
        registros = []
        for row in range(self.registro_validaciones.rowCount()):
            nro_factura = self.registro_validaciones.item(row, 1).text() if self.registro_validaciones.item(row, 1) else ""
            estado = self.registro_validaciones.item(row, 3).text() if self.registro_validaciones.item(row, 3) else ""
            etiquetas_faltantes = self.registro_validaciones.item(row, 4).text().strip() if self.registro_validaciones.item(row, 4) else ""

            etiquetas_faltantes_lista = etiquetas_faltantes.split(", ") if etiquetas_faltantes else []
            registro = {
                "nombre_validador": self.info_validador.text().replace("Validador: ", "").strip(),
                "nro_factura": nro_factura.strip(),
                "etiquetas_incorrectas": etiquetas_faltantes_lista if estado == "Validada (con detalles)" else [],
                "conductor": self.info_conductor.text().replace("Conductor: ", "").strip(),
                "peoneta": self.info_peoneta.text().replace("Peoneta: ", "").strip(),
                "vehiculo": self.info_vehiculo.text().replace("Vehículo: ", "").strip(),
                "patente": self.info_patente.text().replace("Patente: ", "").strip()
            }

            # Verificar que los datos obligatorios no sean vacíos
            if not registro["nombre_validador"] or not registro["nro_factura"]:
                QMessageBox.warning(self, "Error", "Faltan datos obligatorios en la validación.")
                return

            registros.append(registro)

        # Enviar cada registro individualmente
        url = "http://127.0.0.1:8000/api/validacion"
        for registro in registros:
            # print("Enviando datos al backend:", json.dumps(registro, indent=4))  # Para depuración
            response = requests.post(url, json=registro)

            if response.status_code != 200:
                print("Error en la respuesta del backend:", response.text)
                QMessageBox.warning(self, "Error", f"No se pudo enviar la validación al backend. \nError: {response.text}")
                return  # Detener el proceso si hay un error en la primera solicitud

        # Confirmar envío exitoso
        QMessageBox.information(self, "Validación", "Datos enviados al backend correctamente")

        # Limpiar la tabla de facturas validadas
        self.registro_validaciones.setRowCount(0)

        # Volver a la pantalla de inicio de sesión
        self.main_app.cambiar_a_login()

    