from io import StringIO
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
import pandas as pd
from sqlalchemy.orm import Session
from app.models.invoice_models import Factura, FacturaCreate  # Asegúrate de importar tus modelos
from app.db import get_db
import numpy as np

router = APIRouter()

# Función para convertir valores a flotante con manejo de excepciones
def convert_to_float(value):
    try:
        if value is None:
            return None
        if isinstance(value, str):
            return float(value.replace(',', '.'))
        return float(value)
    except (ValueError, TypeError):
        return None

# Función para convertir a tipo fecha con manejo de excepciones
def convert_to_date(value):
    try:
        if value is None:
            return None
        return pd.to_datetime(value).date()
    except (ValueError, TypeError):
        return None

@router.post("/upload-csv/", tags=['Subir CSV'])
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
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
    print("📄 Diccionario resultante:")
    print(data_dict)

    # Mapear y guardar en la base de datos
    for record in data_dict:
        factura_data = FacturaCreate(
            fecha=convert_to_date(record.get('Fecha Factura')),
            rif=record.get('RIF'),
            numero_control=record.get('N de Control'),
            monto=convert_to_float(record.get('Total Ventas con IVA')),
            moneda='VES',  # Aquí se podría hacer más flexible si fuera necesario
            razon_social=record.get('Nombre o Razon Social'),
            nota_debito=record.get('Nota de Debito'),
            nota_de_credito=record.get('Nota de Credito'),
            tipo_de_operacion=record.get('Tipo Operacion'),
            numero_documento=record.get('N Documento Afectado'),
            fecha_comprobante=convert_to_date(record.get('Fecha Comprobante Retencion')),
            base_imponible_g=convert_to_float(record.get('Base Imponible G')),
            por_alicuota_g=convert_to_float(record.get('% Alicuota G')),
            impuesto_iva_g=convert_to_float(record.get('Impuesto IVA G')),
            base_imponible_r=convert_to_float(record.get('Base Imponible R')),
            por_alicuota_r=convert_to_float(record.get('% Alicuota R')),
            impuesto_iva_r=convert_to_float(record.get('Impuesto IVA R')),
            base_imponible_a=convert_to_float(record.get('Base Imponible A')),
            por_alicuota_a=convert_to_float(record.get('% Alicuota A')),
            impuesto_iva_a=convert_to_float(record.get('Impuesto IVA A')),
            iva_retenido=convert_to_float(record.get('IVA Retenido')),
            igtf=convert_to_float(record.get('IGTF')),
            tasa_bcv=convert_to_float(record.get('Tasa BCV')),
            iva_cta_tercero=convert_to_float(record.get('IVA Cta Tercero'))
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

    return JSONResponse(content={"message": "CSV procesado y datos guardados correctamente"})