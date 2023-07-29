import mysql.connector
import json
from dotenv import load_dotenv
import os
load_dotenv()
import mostrar_data as m_data

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
dn_n = os.getenv('DB_BASE')
db_port = os.getenv('db_port')

debug = os.getenv('DEBUG')
#print(db_host,db_user,db_pass,dn_n,db_port )

#sirve para almacenar datos de sql donde recive el "query" y retorna la solicitud
def SQL_CONSULTA(query):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, database=dn_n)#, port=db_port)
    cursor = cnx.cursor()
    query
    cursor.execute(query)
    solicitud = cursor.fetchall()
    return solicitud

#sirve para almacenar datos de sql donde recive el scrip "query, y data"
def SQL_INSERTAR(query, data):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, database=dn_n)#, port=db_port)
    cursor = cnx.cursor()
    query
    cursor.execute(query, data)
    cnx.commit()
    cursor.close()

#sirve para almacenar datos de sql donde recive el scrip "query, y data"
#def BUSCAR(query, data):
#    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, database=dn_n)#, port=db_port)
#    cursor = cnx.cursor()
#    query
#    cursor.execute(query, data)
#    solicitud = cursor.fetchall()
    #solicitud = list(filter(None, solicitud))
#    result = ' '.join([word for row in solicitud for word in row])
#    return result


def BUSCAR(query, data):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, database=dn_n)
    cursor = cnx.cursor()
    cursor.execute(query, data)
    solicitud = cursor.fetchall()
    result = ' '.join([word if word is not None else '' for row in solicitud for word in row])
    return result

#sirve para almacenar datos de sql donde recive el scrip "query, y data"
def BUSCAR_2(query, data):
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, database=dn_n)
    cursor = cnx.cursor()
    query
    cursor.execute(query, data)
    solicitud = cursor.fetchall()
    return solicitud
