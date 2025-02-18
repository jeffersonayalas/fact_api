#En este script se debe recibir el id de odoo, realizar la consulta a la base de datos de facturacion
#Y devolver las facturas del cliente

import xmlrpc.client
import json
import environ

env = environ.Env()
environ.Env.read_env()

def format_name(name):
    parts = name.split(' - ')

    if len(parts) == 2:
        return parts[1]
    
    else:
        return name

def buscar_cliente_odoo(ci :str):
    url      = env('ODOO_URL')
    db       = env('ODOO_DB')
    username = env('ODOO_USERNAME')
    password = env('ODOO_PASSW')

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    common.version()

    uid = common.authenticate(db, username, password, {})

    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    client_id = models.execute_kw(db, uid, password, 'res.partner.category', 'search', [[['name','=','Clientes']]])[0]

    model_search = 'identification_id' if ((ci[0] == "V" or ci[0] == "E") and len(ci[2:]) < 8) else 'vat'
    ci = ci[2:] if (ci[0] == "V" or ci[0] == "E") else ci
    print(f"CI: {ci}")

    client_info = models.execute_kw(db, uid, password, 'res.partner', 'search', [['&',[model_search,'like', ci],['category_id','=',[client_id]]]])

   
    if len(client_info) > 1:
        return 'mas de un id'

    if not client_info:
        return False
    # Luego, obtenemos la información del cliente usando el id
    client_info = models.execute_kw(db, uid, password, 'res.partner', 'read', [client_info[0]], {'fields': ['vat', 'identification_id', 'name', 'email', 'street', 'phone', 'ref']})

    if not client_info:
        return False
    
    #print(client_info)
    
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

buscar_cliente_odoo('V-22412921')