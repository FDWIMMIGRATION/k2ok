import trabajo_pesado as tra_pe
import conect_sql as sql

def mostrar_formularios():
    # Diccionario para almacenar los formularios disponibles
    # Consultar los formularios desde la base de datos
    formularios = sql.SQL_CONSULTA("SELECT * FROM tabla_formularios;")
    # Recorrer cada formulario obtenido
    formulario_app = {}
    if not formularios:
        formularios = []
    for formulario in formularios:
        ident_i = formulario[0]
        nombre_formulario = formulario[1]
           # Verificar si el formulario ya ha sido agregado al diccionario
        if nombre_formulario in formulario_app:
            formulario_app[nombre_formulario].append((nombre_formulario, ident_i))
        else:
            formulario_app[nombre_formulario] = [(nombre_formulario, ident_i)]
        # Devolver el diccionario de formularios disponibles
    return formulario_app

#Funcion para mostrar los usuarios para redirigir
def mostrar_redirigir_disponible():
    try:
        selec_usuario = {}
        usu_app = sql.SQL_CONSULTA("SELECT * FROM empl_usr_da;")
        for usuario in usu_app:
            numero = usuario[1]
            nombre_usuario = usuario[3]
            area = usuario[7]
            if numero in selec_usuario:
                selec_usuario[numero].append((nombre_usuario, area ))
            else:
                selec_usuario[numero] = [(nombre_usuario, area)]
        return selec_usuario
    except Exception as e:
        pass
    

#Funcion para mostrar los mensajes en forma automatica
def mensajes_automaticos():
    try:
        tipo = "Automatico"
        area_envio = "CALL_CENTER"
        datas = tra_pe.selecionar_area(tipo, area_envio)  
        mensajes_por_from_number = {}
        for mensaje in datas:
            from_number = mensaje[0]
            mensajes = mensaje[1]
            fecha_hora = mensaje[2]
            tipo_or = mensaje[3]
            orden = mensaje[4]
            area_envio = mensaje[5]
            tipo_com = mensaje[5]
            if from_number in mensajes_por_from_number:
                mensajes_por_from_number[from_number].append((tipo_or, mensajes, fecha_hora))
            else:
                mensajes_por_from_number[from_number] = [(tipo_or, mensajes, fecha_hora)]
        return mensajes_por_from_number
    except Exception as e:
        pass

#Funcion para mostrar los mensajes en forma intervenida
def mensajes_intervenido():
    try:
        tipo = "Persona"
        area_envio = "CALL_CENTER"
        datas2 = tra_pe.selecionar_area(tipo, area_envio) 
        mensajes_por_from_number2 = {}
        for mensaje2 in datas2:
            from_number2 = mensaje2[0]
            mensajes2 = mensaje2[1]
            fecha_hora2 = mensaje2[2]
            tipo_or2 = mensaje2[3]
            orden2 = mensaje2[4]
            area_envio2 = mensaje2[5]
            tipo_com2 = mensaje2[5]
            if from_number2 in mensajes_por_from_number2:
                mensajes_por_from_number2[from_number2].append((tipo_or2, mensajes2, fecha_hora2))
            else:
                mensajes_por_from_number2[from_number2] = [(tipo_or2, mensajes2, fecha_hora2)]
        return mensajes_por_from_number2
    except Exception as e:
        pass

#Funcion para mostrar las agendas dispobibles
def mostrar_agenda_disponible():
    try:
        selec_agenda = {}
        usu_app = sql.SQL_CONSULTA("""SELECT agenda.id, agenda.from_number_user, agenda.fecha, agenda.hora, agenda.from_number_cliente, empl_usr_da.nombre, empl_usr_da.Area, empl_usr_da.Proceso_a_cargo FROM agenda JOIN empl_usr_da ON agenda.from_number_user = empl_usr_da.from_number
        WHERE agenda.from_number_cliente IS NULL AND empl_usr_da.Proceso_a_cargo = 'SI';""")
        for usuario in usu_app:
            numero = usuario[0]
            fecha = str(usuario[2])  # Convertir la fecha a cadena
            hora = usuario[3].seconds // 3600  # Obtener las horas como entero
            nombre_usuario = usuario[5]
            area = usuario[6]
            if numero in selec_agenda:
                selec_agenda[numero].append((fecha, hora, area, nombre_usuario))
            else:
                selec_agenda[numero] = [(fecha, hora, area, nombre_usuario)]
        return selec_agenda
    except Exception as e:
        pass
    

#Funcion para mostrar las pregutas de los formularios
def mostrar_etiquetas():
    try:
        form_2 = {} 
        form_pre = tra_pe.preguntas_bot_form_sin()
        for mensaj in form_pre:
            index_1 = mensaj[0]
            number2 = mensaj[1]
            rta = mensaj[2]
            mensaj2 = mensaj[3]
            if number2 in form_2:
                form_2[number2].append((rta, mensaj2, number2))
            else:
                form_2[number2] = [(rta, mensaj2, number2)]
        return form_2
    except Exception as e:
        pass

#muestra mensajes bloque 2
def procesar_datos(selected_number):
    mensajes_por_from_number2 = {}  # muestra los datos de la etiqueta bloque 2
    form_2 = {}  # muestra las preguntas del bot en el bloque 3
    eti_app = {}  # muestra los datos de la etiqueta bloque 4

    datas2 = tra_pe.llamar_usuario(selected_number)  # solicita datos usuario
    # muestra los datos de la etiqueta bloque 2
    for mensaje2 in datas2:
        from_number2 = mensaje2[0]
        mensajes2 = mensaje2[1]
        fecha_hora2 = mensaje2[2]
        tipo_or2 = mensaje2[3]
        orden2 = mensaje2[4]
        area_envio2 = mensaje2[5]
        tipo_com2 = mensaje2[5]
        if from_number2 in mensajes_por_from_number2:
            mensajes_por_from_number2[from_number2].append((tipo_or2, mensajes2, fecha_hora2))
        else:
            mensajes_por_from_number2[from_number2] = [(tipo_or2, mensajes2, fecha_hora2)]

    form_pre = tra_pe.preguntas_bot_form(selected_number)  # solicita datos usuario
    for mensaj in form_pre:
        index_1 = mensaj[0]
        from_number2 = mensaj[1]
        rta = mensaj[2]
        mensaj2 = mensaj[3]
        if from_number2 in form_2:
            form_2[from_number2].append((rta, mensaj2))
        else:
            form_2[from_number2] = [(rta, mensaj2)]

    # muestra los datos de la etiqueta bloque 4
    formularios = tra_pe.preguntas_bot_form_pru(selected_number)
    for mensaj in formularios:
        index_1 = mensaj[0]
        from_number2 = mensaj[1]
        rta = mensaj[2]
        mensaj2 = mensaj[3]
        if from_number2 in eti_app:
            eti_app[from_number2].append((rta, mensaj2,from_number2, index_1))
        else:
            eti_app[from_number2] = [(rta, mensaj2,from_number2, index_1)]
    return mensajes_por_from_number2, form_2, eti_app

def mostrar_datos_actualizados_clinte():
    selec_redireccion = {}
    selec_agenda_pa = {}
    
    # mostrar clientes redirecionados a cada usuario
    usu_app = sql.SQL_CONSULTA("""SELECT r.from_number, r.from_number_prof, r.fecha_hora
    FROM redirecion_cliente r INNER JOIN ( SELECT from_number_prof, MAX(fecha_hora) AS ultima_fecha FROM redirecion_cliente
        GROUP BY from_number_prof ) t ON r.from_number_prof = t.from_number_prof AND r.fecha_hora = t.ultima_fecha; """)
    for usuario in usu_app:
        fecha = str(usuario[0])  # Convertir la fecha a cadena
        from_number_user = usuario[1]
        hora = usuario[2]
                    # Crear una cadena con el formato deseado
        if from_number_user in selec_redireccion:
            selec_redireccion[from_number_user].append((from_number_user, hora, fecha))
        else:
            selec_redireccion[from_number_user] = [(from_number_user, hora, fecha)]

    # mostrar usuarios agendados
    usu_app = sql.SQL_CONSULTA("""SELECT agenda.id, agenda.from_number_user, agenda.fecha, agenda.hora, agenda.from_number_cliente
        FROM agenda JOIN empl_usr_da ON agenda.from_number_user = empl_usr_da.from_number
        WHERE agenda.from_number_cliente IS NOT NULL ORDER BY agenda.fecha, agenda.hora ASC;""")
    for usuario in usu_app:
        idexs = usuario[0]
        
        fecha = str(usuario[2])  # Convertir la fecha a cadena
        hora = usuario[3].seconds // 3600  # Obtener las horas como entero
        from_number_user = usuario[4]
        from_numbe_aut = usuario[1]
        
                # Crear una cadena con el formato deseado
        if from_number_user in selec_agenda_pa:
            selec_agenda_pa[from_number_user].append((from_number_user, hora, idexs, from_numbe_aut))
        else:
            selec_agenda_pa[from_number_user] = [(from_number_user, hora, idexs, from_numbe_aut)]
    return selec_redireccion, selec_agenda_pa

# muestra el nombre de los clientes
def nombre_clientes():
    nombre_cliente = {}
    for mensaj in sql.SQL_CONSULTA("SELECT * FROM tabla_cliente;"):
        from_number2 = mensaj[1]
        nombre = mensaj[2]
        etiqueta = mensaj[3]
        if from_number2 in nombre_cliente:
            if etiqueta == 'Nombre Completo Del Cliente':
                nombre_cliente[from_number2].append((nombre, etiqueta, from_number2))
        else:
            if etiqueta == 'Nombre Completo Del Cliente':
                nombre_cliente[from_number2] = [(nombre, etiqueta, from_number2)]
    return nombre_cliente

# muestra el nombre de los empleados
def nombre_personal_1():
    multimedi = sql.SQL_CONSULTA("select * from empl_usr_da;")
    nombre_personal = {}
    for item in multimedi:
        id_ta = item[0]
        nombre = item[3]
        if nombre in nombre_personal:
            nombre_personal[id_ta].append(id_ta, nombre)
        else:
            nombre_personal[id_ta] = [id_ta, nombre]
    return nombre_personal

# muestra el las agendas sin confirmar
def agenda_confirmar():
    agenda_confirmar_p = {}
    for mensaj in sql.SQL_CONSULTA("SELECT * FROM agenda;"):
        id_Ag = mensaj[0]
        usuarios_ = mensaj[1]
        id_Ag_3 = mensaj[2]
        id_Ag_4 = mensaj[3]
        id_Ag_5 = mensaj[4]
        if usuarios_ in agenda_confirmar_p:
            if id_Ag_5 == 'PENDIENTE':
                agenda_confirmar_p[usuarios_].append((id_Ag, usuarios_, id_Ag_3, id_Ag_4, id_Ag_5))
        else:
            if id_Ag_5 == 'PENDIENTE':
                agenda_confirmar_p[usuarios_] = [(id_Ag, usuarios_, id_Ag_3, id_Ag_4, id_Ag_5)]
    return agenda_confirmar_p

#muestra mensajes disponibles para entrenar
def entrenar_datos():
    mjs_entre_re = {}  # muestra los datos de la etiqueta bloque 2
    for mensaje2 in sql.SQL_CONSULTA("SELECT DISTINCT message_body FROM mensajes_whatsapp WHERE message_body IS NOT NULL AND message_body <> '';"):
        mjs_entre = mensaje2[0]
        if mjs_entre in mjs_entre_re:
            mjs_entre_re[mjs_entre].append((mjs_entre))
        else:
            mjs_entre_re[mjs_entre] = [(mjs_entre)]
    return mjs_entre_re

def respu_entre_datos():
    mjs_respu_re = {}  # muestra los datos de la etiqueta bloque 2
    for mensaje2 in sql.SQL_CONSULTA("SELECT texto FROM medio_embeddings WHERE texto IS NOT NULL AND texto <> '';"):
        mjs_entre = mensaje2[0]
        if mjs_entre in mjs_respu_re:
            mjs_respu_re[mjs_entre].append((mjs_entre))
        else:
            mjs_respu_re[mjs_entre] = [(mjs_entre)]
    return mjs_respu_re
