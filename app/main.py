from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import clients, invoices  # Importar las rutas de clientes y facturas
from app.models.invoice_models import Base
from app.db import engine  # Importar la función de creación de tablas
import pandas as pd
from io import StringIO


app = FastAPI(title="Facturas", version="2.0")

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://example.com",
    "https://www.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir las orígenes definidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload-csv/", tags=['Subir CSV'])
async def upload_csv(file: UploadFile = File(...)):
    # Verificar que el archivo sea un CSV
    if file.content_type != 'text/csv':
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV")

    # Leer el archivo CSV
    contents = await file.read()
    string_io = StringIO(contents.decode('utf-8'))
    
    try:
        # Crear un DataFrame de Pandas a partir del CSV
        df = pd.read_csv(string_io)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al procesar el CSV")

    # Aquí puedes realizar operaciones con el DataFrame (df)
    # Por ejemplo, obtener un resumen de los datos
    summary = df.describe().to_dict()  # Obtiene un resumen estadístico

    return JSONResponse(content={"data_summary": summary})

# Incluir routers
app.include_router(clients.router)  # Incluir el router de clientes
app.include_router(invoices.router)  # Incluir el router de facturas

Base.metadata.create_all(bind=engine)
