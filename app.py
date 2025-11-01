from flask import Flask, render_template, request, flash, redirect
from flask_mail import Mail, Message
import os

app = Flask(__name__)  # <-- esta línea debe ir primero
app.secret_key = os.environ.get("SECRET_KEY", "clave_temporal")  # para mensajes flash

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'deldiego9.es@gmail.com'
app.config['MAIL_PASSWORD'] = 'qeqhqlofdejntmvb'
app.config['MAIL_DEFAULT_SENDER'] = 'deldiego9@gmail.com'

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
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        mensaje = request.form.get('mensaje')

        try:
            msg = Message(
                subject=f"Nuevo mensaje de {nombre}",
                recipients=['deldiego9.es@gmail.com', 'deldiego9@gmail.com']
            )
            msg.body = f"""
Has recibido un nuevo mensaje desde tu sitio web Stone Art Ecuador:

Nombre: {nombre}
Correo: {email}

Mensaje:
{mensaje}
"""
            mail.send(msg)
            flash("✅ Mensaje enviado correctamente. ¡Gracias por contactarnos!", "success")
        except Exception as e:
            flash(f"❌ Error al enviar el mensaje: {e}", "danger")

        return redirect('/contacto')

    return render_template('contacto.html')

# ---------------- Ejecutar la app ----------------
if __name__ == '__main__':
    app.run(debug=True)
