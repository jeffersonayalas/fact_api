from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.models.invoice_models import ClienteResponse, ClienteBase, Cliente
from sqlalchemy.exc import IntegrityError
from app.db import get_db
from typing import List, Dict

def verify_rif(rif):
    rif = rif.split("-")
    number_rif = rif[1]

    if len(number_rif) > 8 : #Devover posible rif 
        return number_rif


router = APIRouter()

@router.post("/clientes/", response_model=ClienteResponse, tags=['Insertar Cliente'])
async def insert_cliente(cliente: ClienteBase, db: Session = Depends(get_db)):
    # Verifica si ya existe un cliente con el mismo RIF
    existing_cliente = db.query(Cliente).filter(Cliente.rif.like(f"%{cliente.rif}%")).first()
    
    if existing_cliente:
        raise HTTPException(status_code=400, detail="El cliente ya existe con ese RIF.")
    
        existing_cliente = db.query(Cliente).filter(Cliente.odoo_id == cliente.odoo_id).first()

        if existing_cliente:
            # Aquí puedes decidir si quieres lanzar un error,
            # actualizar el cliente existente o manejarlo de otra manera.
            raise HTTPException(status_code=400, detail="El cliente ya existe con el mismo odoo_id.")
    
    # Crea una nueva instancia de Cliente usando los datos recibidos
    new_cliente = Cliente(**cliente.dict())

    # Añadir el cliente a la sesión de la base de datos
    db.add(new_cliente)

    # Confirmar los cambios en la base de datos
    db.commit()

    # Refrescar el objeto para obtener el estado más actualizado
    db.refresh(new_cliente)

    # Devolver el cliente como ClienteResponse, asegurando que uuid es un string
    return ClienteResponse(
        uuid=str(new_cliente.uuid),  # Convertir UUID a string
        odoo_id=str(new_cliente.odoo_id),  # Asegúrate de que otros campos también sean cadenas si es necesario
        rif=new_cliente.rif,
        cod_galac=new_cliente.cod_galac,
        nombre_cliente=new_cliente.nombre_cliente
    )

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


@router.post("/buscar-codigo", response_model=Dict[str, str], tags=["Insertar Codigo de Galac"])
async def buscar_codigo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    resultados = {}

    # Crear un archivo para resultados
    with open('clientes.txt', "a") as archivo:  # Usar "a" para agregar resultados
        try:
            # Obtener todos los clientes
            clientes = db.query(Cliente).all()

            # Leer el archivo .txt cargado
            contenido = await file.read()

            # Convertir el contenido a texto
            contenido_texto = contenido.decode("utf-8").splitlines()

            # Iterar sobre cada cliente
            for cliente in clientes:
                rif = cliente.rif.replace("-", "")

                # Inicializar codigo_galac
                codigo_galac = None 

                # Iterar sobre el contenido del archivo
                for line in contenido_texto:
                    array = line.split(";")
                    if len(array) < 3:  # Seguridad: Verificar que hay suficientes elementos
                        continue

                    # Obtener el RIF desde el archivo
                    rif_txt = array[2].replace("-", "") 

                    # Comparar RIFs
                    if rif == rif_txt:
                        codigo_galac = array[0]
                        # Escribir al archivo resultados
                        archivo.write(f"{rif} <----> {rif_txt}\n")
                        print(f"RIF BD: {rif} RIF TXT: {rif_txt} CODIGO G: {codigo_galac}")

                        # Verificar si cod_galac está vacío antes de asignar
                        if not cliente.cod_galac:  # Asegúrate que esta propiedad existe
                            cliente.cod_galac = codigo_galac  # Asigna el código de Galac
                            db.add(cliente)  # Marca el cliente para actualización

                        # Guardar el resultado en el diccionario
                        resultado_clave = cliente.rif
                        resultados[resultado_clave] = codigo_galac

                if codigo_galac is None:
                    archivo.write(f"RIF O CEDULA: {rif}\n")

            # Hacer commit a la base de datos
            db.commit()

        except Exception as e:
            archivo.write(f"Error: {str(e)}\n")
            raise

    return resultados


