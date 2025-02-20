import pandas as pd


def read_csv(ci, file):
    # Leer el archivo CSV, usando ';' como delimitador y omitiendo las primeras 7 filas
    df = pd.read_csv('ventas_enero_2025.csv', encoding='utf-8', sep=';', skiprows=7)

    # Imprimir las columnas disponibles
    #print("Columnas disponibles:", df.columns.tolist())

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip()

    facturas_cliente = []

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

        # Imprimir los datos para depuración
        # Verificar si el RIF coincide con el CI ingresado
        n_factura = str(datos['n_de_factura']).replace(".0", "")

        #print(n_factura)
        if ci in str(datos['rif']):
            facturas_cliente.append([n_factura, datos['n_de_control']])

    return facturas_cliente