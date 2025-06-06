from src.models.dashboard import *
def cargar_y_filtrar_bitacoras():
    try:
        bitacoras = leer_bitacoras_desde_excel()
        bitacoras = [b for b in bitacoras if b.responsabilidad == 'Cliente']

    except Exception as e:
        print(f"Error: {e}")
    return bitacoras
