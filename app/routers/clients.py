from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from app.models.invoice_models import ClienteResponse, ClienteBase, Cliente
from sqlalchemy.exc import IntegrityError
from app.db import get_db
from typing import List, Dict


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


@router.post("/buscar-codigo", response_model=Dict[str, str], tags=["Insertar Codigo de Galac"])
async def buscar_codigo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    resultados = {}

    # Crear un archivo para resultados
    with open('clientes.txt', "w") as archivo:
        # Obtener todos los clientes
        clientes = db.query(Cliente).all()

        # Leer el archivo .txt cargado
        contenido = await file.read()

        # Convertir el contenido a texto
        contenido_texto = contenido.decode("utf-8").splitlines()

        # Iterar sobre cada cliente
        for cliente in clientes:
            rif = cliente.rif.replace("-", "")

            # Iterar sobre el contenido del archivo
            for line in contenido_texto:
                array = line.split(";")

                # Obtener el RIF desde el archivo
                rif_txt = array[2].replace("-", "") if "-" in array[2] else array[2]

                # Comparar RIFs
                if rif == rif_txt:
                    codigo_galac = array[0]

                    # Escribir al archivo resultados
                    archivo.write(f"{rif} <----> {rif_txt}\n")
                    print(f"RIF BD: {rif} RIF TXT: {rif_txt} CODIGO G: {codigo_galac}")

                    # Verificar si cod_galac está vacío antes de asignar
                    if not cliente.cod_galac:  # Asumiendo que cod_galac es el nombre correcto del campo
                        cliente.cod_galac = codigo_galac  # Asigna el código de Galac
                        db.add(cliente)  # Marca el cliente para actualización

                        # Guardar el resultado en el diccionario
                        resultado_clave = cliente.rif
                        resultados[resultado_clave] = codigo_galac
                else:
                    archivo.write("RIF O CEDULA: " + str(rif) + "/n")

        # Hacer commit a la base de datos
        db.commit()

    return resultados

