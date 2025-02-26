from io import StringIO
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import pandas as pd
from sqlalchemy.orm import Session
from app.models.invoice_models import Cliente, Factura, FacturaCreate  # Asegúrate de importar tus modelos
from app.db import get_db
import re
import numpy as np
import asyncio


from .utils.odoo_con import buscar_cliente_odoo

router = APIRouter()

# Función para convertir valores a flotante con manejo de excepciones

def convert_to_float(value):
    try:
        if not value or str(value).strip() == '':
            return 0.0
        value = re.sub(r'[^\d,.-]', '', str(value))  # Elimina caracteres extraños
        value = value.replace(',', '.')  # Convertir a punto decimal
        return float(value)
    except (ValueError, TypeError):
        return 0.0



###########################################################
###########################################################
#########################################################

def agregar_ceros(numero):
    if not numero:
        return "00000000"
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

# Configuración básica del log de errores generales
logging.basicConfig(filename="error_log.log", level=logging.ERROR, format="%(asctime)s - %(message)s")

# Configuración del logger para cédulas no encontradas
cedula_not_found_logger = logging.getLogger("cedula_not_found")
cedula_not_found_logger.setLevel(logging.WARNING)  # Nivel de severidad WARNING

# Crear un manejador de archivo para este logger
handler = logging.FileHandler("cedula_not_found.log")
handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
cedula_not_found_logger.addHandler(handler)

###########################################################
###########################################################
###########################################################


def validar_y_generar_rif(documento):
    """
    Valida el formato del documento (RIF) y siempre retorna una lista.

    Parámetros:
        documento (str o int): El documento a validar o procesar.

    Retorna:
        - Si el formato es correcto, devuelve una lista con el documento.
        - Si el documento es solo numérico, devuelve una lista con las 4 configuraciones posibles.
        - Si el formato no es válido, devuelve una lista vacía.
    """
    # Convertir a string si es un número
    if isinstance(documento, int):
        documento = str(documento)
    
    documento = documento.strip().upper()  # Normalizar el documento
    
    # Expresión regular para validar el formato del RIF
    rif_pattern = re.compile(r'^[VJGP]-\d{6,}$')
    
    # Validar si el documento tiene un formato de RIF válido
    if rif_pattern.match(documento):
        print(f"✅ RIF válido: {documento}")
        return [documento]  # Retornar el documento en una lista
    
    # Si el documento es solo numérico, generar las 4 configuraciones
    if documento.isdigit():
        documentos = [f"{prefix}-{documento}" for prefix in ["V", "J", "G", "P"]]
        return documentos
    
    # Si no cumple con ningún formato válido, retornar una lista vacía
    return []

###########################################################
###########################################################
###########################################################

def search_client(rif: str, db: Session):
    """
    Primero busca al cliente en la BD local, si no se encuentra se busca en Odoo
    probando diferentes configuraciones de RIF y se mapea su RIF con su Odoo_Id.
    """
    print(f"--- 🔍 Buscando Cliente: {rif} 🔍 ---")
    posibles_rif = validar_y_generar_rif(rif)

    print(f"⚠️ Posibles RIF: {posibles_rif}")

    for rif_attempt in posibles_rif:
        print(f"🔍 Buscando cliente con RIF: {rif_attempt}")
        client = db.query(Cliente).filter(Cliente.rif == rif_attempt).first()

        if client:
            print(f"✅ Cliente encontrado en BD local: {client.__dict__}")
            return client.odoo_id

        print(f"🟡 Cliente no encontrado en BD local. Buscando en Odoo con {rif_attempt}...")
        client_odoo = buscar_cliente_odoo(rif_attempt)

        if isinstance(client_odoo, dict) and 'id' in client_odoo:
            odoo_id = client_odoo['id']

            # 🔍 **Verificar si el odoo_id ya existe en la BD**
            existing_client = db.query(Cliente).filter(Cliente.odoo_id == odoo_id).first()
            if existing_client:
                print(f"⚠️ Cliente ya existe en BD con diferente RIF: {existing_client.rif}")
                return existing_client.odoo_id

            new_client = Cliente(
                odoo_id=odoo_id,
                rif=rif_attempt,
                cod_galac="",
                nombre_cliente=client_odoo.get('name', 'Nombre no disponible')
            )

            try:
                db.add(new_client)
                db.commit()
                return new_client.odoo_id
            except IntegrityError:
                db.rollback()
                print(f"⚠️ Entrada duplicada detectada para Odoo ID {odoo_id}. Recuperando entrada existente...")
                existing_client = db.query(Cliente).filter(Cliente.odoo_id == odoo_id).first()
                
                if existing_client:
                    return existing_client.odoo_id
                else:
                    logging.error(f"⚠️ Error inesperado: Odoo ID {odoo_id} no encontrado tras duplicación.")
                    return None
            except Exception as e:
                db.rollback()
                print(f"🔴 Error al guardar cliente en BD: {str(e)}")
                logging.error(f"Error inesperado: {str(e)}")
                return None

    print(f"😥 Cliente no encontrado en Odoo para ningún RIF posible: {rif}")
    cedula_not_found_logger.warning(f"Cédula no encontrada: {rif}")
    return None


###########################################################
###########################################################
###########################################################

@router.post("/upload-csv/", tags=['Subir CSV'])
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Este endpoint recibe un archivo CSV generado por The factory y lo procesa para guardar los datos en la base de datos.
    """
    # Verificar que el archivo sea un CSV
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV")
    
    print(f"\ud83d\udcc2 Nombre del archivo: {file.filename}")

    # Leer el archivo CSV
    contents = await file.read()
    string_io = StringIO(contents.decode('utf-8'))
    
    try:
        df = pd.read_csv(string_io, encoding='utf-8', sep=';', skiprows=7, dtype=str)  # Lee todo como string
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Formato de CSV inválido")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Error de codificación, asegúrate de que el archivo esté en UTF-8")

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()

    # Reemplazar NaN, inf y -inf con None
    df = df.replace([np.nan, np.inf, -np.inf], None)

    # Convertir el DataFrame a un diccionario
    data_dict = df.to_dict(orient='records')

    # Lista para almacenar entradas duplicadas
    duplicados = []

    async def process_record(record):
        odoo_id = search_client(record.get('RIF'), db)
        print(f"\ud83d\udd0d ID de cliente en Odoo: {odoo_id}")

        existing_factura = db.query(Factura).filter(
            Factura.numero_control == str(record.get('N de Control')),
            Factura.rif == record.get('RIF')
        ).first()

        if existing_factura:
            duplicados.append(record)
            print(f"\ud83d\udd34 Entrada duplicada encontrada: {record}")
            return  # Ignorar esta entrada y continuar

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
            moneda='VES',
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

        factura = Factura(**factura_data.model_dump())

        try:
            db.add(factura)
            db.commit()
        except IntegrityError:
            db.rollback()
            print(f"⚠️ Factura duplicada detectada: {factura_data.numero_control}, {factura_data.rif}")
            duplicados.append(record)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al guardar en la base de datos: {str(e)}")

    # Ejecutar tareas en paralelo
    await asyncio.gather(*(process_record(record) for record in data_dict))

    return JSONResponse(content={
        "message": "CSV procesado y datos guardados correctamente",
        "duplicados": duplicados
    })
