#Archio main, llama a cada parte del proceso (Filtros)
from src.filters.cargaBitacora_filter import *
from dotenv import load_dotenv, dotenv_values
if __name__ == "__main__":
    load_dotenv(dotenv_path="../Config.env")
    config = dotenv_values()

    bitacoras=cargar_y_filtrar_bitacoras()
    for b in bitacoras:
        print(b)