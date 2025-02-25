import pandas as pd
import requests

# Configura la URL de tu API
BASE_URL = "http://localhost:8000"  # Cambia según tu configuración
CLIENTE_ENDPOINT = f"{BASE_URL}/clientes/"

def leer_txt(archivo_txt):
    """Lee el archivo TXT e inserta los datos en la base de datos."""
    try:
        with open(archivo_txt, 'r', encoding='utf-8') as file:
            # Lee todas las lineas del archivo
            data_clientes = file.readlines()
            
        hoja_cliente = ""
        
        for linea in data_clientes:
            datos_cliente = linea.strip().split(";")  # strip() para eliminar espacios en blanco
            
            # Verifica que la línea tenga los elementos esperados
            if len(datos_cliente) in [26, 27]:  # Cambié para evitar valores mágicos
                cod_galac, nombre, rif = datos_cliente[0], datos_cliente[1], datos_cliente[2]

                dict_data = {
                    'codigo_galac': cod_galac,
                    'nombre_cliente': nombre,
                    'rif_cliente': rif
                }

                try:
                    #print("Cliente: ", datos_cliente)
                    insertar_clientes(dict_data)

                    sep = "---------------------------------------------\n"
                    hoja_cliente += str(f"{sep}Nombre: {nombre}\nRif: {rif}\n")

                except Exception as e:
                    print(f"Error al insertar cliente {nombre}. Error: {e}")
            else:
                print(f"Línea incorrecta: {linea.strip()}")
                continue

    except FileNotFoundError:
        print(f"Archivo {archivo_txt} no encontrado.")
    except Exception as e:
        print(f"Error al leer o procesar el archivo: {e}")

# Función para insertar clientes
def insertar_clientes(cliente):
    cliente_data = {
        "uuid": None,  # Se generará un UUID en el servidor
        "odoo_id": cliente.get('odoo_id', None),
        "rif": cliente.get('rif_cliente', None),
        "cod_galac": cliente.get('codigo_galac', None),
        "nombre_cliente": cliente.get('nombre_cliente')
    }
 
    try:
        response = requests.post(CLIENTE_ENDPOINT, json=cliente_data)

        if response.status_code == 200:
            print(f"Cliente creado: {cliente_data['nombre_cliente']}")
        else:
            print(f"Error al crear cliente {cliente_data['nombre_cliente']}: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con el servidor: {e}")

# Main
if __name__ == "__main__":
    leer_txt("db_contactos.txt")  # Cambia esto al nombre de tu archivo
