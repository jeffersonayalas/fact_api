from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import clients, invoices  # Importar las rutas de clientes y facturas
#from app.db import init_db  # Importar la función de creación de tablas

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



# Incluir routers
app.include_router(clients.router)  # Incluir el router de clientes
app.include_router(invoices.router)  # Incluir el router de facturas
