import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QCheckBox, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt

class WithdrawalScreen(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle("Retiro de Existencias")
        self.setGeometry(100, 100, 400, 300)  # Ajustar tamaño de la ventana
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # **Título "Retiro" en negrita y grande**
        self.titulo_label = QLabel("Retiro")
        self.titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titulo_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.titulo_label)

        # Cargar datos locales
        self.cargar_datos()

        # **Selección del validador**
        self.label_validador = QLabel("Validador:")
        self.label_validador.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.combo_validador = QComboBox()
        self.combo_validador.addItems(self.datos["validadores"])

        # **Campo para ingresar quien retira**
        self.label_retiro = QLabel("Quien Retira:")
        self.label_retiro.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.input_retiro = QLineEdit()

        # **Campo para ingresar patente**
        self.label_patente = QLabel("Patente:")
        self.label_patente.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.input_patente = QLineEdit()

        # **Checkbox para Vehículo refrigerado**
        self.checkbox_refrigerado = QCheckBox("Vehículo refrigerado")
        self.checkbox_refrigerado.setStyleSheet("font-size: 15px;")

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
        layout.addWidget(self.label_retiro)
        layout.addWidget(self.input_retiro)
        layout.addWidget(self.label_patente)
        layout.addWidget(self.input_patente)
        layout.addWidget(self.checkbox_refrigerado)
        layout.addLayout(botones_layout)  # Agregar los botones alineados al final

        self.setLayout(layout)

    def cargar_datos(self):
        """Carga los datos locales desde JSON."""
        if not os.path.exists("datos_locales.json"):
            QMessageBox.critical(self, "Error", "No se encontró el archivo de datos locales.")
            return

        with open("datos_locales.json", "r") as file:
            self.datos = json.load(file)


    def guardar_datos(self):
        """Guarda los datos ingresados y pasa al siguiente paso."""
        validador = self.combo_validador.currentText()
        quien_retira = self.input_retiro.text().strip()
        patente = self.input_patente.text().strip()
        refrigerado = self.checkbox_refrigerado.isChecked()

        if not all([validador, quien_retira, patente]):
            QMessageBox.warning(self, "Error", "Debe completar todos los campos antes de continuar.")
            return

        # Guardar en la aplicación principal
        self.main_app.datos_retiro = {
            "validador": validador,
            "quien_retira": quien_retira,
            "patente": patente,
            "refrigerado": refrigerado
        }

        QMessageBox.information(self, "Datos guardados", "Los datos han sido guardados correctamente.")
        # Aquí puedes agregar el cambio a otra pantalla o lógica adicional

    def volver_a_home(self):
        """Regresa a la pantalla de Home."""
        self.main_app.regresar_a_home()
