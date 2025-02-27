import xmlrpc.client
import json

from dotenv import load_dotenv  # Importar python-dotenv
import os  # Para acceder a las variables de entorno

# Cargar variables de entorno desde el archivo .env
load_dotenv()



def format_name(name):
    parts = name.split(' - ')

    if len(parts) == 2:
        return parts[1]
    
    else:
        return name


def buscar_cliente_odoo(ci :str):
    url      = os.getenv('ODOO_URL')
    db       = os.getenv('ODOO_DB')
    username = os.getenv('ODOO_USERNAME')
    password = os.getenv('ODOO_PASSW')

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    common.version()

    uid = common.authenticate(db, username, password, {})

    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    client_id = models.execute_kw(db, uid, password, 'res.partner.category', 'search', [[['name','=','OPORTUNIDAD']]])[0]

    model_search = 'identification_id' if ((ci[0] == "V" or ci[0] == "E") and len(ci[2:]) < 8) else 'vat'
    ci = ci[2:] if (ci[0] == "V" or ci[0] == "E") else ci
    print(f"CI: {ci}")

    client_info = models.execute_kw(db, uid, password, 'res.partner', 'search', [['&',[model_search,'like', ci],['category_id','!=',[client_id]], ['parent_id', '=', False]]])

    print(client_info)
    # print(client_info)
    if len(client_info) > 1:
        return 'mas de un id'

    if not client_info:
        return False
    # Luego, obtenemos la información del cliente usando el id
    client_info = models.execute_kw(db, uid, password, 'res.partner', 'read', [client_info[0]], {'fields': ['vat', 'name', 'email', 'street', 'phone', 'ref']})

    if not client_info:
        return False
    
    print(client_info)
    
    client_info = client_info[0]
    print(client_info)

    name = format_name(client_info['name'])

    client = {
        'id':      client_info['id'],
        'name':    name,
        'email':   client_info['email'],
        'ci':      client_info['vat'],
        'street':  client_info['street'], 
        'phone':   client_info['phone'],
        'ref':     client_info['ref'] 
        }
    
    return client



def buscar_cliente_odoo2(ci: str):
    url      = os.getenv('ODOO_URL')
    db       = os.getenv('ODOO_DB')
    username = os.getenv('ODOO_USERNAME')
    password = os.getenv('ODOO_PASSW')

    # Conexión al servidor
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    common.version()

    uid = common.authenticate(db, username, password, {})

    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Obtener el ID de la categoría 'Clientes'
    client_id = models.execute_kw(db, uid, password, 'res.partner.category', 'search', [[['name', '=', 'Clientes']]])[0]

    # Determinar el campo de búsqueda basado en el formato de ci
    model_search = 'identification_id' if ((ci[0] == "V" or ci[0] == "E") and len(ci[2:]) < 8) else 'vat'
    ci = ci[2:] if (ci[0] == "V" or ci[0] == "E") else ci
    print(f"CI: {ci} || Model: {model_search}")

    # Búsqueda de cliente con filtros por identificación y category_id
    client_info = models.execute_kw(db, uid, password, 'res.partner', 'search',
                                    [['&', [model_search, 'like', ci], ['category_id', '=', client_id]]])

    if not client_info:
        return False

    # Leer información del cliente usando el ID obtenido
    client_info = models.execute_kw(db, uid, password, 'res.partner', 'read', [client_info],
                                    {'fields': ['parent_id', 'vat', 'name', 'email', 'street', 'phone', 'ref',
                                                'parent_name']})

    # Verificar si el cliente tiene un parent_id
    if client_info and client_info[0]['parent_id']:
        parent_id = client_info[0]['parent_id'][0]  # Obtener el ID del parent
        # Buscar información del parent_id
        parent_info = models.execute_kw(db, uid, password, 'res.partner', 'read', [parent_id],
                                        {'fields': ['id', 'name', 'vat', 'email', 'street', 'phone', 'ref']})

        parent_info = parent_info[0]
        client={
            'id': parent_info['id'],
            'name': parent_info['name'],
            'email': parent_info['email'],
            'ci': parent_info['vat'],
            'street': parent_info['street'],
            'phone': parent_info['phone'],
            'ref': parent_info['ref']
        }

        return client

    return False  # Si no hay parent_id, devolver False
