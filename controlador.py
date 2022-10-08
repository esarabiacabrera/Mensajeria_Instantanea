import sqlite3

# Función que muestra los correos enviados usando las 2 tablas
def verEnviados(correo):
    # Conectar la BD
    db = sqlite3.connect("static\mensajeria.db")
    # Obtener todas los campos de la tabla
    db.row_factory = sqlite3.Row
    # Crea el apuntado para manipular la BD
    cur= db.cursor()
    # Realizar la consulta la BD - Escojo la info de las 2 tablas y las ordeno por fecha de forma descendente
    cur.execute("""SELECT m.asunto, m.mensaje, m.fecha, m.hora, u.userName FROM usuarios u, mensajeria m 
                    WHERE u.correo = m.ID_User_Recibe AND m.ID_User_Envia = ? ORDER BY fecha desc, hora desc""",[correo])
    resultado = cur.fetchall()
    return resultado

# Función que muestra los correos recibos usando las 2 tablas
def verRecibidos(correo):
    # Conectar la BD
    db = sqlite3.connect("static\mensajeria.db")
    # Obtener todas los campos de la tabla
    db.row_factory = sqlite3.Row
    # Crea el apuntado para manipular la BD
    cur= db.cursor()
    # Realizar la consulta la BD - Escojo la info de las 2 tablas y las ordeno por fecha de forma descendente
    cur.execute("""SELECT m.asunto, m.mensaje, m.fecha, m.hora, u.userName FROM usuarios u, mensajeria m 
                    WHERE u.correo = m.ID_User_Envia AND m.ID_User_Recibe = ? ORDER BY fecha desc, hora desc""",[correo])
    resultado = cur.fetchall()
    return resultado



def validarUsuario(usuario):
    db=sqlite3.connect("static\mensajeria.db")
    db.row_factory=sqlite3.Row
    cursor=db.cursor()
    resultado = cursor.execute('SELECT userName, password FROM usuarios WHERE correo = ? and estado = ?', (usuario,1)).fetchone()
    return resultado



# Función que verifica el usuario, contraseña y estado de activación
def comprobarUsuario(usuario, contrasena):
    # Conectar la BD
    db = sqlite3.connect("static\mensajeria.db")
    # Obtener todas los campos de la tabla
    db.row_factory = sqlite3.Row
    # Crea el apuntado para manipular la BD
    cur= db.cursor()
    # Realizar la consulta la BD
    cur.execute("SELECT * FROM usuarios WHERE correo = ? AND password = ? AND estado = ?",[usuario, contrasena,'1'])
    resultado = cur.fetchall()
    return resultado

# Función que muestra la consulta de los destinatarios
def listarDestinatarios(usuario):
    # Conectar la BD
    db = sqlite3.connect("static\mensajeria.db")
    # Obtener todas los campos de la tabla
    db.row_factory = sqlite3.Row
    # Crea el apuntado para manipular la BD
    cur= db.cursor()
    # Realizar la consulta la BD - De todos los usuarios que no sea uno
    cur.execute("SELECT * FROM usuarios WHERE correo <> ? ",[usuario])
    resultado = cur.fetchall()
    return resultado



# Función que agrega el usuario dentro de la BD
def registrarUsuario(nombre, email, contrasena, code):
    try:
        # Conectar la BD
        db = sqlite3.connect("static\mensajeria.db")
        # Obtener todas los campos de la tabla
        db.row_factory = sqlite3.Row
        # Crea el apuntado para manipular la BD
        cur= db.cursor()
        # Realizar la consulta la BD
        cur.execute("INSERT INTO usuarios (userName, correo, password, estado, activateCode) VALUES (?, ?, ?, ?, ?)",[nombre, email, contrasena, '0', code])
        
        # Confirmar la inserción de la instruccion de la Base de datos
        db.commit()
        return "Usuario registrado de forma satisfactoria !"
        
    except :
        return "Error!!! No es posible registrar al usuario - El USUARIO y/o CORREO ya existe. Modifica los campos pertinentes "
     



# Funcion para la consulta del email enviado
def registrarMail(origen, destino, asunto, mensaje):
    # Conectar la BD
    db = sqlite3.connect("static\mensajeria.db")
    # Obtener todas los campos de la tabla
    db.row_factory = sqlite3.Row
    # Crea el apuntado para manipular la BD
    cur= db.cursor()
    # Realizar la consulta la BD
    # Se agrega para la Fecha comando SQLite - DATE('now')
    # Se agrega para la Hora comando SQLite - TIME('now')
    cur.execute("INSERT INTO mensajeria (asunto, mensaje, fecha, hora, ID_User_Envia, ID_User_Recibe, estado) VALUES (?, ?, DATE('now'), TIME('now'), ?, ?, ?)",[asunto, mensaje, origen, destino, '0'])
    
    # Confirmar la inserción de la instruccion de la Base de datos
    db.commit()
    return "1"


# Metodo Update - Función para obtener codigo de activacion
def activarUsuario(codigo):
    # Conectar la BD
    db = sqlite3.connect("static\mensajeria.db")
    # Obtener todas los campos de la tabla
    db.row_factory = sqlite3.Row
    # Crea el apuntado para manipular la BD
    cur= db.cursor()
    # Realizar la consulta la BD
    cur.execute("UPDATE usuarios SET estado = ? WHERE activateCode = ? ",['1',codigo])
    
    # Confirmar la inserción de la instruccion de la Base de datos
    db.commit()

    # Hacer nuevamente la consulta de ese codigo - Unico para cada usuario
    cur.execute("SELECT * FROM usuarios WHERE activateCode = ? AND estado = ?",[codigo,'1'])
    resultado = cur.fetchall()

    return "1" 

# Función que actualiza la contraseña del usuario
def actualizarPass(password, correo):
    # Conectar la BD
    db = sqlite3.connect("static\mensajeria.db")
    # Obtener todas los campos de la tabla
    db.row_factory = sqlite3.Row
    # Crea el apuntado para manipular la BD
    cur= db.cursor()
    # Realizar la consulta la BD - Escojo la info de las 2 tablas y las ordeno por fecha de forma descendente
    cur.execute("UPDATE usuarios SET password = ? WHERE correo = ?",[password, correo])
    
    # Confirmar la inserción de la instruccion de la Base de datos
    db.commit()

    return "1"