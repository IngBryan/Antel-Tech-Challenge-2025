from google.cloud import storage

def listar_archivos(bucket_name):

    client = storage.Client.from_service_account_json("clave.json")
    bucket = client.bucket(bucket_name)


    blobs = bucket.list_blobs()

    print(f"Archivos en el bucket '{bucket_name}':")

    for blob in blobs:
        print(f"- {blob.name}")

if __name__ == "__main__":
    # Reemplazá con el nombre real de tu bucket (sin gs://)
    bucket_name = "docs_equipo2"
    listar_archivos(bucket_name)
