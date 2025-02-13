import pandas as pd

# Leer el archivo CSV, saltando las primeras 7 filas para empezar desde la línea 8
df = pd.read_csv('ventas_enero_2024.csv', encoding='utf-8', skiprows=7)

def send_to_database(info):
    print(str(info) + "\n")

# Iterar a través de cada fila en el DataFrame
for index, row in df.iterrows():
    # Crear un nuevo diccionario para cada fila
    datos = {
        'fecha_factura': row['Fecha Factura'],
        'rif': row['RIF'],
        'nombre_o_razon_social': row['Nombre o Razon Social'],
        'n_de_control': row['N de Control'],
        'n_de_factura': row['N de Factura'],
        'total_ventas_con_iva': row['Total Ventas con IVA'],
        'moneda': 'Bs.S'
    }

    # Enviar los datos a la función
    send_to_database(datos)




    
