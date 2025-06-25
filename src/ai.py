from google.cloud import aiplatform
import asyncio
from vertexai.preview.generative_models import GenerativeModel
import os
from dotenv import load_dotenv,dotenv_values
import unicodedata
from io import StringIO
import pandas as pd
from datetime import timedelta
from io import BytesIO
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../Config.env"))
config = dotenv_values()
ruta_json = os.getenv("CLAVE")
bucket_name=os.getenv("NOMBRE_BUCKET")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ruta_json
prefix=os.getenv("RUTA_ARCHIVO")
from vertexai import init
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import storage

from src.schema import (
    AntelMovilGlobal,
    AntelMovilNoGlobal,
    Reclamos,
    MotivosIZI611,
    Whatsapp,
    Salientes,
    MotivosContacto,
    Incidencias,
    Automatismos,
    Reporte,
)

def procesar_excepcion_menor_20(bucket_name, prefix=""):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # Buscar el blob que contiene "excepcion_20%" (insensible a mayúsculas)
    blobs = list(storage_client.list_blobs(bucket, prefix=prefix))
    blob_excepcion = next((b for b in blobs if "excepción_20%" in b.name.lower()), None)

    for blob in blobs:
        nombre = blob.name.lower()
        if "informe móvil" in nombre and "excepción_20%" in nombre:
            print("Ya existe un archivo que contiene 'informe móvil' y 'excepción_20%'. No se procesa.")
            return None, 1, 1

    if not blob_excepcion:
        print("No se encontró un archivo con 'excepción_20%' en el nombre.")
        return None, None, None

    print(f"Procesando archivo: {blob_excepcion.name}")

    # Descargar el contenido del CSV
    csv_content = blob_excepcion.download_as_text()
    df = pd.read_csv(StringIO(csv_content))

    # Asegurarse de que la columna Mes es datetime
    df["Mes"] = pd.to_datetime(df["Mes"], errors="coerce")

    # Obtener el último mes (año + mes)
    ultimo_mes = df["Mes"].dt.to_period("M").max()

    # Filtrar por ese mes
    df_mes = df[df["Mes"].dt.to_period("M") == ultimo_mes]

    # Obtener días con Promeido >= 0.20
    lista_dias = df_mes[df_mes["Promeido"] >= 0.20]["Mes"].dt.day.tolist()

    # Filtrar por Promeido < 0.20
    df_filtrado = df_mes[df_mes["Promeido"] < 0.20]
    df_resumen = resumir_llamadas(df_filtrado)

    # Convertir de nuevo a CSV
    output = StringIO()
    df_resumen.to_csv(output, index=False)
    output.seek(0)

    # Nombre del nuevo archivo
    nuevo_nombre = blob_excepcion.name.replace("excepción_20%", "Excepción_menor_20")

    # Subir el archivo filtrado al bucket
    blob_nuevo = bucket.blob(nuevo_nombre)
    blob_nuevo.upload_from_string(output.getvalue(), content_type="text/csv")

    print(f"Archivo filtrado subido como: {nuevo_nombre}")

    return lista_dias, ultimo_mes.month, ultimo_mes.year

def resumir_llamadas(df):
    columnas_a_sumar = [
        "Ofrecidas",
        "Atendidas",
        "Atendidas dentro del umbral",
        "Abandonadas"
    ]

    # Asegurarse de que las columnas existan y sean numéricas
    for col in columnas_a_sumar:
        if col not in df.columns:
            raise ValueError(f"Columna faltante: {col}")
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    suma = df[columnas_a_sumar].sum().to_frame().T  # .T para que quede como una fila

    return suma

async def armar_reporte() -> Reporte:
    storage_client = storage.Client()
    aiplatform.init(project="accesa-equipo2", location="us-central1")
    genmodel = GenerativeModel("gemini-2.0-flash")
    #genmodel = GenerativeModel("gemini-2.5-pro")

    bucket = storage_client.bucket(bucket_name)

    lista_dias, mes, anio = procesar_excepcion_menor_20(bucket_name, prefix)

    blobs = storage_client.list_blobs(bucket, prefix=prefix)

    names = []
    json_uris = []
    for blob in blobs:
        if blob.name.endswith(".csv"):
            names.append(blob.name)
            uri = f"gs://{bucket_name}/{blob.name}"
            json_uris.append(uri)
            print(uri)

    def get_text_from_gcs(uri: str) -> str:
        # Convierte gs://bucket/path.txt → bucket, path.txt
        print(f"Descargando {uri}")
        if not uri.startswith("gs://"):
            raise ValueError("URI debe comenzar con gs://")

        _, path = uri.split("gs://", 1)
        bucket_name, blob_name = path.split("/", 1)

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.download_as_text()

    tasks = [asyncio.to_thread(get_text_from_gcs, uri) for uri in json_uris]
    texts = await asyncio.gather(*tasks)

    model_map = [
        (
            AntelMovilNoGlobal,
            [
                "Excepción_20%",
            ],
            "antel_movil_no_global",
        ),
        (
            AntelMovilGlobal,
            [
                "historic_reports_congestion_output",
                "historic_reports_SKILL_output",
                "sites_services_inf_recover_DateDay_output",
            ],
            "antel_movil_global",
        ),
        (
            Reclamos,
            [
                "Resumen del rendimiento de cola - Reclamos",
            ],
            "reclamos",
        ),
        (Incidencias, ["ReporteBitácoraDeIncidencias"], "incidencias"),
        (
            MotivosIZI611,
            ["Rendimiento de conclusión - tipif. Reclamos"],
            "motivosIzi611",
        ),
        (Whatsapp, ["wpp roaming"], "whatsapp"),
        (Salientes, ["Resumen del rendimiento de cola - salientes 611"], "salientes"),
        (
            MotivosContacto,
            ["Rendimiento de conclusión - tipif. 611"],
            "motivos_contacto",
        ),
        (
            Automatismos,
            ["historic_reports_automatismo_output - automatismos"],
            "automatismos",
        ),
    ]

    json_data = {}
    prompts = []
    for model, part_names, attr_name in model_map:
        # encontrar los archivos
        full_text = ""
        ns = []
        # print(part_names)
        for part_name in part_names:
            for name, text in zip(names, texts): 
                # si coinciden los nombres
                if part_name in name:
                    ns.append(name)
                    full_text += f"\nACA EMPIEZA EL ARCHIVO {name}\n"
                    full_text += text
                    full_text += f"\nACA TERMINA EL ARCHIVO {name}\n"
        # print(full_text)

        # print(f"Armando {model} con {ns}")
        generation_config = {
            "response_mime_type": "application/json",
            "response_json_schema": model.model_json_schema(),
        }

        prompts.append((
            "Llena a partir de los siguientes datos:\n\n" + full_text,
            generation_config
        ))

    def f(args):
        prompt, cfg = args
        print("Generando...")
        return genmodel.generate_content(prompt, generation_config=cfg)

    tasks = [asyncio.to_thread(f, args) for args in prompts]
    fields = [field for (_, _, field) in model_map]
    results = await asyncio.gather(*tasks)
    
    import json
    json_data = {field: json.loads(result.text) for result, field in zip(results, fields)}

    reporte = Reporte(
        **json_data,
        lista_dias=lista_dias,
        mes=mes,
        anio=anio
    )

    return reporte

if __name__ == "__main__":
    reporte = asyncio.run(armar_reporte())
    print(reporte)

