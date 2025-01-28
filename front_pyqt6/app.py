import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMainWindow
from views.home import HomeScreen
from views.delivery import DeliveryScreen
from views.withdrawal import WithdrawalScreen
from views.deliveryValidation import DeliveryValidationScreen


class MainApp(QMainWindow):
    def __init__(self, flujo="despacho", datos_generales=None):
        super().__init__()
        self.setWindowTitle("Validador de Facturas")
        self.setGeometry(100, 100, 500, 300)

        if datos_generales is None:
            datos_generales = {
                "validador": "No definido",
                "conductor": "",
                "peoneta": "",
                "vehiculo": "",
                "patente": "",
                "quien_retira": "",
                "refrigerado": False
            }

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Configura las pantallas
        self.home_screen = HomeScreen(self)
        self.delivery_screen = DeliveryScreen(self)
        self.withdrawal_screen = WithdrawalScreen(self)
        self.delivery_validation_screen = DeliveryValidationScreen(self, flujo, datos_generales)

        self.stacked_widget.addWidget(self.home_screen)
        self.stacked_widget.addWidget(self.delivery_screen)
        self.stacked_widget.addWidget(self.withdrawal_screen)
        self.stacked_widget.addWidget(self.delivery_validation_screen)

        self.stacked_widget.setCurrentWidget(self.home_screen)


    def cambiar_a_delivery(self):
        """Cambia de Home a despacho."""
        self.stacked_widget.setCurrentWidget(self.delivery_screen)
        self.setGeometry(100, 100, 500, 300)

    def cambiar_a_withdrawal(self):
        """Cambia de Home a retiro."""
        self.stacked_widget.setCurrentWidget(self.withdrawal_screen)
        self.setGeometry(100, 100, 500, 300)

    def cambiar_a_pantalla_validacion(self, flujo, datos_generales):
        self.delivery_validation_screen = DeliveryValidationScreen(self, flujo, datos_generales)

        # Registra la pantalla en el stack si no está ya añadida
        if self.stacked_widget.indexOf(self.delivery_validation_screen) == -1:
            self.stacked_widget.addWidget(self.delivery_validation_screen)

        # Cambia a la pantalla de validación
        self.stacked_widget.setCurrentWidget(self.delivery_validation_screen)

    
    def regresar_a_home(self):
        """Regresa a la pantalla de Home."""
        self.stacked_widget.setCurrentWidget(self.home_screen)
        self.showNormal()
        self.setGeometry(100, 100, 500, 300)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec())
