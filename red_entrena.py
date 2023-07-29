import pandas as pd
import numpy as np
import json
import openai
from openai.embeddings_utils import cosine_similarity
from openai.embeddings_utils import get_embedding
import mysql.connector
import conect_sql as sql

from dotenv import load_dotenv
import os
load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
dn_n = os.getenv('DB_BASE')
port = os.getenv('db_port')
tk_op = os.getenv('TOKEN_OPEN')
TK_WAP = os.getenv('TOKEN_WAP')
debug = os.getenv('DEBUG')
toke_app = TK_WAP
toke_api_chat = tk_op

openai.api_key = tk_op

#sirve para entrenar embedding donde recive un texto donde esta escrito las palabras a entrenar y la tabla de sql a donde se van a guardar
def embed_text(path="respuestas_empresa.csv", tabla_sql="medio_embeddings"):
    df = pd.read_csv(path)
    df['Embedding'] = df['texto'].apply(lambda x: get_embedding(x, engine='text-embedding-ada-002'))
    # Conexión a la base de datos
    cnx = mysql.connector.connect(user=db_user, password=db_pass, host=db_host, port=port, database=dn_n)
    cursor = cnx.cursor()
    # Inserción de los datos en la tabla
    for index, row in df.iterrows():
        query = f"INSERT INTO {tabla_sql} (texto, embedding) VALUES (%s, %s)"
        values = (row['texto'], json.dumps(row['Embedding']))
        cursor.execute(query, values)
    # Cierre de la conexión a la base de datos
    cnx.commit()
    cursor.close()
    cnx.close()

# sirve para hacer convertir preguntas a un embedding y escanea el presentrenado para entregar el mejor resultado tambien resibe la tabla que se quiera sacar la informacion
##################################
## responde mensajes de preguntas similares anteriores
def mensajes_amacenada(n_resultados=1):
    mensj = sql.SQL_CONSULTA("""SELECT m.id, MAX(m.message_bot) AS message_bot, MAX(hp.embedding) AS embedding FROM mensajes_whatsapp m
INNER JOIN histo_pregun hp ON m.message_body = hp.texto LEFT JOIN estado_usuario eu ON m.from_number = eu.from_number
WHERE m.message_bot IS NULL 
    AND hp.embedding IS NOT NULL 
    AND eu.tipo_com = 'Automatico'
GROUP BY m.id, m.from_number, eu.tipo_com;""")
    for mensaje in mensj:
        message_id, message_body, message_bot = mensaje
        #mensajes sin responder, busca en preguntas anteriores
        datos = pd.DataFrame(sql.SQL_CONSULTA(f"SELECT texto, embedding FROM medio_embeddings;"), columns=["texto", "embedding"])
        datos["embedding"] = datos["embedding"].apply(lambda x: json.loads(x.decode()))
        data = pd.DataFrame(mensj, columns=["id","message_bot", "embedding"])
        data["embedding"] = data["embedding"].apply(lambda x: json.loads(x.decode()))
        columna_embedding = data["embedding"].iloc[0]
        #compara los datos
        datos["Similitud"] = datos['embedding'].apply(lambda x: cosine_similarity(x, columna_embedding))
        datos = datos.sort_values("Similitud", ascending=False)
        datos = datos.iloc[0]['texto'].strip()
        if datos:
        #    print(datos)
        #    sql.SQL_INSERTAR("UPDATE mensajes_whatsapp SET message_bot = %s, estado = %s WHERE id = %s", (datos, "pendiente", message_id))

        # Extract the text before the "*s*" characters
            index_of_separator = datos.find("*s*")
            if index_of_separator != -1:
                datos_guardar = datos[:index_of_separator]
            else:
                datos_guardar = datos
            if datos_guardar:
                print(datos_guardar)
                sql.SQL_INSERTAR("UPDATE mensajes_whatsapp SET message_bot = %s, estado = %s WHERE id = %s", (datos_guardar, "pendiente", message_id))

## responde mensajes de preguntas nuevas, almacena la pregunta para usarla despues
def mensajes_no_almacen(n_resultados=1):
    msj_n = sql.SQL_CONSULTA("""SELECT m.id, m.message_body, m.from_number, m.message_bot
FROM mensajes_whatsapp m
LEFT JOIN histo_pregun hp ON hp.texto = m.message_body
WHERE m.message_bot IS NULL
  AND hp.embedding IS NULL
  AND m.from_number IN (
    SELECT from_number
    FROM estado_usuario
    WHERE tipo_com = 'Automatico'
  );""")
    for mensaj in msj_n:
        message_id, message_body, from_number,  message_bot = mensaj
        buscar = pd.DataFrame(sql.SQL_CONSULTA(f"SELECT texto, embedding FROM medio_embeddings;"), columns=["texto", "embedding"])
        buscar["embedding"] = buscar["embedding"].apply(lambda x: json.loads(x.decode()))
        busqueda_embed = get_embedding(message_body, engine="text-embedding-ada-002")    
        almacen = sql.SQL_INSERTAR(f"INSERT INTO histo_pregun (texto, embedding) VALUES (%s, %s)", (message_body, json.dumps(busqueda_embed)))
        buscar["Similitud"] = buscar['embedding'].apply(lambda x: cosine_similarity(x, busqueda_embed))
        buscar = buscar.sort_values("Similitud", ascending=False)
        buscar = buscar.iloc[0]['texto'].strip()
        if buscar:
        #    print(buscar)
        #    sql.SQL_INSERTAR("UPDATE mensajes_whatsapp SET message_bot = %s, estado = %s WHERE id = %s", (buscar, "pendiente", message_id))

            index_of_separator = buscar.find("*s*")
            if index_of_separator != -1:
                datos_guardar = buscar[:index_of_separator]
            else:
                datos_guardar = buscar
            if datos_guardar:
                print(datos_guardar)
                sql.SQL_INSERTAR("UPDATE mensajes_whatsapp SET message_bot = %s, estado = %s WHERE id = %s", (datos_guardar, "pendiente", message_id))

## activa las funciones para responder las preguntas
def responder_mensajes():
    #embed_text(path="respuestas_empresa.csv", tabla_sql="medio_embeddings")
    mensajes_amacenada()
    mensajes_no_almacen()