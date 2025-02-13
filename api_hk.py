import requests

# URL del endpoint
BASE_URL = 'https://demoemisionv2.thefactoryhka.com.ve/api/DescargaArchivo'  # Cambia esto a la URL de tu API

# Función para enviar los datos al endpoint y descargar el documento
def download_document(serie, tipo_documento, numero_documento, tipo_archivo, token):
    # Preparar el cuerpo de la solicitud en formato JSON
    payload = {
        "serie": serie,
        "tipoDocumento": tipo_documento,
        "numeroDocumento": numero_documento,
        "tipoArchivo": tipo_archivo
    }

    # Configurar los encabezados
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'  # Token de acceso
    }

    # Realizar la solicitud POST
    try:
        response = requests.post(BASE_URL, json=payload, headers=headers)

        # Verificar el código de estado de la respuesta
        if response.status_code == 200:
            with open('documento_descargado.pdf', 'wb') as f:
                f.write(response.content)
            print('Documento descargado exitosamente como "documento_descargado.pdf".')
        else:
            print('Error al descargar el documento:', response.status_code, response.text)

    except requests.exceptions.RequestException as e:
        print('Error al realizar la solicitud:', str(e))

# Ejemplo de uso de la función
if __name__ == '__main__':
    # Información de prueba
    serie = ""  # Cambia esto si es necesario
    tipo_documento = "01"  # Código del documento
    numero_documento = "00372809"  # Número del documento
    tipo_archivo = "PDF"
    token = "yfmwkiujprcs_tfhka"  # Cambia este valor por tu token real

    download_document(serie, tipo_documento, numero_documento, tipo_archivo, token)


