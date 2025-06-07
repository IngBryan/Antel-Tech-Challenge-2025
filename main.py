import os
from dotenv import load_dotenv,dotenv_values
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
import jwt
import datetime
from functools import wraps
import json

load_dotenv(dotenv_path="./Config.env")
config = dotenv_values()
USUARIO = os.getenv('USUARIO')
CONTRASENA = os.getenv('CONTRASENA')
print(f"USUARIO = {USUARIO}")
print(f"CONTRASENA = {CONTRASENA}")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'trooperx30'

# Defino variables globales aquí
labels = [
    "Reporte Genesys: Rendimiento de conclusión - tipif. 611",
    "Reporte Genesys: Rendimiento de conclusión - tipif. Reclamos",
    "Reporte Genesys: Resumen del rendimiento de cola - Reclamos",
    "Reporte Genesys: Resumen del rendimiento de cola - salientes 611",
    "Reporte Dashboard: ReporteBitácoraDeIncidencias",
    "Reporte PortalDesk: historic_reports_automatismo_output - automatismos",
    "Reporte PortalDesk: historic_reports_congestion_output",
    "Reporte PortalDesk: historic_reports_SKILL_output",
    "Reporte PortalDesk: LlamadasXhabilidad",
    "Reporte Ucontact:  wpp roaming",
    "Reporte Historico: Informe Movil"
]

# Esta variable guardará el mapeo archivo -> label globalmente
file_label_map_json = {}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return redirect(url_for('main'))
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return redirect(url_for('main'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def main():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['usuario']
    contrasena = request.form['contrasena']

    if usuario == USUARIO and contrasena == CONTRASENA:
        token = jwt.encode({
            'usuario': usuario,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm='HS256')

        print("Token generado:", token)
        resp = make_response(redirect(url_for('home')))
        resp.set_cookie('token', token)
        return resp
    else:
        return render_template('login.html', error='Usuario o contraseña incorrectos')

@app.route('/home')
@token_required
def home():
    # Uso la variable global labels
    return render_template("index.html", labels=labels)

@app.route('/api/upload', methods=['POST'])
@token_required
def api_upload():
    global file_label_map_json  # para modificar la variable global

    files = []
    file_label_map_str = request.form.get('fileLabelMap')

    try:
        file_label_map = json.loads(file_label_map_str) if file_label_map_str else {}
    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': 'Error al parsear fileLabelMap'}), 400

    os.makedirs('data/input/Procesar', exist_ok=True)

    for i in range(1, 12):
        file = request.files.get(f'file{i}')
        if file:
            filename = file.filename
            file.save(f'data/input/Procesar/{filename}')
            label = file_label_map.get(f'file{i}', {}).get('label', 'label desconocido')
            files.append({'filename': filename, 'label': label})

    # Actualizo la variable global
    file_label_map_json = file_label_map

    return jsonify({'status': 'ok', 'files_received': files})

if __name__ == "__main__":
    app.run(debug=True)
