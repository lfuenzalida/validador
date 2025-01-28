import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    #CONNECTION MARIADB (REG)
    REG_NAME = os.getenv("DB_REG_NAME")   
    REG_USER = os.getenv("DB_REG_USER")
    REG_PASSWORD = os.getenv("DB_REG_PASSWORD") 
    REG_HOST = os.getenv("DB_REG_HOST")  
    REG_PORT = os.getenv("DB_REG_PORT")  
