# Importar librerias de Flask
# Render Template - Retornar o llamar una plantilla en HTML
import email
from flask import Flask, render_template, request, flash, session, redirect

import os

# Importar la libreria seguridad
from werkzeug.security import generate_password_hash, check_password_hash
import utils


# Encriptar el password mediante hash
import hashlib
import controlador

# Importar libreria - codigo de activación
from datetime import datetime

# Importar el archivo de envioemail - Contiene protocolo SMTP
import envioemail



app = Flask(__name__)
app.secret_key = os.urandom(24)

# Crear una variable global para el usuario
email_origen = ""

@app.route("/")
def inicio():
    return render_template("login.html")

@app.route("/validarUsuario", methods=["GET", "POST"])
def validarUsuario():
    if request.method == "POST":
        user = request.form["txtusuario"]

        # Evitar inyeccion Codigo SQL
        user = user.replace("SELECT","").replace("INSERT","").replace("DELETE","").replace("UPDATE","").replace("WHERE","")
        
        passw = request.form["txtpass"]
        passw = passw.replace("SELECT","").replace("INSERT","").replace("DELETE","").replace("UPDATE","").replace("WHERE","")


        respuesta = controlador.validarUsuario(user)

        global email_origen

        if respuesta!= None:
            claveHash = respuesta[1]
            usuario_bd = respuesta[0]

            if(check_password_hash(claveHash, passw)):
                email_origen = user
                session['usuario']= user #creación de la variable de sesion
              #  flash("Usuario Logueado, "+usuario_bd)
                listaUsua=controlador.listarDestinatarios(user)
                return render_template('principal.html', datas = listaUsua,usuario=usuario_bd)

            else:
                mensaje = "Error: Auntenticación!!! Lo invitamos a verificar su usuario(correo) y contraseña"
                return render_template("informacion.html", datas = mensaje)

        else:
            mensaje = "Error: Auntenticación!!! Lo invitamos a verificar su usuario(correo) y contraseña"
            return render_template("informacion.html", datas = mensaje)



@app.route("/registrarUsuario", methods=["GET", "POST"])
def registrarUsuario():
    if request.method == "POST":
        name = request.form["txtnombre"]
        name = name.replace("SELECT","").replace("INSERT","").replace("DELETE","").replace("UPDATE","").replace("WHERE","")

        email = request.form["txtusuarioregistro"]
        email = email.replace("SELECT","").replace("INSERT","").replace("DELETE","").replace("UPDATE","").replace("WHERE","")
        passw = request.form["txtpassregistro"]

        if not name:
          error = 'Debes ingresar el nombre del usuario'
          flash( error )
          return render_template( 'login.html' )

        if not utils.isUsernameValid( name ):
            error = "El usuario debe ser alfanumerico o incluir solo '.','_','-'"
            flash( error )
            return render_template( 'login.html' )

        if not utils.isPasswordValid( passw ):
            error = 'La contraseña debe contenir al menos una minúscula, una mayúscula, un número, un caracter especial y 8 caracteres'
            flash( error )
            return render_template( 'login.html' )

        if not utils.isEmailValid( email ):
            error = 'Correo invalido'
            flash( error )
            return render_template( 'login.html' )

        hashClave = generate_password_hash(passw)
        passw2 = hashClave


        # Generar codigo de activacion - Trae fecha (2022-10-05) y horas - 18:39:15.032274
        codigo = datetime.now()   #Trae la hora y fecha actual
        print(codigo)
        # Eliminar caracteres que no sean numericos
        codigo2 = str(codigo)
        codigo2 = codigo2.replace("-", "")
        codigo2 = codigo2.replace(" ", "")
        codigo2 = codigo2.replace(":", "")
        codigo2 = codigo2.replace(".", "")
        print(codigo2)

        # Generalizar mensaje enviado por correo
        mensaje = "Sr {0}, usuario su codigo de activacion es :\n\n {1} \n\n Recuerde copiarlo y pegarlo para validarlo en la seccion de login y activar su cuenta.\n\nMuchas Gracias".format(name,codigo2)

        # Enviarle el codigo de activacion a la persona registrada - Agregar mensaje en el medio
        envioemail.enviar(email,mensaje,"Codigo de Activación")

        # Obtener la consulta de la BD
        respuesta = controlador.registrarUsuario(name, email, passw2, codigo2)


        return render_template("informacion.html", datas = respuesta)


@app.route("/activarUsuario", methods=["GET", "POST"])
def activarUsuario():
    if request.method == "POST":
        codigo = request.form["txtcodigo"]
        codigo = codigo.replace("SELECT","").replace("INSERT","").replace("DELETE","").replace("UPDATE","").replace("WHERE","")

        # Obtener la consulta de la BD
        respuesta = controlador.activarUsuario(codigo)

        # Hace la validación del codigo de ese usuario 
        if len(respuesta) == 0:
            mensaje = "El código de activación es erroneo, Verificar !!!"

        else:
            mensaje = "El usuario se ha activado exitosamente"

        return render_template("informacion.html", datas = mensaje)



#Nueva ruta para envio de email
@app.route("/enviarMail", methods=["GET", "POST"])
def enviarMail():
    if request.method == "POST":
        emailDestino = request.form["emailDestino"]
        
        asunto = request.form["asunto"]
        asunto = asunto.replace("SELECT","").replace("INSERT","").replace("DELETE","").replace("UPDATE","").replace("WHERE","")


        mensaje = request.form["mensaje"]
        mensaje = mensaje.replace("SELECT","").replace("INSERT","").replace("DELETE","").replace("UPDATE","").replace("WHERE","")

        # Registrar la información para procesar en el controlador
        controlador.registrarMail(email_origen, emailDestino, asunto, mensaje)


        mensaje2 = "Señor Usuario, usted recibió un mensaje nuevo !!! \n\n Por favor ingrese a la plataforma para observar su email, en la Pestaña: Historial \n\n Muchas gracias"

        # Colocar procedimiento de enviar email - Mensaje no se envia - Asunto
        envioemail.enviar(emailDestino,mensaje2,"Nuevo mensaje enviado")
        return "Email enviado Satisfactoriamente"

# Nueva ruta para visualizar el historial de Enviados

@app.route("/historialEnviados", methods=["GET", "POST"])
def historialEnviados():
    
    # Realizar la consulta de los correos enviados - Por fecha y hora descendente - Se entra la variable global
    resultado = controlador.verEnviados(email_origen)

    # Crear formato HTML para visualizar el resultado
    return render_template("respuesta.html", datas = resultado)

# Nueva ruta para visualizar el historial de recibidos

@app.route("/historialRecibidos", methods=["GET", "POST"])
def historialRecibidos():
    
    # Realizar la consulta de los correos enviados - Por fecha y hora descendente - Se entra la variable global
    resultado = controlador.verRecibidos(email_origen)

    # Crear formato HTML para visualizar el resultado
    return render_template("respuesta.html", datas = resultado)


@app.route("/actualizarPassword", methods=["GET", "POST"])
def actualizarPassword():
    if request.method == "POST":
        passw = request.form["passw"]
        passw = passw.replace("SELECT","").replace("INSERT","").replace("DELETE","").replace("UPDATE","").replace("WHERE","")
       
       # Encriptar usando sha256 - Asi se muestra la info decodificada
        hashClave = generate_password_hash(passw)
        passw2 = hashClave

        respuesta = controlador.actualizarPass(passw2, email_origen)

        return "Actualización de Contraseña satisfactoria!!"+ passw2 + email_origen

@app.route("/cerrarSesion")
def cerrarSesion():
  session.clear()
  flash('Sesión cerrada')
  return redirect('/')

@app.route("/recuperarContrasenia", methods=['GET','POST'])
def recuperarContrasenia():
  if request.method == "POST":
    email = request.form["emailRecuperar"]

  email = email.replace("SELECT","").replace("INSERT","").replace("DELETE","").replace("UPDATE","").replace("WHERE","")
  respuesta = controlador.validarUsuario(email)

  if respuesta!= None:
    # Generar codigo de activacion - Trae fecha (2022-10-05) y horas - 18:39:15.032274
    codigo = datetime.now()   #Trae la hora y fecha actual
    print(codigo)
    # Eliminar caracteres que no sean numericos
    codigo2 = str(codigo)
    codigo2 = codigo2.replace("-", "")
    codigo2 = codigo2.replace(" ", "")
    codigo2 = codigo2.replace(":", "")
    codigo2 = codigo2.replace(".", "")

    hashClave = generate_password_hash(codigo2)
    passw2 = hashClave
    respuesta2 = controlador.actualizarPass(passw2, email)
    # Generalizar mensaje enviado por correo
    mensaje = "Sr {0}, usuario su clave tesmporal es :\n\n {1} \n\n Recuerde copiarla y pegarla; posteriormente cambie la contraseña.\n\nMuchas Gracias".format(respuesta[0],codigo2)

    # Enviarle el codigo de activacion a la persona registrada - Agregar mensaje en el medio
    envioemail.enviar(email,mensaje,"Recuperar contraseña")
    return redirect('/')



