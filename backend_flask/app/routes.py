from flask import Blueprint, jsonify, request
from app.controllers import obtener_factura, obtener_detalle_factura, registrar_flujo

factura_bp = Blueprint('factura', __name__, url_prefix='/api')

@factura_bp.route('/factura/<int:nro_documento>', methods=['GET'])
def get_factura(nro_documento):
    response, status = obtener_factura(nro_documento)
    return jsonify(response), status

@factura_bp.route('/factura/<int:nro_documento>/detalles', methods=['GET'])
def get_factura_detalle(nro_documento):
    response, status = obtener_detalle_factura(nro_documento)
    return jsonify(response), status

@factura_bp.route('/<tipo_flujo>', methods=['POST'])
def flujo_endpoint(tipo_flujo):
    print(f"Solicitud recibida para flujo: {tipo_flujo}")
    """Recibe datos de validación y los registra según el tipo de flujo."""
    try:
        registros = request.get_json().get('registros', [])
        if not registros:
            return {"error": "No se enviaron registros."}, 400

        return registrar_flujo(tipo_flujo, registros)

    except Exception as e:
        return {"error": str(e)}, 500

@factura_bp.route('/test', methods=['GET'])
def test_endpoint():
    """
    Endpoint de prueba para verificar que el backend está corriendo correctamente.
    """
    return jsonify({"message": "El backend está funcionando correctamente."}), 200


