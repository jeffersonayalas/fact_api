from sqlalchemy import Column, Integer, String, Date as SQLAlchemyDate, Float
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

Base = declarative_base()

class Cliente(Base):
    __tablename__ = "clientes"
    odoo_id = Column(Integer, primary_key=True, nullable=True)
    rif = Column(String)
    cod_galac = Column(String)
    nombre_cliente = Column(String)

class ClienteBase(BaseModel):
    rif: str
    cod_galac: Optional[str] = None
    nombre_cliente: str

class ClienteResponse(BaseModel):
    odoo_id: int
    rif: str
    cod_galac: Optional[str] = None
    nombre_cliente: str

    class Config:
        from_attributes = True  # Cambiar orm_mode por from_attributes

class Factura(Base):
    __tablename__ = "facturas"
    id = Column(Integer, primary_key=True)
    fecha = Column(SQLAlchemyDate)  # Usando SQLAlchemy Date
    rif = Column(String)
    numero_control = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    moneda = Column(String, nullable=False)
    razon_social = Column(String)
    nota_debito = Column(String)
    nota_de_credito = Column(String)
    tipo_de_operacion = Column(String)
    numero_documento = Column(String)
    fecha_comprobante = Column(SQLAlchemyDate)
    fecha_comprobante_retencion = Column(SQLAlchemyDate)
    total_ventas_con_iva = Column(String)
    ventas_internas_no_grabadas = Column(String)
    base_imponible_g = Column(Float)
    por_alicuota_g = Column(Float)
    impuesto_iva_g = Column(Float)
    base_imponible_r = Column(Float)
    por_alicuota_r = Column(Float)
    impuesto_iva_r = Column(Float)
    base_imponible_a = Column(Float)
    por_alicuota_a = Column(Float)
    impuesto_iva_a = Column(Float)
    iva_retenido = Column(Float)
    igtf = Column(Float)
    tasa_bcv = Column(Float)
    iva_cta_tercero = Column(Float)


class FacturaBase(BaseModel):
    fecha: date  # Aquí se usa la clase date de datetime
    rif: str
    numero_control: str
    monto: float
    moneda: str
    razon_social: Optional[str] = None
    nota_debito: Optional[str] = None
    nota_de_credito: Optional[str] = None
    tipo_de_operacion: Optional[str] = None
    numero_documento: Optional[str] = None
    fecha_comprobante: Optional[date] = None  # Usar date
    fecha_comprobante_retencion: Optional[date] = None  # Usar date
    total_ventas_con_iva: Optional[str] = None
    ventas_internas_no_grabadas: Optional[str] = None
    base_imponible_g: Optional[float] = None
    por_alicuota_g: Optional[float] = None
    impuesto_iva_g: Optional[float] = None
    base_imponible_r: Optional[float] = None
    por_alicuota_r: Optional[float] = None
    impuesto_iva_r: Optional[float] = None
    base_imponible_a: Optional[float] = None
    por_alicuota_a: Optional[float] = None
    impuesto_iva_a: Optional[float] = None
    iva_retenido: Optional[float] = None
    igtf: Optional[float] = None
    tasa_bcv: Optional[float] = None
    iva_cta_tercero: Optional[float] = None

class Factura(FacturaBase):
    id: int  # ID para la respuesta
    class Config:
        orm_mode = True
