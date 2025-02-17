from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker


# Crear la URL de conexión
url = URL.create(
    drivername='postgresql',
    username='postgres',
    password='python24',
    host='localhost',
    port='5432',
    database='data_facturas'
)

# Imprimir la URL para verificar
print(url)

engine = create_engine(url)
Session = sessionmaker(bind=engine)
session = Session()