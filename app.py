from flask import Flask, render_template, request, flash, redirect
import requests
import os
import threading

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_temporal")

# ---------------- Configuración de Brevo (Sendinblue) ----------------
BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
BREVO_URL = "https://api.brevo.com/v3/smtp/email"

def enviar_correo_async(datos):
    """Envía correo en un hilo separado usando la API de Brevo"""
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    response = requests.post(BREVO_URL, headers=headers, json=datos)
    print(f"📧 Envío de correo -> Status: {response.status_code}, Respuesta: {response.text}")


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
            # --- Correo para Stone Art Ecuador ---
            datos_empresa = {
                "sender": {"name": "Stone Art Ecuador", "email": "deldiego9.es@gmail.com"},
                "to": [
                    {"email": "deldiego9.es@gmail.com", "name": "Stone Art Ecuador"},
                    {"email": "deldiego9@gmail.com", "name": "Stone Art Ecuador"},
                ],
                "subject": f"Nuevo mensaje de {nombre}",
                "htmlContent": f"""
                    <h3>Nuevo mensaje desde el formulario de contacto</h3>
                    <p><b>Nombre:</b> {nombre}</p>
                    <p><b>Email:</b> {email}</p>
                    <p><b>Mensaje:</b><br>{mensaje}</p>
                """,
            }

            # --- Correo de confirmación para el usuario ---
            datos_usuario = {
                "sender": {"name": "Stone Art Ecuador", "email": "deldiego9.es@gmail.com"},
                "to": [{"email": email, "name": nombre}],
                "subject": "Gracias por contactarte con Stone Art Ecuador",
                "htmlContent": f"""
                    <p>Hola <b>{nombre}</b>,</p>
                    <p>Gracias por escribirnos. Hemos recibido tu mensaje y te responderemos lo antes posible.</p>
                    <br>
                    <p>Saludos,<br><b>Stone Art Ecuador</b></p>
                """,
            }

            threading.Thread(target=enviar_correo_async, args=(datos_empresa,)).start()
            threading.Thread(target=enviar_correo_async, args=(datos_usuario,)).start()

            flash("✅ Tu mensaje se ha enviado correctamente. Revisa tu correo para confirmar el envío.", "exito")
        except Exception as e:
            flash(f"❌ Error al enviar el mensaje: {e}", "error")

        return redirect('/contacto')

    return render_template('contacto.html')


@app.route("/ping")
def ping():
    return "App funcionando correctamente!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
