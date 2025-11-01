from flask import Flask, render_template, request, flash, redirect
from flask_mail import Mail, Message
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_temporal")  # Mensajes flash

# ---------------- Configuración Flask-Mail ----------------
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

mail = Mail(app)

# ---------------- Rutas de la web ----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/galeria')
def galeria():
    carpeta_imagenes = os.path.join('static', 'images', 'obras')
    obras = []

    prioridad = {"piedra": 1, "madera": 2, "pintura": 3}

    for archivo in os.listdir(carpeta_imagenes):
        if archivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            nombre_sin_extension = os.path.splitext(archivo)[0]
            descripcion = nombre_sin_extension.replace('_', ' ').title()

            key = None
            for k in prioridad:
                if k in nombre_sin_extension.lower():
                    key = k
                    break
            orden = prioridad.get(key, 99)

            obras.append({"imagen": archivo, "descripcion": descripcion, "orden": orden})

    obras.sort(key=lambda x: (x["orden"], x["imagen"]))
    return render_template('galeria.html', obras=obras)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        mensaje = request.form['mensaje']

        try:
            # Enviar a dos correos diferentes
            destinatarios = ['deldiego9@gmail.com', 'deldiego9.es@gmail.com']
            msg = Message(f"Nuevo mensaje de {nombre}", recipients=destinatarios)
            msg.body = f"De: {nombre}\nCorreo: {email}\n\nMensaje:\n{mensaje}"
            mail.send(msg)
            flash("✅ Tu mensaje se ha enviado correctamente. Nos pondremos en contacto contigo.", "exito")
        except Exception as e:
            flash(f"❌ Error al enviar el mensaje: {e}", "error")

        return redirect('/contacto')

    return render_template('contacto.html')

# ---------------- Endpoint de prueba ----------------
@app.route('/prueba-correo')
def prueba_correo():
    try:
        msg = Message("Prueba de Render",
                      recipients=["deldiego9@gmail.com", "deldiego9.es@gmail.com"])
        msg.body = "Si recibes este correo, Flask-Mail funciona en Render."
        mail.send(msg)
        return "Correo enviado correctamente"
    except Exception as e:
        return f"Error al enviar correo: {e}"

# ---------------- Nota importante ----------------
# NO incluyas app.run() en producción, Gunicorn se encarga de iniciar la app
# Start Command en Render: gunicorn app:app

