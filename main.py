TOKEN_WAP="Bearer EAAZAHFRCywvgBAPZClNahdDnaY4AEwofIxVQGlmDiwUVwE1xt8IBI8ciXGvkpfWb03RXuxyJ4Kul4aspt1V4ZCVjLZCzOzJcWm3zuZB7Yz5arWXiYRtrIkBB17mQ84Qjf26ROMlp0wQYZCwlZCZCxvy30U59htK4R6n9xwEjk1C4fr0URPZBlBSGQ"

from flask import Flask, render_template, abort, request, redirect, url_for, jsonify, send_from_directory, Response, flash, session
from flask_socketio import SocketIO, emit
import base64
import conect_sql as sql
import whatsapp as wapp
import os
import json
import requests
import mysql.connector
import http.client
import red_entrena as red_emb
import trabajo_pesado as tra_pe
import mostrar_data as m_data
import pandas as pd
import csv
from datetime import datetime
from dotenv import load_dotenv
import openai
from openai.embeddings_utils import cosine_similarity
from openai.embeddings_utils import get_embedding

from flask import Flask, request, abort, jsonify
load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
dn_n = os.getenv('DB_BASE')
tk_op = os.getenv('TOKEN_OPEN')
port = os.getenv('db_port')
TK_WAP = os.getenv('TOKEN_WAP')
debug = os.getenv('DEBUG')

WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN')

toke_app = TK_WAP
toke_api_chat = tk_op

app = Flask(__name__)
socketio = SocketIO(app)
WEBHOOK_TOKEN = "aY4AEwofIxVQGlmDiwUVwE1xt8IBI8ciXGvkpfWb03RXuxyJ4Kul4asp"
API_TOKEN = "5tDtpBAAU7bajnoMQLHpT3BlbkFJDapAfqdS6g7gm8WHa1tl_llamada"
def verificar_token(token):
    """
    Verifica si el token proporcionado coincide con el token de acceso esperado.
    """
    return token == API_TOKEN

##############################################################
token_1 = os.environ.get(toke_app)
app.secret_key = "clave_secreta"
app.config['SESSION_TYPE'] = 'filesystem'
###Session(app)

# login de cada usuario en el sistema
@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje_error = ''
    if request.method == "POST":
        usuario = request.form['fUsuario']
        contraseña = request.form['fContraseña']
        usuarios = sql.SQL_CONSULTA("select from_number, etiqueta, Permisos, nombre, Area, Proceso_a_cargo from empl_usr_da;")
        for u in usuarios:
            if u[0] == usuario and u[1] == contraseña:
                session['usuario'] = usuario
                session['num_usuario'] = usuarios.index(u)
                session['Permisos'] = u[2]  # Save the "Permisos" value in the session
                return redirect(url_for('home_1'))
        mensaje_error = 'Usuario o contraseña incorrectos. Por favor, intente nuevamente.'
    return render_template('1_a_login.html', mensaje_error=mensaje_error)

@app.route("/prueba3", methods=["GET", "POST"])
def home_1():
    if 'usuario' in session:
        usuario = session['usuario']
        perm_us = tra_pe.permisos_usuario(usuario)
        return render_template("2_listado.html", usuario=usuario, permisos=perm_us)
    else:
        return redirect(url_for('login'))

#Ruta para recivir y almacenar los datos de la api de WHATSAPP
@app.route("/webhook_app", methods=["GET", "POST"])
def webhook_app():
    if request.method == "GET":
        if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
            if not request.args.get("hub.verify_token") == "abcde":
                return "Verification token mismatch", 403
            return request.args["hub.challenge"], 200
        return "Hello world", 200
    elif request.method == "POST":
        body = request.json
        #print(body)
        if body.get("object") == "whatsapp_business_account":
            for entry in body["entry"]:
                for change in entry["changes"]:
                    if change.get("field") == "messages":
                        value = change.get("value")
                        if "messages" not in value or len(value["messages"]) == 0:
                            # Si el mensaje no tiene la clave "messages" o está vacío, lo ignoramos
                            continue
                        else:
                            if value["messages"][0]["type"] == "text":
                                phone_number_id = value["metadata"]["phone_number_id"]
                                from_number = value["contacts"][0]["wa_id"]
                                message_body = value["messages"][0]["text"]["body"]
                                insert_query = sql.SQL_INSERTAR("INSERT INTO mensajes_whatsapp (from_number, message_body) VALUES (%s, %s)", data=(from_number, message_body))
                                tra_pe.reordenar_clientes()
                                tra_pe.clasificar_area()
                                tra_pe.estado_usuario(from_number)
                                red_emb.responder_mensajes()
                                wapp.enviar_messages()
                            
                            elif value["messages"][0]["type"] in ["document", "audio", "image"]:
                                # Obtener los valores necesarios
                                from_number = body['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
                                message = body['entry'][0]['changes'][0]['value']['messages'][0]
                                message_type = message['type']
                                mime_type = None
                                file_id = None
                                if message_type == 'document':
                                    mime_type = message['document']['mime_type']
                                    file_id = message['document']['id']
                                elif message_type == 'audio':
                                    mime_type = message['audio']['mime_type']
                                    file_id = message['audio']['id']
                                elif message_type == 'image':
                                    mime_type = message['image']['mime_type']
                                    file_id = message['image']['id']
                                sql.SQL_INSERTAR("INSERT INTO multimedia (from_number, type_mul, mime_type, file_id) VALUES (%s, %s, %s, %s)", data=(from_number, message_type, mime_type, file_id))
                                wapp.mensajes_no_almacen()
                                tra_pe.reordenar_clientes()
                                tra_pe.clasificar_area()
        return "ok", 200
    pass
##############################################################

#modulo de call center
@app.route("/463nd4", methods=["GET", "POST"])
def home():
    if 'usuario' in session:
        usuario = session['usuario']
        perm_us = tra_pe.permisos_usuario(usuario)
        perm_agen = tra_pe.permisos_agenda(usuario)

        #Funcion para mostrar los mensajes en forma automatica
        mensajes_por_from_number = {}
        mensajes_por_from_number = m_data.mensajes_automaticos()
        
        #Funcion para mostrar los mensajes en forma automatica
        mensajes_por_from_number2 = {}
        mensajes_por_from_number2 = m_data.mensajes_intervenido()

        #Funcion para mostrar las pregutas de los formularios
        form_2 = {} 
        form_2 = m_data.mostrar_etiquetas()

        #Funcion para mostrar los usuarios para redirigir
        selec_usuario = {}
        selec_usuario = m_data.mostrar_redirigir_disponible()
        
        #funcion par mostrar los formularios disponibles
        formulario_app = {}
        formulario_app = m_data.mostrar_formularios()
        
        #Funcion para mostrar las agendas dispobibles
        selec_agenda = {}
        selec_agenda = m_data.mostrar_agenda_disponible()
        
        #Funcion para mostrar el nombre del cliente
        nombre_cliente = {}
        nombre_cliente = m_data.nombre_clientes()
        
        #boton de cerrar archivar o blokear
        if request.method == "POST" and 'ok_button' in request.form:
            tipo_peticion = request.form.get('tipo_peticion')
            from_number = request.form.get('from_number')
            if tipo_peticion == "":
                pass
            elif tipo_peticion != "":
                tra_pe.estado_usuario_cambio(from_number, tipo_peticion)
                pass

        # boton encargado de enviar la respuesta de las etiquetas
        if request.method == "POST" and 'ok_button_etiqueta' in request.form:
            tipo_formulario = request.form.get('tipo_respuesta_etiqueta')
            from_number2 = request.form.get('from_number2')
            boton = request.form.get('ok_button_formulario')
            mensaje = request.form.get('mensaje_texto2')
            if tipo_formulario == "":
                pass
            elif tipo_formulario != "":
                sql.SQL_INSERTAR("UPDATE tabla_cliente SET documento = %s WHERE from_number = %s AND (documento IS NULL OR documento = '') AND etiqueta = %s", (mensaje, from_number2, tipo_formulario))
                pass

        #boton redirigir cliente
        if request.method == "POST" and 'from_number_rediri' in request.form:
            tipo_peticion_re = request.form.get('tipo_redirigir_usr')
            from_number_re = request.form.get('from_number_rediri')
            if tipo_peticion_re == "":
                pass
            elif tipo_peticion_re != "":
                sql.SQL_INSERTAR("INSERT INTO redirecion_cliente (from_number, from_number_prof) VALUES (%s, %s)", data = (tipo_peticion_re, from_number_re))
                pass

        # boton encargado de solicitar formularios
        if request.method == "POST" and 'ok_button_formulario' in request.form:
            tipo_formulario = request.form.get('tipo_formulario')
            from_number2 = request.form.get('from_number2')
            boton = request.form.get('ok_button_formulario')
            #tipo = tipo_formulario
            documento = "999999"
            tipo_peticion = "CREAR"
            if tipo_formulario == "":
                pass
            elif tipo_formulario != "":
                tra_pe.ejec(from_number2, documento, tipo_formulario)
                pass

        #boton seleciona agenda
        if request.method == "POST" and 'from_number_rediri_agenda' in request.form:
            id_ = request.form.get('tipo_redirigir_usr_agenda')
            from_number_cliente = request.form.get('from_number_rediri_agenda')
            if id_ == "":
                pass
            elif id_ != "":
                sql.SQL_INSERTAR("UPDATE agenda SET from_number_cliente = %s WHERE id = %s", data=(from_number_cliente, id_))
                pass

        if request.method == "POST" in request.form:
            mensajes_por_from_number = m_data.mensajes_automaticos()
            mensajes_por_from_number2 = m_data.mensajes_intervenido()
            form_2 = m_data.mostrar_etiquetas()
            selec_usuario = m_data.mostrar_redirigir_disponible()

            formulario_app = m_data.mostrar_formularios()
            selec_agenda = m_data.mostrar_agenda_disponible()
            nombre_cliente = m_data.nombre_clientes()

        form1 = formulario_app

        return render_template("3_call_center_prueba.html", mensajes = mensajes_por_from_number, 
                            mensajes2 = mensajes_por_from_number2, selec_usu = selec_usuario, 
                            agend_a = selec_agenda, respt_form = form_2, 
                            #form1 = formulario_app, usuario = usuario,
                            form1 = form1, usuario = usuario,
                            nombre_clien = nombre_cliente, permiso = perm_us)
#################################################################################################

@app.route("/save-message", methods=["POST"])
def save_message():
    # Obtener el mensaje y from_number del formulario
    message_bot = request.form["message"]
    from_number = request.form["from_number"]
    # Insertar el mensaje en la base de datos
    sql.SQL_INSERTAR("INSERT INTO mensajes_whatsapp (from_number, message_bot, estado, tipo_com) VALUES (%s, %s, %s, %s)", data = (from_number, message_bot, "pendiente", "persona"))
    wapp.enviar_messages()# responder el mensaje a el usuario
    tra_pe.reordenar_clientes()
    tra_pe.clasificar_area()
    tra_pe.estado_usuario_cambio(from_number, "Persona")
    # Devolver una respuesta vacía con un código de estado 200
    return "", 200

@app.route("/save-message", methods=["POST"])
def save_message2():
    # Obtener el mensaje y from_number del formulario
    message_bot = request.form["message2"]
    from_number = request.form["from_number2"]
    # Insertar el mensaje en la base de datos
    sql.SQL_INSERTAR("INSERT INTO mensajes_whatsapp (from_number, message_bot, estado, tipo_com) VALUES (%s, %s, %s, %s)", data = (from_number, message_bot, "pendiente", "persona"))
    wapp.enviar_messages()# responder el mensaje a el usuario
    tra_pe.reordenar_clientes()
    tra_pe.clasificar_area()
    tra_pe.estado_usuario_cambio(from_number, "Persona")
    # Devolver una respuesta vacía con un código de estado 200
    return "", 200
###############################################################################

def send_message(data):
    socketio.emit('message', data)

#################################################################################################
@app.route("/adm1z", methods=["GET", "POST"])
def home_2():
    if 'usuario' in session:
        usuario = session['usuario']
        perm_us = tra_pe.permisos_usuario(usuario)
        perm_agen = tra_pe.permisos_agenda(usuario)
        #print(usuario)
        #print(perm_us)

        selected_number = None
        #selected_number = None
        mensajes_por_from_number2 = {}  # muestra los datos de la etiqueta bloque 2
        form_2 = {}  # muestra las preguntas del bot en el bloque 3
        eti_app = {}  # muestra los datos de la etiqueta bloque 4
        #dicionario datos usuarios que se agendaron y redirecionaron
        selec_redireccion = {}
        selec_agenda_pa = {}
        #muestra datos basicos de administracion
        formulario_app = {}
        selec_agenda = {}
        selec_usuario = {}
        #muestra datos basicos del cliente
        nombre_cliente = {}
        # llama a los datos iniciales para mostrar
        selec_redireccion, selec_agenda_pa = m_data.mostrar_datos_actualizados_clinte()
        selec_usuario = m_data.mostrar_redirigir_disponible()
        formulario_app = m_data.mostrar_formularios()
        selec_agenda = m_data.mostrar_agenda_disponible()
        #print("peticion de datos iniciales")
        nombre_cliente = m_data.nombre_clientes()
        
        if request.method == "POST" and "selected_value" in request.form:
            mensajes_por_from_number2 = {}  # muestra los datos de la etiqueta bloque 2
            form_2 = {}  # muestra las preguntas del bot en el bloque 3
            eti_app = {}  # muestra los datos de la etiqueta bloque 4
            selected_number = request.form.get("selected_value")
            selected_number = str(selected_number.split(",")[0])
            
            # Resto del código para obtener los datos que deseas enviar a la plantilla
            selec_redireccion, selec_agenda_pa = m_data.mostrar_datos_actualizados_clinte()
            selec_usuario = m_data.mostrar_redirigir_disponible()

            formulario_app = m_data.mostrar_formularios()
            selec_agenda = m_data.mostrar_agenda_disponible()
            nombre_cliente = m_data.nombre_clientes()
            resultado_prueba = m_data.procesar_datos(selected_number)
            mensajes_por_from_number2, form_2, eti_app = resultado_prueba
            
        # boton solicitar informacion de el usuario en lado izquierdo despliega los mensajes del usuario
        if request.method == "POST" and 'phone_number' in request.form:
            selected_number = request.form.get("phone_number")
            mensajes_por_from_number2, form_2, eti_app = m_data.procesar_datos(selected_number)
            print("boton solicitar informacion de el usuario en lado izquierdo")

    ###############################################################################
        area_envio = "CALL_CENTER"
        data_cliente = tra_pe.selecionar_areas(area_envio) 

            #boton redirigir cliente
        if request.method == "POST" and 'from_number_rediri' in request.form and 'ok_button_redirec' in request.form:
            print("boton redirigir cliente")
            tipo_peticion_re = request.form.get('tipo_redirigir_usr')
            from_number_re = request.form.get('from_number_rediri')
            if tipo_peticion_re == "":
                pass
            elif tipo_peticion_re != "":
                sql.SQL_INSERTAR("INSERT INTO redirecion_cliente (from_number, from_number_prof) VALUES (%s, %s)", 
                                data = (tipo_peticion_re, from_number_re))
                pass
            mensajes_por_from_number2, form_2, eti_app = m_data.procesar_datos(from_number_re)

        #boton selecionar agenda
        if request.method == "POST" and 'from_number_rediri_agenda' in request.form and 'ok_button_agenda' in request.form:
            print("boton selecionar agenda")
            id_ = request.form.get('tipo_redirigir_usr_agenda')
            from_number_cliente = request.form.get('from_number_rediri_agenda')
            if id_ == "":
                pass
            elif id_ != "":
                sql.SQL_INSERTAR("UPDATE agenda SET from_number_cliente = %s WHERE id = %s", data=(from_number_cliente, id_))
                pass
                #solicita actualizacion del os datos del usuario
            mensajes_por_from_number2, form_2, eti_app = m_data.procesar_datos(from_number_cliente)

        # boton encargado de solicitar formularios
        if request.method == "POST" and 'ok_button_formulario' in request.form:
            tipo_formulario = request.form.get('tipo_formulario')
            from_number2 = request.form.get('from_number2')
            #tipo = tipo_formulario
            documento = "999999"
            #tipo_peticion = "CREAR"
            if tipo_formulario == "":
                pass
            elif tipo_formulario != "":
                tra_pe.ejec(from_number2, documento, tipo_formulario)#tipo_peticion)
                pass
            mensajes_por_from_number2, form_2, eti_app = m_data.procesar_datos(from_number2)

        #peticion de mensajes
        if request.method == "POST" and 'message' in request.form:
            print("peticion de mensajes")
            message_bot = request.form.get('message')
            from_number = request.form.get('from_number2')
            if message_bot != "":
                sql.SQL_INSERTAR("UPDATE tabla_cliente SET documento = %s WHERE from_number = %s AND (documento IS NULL OR documento = '') LIMIT 1", (message_bot, from_number))
                pass
            elif message_bot == "":
                pass
            mensajes_por_from_number2, form_2, eti_app = m_data.procesar_datos(from_number)

        # boton para modificar etiquetas
        if request.method == "POST" and 'ok_button_etiqueta_editar' in request.form:
            from_number = request.form.get('from_number2')
            id_ap = request.form.get('index_cols')
            tipo_res = request.form.get('tipo_respuesta_etiqueta_modificar')
            if id_ap != "" and tipo_res == "Editar":
                sql.SQL_INSERTAR("UPDATE tabla_cliente SET id = %s, documento = %s WHERE id = %s AND (documento IS NOT NULL)", (id_ap, "", id_ap))
                pass
            if id_ap != "" and tipo_res == "Eliminar":
                sql.SQL_INSERTAR("DELETE FROM tabla_cliente WHERE id = %s", (id_ap,))
                pass
            elif id_ap == "":
                pass
            mensajes_por_from_number2, form_2, eti_app = m_data.procesar_datos(from_number)
        
        if request.method == 'POST' and 'fecha' in request.form:
            fecha_seleccionada = request.form['fecha']      
                    
            if fecha_seleccionada != "":
                # Obtener la fecha actual
                fecha_actual = datetime.now().date()
                # Convertir la fecha seleccionada a formato datetime
                fecha_seleccionada_dt = datetime.strptime(fecha_seleccionada, '%m/%d/%Y').date()
                tipo_num = request.form.get('from_number_rediri')

                comp = tra_pe.revisar_fecha_agenda(request.form.get('from_number_rediri'))

                fecha_existe = False
                for from_number_user, fecha in comp:
                    if fecha_seleccionada_dt == fecha:
                        fecha_existe = True
                        break

                if fecha_existe:
                    print('La fecha seleccionada ya existe en la agenda para el usuario correspondiente.')
                    mensaje = 'La fecha seleccionada ya existe en la agenda para el usuario correspondiente.'
                elif fecha_seleccionada_dt < fecha_actual:
                    mensaje = 'Alerta: La fecha seleccionada es pasada.'
                else:
                    from_number = tipo_num
                    fecha = fecha_seleccionada_dt
                    cliente = "PENDIENTE"
                    horas = ["08:00","09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00","17:00","18:00","19:00"]
                    for hora in horas:
                        sql.SQL_INSERTAR("INSERT INTO agenda (from_number_user, fecha, hora, from_number_cliente) VALUES (%s, %s, %s, %s)", data=(from_number, fecha, hora, cliente))
                    #mensaje = 'Fecha Creada.'
                    selec_redireccion, selec_agenda_pa = m_data.mostrar_datos_actualizados_clinte()
                        ###agenda_confirmar_p = m_data.agenda_confirmar()
            elif fecha_seleccionada == "":
                #mensaje = ''
                pass

        # modificar datos de 
        if request.method == "POST" and 'ok_button__confirmar' in request.form:        
            if request.form.get('tipo_mensaje') == "PENDIENTE" and request.form.get('index__cols') != "" and request.form.get('r__modificar') == "Eliminar" :
                sql.SQL_INSERTAR("DELETE FROM agenda WHERE id = %s", (request.form.get('index__cols'),))
                selec_redireccion, selec_agenda_pa = m_data.mostrar_datos_actualizados_clinte()
            elif request.form.get('tipo_mensaje') == "PENDIENTE" and request.form.get('index__cols') != "" and request.form.get('r__modificar') == "Confirmar" :
                sql.SQL_INSERTAR("UPDATE agenda SET from_number_cliente = NULL WHERE id = %s", (request.form.get('index__cols'),))
                selec_redireccion, selec_agenda_pa = m_data.mostrar_datos_actualizados_clinte()
            else:
                pass
        form1 = formulario_app
        return render_template("4_panel_web.html", usuario=usuario, msj2=mensajes_por_from_number2, 
                            form1 = formulario_app, respt_form = form_2, selec_usu = selec_usuario, 
                            agend_a = selec_agenda, sel_age_pa = selec_agenda_pa, 
                            selec_redire = selec_redireccion, eti_app_m = eti_app,
                            nombre_clien = nombre_cliente, permiso = perm_us, perm_agen = perm_agen)
#################################################################################################

@app.route('/ENTRENAMSJ', methods=['POST', 'GET'])
def ENTRENAMSJ():
    mjs_entre_re = {}
    mjs_entre_re = m_data.entrenar_datos()
    nombre_personal = {}
    nombre_personal = m_data.nombre_personal_1()
    mjs_respu_re = {}
    mjs_respu_re = m_data.respu_entre_datos()
    
    if request.method == "POST" and 'enviar_confirmar' in request.form:
        nombre_form = request.form.get("index_nombre_form")
        datos_adicionales = ','.join(['"{}"'.format(item) for item in request.form.getlist("casillas[]")])
        codigo = 'datos_adicionales = [{}]\n'.format(datos_adicionales)
        separador = "*s*"
        casillas = [f"{item}{separador}{nombre_form}" for item in request.form.getlist('casillas[]')]

        with open('respuestas_empresa.csv', 'w', newline='', encoding='utf-8') as csvfile:
            # Define the field names for the CSV file
            fieldnames = ['texto']
            # Create a CSV writer object using DictWriter
            csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Write the header row
            csvwriter.writeheader()
            # Write the 'casillas' list as rows in the 'texto' column
            for casilla in casillas:
                csvwriter.writerow({'texto': casilla})
        red_emb.embed_text(path="respuestas_empresa.csv", tabla_sql="medio_embeddings")

        # If you want to apply the lambda function to each item in the list, you can do this:
        ##casilla2_list = [get_embedding(casilla, engine='text-embedding-ada-002') for casilla in casillas]
        ##print(casilla2_list)

        # Convert casilla2_list to a string representation (e.g., JSON)
        ##casilla2_list_str = json.dumps(casilla2_list)

        # Conexión a la base de datos
        ##cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, database=dn_n)
        ##cursor = cnx.cursor()

        # Save casilla and casilla2_list_str as separate fields in the database
        ##query = "INSERT INTO medio_embeddings (texto, embedding) VALUES (%s, %s)"
        ##for casilla, embedding in zip(casillas, casilla2_list_str):
        ##    values = (casilla, embedding)
        ##    cursor.execute(query, values)

        # Cierre de la conexión a la base de datos
        ##cnx.commit()
        ##cursor.close()
        ##cnx.close()
    return render_template('6_MSJ.html',nombre_pers = nombre_personal, form_1 = mjs_entre_re, form_7 = mjs_respu_re)#, nombre_pers = nombre_personal)

#descargar archivos
@app.route('/descargar/<nombre_archivo>')
def descargar_archivo(nombre_archivo):
    # Ruta de la carpeta que contiene el archivo
    ruta_carpeta = 'arcvihos_media/'
    # Genera la ruta completa del archivo
    ruta_archivo = os.path.join(ruta_carpeta, nombre_archivo)
    # Verifica si el archivo existe
    if os.path.isfile(ruta_archivo):
        # Retorna el archivo para su descarga
        return send_from_directory(ruta_carpeta, nombre_archivo, as_attachment=True)
    else:
        # Retorna un mensaje de error si el archivo no existe
        return 'Archivo no encontrado'

@app.route('/')
def index():
    return render_template('1_a_login.html')

# cerrar cesion
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'usuario' in session:
        if request.method == 'POST' and 'cerrar' in request.form:
            session.pop('usuario', None)
            flash('You have been logged out successfully.')
    return redirect(url_for('index'))

# maneja todas las url si intentan acceder no permite
@app.before_request
def before_request():
    if 'usuario' not in session and request.endpoint != 'login' and request.endpoint != 'static':
        if request.endpoint != 'webhook_app':
            return redirect(url_for('login'))

def search_results(query):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    query = "SELECT DISTINCT mc.from_number, tc.documento, tc.etiqueta, CONCAT(COALESCE(mc.from_number, ''), ' - ', COALESCE(tc.documento, '')) AS buscar FROM tabla_cliente mc LEFT JOIN tabla_cliente tc ON mc.from_number = tc.from_number AND tc.etiqueta = 'Nombre Completo Del Cliente' WHERE CONCAT(COALESCE(mc.from_number, ''), ' - ', COALESCE(tc.documento, '')) LIKE '%{}%'; ".format(query)
    cursor.execute(query)
    #results = [row[3] for row in cursor.fetchall()]
    results = [(row[0], row[1]) for row in cursor.fetchall()]
    cursor.close()
    return results

@app.route('/search')
def search():
    query = request.args.get('query')
    results = search_results(query)
    return results

#######################333
def ejec(tipo, codigo):
    sql.SQL_INSERTAR("INSERT INTO tabla_formularios (tipo, codigo) VALUES (%s, %s)", data=(tipo, codigo))

#administrar crear formularios
@app.route("/c0nt16", methods=["GET", "POST"])
def home_3():
    formulario_app = {}
    formulario_app = m_data.mostrar_formularios()

    nombre_personal = {}
    nombre_personal = m_data.nombre_personal_1()
    
    #script crea los formularios
    if request.method == "POST" and request.form.get("nombre_form"):
        datos_adicionales = ','.join(['"{}"'.format(item) for item in request.form.getlist("casillas[]")])  # Unir elementos con comillas dobles y comas
        codigo = 'datos_adicionales = [{}]\n'.format(datos_adicionales)
        codigo += 'for dato in datos_adicionales:\n'
        codigo += '    sql.SQL_INSERTAR("INSERT INTO tabla_cliente (from_number, documento, etiqueta) VALUES (%s, %s, %s)", data=(from_number, "", dato))\n'
        ejec(request.form.get("nombre_form"), codigo)

    # agregar eliminar formulario
    if request.method == "POST" and 'ok_button_etiqueta_editar' in request.form:
        if request.form.get('index_cols') != "" and request.form.get('tipo_respuesta_etiqueta_modificar') == "Eliminar" and request.form.get('mensaje') != "1.Nombre":
            sql.SQL_INSERTAR("DELETE FROM tabla_formularios WHERE id = %s", (request.form.get('index_cols'),))
            pass
        elif request.form.get('index_cols') == "":
            pass

    # crear usuarios de la empresa
    if request.method == "POST" and 'Enviar_crear_funcionario' in request.form:
        nombre = request.form.get('nombre')#
        Documento = request.form.get('Documento')
        Celular = request.form.get('Celular')#
        Correo = request.form.get('Correo')
        Actividad = request.form.get('Actividad')#
        Permisos = request.form.get('Permisos')#
        Agenda = request.form.get('Agenda')#
        Pais = request.form.get('Pais')
        Area = request.form.get('Area')#
        Contra = request.form.get('Contraseña')#

        #comp = tra_pe.revisar_fecha_agenda(request.form.get('from_number_rediri'))
        ver_cali = tra_pe.revisar_usuario_creado(request.form.get('Celular'))
        print(ver_cali)
        #if ver_cali and isinstance(ver_cali, list) and len(ver_cali) > 0 and len(ver_cali[0]) > 0:
        #    if ver_cali[0][0] != request.form.get('Celular'):
        if request.form.get('Celular') != '':
            #if ver_cali[0][0] != request.form.get('Celular'):
            if ver_cali != request.form.get('Celular'):

                if nombre != "" and Celular != "" and Actividad != "" and Permisos != "" and Agenda != "" and Contra != "":
                    if Permisos != 'DESARROLLADOR':
                        nombre = nombre
                        from_number = Celular
                        etiqueta = Contra
                        Permisos = Permisos
                        Area = Area
                        sql.SQL_INSERTAR("INSERT INTO empl_usr_da (from_number, nombre, etiqueta, Permisos, Area, Proceso_a_cargo) VALUES (%s, %s, %s, %s, %s, %s)", data = (from_number, nombre, etiqueta, Permisos, Area, Agenda))
                    else:
                        pass

    # eliminar empleados
    if request.method == "POST" and 'ok_button_etiqueta_elim' in request.form:
        if request.form.get('index_col_') != "" and request.form.get('tipo_respuesta_etiqueta_modificar_1') == "Eliminar" and request.form.get('usuario_elm') != 'DIDIER CABRERA MAMIAN':
            sql.SQL_INSERTAR("DELETE FROM empl_usr_da WHERE id = %s", (request.form.get('index_col_'),))
            pass
        elif request.form.get('index_col_') == "":            
            pass

    formulario_app = {}
    formulario_app = m_data.mostrar_formularios()
    
    nombre_personal = m_data.nombre_personal_1()
    #form_1 = formulario_app
    return render_template('5_configuracion.html', form_1 = formulario_app, nombre_pers = nombre_personal)

@app.route("/apir", methods=['GET', 'POST'])
def obtener_mensajes():
    token = request.args.get("token")
    if not verificar_token(token):
        return "Acceso no autorizado", 401
    mensajes = sql.SQL_CONSULTA("select * from empl_usr_da;")
    print("mensaje")
    return jsonify(mensajes)

if __name__ == "__main__":
    #app.run()
    app.run(debug= True, host=("0.0.0.0"))
    #app.run(port = 5000, debug= True, host=("0.0.0.0"))
 #   socketio.run(app, allow_unsafe_werkzeug=True)
#app.run(host=("0.0.0.0"))