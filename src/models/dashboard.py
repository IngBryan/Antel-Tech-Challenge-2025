import pandas as pd
import os

class BitacoraDeInsidencia:
    def __init__(self, fecha, sitio, servicio, responsabilidad, motivo, afectacion, descripcion):
        self.fecha = fecha
        self.sitio = sitio
        self.servicio = servicio
        self.responsabilidad = responsabilidad
        self.motivo = motivo
        self.afectacion = afectacion
        self.descripcion = descripcion

    def __repr__(self):
        return f"<BitacoraDeInsidencia {self.fecha} - {self.sitio}>"
def leer_bitacoras_desde_excel():

    ruta_archivo = os.getenv("DASHBOARD_BITACTORA_DE_INSIDENCIAS")
    print(ruta_archivo)
    if not ruta_archivo:
        raise ValueError("No se encontró la ruta del archivo en el .env")

    try:
        df = pd.read_excel(ruta_archivo, engine='openpyxl')
    except Exception as e:
        raise RuntimeError(f"Error al leer el archivo Excel: {e}")

    bitacoras = []
    for _, fila in df.iterrows():
        bitacora = BitacoraDeInsidencia(
            fecha=fila.get('fecha'),
            sitio=fila.get('sitio'),
            servicio=fila.get('servicio'),
            responsabilidad=fila.get('responsabilidad'),
            motivo=fila.get('motivo'),
            afectacion=fila.get('afectación'),
            descripcion=fila.get('descripción')
        )
        bitacoras.append(bitacora)

    return bitacoras