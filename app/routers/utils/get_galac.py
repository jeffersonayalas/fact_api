from typing import List, Dict
from routers.csv import validar_y_generar_rif
from sqlalchemy.orm import Session
from db import get_db
from app.models.invoice_models import Cliente

""" 
async def buscar_cod_galac(rif: str, db: Session):
    #abrir archivo
    archivo = open("db_contactos.txt", "r")

    #Leemos contenido del archivo
    # Leer el archivo .txt cargado
    contenido = await archivo.read()
    # Convertir el contenido a texto
    contenido_texto = contenido.decode("utf-8").splitlines()

    for line in contenido_texto:
            array = line.split(";")
            rif_txt = array[2]
            cod_galac = array[0]

            if "-" in rif_txt:
                rif_txt = rif_txt.replace("-", "")

            #Validar el rif 
            if len(rif_txt) > 1:  # Asegurarse de que el RIF tiene al menos 2 caracteres
                rif_txt = rif_txt[0] + '-' + rif_txt[1:]  # Inserta un guion en la segunda posición
            
            datos_rif = validar_y_generar_rif(rif_txt)

            #Se realiza busqueda por rif generado
            for rif in datos_rif:
                client = db.query(Cliente).filter(Cliente.rif == rif).first()
                if client != None:
                      client.cod_galac = cod_galac

                else:
                
"""  

def buscar_cod_galac(rif):
    #Abrir archivo
    archivo = open("db_contactos.txt", "r")

    #Leemos contenido del archivo
    # Leer el archivo .txt cargado
    contenido = archivo.read()
    # Convertir el contenido a texto
    contenido_texto = contenido.decode("utf-8").splitlines()
    cod_galac = None

    if cod_galac != None:
        for line in contenido_texto:
                array = line.split(";")
                rif_txt = array[2].replace("-", "")
                cod_galac = array[0]

                if rif == rif_txt:
                    archivo.write(str(rif) + "<---->" +str(rif_txt) + "\n")
                    print("RIF BD: " + str(rif) + "RIF TXT: " + str(rif_txt) + "CODIGO G: " + str())
                    return cod_galac
    else:
         print("Codigo no encontrado. ")
         clientes = open("clientes.txt", 'w')
         clientes.write(str(rif) + "\n")



 
