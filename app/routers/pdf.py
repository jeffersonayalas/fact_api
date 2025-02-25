from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import requests
import base64
from io import BytesIO

app = FastAPI()
router = APIRouter()

API_AUTH_URL = "https://emision.thefactoryhka.com.ve/api/Autenticacion"
API_PDF_URL = "https://emision.thefactoryhka.com.ve/api/DescargaArchivo"

TOKEN_USUARIO = "crnthbqdrqrx_tfhka"
TOKEN_PASSWORD = "_$/5ZQii,Q:W"

def get_token():
    datos = {"usuario": TOKEN_USUARIO, "clave": TOKEN_PASSWORD}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(API_AUTH_URL, json=datos, headers=headers)
        if response.status_code == 200:
            return response.json().get("token")
        else:
            raise HTTPException(status_code=response.status_code, detail="Error obteniendo token")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error en la solicitud: {str(e)}")

def obtain_pdf(numero, token):
    data = {"serie": "", "tipoDocumento": "01", "numeroDocumento": numero, "tipoArchivo": "PDF"}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    try:
        response = requests.post(API_PDF_URL, json=data, headers=headers)
        if response.status_code == 200:
            return response.content  # Retorna el contenido binario del PDF
        else:
            raise HTTPException(status_code=response.status_code, detail="Error obteniendo PDF")
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error en la solicitud: {str(e)}")

@router.get("/obtener-pdf/{numero}", tags=["Obtener PDF"])
async def obtener_pdf(numero: str):
    token = get_token()
    pdf_bytes = obtain_pdf(numero, token)
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": "inline; filename=documento.pdf"})


