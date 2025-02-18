from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.invoice_models import Factura, FacturaBase
from app.db import get_db

router = APIRouter()

@router.post("/insertar/", response_model=Factura, tags=['Insertar Factura'])
async def insert_factura(factura: FacturaBase, db: Session = Depends(get_db)):
    new_factura = Factura(**factura.dict())
    db.add(new_factura)
    db.commit()
    db.refresh(new_factura)
    return new_factura

#Endpoint al cual se le envia el id de cliente (rif y retorna el numero de factura)
@router.get("/{id}", response_model=Factura, tags=['Retornar Factura'])
async def get_fact(id: str, db: Session = Depends(get_db)):
    fact_query = db.query(Factura).filter(Factura.rif == id).all()

    if fact_query is None:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return fact_query
