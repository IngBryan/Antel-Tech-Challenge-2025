from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
import os
from dotenv import load_dotenv,dotenv_values
import unicodedata
from io import StringIO
import pandas as pd
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../Config.env"))
config = dotenv_values()
ruta_json = os.getenv("CLAVE")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ruta_json

from vertexai import init
from vertexai.generative_models import GenerativeModel, Part
from google.cloud import storage

from schema import (
    AntelMovil611,
    Reclamos,
    MotivosIZI611,
    Whatsapp,
    Salientes,
    MotivosContacto,
    Incidencias,
    Automatismos,
    Reporte,
)


def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto.lower())
        if unicodedata.category(c) != 'Mn'
    )

def buscar_y_descargar_archivos(bucket_name, prefix, keywords):
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)

    encontrados = {}
    for keyword in keywords:
        encontrados[keyword] = None

    for blob in blobs:
        for keyword in keywords:
            if encontrados[keyword] is None and normalizar(keyword) in normalizar(blob.name):
                print(f"Archivo encontrado para '{keyword}': {blob.name}")
                encontrados[keyword] = blob.download_as_text()
        if all(v is not None for v in encontrados.values()):
            break

    return encontrados


def armar_reporte() -> Reporte:
    storage_client = storage.Client()
    aiplatform.init(project="accesa-equipo2", location="us-central1")
    genmodel = GenerativeModel("gemini-2.0-flash-001")  # O usa "gemini-1.5-pro"

    # Define tu bucket y prefijo (carpeta dentro del bucket si aplica)
    bucket_name = "docs_equipo2"
    prefix = "csvs/"  # si querés filtrar una carpeta, ej: "datos/"
    keywords = ["excepcion_20%", "sites_services_inf_recover_DateDay_output"]

    archivos_texto = buscar_y_descargar_archivos(bucket_name, prefix, keywords)
    df1 = pd.read_csv(StringIO(archivos_texto["sites_services_inf_recover_DateDay_output"]), header=1)
    df2 = pd.read_csv(StringIO(archivos_texto["excepcion_20%"]))

    # Aseguramos nombres en minúsculas y sin tildes
    df1.columns = [normalizar(c).strip().lower() for c in df1.columns]
    df2.columns = [normalizar(c).strip().lower() for c in df2.columns]

    # Agrupamos por día
    df1_grouped = df1.groupby('fecha')['ofrecidas'].sum()

    # Convertimos 'mes' a fecha si está en ese nombre
    df2['mes'] = pd.to_datetime(df2['mes'], errors='coerce')

    for idx, row in df2.iterrows():
        if pd.isna(row['ofrecidas']):
            if not pd.isna(row['mes']):
                dia = row['mes'].day
                if dia in df1_grouped.index:
                    df2.at[idx, 'ofrecidas'] = df1_grouped[dia]
                else:
                    df2.at[idx, 'ofrecidas'] = 0
            else:
                df2.at[idx, 'ofrecidas'] = 0

    print(df2.to_csv(index=False))

    # Listar todos los archivos JSON en el bucket con el prefijo
    bucket = storage_client.bucket(bucket_name)
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
        if not uri.startswith("gs://"):
            raise ValueError("URI debe comenzar con gs://")

        _, path = uri.split("gs://", 1)
        bucket_name, blob_name = path.split("/", 1)

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.download_as_text()

    texts = [get_text_from_gcs(uri) for uri in json_uris]

    model_map = [
        (
            AntelMovil611,
            [
                "historic_reports_congestion_output",
                "historic_reports_SKILL_output",
                "sites_services_inf_recover_DateDay_output",
                "Excepción_20%",
            ],
            "antel_movil",
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
    for model, part_names, attr_name in model_map:
        # encontrar los archivos
        full_text = ""
        ns = []
        for part_name in part_names:
            for name, text in zip(names, texts):
                # si coinciden los nombres
                if part_name in name:
                    ns.append(name)
                    full_text += f"\nACA EMPIEZA EL ARCHIVO {name}\n"
                    full_text += text
                    full_text += f"\nACA TERMINA EL ARCHIVO {name}\n"

        print(f"Armando {model} con {ns}")
        generation_config = {
            "response_mime_type": "application/json",
            "response_json_schema": model.model_json_schema(),
        }

        response = genmodel.generate_content(
            "Llena a partir de los siguientes datos:\n\n" + full_text,
            generation_config=generation_config,
        )

        import json

        json_data[attr_name] = json.loads(response.text)
        print(response.text)

    return Reporte(**json_data)


if __name__ == "__main__":
    reporte = armar_reporte()
    print(reporte)

# Convertimos cada URI en un Part con el mime_type correcto para JSON
# parts = [Part.from_uri(uri, mime_type="text/csv") for uri in json_uris]

# parts = ""
# for text, name in zip(texts, names):
#     parts += f"\n\n A CONTINUACIÓN EMPIEZA EL ARCHIVO {name}"
#     parts += text
#     parts += f"\n\n AQUI TERMINA EL ARCHIVO {name}"


# from schema import Reporte

# generation_config = {
#     "response_mime_type": "application/json",
#     "response_json_schema": Reporte.model_json_schema(),
# }

# response = genmodel.generate_content(
#     # ["Llena a partir de los siguientes datos:"] + parts,
#     "Llena a partir de los siguientes datos:\n\n" + parts,
#     generation_config=generation_config,
# )

# print(response.text)
