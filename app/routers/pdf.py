from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException
from app.db import get_db
from methods import get_pdf


router = APIRouter()

@router.post("/obtener-pdf/", tags=["Obtener PDF"])
async def obtener_pdf(data):
  
    
    # Obtener el PDF codificado en bits utilizando la función get_api
    try:
        pdf_bytes = get_pdf(data)  # Llama a tu función

        if not pdf_bytes:
            raise HTTPException(status_code=404, detail="PDF no encontrado para el documento proporcionado.")

        # Convertir los bytes del PDF a un objeto BytesIO para la respuesta
        pdf_stream = BytesIO(pdf_bytes)

        # Retornar el PDF en la respuesta
        return StreamingResponse(pdf_stream, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename=documento_.pdf"
        })

    except Exception as e:
        # Manejo de excepciones
        raise HTTPException(status_code=500, detail=str(e))

# Para correr la aplicación usa: uvicorn nombre_del_archivo:app --reload
