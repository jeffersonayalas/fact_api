from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker, declarative_base

# Crear la URL de conexión
url = URL.create(
    drivername='postgresql',
    username='postgres',
    password='python24',
    host='localhost',
    port='5432',
    database='data_facturas'
)

# Crear el motor de SQLAlchemy
engine = create_engine(url)

# Crear una sesión
SessionLocal = sessionmaker(bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener una base de datos en cada petición
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
