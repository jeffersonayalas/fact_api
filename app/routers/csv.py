from io import StringIO
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import pandas as pd
from sqlalchemy.orm import Session
from app.models.invoice_models import Cliente, Factura, FacturaCreate  # Asegúrate de importar tus modelos
from app.db import get_db
import numpy as np

from .utils.odoo_con import buscar_cliente_odoo

router = APIRouter()

# Función para convertir valores a flotante con manejo de excepciones
def convert_to_float(value):
    try:
        if value is None or value == '':
            return 0.0  # En lugar de None, devolvemos 0.0
        if isinstance(value, str):
            return float(value.replace(',', '.'))
        return float(value)
    except (ValueError, TypeError):
        return 0.0  # En caso de error, devolvemos 0.0



###########################################################
###########################################################
#########################################################

def agregar_ceros(numero):
    return str(numero).zfill(8)

###########################################################
###########################################################
#########################################################

def convert_to_date(value):
    try:
        if value is None:
            return None
        return pd.to_datetime(value).date()
    except (ValueError, TypeError):
        return None
    
###########################################################
###########################################################
###########################################################

import logging
from sqlalchemy.exc import IntegrityError

# Configuración básica del log de errores
logging.basicConfig(filename="error_log.log", level=logging.ERROR, format="%(asctime)s - %(message)s")

def search_client(rif: str, db: Session):
    """
        Primero se busca al cliente en BD local, si no se encuentra se busca en Odoo
        y se mapea su RIF con su Odoo_Id.
    """
    client = db.query(Cliente).filter(Cliente.rif == rif).first()
    print(f"🔍 Buscando cliente con RIF: {rif}")
    
    if client is not None:
        print(f"✅ Cliente encontrado en la base de datos: {client}")
        return client.odoo_id  # Si ya existe, devolvemos el odoo_id

    print("🔴 Cliente no encontrado en la base de datos. Buscando en Odoo...")
    client = buscar_cliente_odoo(rif)  # Buscar en Odoo

    if isinstance(client, dict) and 'id' in client:
        print(f"🔍 Cliente encontrado en Odoo: {client}")
        new_client = Cliente(
            odoo_id=client.get('id'),
            rif=rif,
            cod_galac="",
            nombre_cliente=client.get('name', 'Nombre no disponible')
        )
        try:
            db.add(new_client)
            db.commit()
            return new_client.odoo_id  # Retornamos el 'id' de Odoo
        except IntegrityError as e:
            db.rollback()
            print(f"⚠️ Entrada duplicada detectada para Odoo ID {client.get('id')}, recuperando entrada existente...")

            # Buscar y devolver la entrada existente en la base de datos
            existing_client = db.query(Cliente).filter(Cliente.odoo_id == client.get('id')).first()
            
            if existing_client:
                logging.error(f"Duplicated entry: {existing_client}")
                return existing_client.odoo_id
            else:
                logging.error(f"⚠️ Error inesperado: el cliente con Odoo ID {client.get('id')} no fue encontrado después del error de duplicación.")
                return None
        except Exception as e:
            db.rollback()
            print(f"🔴 Error al guardar cliente en BD local: {str(e)}")
            logging.error(f"Error inesperado al insertar cliente: {str(e)}")
            return None
    else:
        print(f"🔴 Error al buscar cliente en Odoo: {client}")
        return None


###########################################################
###########################################################
###########################################################


@router.post("/upload-csv/", tags=['Subir CSV'])
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Este endpoint recibe un archivo CSV generadop por The factory y lo procesa para guardar los datos en la base de datos.
    """
    # Verificar que el archivo sea un CSV
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV")
    
    print(f"📂 Nombre del archivo: {file.filename}")

    # Leer el archivo CSV
    contents = await file.read()
    string_io = StringIO(contents.decode('utf-8'))
    
    try:
        # Leer el CSV, ignorando las primeras 7 filas y usando ';' como separador
        df = pd.read_csv(string_io, encoding='utf-8', sep=';', skiprows=7)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="Error al procesar el CSV")

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()

    # Reemplazar NaN, inf y -inf con None
    df = df.replace([np.nan, np.inf, -np.inf], None)

    # Convertir el DataFrame a un diccionario
    data_dict = df.to_dict(orient='records')

    # Imprimir el diccionario resultante
    # print("📄 Diccionario resultante:")
    # print(data_dict)

    # Lista para almacenar entradas duplicadas
    duplicados = []

    # Mapear y guardar en la base de datos
    for record in data_dict:
        odoo_id = search_client(record.get('RIF'), db)
        print(f"🔍 ID de cliente en Odoo: {odoo_id}")

        # Verificar si la factura ya existe
        existing_factura = db.query(Factura).filter(
            Factura.numero_control == str(record.get('N de Control')),
            Factura.rif == record.get('RIF')
        ).first()

        if existing_factura:
            duplicados.append(record)
            print(f"🔴 Entrada duplicada encontrada: {record}")
            continue  # Ignorar esta entrada y continuar con la siguiente

        numero_factura_valor = record.get('N de Factura')
        numero_factura = ""

        try:
            numero_factura = str(agregar_ceros(int(numero_factura_valor))) if numero_factura_valor else ""
        except (ValueError, TypeError):
            numero_factura = ""

        factura_data = FacturaCreate(
            fecha=convert_to_date(record.get('Fecha Factura')),
            rif=record.get('RIF'),
            numero_control=record.get('N de Control'),
            numero_factura=numero_factura,
            monto=convert_to_float(record.get('Total Ventas con IVA', 0.0)),
            moneda='VES',  # Se podría hacer más flexible si fuera necesario
            razon_social=record.get('Nombre o Razon Social'),
            nota_debito=record.get('Nota de Debito'),
            nota_de_credito=record.get('Nota de Credito'),
            tipo_de_operacion=record.get('Tipo Operacion'),
            numero_documento=record.get('N Documento Afectado'),
            fecha_comprobante=convert_to_date(record.get('Fecha Comprobante Retencion')),
            base_imponible_g=convert_to_float(record.get('Base Imponible G', 0.0)),
            por_alicuota_g=convert_to_float(record.get('% Alicuota G', 0.0)),
            impuesto_iva_g=convert_to_float(record.get('Impuesto IVA G', 0.0)),
            base_imponible_r=convert_to_float(record.get('Base Imponible R', 0.0)),
            por_alicuota_r=convert_to_float(record.get('% Alicuota R', 0.0)),
            impuesto_iva_r=convert_to_float(record.get('Impuesto IVA R', 0.0)),
            base_imponible_a=convert_to_float(record.get('Base Imponible A', 0.0)),
            por_alicuota_a=convert_to_float(record.get('% Alicuota A', 0.0)),
            impuesto_iva_a=convert_to_float(record.get('Impuesto IVA A', 0.0)),
            iva_retenido=convert_to_float(record.get('IVA Retenido', 0.0)),
            igtf=convert_to_float(record.get('IGTF', 0.0)),
            tasa_bcv=convert_to_float(record.get('Tasa BCV', 0.0)),
            iva_cta_tercero=convert_to_float(record.get('IVA Cta Tercero', 0.0)),
            odoo_id=odoo_id
        )


        # Crear la factura en base de datos
        factura = Factura(**factura_data.model_dump())  # Create SQLAlchemy object

        # Agregar la factura a la sesión
        db.add(factura)

    try:
        # Confirmar los cambios en la base de datos
        db.commit()
    except Exception as e:
        # Revertir los cambios en caso de error
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar en la base de datos: {str(e)}")

    return JSONResponse(content={
        "message": "CSV procesado y datos guardados correctamente",
        "duplicados": duplicados
    })