
import os
import json
import requests
import http.client
import conect_sql as sql
import os

from dotenv import load_dotenv
load_dotenv()

#db_host = os.getenv('DB_HOST')
#db_user = os.getenv('DB_USER')
#db_pass = os.getenv('DB_PASSWORD')
#dn_n = os.getenv('DA_BASE')

#tk_op = os.getenv('TOKEN_OPEN')
TK_WAP = os.getenv('TOKEN_WAP')
debug = os.getenv('DEBUG')

toke_app = TK_WAP

#sirve para enviar mensajes de texto a los usuarios por whatsapp donde recibe "numero" y "mensaje"
def send_message(from_number, message_bot):
    conn = http.client.HTTPSConnection("graph.facebook.com")
    payload = json.dumps({
      "messaging_product": "whatsapp",
      "to": from_number,
      "text": {
        "body": message_bot
      }
    })
    headers = {
        'Authorization': toke_app ,
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/v14.0/103963179170556/messages", payload, headers)
    res = conn.getresponse()
    data = res.read()

#enviar documentos whatsapp
#import http.client
#import json
#def send_message(from_number):
#    conn = http.client.HTTPSConnection("graph.facebook.com")
#    payload = json.dumps({
#        "messaging_product": "whatsapp",
#        "recipient_type": "individual",
#        "to":  from_number,
#        "type": "document",
#        "document": { "link" : "https://repositorio.uta.edu.ec/bitstream/123456789/32675/1/t1793si.pdf"}
#            }
#    )
#    headers = {
#        'Content-Type': 'application/json',
#        'Authorization': 'Bearer EAAZAHFRCywvgBAPZClNahdDnaY4AEwofIxVQGlmDiwUVwE1xt8IBI8ciXGvkpfWb03RXuxyJ4Kul4aspt1V4ZCVjLZCzOzJcWm3zuZB7Yz5arWXiYRtrIkBB17mQ84Qjf26ROMlp0wQYZCwlZCZCxvy30U59htK4R6n9xwEjk1C4fr0URPZBlBSGQ'
#    }
#    conn.request("POST", "/v14.0/103963179170556/messages", payload, headers)#109788295241930/messages", payload, headers)#
#    res = conn.getresponse()
#    data = res.read()
#    print(data.decode("utf-8"))

#import requests
import conect_sql as sql
#import os
def mensajes_no_almacen():
    multimedi = sql.SQL_CONSULTA("SELECT id, from_number, type_mul, REPLACE(REPLACE(REPLACE(RIGHT(mime_type, 4), '/', ''), 'ment', 'docx'), 'heet', 'xlsx') AS tipo_archi, file_id, nombre_carpe FROM multimedia WHERE nombre_carpe IS NULL OR nombre_carpe = '';")
    for mensaj in multimedi:
        message_id, from_number, type_mul, tipo_archi, file_id, nombre_carpe = mensaj
        access_token = 'EAAZAHFRCywvgBAPZClNahdDnaY4AEwofIxVQGlmDiwUVwE1xt8IBI8ciXGvkpfWb03RXuxyJ4Kul4aspt1V4ZCVjLZCzOzJcWm3zuZB7Yz5arWXiYRtrIkBB17mQ84Qjf26ROMlp0wQYZCwlZCZCxvy30U59htK4R6n9xwEjk1C4fr0URPZBlBSGQ'
        api_url = f'https://graph.facebook.com/v16.0/{file_id}/'

        # Configura los encabezados de la solicitud
        headers = {'Authorization': f'Bearer {access_token}'}
        # Realiza la solicitud GET
        response = requests.get(api_url, headers=headers)
        # Verifica el código de respuesta
        if response.status_code == 200:
            # Maneja la respuesta de la solicitud
            media_data = response.json()
            url = media_data['url']

            # Realiza la solicitud GET y guarda el contenido en el archivo
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                file_name = f"{from_number}_{file_id}.{tipo_archi}"
                file_path = os.path.join("arcvihos_media", file_name)
                with open(file_path, 'wb') as file:
                    #print(file_path)
                    file.write(response.content)
                    sql.SQL_INSERTAR("UPDATE multimedia SET nombre_carpe = %s WHERE id = %s", (file_name, message_id))#(file_path, message_id))
            else:
                print(f'Error al descargar el archivo: {response.text}')
        else:
            print('Error al realizar la solicitud:', response.text)

#Funcion para enviar mensajes de WHATSAPP
def enviar_messages():
    try:
        # Consultar los mensajes pendientes en la base de datos
        envio = sql.SQL_CONSULTA("SELECT id, message_bot, from_number, estado FROM mensajes_whatsapp WHERE estado = 'pendiente'")
        # Iterar sobre cada mensaje pendiente
        if envio:
            for message_id, message_bot, from_number, estado in envio:
                # Enviar el mensaje utilizando el objeto wapp redirijirse a import whatsapp as wapp si requiere mas indormacion
                send_message(from_number, message_bot)
                # Actualizar el estado del mensaje a 'entregado' en la base de datos
                sql.SQL_INSERTAR("UPDATE mensajes_whatsapp SET estado = %s WHERE id = %s", ("entregado", message_id))
    except:
        pass