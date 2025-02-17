from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker


url = URL(
    drivername = 'postgres',
    username = 'postgres',
    password = 'python24',
    host = 'localhost',
    database = 'posgres',
    port = '5432'
)

engine = create_engine(url)
Session = sessionmaker(bind=engine)
session = Session()