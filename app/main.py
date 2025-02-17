from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from src.models.invoice_models import Cliente, Factura
from db import session




app = FastAPI()

db: List[Cliente] = [
 Cliente(
 odoo_id=None,
 rif="J-310898065",
 cod_galac = "Z98FVWQ994",
 nombre_cliente = "MEDINA ALVAREZ DURLEY JHOAN",
 ),
 Factura(
 id="00345513",
 fecha = "22-01-2024",
 rif = "v-29694682",
 numero_control = "00-00266268",
 monto = 1273.91,
 moneda = "Bs.s"
 )
]

# CORS (Cross-Origin Resource Sharing) middleware configuration
origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://example.com",
    "https://www.example.com",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)



#Endpoint para insertar una factura

@app.post("/")
async def insert_fact(
    id: int, rif: str, n_control: str, monto: float, moneda: str, razon_social: str, nota_debito: str, nota_credito: str, tipo_operacion: str,
    num_documento: str, fecha_comprobante: str, fecha_comprobante_ret: str, total_ventas_iva: str, ventas_internas: str,
    
    ):
    return "Helloworld"




@app.get("/{id}") #Endpoind que recibe el numero de factura y retorna la informacion necesaria para la factura
async def get_fact(id: int):
    fact_query = session.query(Facturas).filter(Facturas.id == id)
    fact = fact_query.first()
    if fact is None:
        raise HTTPException(status_code = 404, detail="Not found")
    return {"greeting":"Hello world"}



