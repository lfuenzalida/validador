from app.database import get_db_gexus_connection, get_db_reg_connection
import psycopg2
import pandas as pd
import os 
from datetime import date
from app.config import Config
from flask import jsonify

def obtener_factura(nro_documento):
    """
    Obtiene la información general de una factura con el total de kilos netos.
    """
    sql = """
          SELECT 
            ef.nro_documento AS factura,
            c.razon_social AS cliente,
            c.rut_cliente AS rut,
            e.razon_social AS facturador,
            ef.total,  
            SUM(df.kilo_neto) AS kilo_neto_total,
            SUM(df.caja) AS cat_cajas
        FROM enc_venta ef
        JOIN det_venta df 
            ON ef.nro_documento = df.nro_documento 
            AND ef.nro_operacion = df.nro_operacion  -- 🔹 Solo las ventas de la última fecha
        JOIN cliente c
            ON c.rut_cliente = ef.rut_cliente 
        JOIN empresa e 
            ON e.rut_empresa = ef.rut_empresa 
        WHERE ef.nro_documento = %s
        AND ef.fecha_documento = (
            SELECT MAX(fecha_documento) 
            FROM enc_venta 
            WHERE nro_documento = %s
        )
        GROUP BY ef.nro_documento, c.razon_social, c.rut_cliente, e.razon_social, ef.total;
    """
    try:
        conn = get_db_gexus_connection()
        if not conn:
            return {"error": "No se pudo conectar a la base de datos"}, 500

        with conn.cursor() as cursor:
            cursor.execute(sql, (nro_documento, nro_documento))
            row = cursor.fetchone()

        conn.close()

        if row:
            return {
                "factura": row[0],
                "cliente": row[1],
                "rut": row[2],
                "facturador": row[3],
                "total": float(row[4]),
                "total kilos": float(row[5]),
                "total Cajas": int (row[6])
            }, 200
        else:
            return {"error": "Factura no encontrada"}, 404

    except Exception as e:
        return {"error": str(e)}, 500


def obtener_detalle_factura(nro_documento):
    """
    Obtiene los detalles de cada etiqueta en la factura.
    """
    sql = """
        SELECT 
            dve.nro_etiqueta, 
            c.descripcion AS corte, 
            e.descripcion AS marca,
            h.kilo_neto AS kilos
        FROM det_venta_etiqueta dve 
        INNER JOIN historial_etiqueta h 
            ON dve.nro_etiqueta = h.nro_etiqueta 
        INNER JOIN enc_venta ev 
            ON dve.nro_operacion = ev.nro_operacion 
            AND ev.nro_operacion = (
                SELECT MAX(nro_operacion) 
                FROM enc_venta 
                WHERE nro_documento = dve.nro_documento
            )
        INNER JOIN corte c 
            ON c.cod_corte = h.cod_corte 
        INNER JOIN envasado e 
            ON e.cod_envasado = h.cod_envasado 
        WHERE dve.nro_documento = %s
        ORDER BY e.descripcion ASC, c.descripcion ASC;
    """
    try:
        conn = get_db_gexus_connection()
        if not conn:
            return {"error": "No se pudo conectar a la base de datos"}, 500

        with conn.cursor() as cursor:
            cursor.execute(sql, (nro_documento,))
            rows = cursor.fetchall()

        conn.close()

        if not rows:
            return {"error": "No se encontraron detalles para la factura"}, 404

        detalles = [
            {
                "nro_etiqueta": row[0],  # Orden definido correctamente
                "corte": row[1],
                "marca": row[2],
                "kilos": float(row[3])
            }
            for row in rows
        ]

        return detalles, 200

    except Exception as e:
        return {"error": str(e)}, 500
    
def calcular_digito_verificador(rut):
    """
    Calcula el dígito verificador de un RUT chileno.
    :param rut: Número de RUT (sin dígito verificador).
    :return: Dígito verificador como string ('0'-'9' o 'K').
    """
    suma = 0
    multiplicador = 2
    for digito in reversed(str(rut)):
        suma += int(digito) * multiplicador
        multiplicador = 9 if multiplicador == 7 else multiplicador + 1
    resto = 11 - (suma % 11)
    if resto == 11:
        return '0'
    if resto == 10:
        return 'K'
    return str(resto)


def registrar_flujo(tipo_flujo, registros):
    """Procesa y registra los datos según el tipo de flujo (despacho o retiro)."""
    
    print(f"\n➡️ Recibiendo datos para {tipo_flujo}:")
    for reg in registros:
        print(reg)  # Muestra en consola los registros recibidos

    if tipo_flujo not in ['despacho', 'retiro']:
        print("❌ Error: Tipo de flujo no válido")
        return jsonify({"error": "Tipo de flujo no válido. Use 'despacho' o 'retiro'."}), 400

    connection = get_db_reg_connection()
    if connection is None:
        print("❌ Error: No se pudo conectar a la base de datos")
        return jsonify({"error": "No se pudo conectar a la base de datos."}), 500

    print("✅ Conexión a la base de datos establecida correctamente.")

    try:
        with connection.cursor() as cursor:
            for registro in registros:
                rut_cliente = registro['cliente_rut']
                digito_verificador = calcular_digito_verificador(rut_cliente)  # Calcula el dígito verificador
                
                print(f"🔎 Verificando cliente con RUT: {rut_cliente}-{digito_verificador}")

                # Validar existencia del cliente
                cursor.execute(
                    "SELECT COUNT(*) FROM clientes WHERE rut_cliente = %s AND dig_verificador = %s",
                    (rut_cliente, digito_verificador)
                )
                cliente_existe = cursor.fetchone()[0]

                # Si no existe, registrar el cliente automáticamente
                if cliente_existe == 0:
                    sql_insert_cliente = """
                    INSERT INTO clientes (rut_cliente, dig_verificador, razon_social)
                    VALUES (%s, %s, %s);
                    """
                    print(f"🆕 Registrando nuevo cliente: {rut_cliente} - {registro['cliente_nombre']}")
                    cursor.execute(sql_insert_cliente, (rut_cliente, digito_verificador, registro['cliente_nombre']))

                if tipo_flujo == 'despacho':
                    sql_despacho = """
                    INSERT INTO despacho (nro_factura, cliente_rut, cliente_nombre, nombre_validador, conductor, peoneta, vehiculo, patente, estado, fecha_validacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());
                    """
                    print(f"📦 Insertando despacho: {registro}")
                    cursor.execute(sql_despacho, (
                        registro['nro_factura'], rut_cliente, registro['cliente_nombre'], registro['nombre_validador'],
                        registro['conductor'], registro['peoneta'], registro['vehiculo'], registro['patente'],
                        registro['estado']
                    ))
                    id_despacho = cursor.lastrowid  # Capturar el ID de despacho registrado
                    print(f"✅ Despacho registrado con ID: {id_despacho}")

                    # Insertar detalles en `detalle_salida`
                    for etiqueta in registro.get('etiquetas_validadas', []):
                        sql_detalle_validadas = """
                        INSERT INTO detalle_salida (id_despacho, id_retiro, tipo_salida, nro_etiqueta, tipo_etiqueta)
                        VALUES (%s, NULL, 'despacho', %s, 'validada');
                        """
                        print(f"✅ Insertando etiqueta validada en despacho: {etiqueta}")
                        cursor.execute(sql_detalle_validadas, (id_despacho, etiqueta))

                    for etiqueta in registro.get('etiquetas_no_encontradas', []):
                        sql_detalle_no_encontradas = """
                        INSERT INTO detalle_salida (id_despacho, id_retiro, tipo_salida, nro_etiqueta, tipo_etiqueta)
                        VALUES (%s, NULL, 'despacho', %s, 'no_encontrada');
                        """
                        print(f"⚠️ Insertando etiqueta NO encontrada en despacho: {etiqueta}")
                        cursor.execute(sql_detalle_no_encontradas, (id_despacho, etiqueta))

                elif tipo_flujo == 'retiro':
                    sql_retiro = """
                    INSERT INTO retiro (nro_factura, cliente_rut, cliente_nombre, nombre_validador, quien_retira, refrigerado, patente, estado, fecha_validacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW());
                    """
                    print(f"📦 Insertando retiro: {registro}")
                    cursor.execute(sql_retiro, (
                        registro['nro_factura'], rut_cliente, registro['cliente_nombre'], registro['nombre_validador'],
                        registro['quien_retira'], registro['refrigerado'], registro['patente'], registro['estado']
                    ))
                    id_retiro = cursor.lastrowid  # Capturar el ID de retiro registrado
                    print(f"✅ Retiro registrado con ID: {id_retiro}")

                    # Insertar detalles en `detalle_salida`
                    for etiqueta in registro.get('etiquetas_validadas', []):
                        sql_detalle_validadas = """
                        INSERT INTO detalle_salida (id_despacho, id_retiro, tipo_salida, nro_etiqueta, tipo_etiqueta)
                        VALUES (NULL, %s, 'retiro', %s, 'validada');
                        """
                        print(f"✅ Insertando etiqueta validada en retiro: {etiqueta}")
                        cursor.execute(sql_detalle_validadas, (id_retiro, etiqueta))

                    for etiqueta in registro.get('etiquetas_no_encontradas', []):
                        sql_detalle_no_encontradas = """
                        INSERT INTO detalle_salida (id_despacho, id_retiro, tipo_salida, nro_etiqueta, tipo_etiqueta)
                        VALUES (NULL, %s, 'retiro', %s, 'no_encontrada');
                        """
                        print(f"⚠️ Insertando etiqueta NO encontrada en retiro: {etiqueta}")
                        cursor.execute(sql_detalle_no_encontradas, (id_retiro, etiqueta))

        print("🔄 Confirmando cambios en la base de datos...")
        connection.commit()
        print("✅ Cambios guardados correctamente.")

        return jsonify({"message": "Registros procesados y almacenados correctamente."}), 201

    except Exception as e:
        connection.rollback()
        print(f"❌ Error al registrar datos: {e}")
        return jsonify({"error": f"Error al registrar los datos: {e}"}), 500

    finally:
        connection.close()
        print("🔌 Conexión cerrada con la base de datos.")

