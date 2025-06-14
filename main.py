import os
from dotenv import load_dotenv,dotenv_values
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
import jwt
import datetime
from functools import wraps
import json
from google.cloud import storage
import pandas as pd
import io
from src.ai import armar_reporte
from src.reporte_pdf import generar_pdf

load_dotenv(dotenv_path="Config.env")
config = dotenv_values()
USUARIO = os.getenv('USUARIO')
CONTRASENA = os.getenv('CONTRASENA')

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
    global file_label_map_json

    file_label_map_str = request.form.get('fileLabelMap')
    try:
        file_label_map = json.loads(file_label_map_str) if file_label_map_str else {}
    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': 'Error al parsear fileLabelMap'}), 400

    os.makedirs('data/input/Procesar', exist_ok=True)

    os.environ["CLAVE"] = os.getenv("CLAVE")
    storage_client = storage.Client.from_service_account_json(os.getenv("CLAVE"))
    bucket = storage_client.bucket(os.getenv("NOMBRE_BUCKET"))

    # vaciar bucket antes de subir nuevos archivos
    #blobs = list(bucket.list_blobs())
#
    #for blob in blobs:
    #    blob.delete()

    files_processed = []

    for i, (field_name, file) in enumerate(request.files.items()):
        filename = file.filename.lower()

        # Procesar Excel
        if filename.endswith(('.xls', '.xlsx')):
            try:
                if filename.lower().startswith("informe móvil"):
                    # Abrir el archivo con múltiples hojas
                    xls = pd.ExcelFile(file)

                    hojas_a_procesar = {2: 1, 4: 3}  # nombre_logico: índice_hoja
                    for nro_hoja, index_hoja in hojas_a_procesar.items():
                        try:
                            df = pd.read_excel(xls, sheet_name=index_hoja)
                            csv_buffer = io.StringIO()
                            df.to_csv(csv_buffer, index=False)
                            csv_data = csv_buffer.getvalue()

                            base_name = filename.rsplit('.', 1)[0]
                            if nro_hoja == 2:
                                new_filename = f"{base_name}_Llamadas.csv"
                            else:
                                new_filename = f"{base_name}_Excepción_20%.csv"
                            blob = bucket.blob(f"{os.getenv('RUTA_ARCHIVO')}{new_filename}")
                            blob.upload_from_string(csv_data, content_type='text/csv')
                            print(f"Archivo subido: {new_filename}")
                        except Exception as e:
                            print(f"Error procesando hoja {nro_hoja} de {filename}: {e}")
                            continue

                else:
                    # Leer solo la primera hoja (comportamiento por defecto)
                    df = pd.read_excel(file)
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()

                    new_filename = filename.rsplit('.', 1)[0] + ".csv"
                    blob = bucket.blob(f"{os.getenv('RUTA_ARCHIVO')}{new_filename}")
                    blob.upload_from_string(csv_data, content_type='text/csv')
                    print(f"Archivo subido: {new_filename}")
                    filename = new_filename

            except Exception as e:
                print(f"Error procesando archivo Excel {filename}: {e}")
                continue

        elif filename.endswith('.csv'):
            try:
                blob = bucket.blob(f"{os.getenv("RUTA_ARCHIVO")}{filename}")
                blob.upload_from_file(file, content_type='text/csv')
                print(f"Archivo subido: {filename}")
            except Exception as e:
                print(f"Error subiendo archivo CSV {filename}: {e}")
                continue
        else:
            print(f"Archivo ignorado (tipo no válido): {filename}")
            continue

        # Tomar label del JSON enviado, si lo hay
        label_info = file_label_map.get(field_name)
        label = label_info.get('label') if label_info else labels[i] if i < len(labels) else 'label desconocido'

        files_processed.append({'filename': filename, 'label': label})

    file_label_map_json = file_label_map

    return jsonify({'status': 'ok', 'files_received': files_processed})

@app.route('/api/listar-archivos')
@token_required
def listar_archivos():
    try:
        storage_client = storage.Client.from_service_account_json(os.getenv("CLAVE"))
        bucket = storage_client.bucket(os.getenv("NOMBRE_BUCKET"))
        blobs = bucket.list_blobs()

        archivos = [blob.name for blob in blobs]

        return jsonify({'status': 'ok', 'files': archivos})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/vaciar-bucket', methods=['POST'])
@token_required
def vaciar_bucket():
    try:
        storage_client = storage.Client.from_service_account_json(os.getenv("CLAVE"))
        bucket = storage_client.bucket(os.getenv("NOMBRE_BUCKET"))
        blobs = bucket.list_blobs(prefix=os.getenv("RUTA_ARCHIVO"))

        for blob in blobs:
            blob.delete()

        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/generar-reporte', methods=['POST'])
def generar_reporte():
    try:
        report_data  = armar_reporte()

        pdf_bytes = generar_pdf(report_data)

        storage_client = storage.Client.from_service_account_json(os.getenv("CLAVE"))
        bucket = storage_client.bucket(os.getenv("NOMBRE_BUCKET"))

        blobs = bucket.list_blobs(prefix=os.getenv("RUTA_ARCHIVO"))

        for blob in blobs:
            # Ignorar si es una "carpeta vacía" (GCS trata carpetas como blobs con / al final)
            if blob.name.endswith("/"):
                continue

            nuevo_nombre = blob.name.replace(os.getenv("RUTA_ARCHIVO"), os.getenv("RUTA_PROCESADOS"), 1)
            nuevo_blob = bucket.copy_blob(blob, bucket, new_name=nuevo_nombre)
            blob.delete()

        blob = bucket.blob("reportes/reporte_generado.pdf")
        
        blob.upload_from_string(pdf_bytes, content_type="application/pdf")

        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
