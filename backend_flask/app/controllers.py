from app.database import get_db_connection
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
            e.razon_social AS facturador,
            ef.total,  
            SUM(df.kilo_neto) AS kilo_neto_total
        FROM enc_factura ef
        JOIN det_factura df 
            ON ef.nro_documento = df.nro_documento 
        JOIN cliente c
            ON c.rut_cliente = ef.rut_cliente 
        JOIN empresa e 
            ON e.rut_empresa = ef.rut_empresa 
        WHERE ef.nro_documento = %s
        GROUP BY ef.nro_documento, c.razon_social, e.razon_social, ef.total;
    """
    try:
        conn = get_db_connection()
        if not conn:
            return {"error": "No se pudo conectar a la base de datos"}, 500

        with conn.cursor() as cursor:
            cursor.execute(sql, (nro_documento,))
            row = cursor.fetchone()

        conn.close()

        if row:
            return {
                "factura": row[0],
                "cliente": row[1],
                "facturador": row[2],
                "total": float(row[3]),
                "total kilos": float(row[4])
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
            h.kilo_neto as kilos
        FROM det_venta_etiqueta dve 
        INNER JOIN historial_etiqueta h ON dve.nro_etiqueta = h.nro_etiqueta 
        INNER JOIN corte c ON c.cod_corte = h.cod_corte 
        INNER JOIN envasado e ON e.cod_envasado = h.cod_envasado 
        WHERE dve.nro_documento = %s
        ORDER BY e.descripcion ASC, c.descripcion ASC;
    """
    try:
        conn = get_db_connection()
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


HISTORIAL_PATH = r"\\DESKTOP-KB0S585\validaciones\validaciones.xlsx" 

def inicializar_excel():
    """
    Inicializa el archivo Excel para guardar el historial de validaciones, 
    si no existe.
    """
    if not os.path.exists(HISTORIAL_PATH):
        columnas = [
            "Fecha", "Nombre Validador", "Número de Factura", "Resultado", "Detalle",
            "Conductor", "Peoneta", "Vehículo", "Patente"
        ]
        df = pd.DataFrame(columns=columnas)
        df.to_excel(HISTORIAL_PATH, index=False)
        print(f"✅ Archivo inicializado en {HISTORIAL_PATH}")
    else:
        print(f"✅ Archivo existente detectado en {HISTORIAL_PATH}")

def registrar_validacion(nombre_validador, nro_factura, etiquetas_incorrectas, conductor, peoneta, vehiculo, patente):
    """
    Registra la validación en el archivo Excel con todos los nuevos campos.
    """
    try:
        if not os.path.exists(HISTORIAL_PATH):
            inicializar_excel()
        
        # Formato de fecha DD-MM-AAAA
        formated_date = date.today().strftime("%d-%m-%Y")

        df = pd.read_excel(HISTORIAL_PATH)

        # **Corregir la conversión de la lista a cadena**
        etiquetas_faltantes_str = ", ".join(etiquetas_incorrectas) if etiquetas_incorrectas else "Todo correcto"

        nuevo_registro = {
            "Fecha": formated_date,
            "Nombre Validador": nombre_validador,
            "Número de Factura": nro_factura,
            "Resultado": "Completado" if not etiquetas_incorrectas else "Incompleto",
            "Detalle": etiquetas_faltantes_str,  # **Ahora se guarda como un string correctamente**
            "Conductor": conductor,
            "Peoneta": peoneta,
            "Vehículo": vehiculo,
            "Patente": patente
        }

        # Crear un nuevo DataFrame con el registro y concatenarlo al existente
        nuevo_df = pd.DataFrame([nuevo_registro])
        df = pd.concat([df, nuevo_df], ignore_index=True)
        df.to_excel(HISTORIAL_PATH, index=False)

        return {"message": "Validación registrada con éxito"}
    except Exception as e:
        print(f"❌ Error al registrar validación: {e}")
        return {"error": str(e)}
