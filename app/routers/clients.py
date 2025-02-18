from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.invoice_models import ClienteResponse, ClienteBase, Cliente
from app.db import get_db
from typing import List

router = APIRouter()

@router.post("/clientes/", response_model=ClienteResponse, tags=['Insertar Cliente'])
async def insert_cliente(cliente: ClienteBase, db: Session = Depends(get_db)):
    new_cliente = Cliente(**cliente.dict())
    db.add(new_cliente)
    db.commit()
    db.refresh(new_cliente)
    return new_cliente  # Aquí devuelve el objeto creado que ahora es compatible con Pydantic

@router.get("/clientes/{id}", tags=['Leer Cliente'])
async def leer_cliente(id: str, Session: Session = Depends(get_db)):
    cliente = Session.query(Cliente).filter(Cliente.rif == id).first()

    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@router.get("/clientes/",response_model=List[ClienteResponse], tags=['Leer Clientes'])
async def leer_all_clients(Session: Session = Depends(get_db)):
    clientes = Session.query(Cliente).all()
    return clientes
