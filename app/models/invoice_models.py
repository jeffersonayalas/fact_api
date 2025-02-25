from sqlalchemy import Column, Integer, String, Date as SQLAlchemyDate, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import uuid

Base = declarative_base()

class Cliente(Base):
    __tablename__ = "clientes"

    # Crea el campo uuid como un UUID, usando uuid4 para generar un valor por defecto
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    odoo_id = Column(String, unique=True, nullable=True)  # Campo único
    rif = Column(String, nullable=False)
    cod_galac = Column(String, nullable=True)
    nombre_cliente = Column(String, nullable=False)

class ClienteBase(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))  # UUID siempre generado
    odoo_id: Optional[str] = None
    rif: str
    cod_galac: Optional[str] = None
    nombre_cliente: str

class ClienteResponse(BaseModel):
    uuid: str  # UUID siempre se espera en la respuesta
    odoo_id: Optional[str] = None
    rif: str
    cod_galac: Optional[str] = None
    nombre_cliente: str

    class Config:  # Configurable a nivel de modelo
        orm_mode = True  # Habilitar orm_mode para la conversión entre ORM y modelos Pydantic

class Factura(Base):
    __tablename__ = "facturas"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # UUID auto-generado
    fecha = Column(SQLAlchemyDate)
    rif = Column(String)
    numero_control = Column(String, nullable=True)
    numero_factura = Column(String, nullable=True)
    monto = Column(Float, nullable=False)
    moneda = Column(String, nullable=False)
    razon_social = Column(String, nullable=True)  # Permitir valores nulos
    nota_debito = Column(String, nullable=True)
    nota_de_credito = Column(String, nullable=True)
    tipo_de_operacion = Column(String, nullable=True)
    numero_documento = Column(String, nullable=True)
    fecha_comprobante = Column(SQLAlchemyDate, nullable=True)
    fecha_comprobante_retencion = Column(SQLAlchemyDate, nullable=True)
    total_ventas_con_iva = Column(String, nullable=True)
    ventas_internas_no_grabadas = Column(String, nullable=True)
    base_imponible_g = Column(Float, nullable=True)
    por_alicuota_g = Column(Float, nullable=True)
    impuesto_iva_g = Column(Float, nullable=True)
    base_imponible_r = Column(Float, nullable=True)
    por_alicuota_r = Column(Float, nullable=True)
    impuesto_iva_r = Column(Float, nullable=True)
    base_imponible_a = Column(Float, nullable=True)
    por_alicuota_a = Column(Float, nullable=True)
    impuesto_iva_a = Column(Float, nullable=True)
    iva_retenido = Column(Float, nullable=True)
    igtf = Column(Float, nullable=True)
    tasa_bcv = Column(Float, nullable=True)
    iva_cta_tercero = Column(Float, nullable=True)
    odoo_id = Column(Integer, nullable=True)

class FacturaBase(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()))  # UUID siempre generado
    fecha: date
    rif: str
    numero_control: Optional[str] = None
    numero_factura: Optional[str] = None
    monto: float
    moneda: str
    razon_social: Optional[str] = None
    nota_debito: Optional[str] = None
    nota_de_credito: Optional[str] = None
    tipo_de_operacion: Optional[str] = None
    numero_documento: Optional[str] = None
    fecha_comprobante: Optional[date] = None
    fecha_comprobante_retencion: Optional[date] = None
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
    odoo_id: Optional[int] = None

class FacturaCreate(FacturaBase):
    pass  # No ID, ya que es auto-generado por la base de datos.

class FacturaResponse(FacturaBase):
    uuid: str  # ID siempre se espera en la respuesta

    class Config:  # Clase Config dentro de FacturaResponse.
        orm_mode = True  # Habilitar orm_mode.