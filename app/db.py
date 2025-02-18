# app/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends
from app.models.invoice_models import Base  # Asegúrate de importar la base de tus modelos
from sqlalchemy.engine import URL

# Configuración de la conexión a la base de datos
#DATABASE_URL = "postgresql://postgres:python24@localhost:5432/data_facturas"

DATABASE_URL = URL.create(
    drivername='postgresql',
    username='postgres',
    password='python24',
    host='localhost',
    port='5432',
    database='data_facturas'
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Esta clase servirá como base para tus modelos
Base = declarative_base()
Base.metadata.create_all(bind=engine)
# Función de dependencia para obtener la sesión de la base de datos

def get_db():
    db = SessionLocal()  # Crea una nueva sesión
    try:
        yield db  # Devuelve la sesión para que se use en el endpoint
    finally:
        db.close()  # Cierra la sesión al finalizar
