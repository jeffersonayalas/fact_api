# app/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends
from app.models.invoice_models import Base  # Asegúrate de importar la base de tus modelos
from sqlalchemy.engine import URL
from dotenv import load_dotenv  # Importar python-dotenv
import os  # Para acceder a las variables de entorno

# Cargar variables de entorno desde el archivo .env
load_dotenv()


# Configuración de la conexión a la base de datos
#DATABASE_URL = "postgresql://postgres:python24@localhost:5432/data_facturas"

drivername = os.getenv("DB_DRIVER")
username=os.getenv("DB_USER")
password=os.getenv("DB_PASSWORD")
host=os.getenv("DB_HOST")
port=os.getenv("DB_PORT")
database=os.getenv("DB_NAME")

DATABASE_URL = URL.create(
    drivername=drivername,
    username=username,
    password=password,
    host=host,
    port=port,
    database="data_facturas"#database
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Esta clase servirá como base para tus modelos
Base = declarative_base()

# Función de dependencia para obtener la sesión de la base de datos
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()  # Crea una nueva sesión
    try:
        yield db  # Devuelve la sesión para que se use en el endpoint
    finally:
        db.close()  # Cierra la sesión al finalizar
