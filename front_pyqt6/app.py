import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from views.login import LoginScreen
from views.validation import ValidationScreen


class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Validador de Facturas")

        # ** Tamaño de la ventana inicialmente más pequeño **
        self.setGeometry(100, 100, 500, 300)  # Tamaño de login

        # Inicializar variables para guardar datos de validación temporalmente
        self.datos_validacion = {}

        # Inicializar pantallas
        self.login_screen = LoginScreen(self)
        self.validation_screen = ValidationScreen(self)

        # Agregar pantallas al stack
        self.addWidget(self.login_screen)
        self.addWidget(self.validation_screen)

        self.setCurrentWidget(self.login_screen)  # Mostrar la pantalla de login al inicio

    def cambiar_a_pantalla_validacion(self):
        """Cambia de la pantalla de login a la pantalla de validación y expande a fullscreen."""
        self.setCurrentWidget(self.validation_screen)
        self.showMaximized()  # Expande la pantalla a full
        self.validation_screen.cargar_datos_validacion(self.datos_validacion)

    def regresar_a_login(self):
        """Regresa al login y restaura el tamaño inicial."""
        self.setCurrentWidget(self.login_screen)
        self.showNormal()  # Restaura tamaño inicial
        self.setGeometry(100, 100, 500, 300)  # Restaura tamaño pequeño


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec())
