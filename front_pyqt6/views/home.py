from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt


class HomeScreen(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.setWindowTitle("Inicio - Validador de Facturas")

        # **Establecer el layout principal**
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar contenido

        # **Título con mejor diseño**
        self.titulo = QLabel("<h1 style='text-align:center;'>Bienvenido al Validador</h1>")
        self.titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar el texto
        layout.addWidget(self.titulo)

        # **Espaciador para dar margen superior**
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # **Botón de Despacho**
        self.boton_despacho = QPushButton("Despacho")
        self.boton_despacho.setFixedSize(200, 50)  # Tamaño fijo para mantener proporción
        self.boton_despacho.clicked.connect(self.ir_a_login)
        layout.addWidget(self.boton_despacho, alignment=Qt.AlignmentFlag.AlignCenter)

        # **Espaciador entre botones**
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # **Botón de Retiro**
        self.boton_retiro = QPushButton("Retiro")
        self.boton_retiro.setFixedSize(200, 50)
        self.boton_retiro.clicked.connect(self.ir_a_retiro)
        layout.addWidget(self.boton_retiro, alignment=Qt.AlignmentFlag.AlignCenter)

        # **Espaciador inferior para centrar todo mejor**
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Aplicar el layout a la ventana
        self.setLayout(layout)

    def ir_a_login(self):
        """Navega al Login para iniciar el proceso de validación."""
        self.main_app.cambiar_a_delivery()


    def ir_a_retiro(self):
        """Navega a la pantalla de Retiro."""
        self.main_app.cambiar_a_withdrawal()

    

