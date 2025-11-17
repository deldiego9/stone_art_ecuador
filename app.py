from flask import Flask, request, render_template, flash, redirect
import requests
import os
import threading

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_temporal")

# ==============================
# CONFIGURACIÓN DE BREVO
# ==============================
BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
BREVO_URL = "https://api.brevo.com/v3/smtp/email"

# Función para enviar correos de manera asíncrona
def enviar_correo_async(datos):
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }
    response = requests.post(BREVO_URL, headers=headers, json=datos)
    print("Respuesta de Brevo:", response.status_code, response.text)

# ==============================
# CONFIGURACIÓN DE CATEGORÍAS
# ==============================
CATEGORIAS = {
    "esculturas": {
        "nombre": "Esculturas",
        "descripcion": "Obras escultóricas en diversos materiales",
        "icono": "🗿"
    },
    "pintura": {
        "nombre": "Pintura",
        "descripcion": "Arte pictórico y obras sobre lienzo",
        "icono": "🎨"
    },
    "tallado_piedra": {
        "nombre": "Tallado en Piedra",
        "descripcion": "Trabajos de tallado en piedra natural",
        "icono": "🪨"
    },
    "madera": {
        "nombre": "Madera",
        "descripcion": "Creaciones artísticas en madera",
        "icono": "🪵"
    },
    "murales": {
        "nombre": "Murales",
        "descripcion": "Arte mural y decoración de espacios",
        "icono": "🖼️"
    },
    "lapidas": {
        "nombre": "Lápidas",
        "descripcion": "Lápidas conmemorativas personalizadas",
        "icono": "⚱️"
    },
    "restauraciones": {
        "nombre": "Restauraciones",
        "descripcion": "Restauración de obras y esculturas",
        "icono": "🔨"
    },
    "fuentes_cascadas": {  # ← NUEVA CATEGORÍA
        "nombre": "Fuentes y Cascadas",
        "descripcion": "Diseño y construcción de fuentes ornamentales y cascadas",
        "icono": "⛲"
    }
}

# ==============================
# RUTAS DE LA WEB
# ==============================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")

@app.route("/galeria")
def galeria():
    return render_template("galeria_categorias.html", categorias=CATEGORIAS)

@app.route("/galeria/<categoria>")
def galeria_categoria(categoria):
    if categoria not in CATEGORIAS:
        flash("❌ Categoría no encontrada", "error")
        return redirect("/galeria")
    
    carpeta_imagenes = os.path.join('static', 'images', 'obras', categoria)
    obras = []
    
    # Verificar que la carpeta existe
    if not os.path.exists(carpeta_imagenes):
        flash(f"⚠️ Aún no hay obras en {CATEGORIAS[categoria]['nombre']}", "error")
        return render_template('galeria_detalle.html', 
                             obras=[], 
                             categoria=CATEGORIAS[categoria],
                             categoria_key=categoria)
    
    # Cargar imágenes de la categoría
    try:
        for archivo in os.listdir(carpeta_imagenes):
            if archivo.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                nombre_sin_extension = os.path.splitext(archivo)[0]
                descripcion = nombre_sin_extension.replace('_', ' ').title()
                obras.append({
                    "imagen": archivo,
                    "descripcion": descripcion,
                    "categoria": categoria
                })
        
        obras.sort(key=lambda x: x["imagen"])
    except Exception as e:
        print(f"Error al cargar imágenes: {e}")
    
    return render_template('galeria_detalle.html', 
                         obras=obras, 
                         categoria=CATEGORIAS[categoria],
                         categoria_key=categoria)

# ==============================
# CONTACTO (GET y POST)
# ==============================
@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        mensaje = request.form.get("mensaje")

        if not all([nombre, email, mensaje]):
            flash("❌ Por favor completa todos los campos.", "error")
            return redirect("/contacto")

        # Correo al administrador
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

        # Correo de confirmación al usuario
        datos_usuario = {
            "sender": {"name": "Stone Art Ecuador", "email": "deldiego9.es@gmail.com"},
            "to": [{"email": email, "name": nombre}],
            "subject": "Gracias por contactarte con Stone Art Ecuador",
            "htmlContent": f"""
                <div style="font-family: Arial, sans-serif; background-color:#f5f5f5; padding:30px;">
                    <div style="max-width:600px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1); padding:30px;">
                        <h2 style="color:#222;">¡Gracias por tu mensaje, {nombre}!</h2>
                        <p>Hemos recibido tu mensaje correctamente y nuestro equipo se pondrá en contacto contigo lo antes posible.</p>
                        <p style="margin-top:20px;">Resumen de tu mensaje:</p>
                        <blockquote style="border-left:4px solid #ccc; padding-left:10px; color:#555;">
                            {mensaje}
                        </blockquote>
                        <p style="margin-top:30px;">Mientras tanto, puedes visitar nuestra <a href="https://stoneartecuador.com/galeria" style="color:#0066cc;">galería</a> para ver más de nuestras obras.</p>
                        <p style="margin-top:40px;">Atentamente,<br><b>El equipo de Stone Art Ecuador</b></p>
                        <div style="text-align:center; margin-top:30px; color:#888; font-size:12px;">
                            © {os.environ.get("YEAR", "2025")} Stone Art Ecuador — Hecho con arte y dedicación en Ecuador 🇪🇨
                        </div>
                    </div>
                </div>
            """,
        }

        # Envío de correos en segundo plano
        threading.Thread(target=enviar_correo_async, args=(datos_admin,)).start()
        threading.Thread(target=enviar_correo_async, args=(datos_usuario,)).start()

        flash("✅ Tu mensaje se ha enviado correctamente. Nos pondremos en contacto contigo.", "exito")
        return redirect("/contacto")

    return render_template("contacto.html")

# ==============================
# RUTAS DE DEBUG (solo desarrollo)
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

    threading.Thread(target=enviar_correo_async, args=(datos_prueba,)).start()
    return "Correo de prueba enviado correctamente."

@app.route("/verificar-key")
def verificar_key():
    if BREVO_API_KEY:
        return f"Clave Brevo encontrada: {BREVO_API_KEY[:6]}... (longitud {len(BREVO_API_KEY)})"
    else:
        return "No se encontró la clave BREVO_API_KEY"

# ==============================
# EJECUCIÓN
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)