from sqlalchemy import Boolean, Column, Integer, String, Date, Float
from sqlalchemy.orm import declarative_base
from db import engine

Base = declarative_base()

class Clientes(Base):
    __tablename__ = "clientes"
    odoo_id = Column(Integer, primary_key=True)
    rif = Column(String)


class Facturas(Base):
    __tablename__ = "facturas"
    id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    rif = Column(String)
    numero_factura = Column(Integer, primary_key=True)  
    numero_control = Column(String, nullable=False)       
    monto = Column(Float, nullable=False)                  
    moneda = Column(String, nullable=False)  


Base.metadata.create_all(engine)  

