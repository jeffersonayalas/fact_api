from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.invoice_models import Factura, FacturaBase, FacturaResponse  # Asegúrate de importar tus modelos
from app.db import get_db

router = APIRouter()

@router.post("/insertar/", response_model=FacturaResponse, tags=['Insertar Factura'])
async def insert_factura(factura: FacturaBase, db: Session = Depends(get_db)):
    new_factura = Factura(**factura.dict())
    db.add(new_factura)
    db.commit()
    db.refresh(new_factura)
    return new_factura  # Aquí puedes devolver el modelo de Pydantic si lo necesitas

# Endpoint al cual se le envía el id de cliente (rif) y retorna el número de factura
@router.get("/{id}", response_model=list[FacturaResponse], tags=['Retornar Factura'])
async def get_fact(id: str, db: Session = Depends(get_db)):
    fact_query = db.query(Factura).filter(Factura.rif == id).all()

    if not fact_query:  # Cambiado a not fact_query para verificar si la lista está vacía
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    return fact_query  # Aquí también puedes mapear a FacturaResponse si es necesario

