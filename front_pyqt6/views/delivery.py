import json
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QHBoxLayout
from PyQt6.QtCore import Qt


class DeliveryScreen(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle("Ingreso de Datos")
        self.setGeometry(100, 100, 400, 300)  # Ajustar tamaño de la ventana
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # **Título "Despacho" en negrita y grande**
        self.titulo_label = QLabel("Despacho")
        self.titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar texto horizontalmente
        self.titulo_label.setStyleSheet("font-size: 24px; font-weight: bold;")  # Espaciado inferior
        layout.addWidget(self.titulo_label)
        

        # Cargar datos locales
        self.cargar_datos()

        # **Selección del validador**
        self.label_validador = QLabel("Validador:")
        self.label_validador.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.combo_validador = QComboBox()
        self.combo_validador.addItems(self.datos["validadores"])

        # **Selección del conductor**
        self.label_conductor = QLabel("Conductor:")
        self.label_conductor.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.combo_conductor = QComboBox()
        self.combo_conductor.addItems(self.datos["conductores"].keys())
        self.combo_conductor.currentTextChanged.connect(self.actualizar_opciones)

        # **Selección del peoneta**
        self.label_peoneta = QLabel("Peoneta:")
        self.label_peoneta.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.combo_peoneta = QComboBox()

        # **Selección del vehículo**
        self.label_vehiculo = QLabel("Vehículo:")
        self.label_vehiculo.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.combo_vehiculo = QComboBox()
        self.combo_vehiculo.currentTextChanged.connect(self.actualizar_patente)

        # **Selección de la patente (se llena según el vehículo seleccionado)**
        self.label_patente = QLabel("Patente:")
        self.label_patente.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.combo_patente = QComboBox()
        self.combo_vehiculo.currentTextChanged.connect(self.actualizar_patente)

        # **Botones de acción**
        self.boton_continuar = QPushButton("Continuar")
        self.boton_continuar.setStyleSheet("background-color: green; color: white; font-weight: bold; padding: 8px;")
        self.boton_continuar.clicked.connect(self.guardar_datos)

        self.boton_volver = QPushButton("Volver al Home")
        self.boton_volver.setStyleSheet("background-color: red; color: white; font-weight: bold; padding: 8px;")
        self.boton_volver.clicked.connect(self.volver_a_home)

        # **Organizar los botones en un layout horizontal**
        botones_layout = QHBoxLayout()
        botones_layout.addWidget(self.boton_volver)
        botones_layout.addWidget(self.boton_continuar)

        # **Agregar widgets al layout principal**
        layout.addWidget(self.label_validador)
        layout.addWidget(self.combo_validador)
        layout.addWidget(self.label_conductor)
        layout.addWidget(self.combo_conductor)
        layout.addWidget(self.label_peoneta)
        layout.addWidget(self.combo_peoneta)
        layout.addWidget(self.label_vehiculo)
        layout.addWidget(self.combo_vehiculo)
        layout.addWidget(self.label_patente)
        layout.addWidget(self.combo_patente)
        layout.addLayout(botones_layout)  # Agregar los botones alineados al final

        self.setLayout(layout)

        # Inicializar opciones con el primer conductor seleccionado
        self.actualizar_opciones()

    def cargar_datos(self):
        """Carga los datos locales desde JSON."""
        if not os.path.exists("datos_locales.json"):
            QMessageBox.critical(self, "Error", "No se encontró el archivo de datos locales.")
            return

        with open("datos_locales.json", "r") as file:
            self.datos = json.load(file)

    def actualizar_opciones(self):
        """Actualiza los combos de peoneta y vehículo según el conductor seleccionado."""
        conductor = self.combo_conductor.currentText()
        if not conductor:
            return

        info_conductor = self.datos["conductores"][conductor]

        # Limpiar y actualizar peonetas
        self.combo_peoneta.clear()
        self.combo_peoneta.addItems(info_conductor["opciones"]["peonetas"])

        # Seleccionar peoneta recomendada
        peoneta_recomendada = info_conductor["recomendada"]["peoneta"]
        index = self.combo_peoneta.findText(peoneta_recomendada)
        if index >= 0:
            self.combo_peoneta.setCurrentIndex(index)

        # Limpiar y actualizar vehículos
        self.combo_vehiculo.clear()
        self.combo_vehiculo.addItems(info_conductor["opciones"]["vehiculos"])

        # Seleccionar vehículo recomendado
        vehiculo_recomendado = info_conductor["recomendada"]["vehiculo"]
        index = self.combo_vehiculo.findText(vehiculo_recomendado)
        if index >= 0:
            self.combo_vehiculo.setCurrentIndex(index)

        # Actualizar patente basada en el vehículo seleccionado
        self.actualizar_patente()

    def actualizar_patente(self):
        """Actualiza la patente según el vehículo seleccionado."""
        vehiculo = self.combo_vehiculo.currentText()
        if not vehiculo:
            return

        patente = self.datos["vehiculos"].get(vehiculo, "No asignada")

        self.combo_patente.clear()
        self.combo_patente.addItem(patente)

    def guardar_datos(self):
        """Guarda los datos seleccionados y pasa a la siguiente pantalla."""
        validador = self.combo_validador.currentText()
        conductor = self.combo_conductor.currentText()
        peoneta = self.combo_peoneta.currentText()
        vehiculo = self.combo_vehiculo.currentText()
        patente = self.combo_patente.currentText()

        if not all([validador, conductor, peoneta, vehiculo, patente]):
            QMessageBox.warning(self, "Error", "Debe seleccionar todos los campos antes de continuar.")
            return

        # Guardar en la aplicación principal
        self.main_app.datos_validacion = {
            "validador": validador,
            "conductor": conductor,
            "peoneta": peoneta,
            "vehiculo": vehiculo,
            "patente": patente
        }

        QMessageBox.information(self, "Datos guardados", "Los datos han sido guardados correctamente.")
        self.main_app.cambiar_a_pantalla_validacion()

    def volver_a_home(self):
        """Regresa a la pantalla de Home."""
        self.main_app.regresar_a_home()
