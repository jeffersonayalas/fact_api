from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.invoice_models import Factura, FacturaBase, FacturaResponse  # Asegúrate de importar tus modelos
from app.db import get_db
from typing import List
from pprint import pprint

router = APIRouter()

@router.post("/insertar/", response_model=FacturaResponse, tags=['Insertar Factura'])
async def insert_factura(factura: FacturaBase, db: Session = Depends(get_db)):
    new_factura = Factura(**factura.dict())
    db.add(new_factura)
    db.commit()
    db.refresh(new_factura)
    return new_factura  # Aquí puedes devolver el modelo de Pydantic si lo necesitas

# Endpoint al cual se le envía el id de cliente (rif) y retorna el número de factura
@router.get("/buscar-facturas/{id}", response_model=List[dict], tags=['Retornar Factura'])
async def get_fact(id: str, db: Session = Depends(get_db)):
    # Validar que el ID sea numérico
    if not id.isdigit():
        raise HTTPException(status_code=400, detail="ID de factura inválido")
    
    # Convertir el ID a entero
    id = int(id)
    
    # Buscar las facturas en la base de datos
    fact_query = db.query(Factura).filter(Factura.odoo_id == id).all()
    
    # Si no se encuentran facturas, lanzar una excepción 404
    if not fact_query:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    # Preparar los datos de las facturas para la respuesta
    # No regresamos el Odoo_id
    fact_data = []
    for fact in fact_query:
        fact_dict = fact.__dict__.copy()  # Convertir el objeto SQLAlchemy a un diccionario
        fact_dict.pop('_sa_instance_state', None)  # Eliminar metadatos de SQLAlchemy
        fact_dict.pop('odoo_id', None)  # Eliminar el campo 'odoo_id'
        fact_data.append(fact_dict)  # Agregar el diccionario a la lista de resultados

    return fact_data