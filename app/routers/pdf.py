from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException
from app.db import get_db
import requests


def obtain_pdf(numero, token):

    # URL de la API
    API_URL = "https://emision.thefactoryhka.com.ve/api/DescargaArchivo"  # Reemplaza con la URL completa de la API

    # Token de autorización (reemplaza 'tu_token_aqui' con el token real que tienes)
    TOKEN = token

    # Datos que se enviarán en el JSON
    data = {
        "serie": "",
        "tipoDocumento": "01",
        "numeroDocumento": numero,
        "tipoArchivo": "PDF"
    }

    # Configurar los encabezados
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {TOKEN}'
    }

    try:
        # Realiza la petición POST a la API
        response = requests.post(API_URL, json=data, headers=headers)
        print(response.status_code)

        # Verifica si la solicitud fue exitosa
        if response.status_code == 200:
            # Guarda el contenido del PDF en un archivo
            with open("output.pdf", "wb") as pdf_file:
                pdf_file.write(response.content)
            #print("PDF:" + str(response.content))
            print("PDF guardado como output.pdf")
            return response.content
            
        else:
            print(f"Error en la solicitud: {response.status_code}")
            print(response.text)  # Muestra el mensaje de error de la API si lo hay

    except requests.exceptions.RequestException as e:
        # Maneja cualquier error durante la conexión
        print(f"Error haciendo la solicitud: {e}")


def get_token(token_usuario, token_password):
    # Datos a enviar en la solicitud
    datos = {
        "usuario": token_usuario,
        "clave": token_password
    }

    # URL de la API de autenticación
    URL = 'https://emision.thefactoryhka.com.ve/api/Autenticacion'

    # Configuración de los encabezados para la solicitud
    headers = {
        'Content-Type': 'application/json',
    }

    try:
        # Realiza la solicitud POST a la API
        response = requests.post(URL, json=datos, headers=headers)
        print(response.status_code)

        # Verifica el código de estado de la respuesta
        if response.status_code == 200:
            # Procesar la respuesta JSON para obtener el token
            print(response.text)
            response_data = response.json()  # Intenta decodificar la respuesta JSON
            token = response_data.get('token')  # Cambia 'token' si la estructura es diferente
            return token
        else:
            print(f"Error en la solicitud: {response.status_code}")
            print("Contenido de la respuesta:", response.text)  # Muestra el mensaje de error

    except requests.exceptions.RequestException as e:
        # Maneja cualquier error durante la conexión
        print(f"Error haciendo la solicitud: {e}")



def get_pdf(data):

    token_usuario = "crnthbqdrqrx_tfhka"  # Reemplaza con el usuario real
    token_password = "_$/5ZQii,Q:W"  # Reemplaza con la clave real

    token = get_token(token_usuario, token_password)
    num_document = data

    pdf = obtain_pdf(num_document, token)
    return pdf


router = APIRouter()

#Endpoint recibe numero de factura y retorna el PDF en bytes
@router.post("/obtener-pdf/", tags=["Obtener PDF"])
async def obtener_pdf(data):
    # Obtener el PDF codificado en bits utilizando la función get_api
    try:
        pdf_bytes = get_pdf(data)  # Llama a tu función
        return pdf_bytes

    except Exception as e:
        # Manejo de excepciones
        raise HTTPException(status_code=500, detail=str(e))
