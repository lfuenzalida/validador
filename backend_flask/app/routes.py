from flask import Blueprint, jsonify, request
from app.controllers import obtener_factura, obtener_detalle_factura, registrar_validacion

factura_bp = Blueprint('factura', __name__)

@factura_bp.route('/factura/<int:nro_documento>', methods=['GET'])
def get_factura(nro_documento):
    response, status = obtener_factura(nro_documento)
    return jsonify(response), status

@factura_bp.route('/factura/<int:nro_documento>/detalles', methods=['GET'])
def get_factura_detalle(nro_documento):
    response, status = obtener_detalle_factura(nro_documento)
    return jsonify(response), status

@factura_bp.route('/validacion', methods=['POST'])
def validar_factura():
    data = request.get_json()
    nombre_validador = data.get("nombre_validador")
    nro_factura = data.get("nro_factura")
    etiquetas_incorrectas = data.get("etiquetas_incorrectas", [])  # **Debe ser una lista**
    conductor = data.get("conductor")
    peoneta = data.get("peoneta")
    vehiculo = data.get("vehiculo")
    patente = data.get("patente")

    if not nombre_validador or not nro_factura:
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    resultado = registrar_validacion(nombre_validador, nro_factura, etiquetas_incorrectas, conductor, peoneta, vehiculo, patente)
    return jsonify(resultado), 200
