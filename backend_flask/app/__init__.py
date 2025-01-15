from flask import Flask
from app.routes import factura_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(factura_bp, url_prefix='/api')
    return app
