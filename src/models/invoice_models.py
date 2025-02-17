from sqlalchemy import Boolean, Column, Integer, String, Date, Float
from sqlalchemy.orm import declarative_base
from db import engine

Base = declarative_base()


class Cliente(Base):
    __tablename__ = "clientes"

    odoo_id = Column(Integer, primary_key=True, nullable=True)
    rif = Column(String)
    cod_galac = Column(String)
    nombre_cliente = Column(String)

class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True) #Numero de factura
    fecha = Column(Date)
    rif = Column(String)
    numero_control = Column(String, nullable=False)       
    monto = Column(Float, nullable=False)                  
    moneda = Column(String, nullable=False)  
    razon_social = Column(String)
    nota_debito = Column(String)
    nota_de_credito = Column(String)
    tipo_de_operacion = Column(String)
    numero_documento = Column(String)
    fecha_comprobante = Column(Date)
    fecha_comprobante_retencion = Column(Date)
    total_ventas_con_iva = Column(String)
    ventas_internas_no_grabadas = Column(String)
    base_imponible_g = Column(String)
    por_alicuota_g = Column(String)
    impuesto_iva_g = Column(String)
    base_imponible_r = Column(String)
    por_alicuota_r = Column(String)
    impuesto_iva_r = Column(String)
    base_imponible_a = Column(String)
    por_alicuota_a = Column(String)
    impuesto_iva_a = Column(String)
    iva_retenido = Column(String)
    igtf = Column(String)
    tasa_bcv = Column(String)
    iva_cta_tercero = Column(String)



Base.metadata.create_all(bind=engine)  

