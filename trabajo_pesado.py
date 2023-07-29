import conect_sql as sql
from dotenv import load_dotenv
import os
load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
dn_n = os.getenv('DB_BASE')
port = os.getenv('db_port')

#tk_op = os.getenv('TOKEN_OPEN')
TK_WAP = os.getenv('TOKEN_WAP')
debug = os.getenv('DEBUG')

def reordenar_clientes():
    eliminar = sql.SQL_CONSULTA("""DELETE FROM orden_cliente WHERE id > 0;
    ALTER TABLE orden_cliente AUTO_INCREMENT = 1 ;""")

    resultados = sql.SQL_CONSULTA("""SELECT t.from_number, ROW_NUMBER() OVER (ORDER BY t.fecha_hora DESC) AS numeracion
    FROM (
        SELECT from_number, fecha_hora
        FROM multimedia
        UNION ALL
        SELECT from_number, fecha_hora
        FROM mensajes_whatsapp
    ) AS t
    INNER JOIN (
        SELECT from_number, MAX(fecha_hora) AS max_fecha_hora
        FROM (
            SELECT from_number, fecha_hora
            FROM multimedia
            UNION ALL
            SELECT from_number, fecha_hora
            FROM mensajes_whatsapp
        ) AS subquery
        GROUP BY from_number
    ) AS max_dates ON t.from_number = max_dates.from_number AND t.fecha_hora = max_dates.max_fecha_hora
    ORDER BY t.fecha_hora DESC;
    """)
    for result in resultados:
        from_number, orden  = result
        insert_query = sql.SQL_INSERTAR("INSERT INTO orden_cliente (from_number, orden) VALUES (%s, %s)", data=(from_number, orden))
    #print(resultados)
def clasificar_area():
    consulta = sql.SQL_CONSULTA(
        """
        SELECT oc.from_number AS from_number, oc.orden, ae.area_envio
        FROM orden_cliente oc
        LEFT JOIN area_envio ae ON oc.from_number = ae.from_number
        LEFT JOIN estado_usuario eu ON oc.from_number = eu.from_number
        WHERE (ae.area_envio IS NULL OR ae.area_envio = '');
        """)
    for i in consulta:
        from_number, orden, area_envi = i
        #print(from_number)
        #from_number = from_number
        area_envio = "CALL_CENTER"
        sql.SQL_INSERTAR("INSERT INTO area_envio (from_number, area_envio) VALUES (%s, %s)", data = (from_number, area_envio))

def estado_usuario(from_number):
    busqueda = sql.BUSCAR_2("SELECT oc.from_number AS from_number, eu.tipo_com FROM orden_cliente oc LEFT JOIN area_envio ae ON oc.from_number = ae.from_number LEFT JOIN estado_usuario eu ON oc.from_number = eu.from_number WHERE oc.from_number = %s and (eu.tipo_com IS NULL OR eu.tipo_com = '') or (eu.tipo_com = 'Cerrado');", (from_number,))
    for mensaj in busqueda:
        from_number, tipo_com = mensaj
        #print(from_number)
        sql.SQL_INSERTAR("INSERT INTO estado_usuario (from_number, tipo_com) VALUES (%s, %s)", data=(from_number, "Automatico"))
        sql.SQL_INSERTAR("UPDATE estado_usuario SET tipo_com = %s WHERE from_number = %s;", data=("Automatico", from_number))


def estado_usuario_cambio(from_number, tipo):
    # Consultar el registro actual en la base de datos
    consulta = "SELECT tipo_com FROM estado_usuario WHERE from_number = %s;"
    resultado = sql.BUSCAR(consulta, data=(from_number,))
    # Verificar si se encontró un registro para el número dado
    if resultado:
        # Actualizar el registro con el nuevo tipo
        consulta = "UPDATE estado_usuario SET tipo_com = %s WHERE from_number = %s;"
        sql.SQL_INSERTAR(consulta, data=(tipo, from_number))
        #print(f"Se actualizó el tipo_com del número {from_number} a {tipo}.")
    else:
        print(f"No se encontró el número {from_number} en la base de datos.")

import mysql.connector
import json

def selecionar_area(tipo, area_envio):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    query = """SELECT DISTINCT combined_data.from_number, combined_data.mensajes, combined_data.fecha_hora, combined_data.tipo_or, oc.orden, ae.area_envio, eu.tipo_com
    FROM (
        SELECT from_number, message_body AS mensajes, fecha_hora, 'msj' AS tipo_or
        FROM mensajes_whatsapp
        WHERE message_body IS NOT NULL AND message_body <> ''
        UNION ALL
        SELECT from_number, message_bot AS mensajes, DATE_ADD(fecha_hora, INTERVAL 0.5 SECOND) AS fecha_hora, 'res' AS tipo_or
        FROM mensajes_whatsapp
        WHERE message_bot IS NOT NULL AND message_bot <> ''
        UNION ALL
        SELECT from_number, nombre_carpe AS mensajes, fecha_hora, 'url_li' AS tipo_or
        FROM multimedia
    ) AS combined_data
    LEFT JOIN orden_cliente oc ON combined_data.from_number = oc.from_number
    LEFT JOIN area_envio ae ON combined_data.from_number = ae.from_number
    LEFT JOIN estado_usuario eu ON combined_data.from_number = eu.from_number
    WHERE eu.tipo_com = %s AND ae.area_envio = %s
    ORDER BY oc.orden ASC, combined_data.fecha_hora ASC ;
    """
    data = (tipo, area_envio)
    
    cursor.execute(query, data)
    solicitud = cursor.fetchall()
    return solicitud


def llamar_usuario(from_number):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    query = """SELECT distinct combined_data.from_number, combined_data.mensajes, combined_data.fecha_hora, combined_data.tipo_or, oc.orden, ae.area_envio, eu.tipo_com
    FROM (
        SELECT from_number, message_body AS mensajes, fecha_hora, 'msj' AS tipo_or
        FROM mensajes_whatsapp
        WHERE message_body IS NOT NULL AND message_body <> ''
        UNION ALL
        SELECT from_number, message_bot AS mensajes, DATE_ADD(fecha_hora, INTERVAL 0.5 SECOND) AS fecha_hora, 'res' AS tipo_or
        FROM mensajes_whatsapp
        WHERE message_bot IS NOT NULL AND message_bot <> ''
        UNION ALL
        SELECT from_number, nombre_carpe AS mensajes, fecha_hora, 'url_li' AS tipo_or
        FROM multimedia
    ) AS combined_data
    LEFT JOIN orden_cliente oc ON combined_data.from_number = oc.from_number
    LEFT JOIN area_envio ae ON combined_data.from_number = ae.from_number
    LEFT JOIN estado_usuario eu ON combined_data.from_number = eu.from_number
    WHERE combined_data.from_number = %s 
    ORDER BY oc.orden ASC, combined_data.fecha_hora ASC ;
    """
    data = (from_number,)
    
    cursor.execute(query, data)
    solicitud = cursor.fetchall()
    return solicitud

def selecionar_areas(area_envio):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    query = """select * from area_envio;
    WHERE area_envio = %s
    """
    data = (area_envio,)
    cursor.execute(query, data)
    solicitud = cursor.fetchall()
    return solicitud
########################################

def seleccionar_formulario(tipo):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    query = """SELECT codigo FROM tabla_FORMULARIOS WHERE tipo = %s"""
    data = (tipo,)
    cursor.execute(query, data)
    solicitud = cursor.fetchall()
    return solicitud

def activar_formulario(tipo):
    cadena = seleccionar_formulario(tipo)
    codigo = cadena[0][0].decode()
    codigo_limpio = codigo.strip()
    print(codigo_limpio)
    return codigo_limpio

def ejec(from_number, documento, tipo):
    exec(activar_formulario(tipo), globals(), locals())

########################################
def preguntas_bot_form(from_number):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    query = """select * from tabla_cliente
    WHERE from_number = %s and (documento IS NULL OR documento = '') ;
    """
    data = (from_number,)
    cursor.execute(query, data)
    solicitud = cursor.fetchall()
    return solicitud

def preguntas_bot_form_sin():
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    query = """select * from tabla_cliente
    WHERE (documento IS NULL OR documento = '') ;
    """
    cursor.execute(query)
    solicitud = cursor.fetchall()
    return solicitud

#muestra las equiquetas y el resultado de estas
def etiquetas_consultoria(from_number):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    query = """select from_number, documento, etiqueta from tabla_cliente WHERE from_number = %s;"""
    data = (from_number,)

    cursor.execute(query, data)
    solicitud = cursor.fetchall()
    return solicitud

#prueba
def preguntas_bot_form_pru(from_number):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    query = """select * from tabla_cliente
    WHERE from_number = %s and (documento IS NOT NULL OR documento != '') ;
    """
    data = (from_number,)
    
    cursor.execute(query, data)
    solicitud = cursor.fetchall()
    return solicitud

def permisos_usuario(from_number):
    consulta = "SELECT Permisos FROM empl_usr_da WHERE from_number = %s;"
    resultado = sql.BUSCAR(consulta, data=(from_number,))    
    return resultado

def permisos_agenda(from_number):
    consulta = "SELECT Proceso_a_cargo FROM empl_usr_da WHERE from_number = %s;"
    resultado = sql.BUSCAR(consulta, data=(from_number,))    
    return resultado

    # Consultar el registro actual en la base de datos
def revisar_fecha_agenda(from_number_user):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    query = """SELECT DISTINCT from_number_user, fecha FROM agenda WHERE from_number_user = %s"""
    data = (from_number_user,)
    cursor.execute(query, data)
    solicitud = cursor.fetchall()
    return solicitud

def revisar_usuario_creado(from_number):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    query = """select from_number from empl_usr_da WHERE from_number = %s"""
    data = (from_number,)
    cursor.execute(query, data)
    solicitud = cursor.fetchall()
    return solicitud