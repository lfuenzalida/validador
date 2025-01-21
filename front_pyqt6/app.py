import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from views.home import HomeScreen
from views.delivery import DeliveryScreen
from views.deliveryValidation import DeliveryValidationScreen
from views.withdrawal import WithdrawalScreen


class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Validador de Facturas")

        # ** Tamaño inicial de la ventana **
        self.setGeometry(100, 100, 500, 300)  # Tamaño inicial para Home

        # Inicializar variables de validación
        self.datos_validacion = {}

        # Inicializar pantallas
        self.home_screen = HomeScreen(self)
        self.delivery_screen = DeliveryScreen(self)
        self.withdrawal_screen = WithdrawalScreen(self)
        self.delivery_validation_screen = DeliveryValidationScreen(self)

        # Agregar pantallas al stack
        self.addWidget(self.home_screen)  # Primera pantalla
        self.addWidget(self.delivery_screen)
        self.addWidget(self.withdrawal_screen)
        self.addWidget(self.delivery_validation_screen)
        

        self.setCurrentWidget(self.home_screen)  # Mostrar Home al inicio

    def cambiar_a_delivery(self):
        """Cambia de Home a despacho."""
        self.setCurrentWidget(self.delivery_screen)
        self.setGeometry(100, 100, 500, 300) 

    def cambiar_a_withdrawal(self):
        """Cambia de Home a retiro."""
        self.setCurrentWidget(self.withdrawal_screen)
        self.setGeometry(100, 100, 500, 300) 

    def cambiar_a_pantalla_validacion(self):
        """Cambia de Login a Validación y expande a pantalla completa."""
        self.setCurrentWidget(self.delivery_validation_screen)
        self.showMaximized()  # Expande la pantalla a full
        self.delivery_validation_screen.cargar_datos_validacion(self.datos_validacion)

    def regresar_a_home(self):
        """Regresa a la pantalla de Home."""
        self.setCurrentWidget(self.home_screen)
        self.showNormal()
        self.setGeometry(100, 100, 500, 300)  # Restaura tamaño pequeño


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec())
