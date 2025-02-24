from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.invoice_models import ClienteResponse, ClienteBase, Cliente
from sqlalchemy.exc import IntegrityError
from app.db import get_db
from typing import List

router = APIRouter()

@router.post("/clientes/", response_model=ClienteResponse, tags=['Insertar Cliente'])
async def insert_cliente(cliente: ClienteBase, db: Session = Depends(get_db)):
    # Verifica si ya existe un cliente con el mismo RIF
    existing_cliente = db.query(Cliente).filter(Cliente.rif == cliente.rif).first()
    
    if existing_cliente:
        raise HTTPException(status_code=400, detail="El cliente ya existe con ese RIF.")

    try:
        # Crea una nueva instancia de Cliente usando los datos recibidos
        new_cliente = Cliente(**cliente.dict())

        # Añadir el cliente a la sesión de la base de datos
        db.add(new_cliente)

        # Confirmar los cambios en la base de datos
        db.commit()

        # Refrescar el objeto para obtener el estado más actualizado
        db.refresh(new_cliente)

        print(new_cliente)  # Para ver el nuevo cliente agregado
        return new_cliente

    except IntegrityError as e:
        db.rollback()  # Deshacer la transacción en caso de un error de integridad
        raise HTTPException(status_code=400, detail="Error al crear cliente: Integridad de datos.")

    except Exception as e:  # Captura cualquier otra excepción
        db.rollback()  # Deshacer la transacción en caso de error
        print(new_cliente)  # Debugging
        raise HTTPException(status_code=500, detail=f"Error al crear cliente: {str(e)}")

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
