import psycopg2
import pymysql
from app.config import Config

def get_db_gexus_connection():
    try:
        conn = psycopg2.connect(
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            host=Config.DB_HOST,
            port=Config.DB_PORT
        )
        return conn
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos: {e}")
        return None
    
def get_db_reg_connection():
    try:
        conn = pymysql.connect(
            host=Config.REG_HOST,
            user=Config.REG_USER,
            password=Config.REG_PASSWORD,
            database=Config.REG_NAME,
            port=int(Config.REG_PORT)
        )
        return conn
    except Exception as e:
        print(f"❌ Error al conectar con la base de datos MariaDB: {e}")
        return None