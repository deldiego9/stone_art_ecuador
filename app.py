from flask import Flask, render_template, request
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        mensaje = request.form['mensaje']

        with open('messages.txt', 'a', encoding='utf-8') as f:
            f.write(f'Nombre: {nombre}\nEmail: {email}\nMensaje: {mensaje}\n{"-"*40}\n')

        return render_template('contacto.html', enviado=True)

    return render_template('contacto.html')

@app.route('/galeria')
def galeria():
    carpeta_imagenes = os.path.join('static', 'images', 'obras')  # ✅ Carpeta correcta
    obras = []

    # Orden opcional por tipo
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

if __name__ == '__main__':
    app.run(debug=True)


