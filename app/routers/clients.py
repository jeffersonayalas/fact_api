from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.invoice_models import ClienteResponse, ClienteBase, Cliente
from app.db import get_db

router = APIRouter()

router = APIRouter()

@router.post("/clientes/", response_model=ClienteResponse, tags=['Insertar Cliente'])
async def insert_cliente(cliente: ClienteBase, db: Session = Depends(get_db)):
    new_cliente = Cliente(**cliente.dict())
    db.add(new_cliente)
    db.commit()
    db.refresh(new_cliente)
    return new_cliente  # Aquí devuelve el objeto creado que ahora es compatible con Pydantic

@router.get("/clientes/{id}")
async def leer_cliente(id: int, Session: Session = Depends(get_db)):
    cliente = Session.query(Cliente).filter(Cliente.id == id).first()
    return cliente
