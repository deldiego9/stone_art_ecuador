from flask import Flask, request, render_template, jsonify
import requests
import os

app = Flask(__name__)

# ==============================
# CONFIGURACIÓN DE CLAVE API
# ==============================
BREVO_API_KEY = os.environ.get("BREVO_API_KEY")

# ==============================
# RUTA PRINCIPAL
# ==============================
@app.route("/")
def index():
    return render_template("index.html")

# ==============================
# RUTA DE CONTACTO
# ==============================
@app.route("/contacto", methods=["POST"])
def contacto():
    nombre = request.form.get("nombre")
    email = request.form.get("email")
    mensaje = request.form.get("mensaje")

    if not all([nombre, email, mensaje]):
        return jsonify({"status": "error", "message": "Faltan campos obligatorios"}), 400

    # --- Correo al administrador ---
    datos_admin = {
        "sender": {"name": "Stone Art Web", "email": "deldiego9.es@gmail.com"},
        "to": [{"email": "deldiego9.es@gmail.com", "name": "Stone Art Ecuador"}],
        "subject": f"Nuevo mensaje de {nombre}",
        "htmlContent": f"""
            <h2>Nuevo mensaje desde la web</h2>
            <p><b>Nombre:</b> {nombre}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Mensaje:</b></p>
            <p>{mensaje}</p>
        """,
    }

    # --- Correo de confirmación para el usuario (sin logo) ---
    datos_usuario = {
        "sender": {"name": "Stone Art Ecuador", "email": "deldiego9.es@gmail.com"},
        "to": [{"email": email, "name": nombre}],
        "subject": "Gracias por contactarte con Stone Art Ecuador",
        "htmlContent": f"""
            <div style="font-family: Arial, sans-serif; background-color:#f5f5f5; padding:30px;">
                <div style="max-width:600px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1);">
                    <div style="padding:30px; color:#333; text-align:center;">
                        <h2 style="color:#222;">¡Gracias por tu mensaje, {nombre}!</h2>
                        <p>Hemos recibido tu mensaje correctamente y nuestro equipo se pondrá en contacto contigo lo antes posible.</p>
                        <p style="margin-top:20px;">Resumen de tu mensaje:</p>
                        <blockquote style="border-left:4px solid #ccc; padding-left:10px; color:#555;">
                            {mensaje}
                        </blockquote>
                        <p style="margin-top:30px;">Mientras tanto, puedes visitar nuestra <a href="https://stoneartecuador.com/galeria" style="color:#0066cc;">galería</a> para ver más de nuestras obras.</p>
                        <p style="margin-top:40px;">Atentamente,<br><b>El equipo de Stone Art Ecuador</b></p>
                    </div>
                    <div style="background-color:#222; color:white; text-align:center; padding:15px; font-size:12px;">
                        © {os.environ.get("YEAR", "2025")} Stone Art Ecuador — Hecho con arte y dedicación en Ecuador 🇪🇨
                    </div>
                </div>
            </div>
        """,
    }

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    # Envío al administrador
    r1 = requests.post("https://api.brevo.com/v3/smtp/email", json=datos_admin, headers=headers)

    # Envío al usuario
    r2 = requests.post("https://api.brevo.com/v3/smtp/email", json=datos_usuario, headers=headers)

    if r1.status_code == 201 and r2.status_code == 201:
        return jsonify({"status": "success", "message": "Correos enviados correctamente"})
    else:
        return jsonify({
            "status": "error",
            "detalle_admin": r1.text,
            "detalle_usuario": r2.text
        }), 500

# ==============================
# RUTA DE PRUEBA DE CORREO
# ==============================
@app.route("/prueba-correo")
def prueba_correo():
    if not BREVO_API_KEY:
        return "No se encontró la clave BREVO_API_KEY"

    datos_prueba = {
        "sender": {"name": "Stone Art Ecuador", "email": "deldiego9.es@gmail.com"},
        "to": [{"email": "deldiego9.es@gmail.com"}],
        "subject": "📧 Prueba de correo desde Stone Art",
        "htmlContent": "<h2>El sistema de correos funciona correctamente 🎉</h2>",
    }

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    respuesta = requests.post("https://api.brevo.com/v3/smtp/email", json=datos_prueba, headers=headers)
    return f"Respuesta de Brevo: {respuesta.status_code} {respuesta.text}"

# ==============================
# DEBUG DE CLAVE (solo para pruebas)
# ==============================
@app.route("/verificar-key")
def verificar_key():
    if BREVO_API_KEY:
        return f"Clave Brevo encontrada: {BREVO_API_KEY[:6]}... (longitud {len(BREVO_API_KEY)})"
    else:
        return "No se encontró la clave BREVO_API_KEY"

# ==============================
# EJECUCIÓN LOCAL
# ==============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
