from flask import Flask, render_template, request, flash, redirect
import requests
import os
import threading

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_temporal")

# ---------------- Configuración de Brevo ----------------
BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
BREVO_URL = "https://api.brevo.com/v3/smtp/email"

def enviar_correo_async(datos):
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    response = requests.post(BREVO_URL, headers=headers, json=datos)
    print("Respuesta de Brevo:", response.status_code, response.text)

    # ---------------- Ruta temporal para verificar la API Key ----------------
@app.route("/verificar-key")
def verificar_key():
    if BREVO_API_KEY:
        return f"Clave Brevo encontrada: {BREVO_API_KEY[:6]}... (longitud {len(BREVO_API_KEY)})"
    else:
        return "No se encontró la clave BREVO_API_KEY"

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
            datos = {
                # Sender verificado en Brevo
                "sender": {"name": "Stone Art Ecuador", "email": "deldiego9.es@gmail.com"},
                "to": [
                    {"email": "deldiego9@gmail.com", "name": "Stone Art Ecuador"},
                    {"email": "deldiego9.es@gmail.com", "name": "Stone Art Ecuador"},
                ],
                "subject": f"Nuevo mensaje de {nombre}",
                "htmlContent": f"<p><b>Nombre:</b> {nombre}</p><p><b>Email:</b> {email}</p><p><b>Mensaje:</b><br>{mensaje}</p>",
            }

            threading.Thread(target=enviar_correo_async, args=(datos,)).start()
            flash("✅ Tu mensaje se ha enviado correctamente. Nos pondremos en contacto contigo.", "exito")
        except Exception as e:
            flash(f"❌ Error al enviar el mensaje: {e}", "error")

        return redirect('/contacto')

    return render_template('contacto.html')

# ---------------- Ping de verificación ----------------
@app.route("/ping")
def ping():
    return "App funcionando correctamente!"

# ---------------- Ruta de prueba de correo ----------------
@app.route('/prueba-correo')
def prueba_correo():
    datos = {
        "sender": {"name": "Stone Art Ecuador", "email": "deldiego9.es@gmail.com"},
        "to": [
            {"email": "deldiego9@gmail.com", "name": "Diego"},
            {"email": "deldiego9.es@gmail.com", "name": "Diego"},
        ],
        "subject": "Correo de prueba desde Brevo",
        "htmlContent": "<p>¡El sistema de correo funciona correctamente con Brevo 🎉!</p>",
    }

    threading.Thread(target=enviar_correo_async, args=(datos,)).start()
    return "Correo de prueba enviado correctamente con Brevo"
