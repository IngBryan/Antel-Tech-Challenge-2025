#Archio main, llama a cada parte del proceso (Filtros)
from models.dashboard import *
from dotenv import load_dotenv, dotenv_values

if __name__ == "__main__":
    load_dotenv(dotenv_path="../Config.env")
    config = dotenv_values()

    try:
        bitacoras = leer_bitacoras_desde_excel()
        for b in bitacoras:
            print(b)
    except Exception as e:
        print(f"Error: {e}")