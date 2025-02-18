# app/db.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends
from app.models.invoice_models import Base  # Asegúrate de importar la base de tus modelos

# Configuración de la conexión a la base de datos
DATABASE_URL = "postgresql://postgres:python24@localhost:5432/data_facturas"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Esta clase servirá como base para tus modelos
Base = declarative_base()

# Función de dependencia para obtener la sesión de la base de datos
def init_db():
    # Crea todas las tablas en la base de datos solo si no existen
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()  # Crea una nueva sesión
    try:
        yield db  # Devuelve la sesión para que se use en el endpoint
    finally:
        db.close()  # Cierra la sesión al finalizar
