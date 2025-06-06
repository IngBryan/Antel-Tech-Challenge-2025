import pandas as pd
import os
from .utils import excel_a_csv
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
        return (f"<BitacoraDeInsidencia fecha={self.fecha}, sitio={self.sitio}, servicio={self.servicio}, "
                f"responsabilidad={self.responsabilidad}, motivo={self.motivo}, afectacion={self.afectacion}, "
                f"descripcion={self.descripcion}>")
def leer_bitacoras_desde_excel():
    ruta_archivo = os.getenv("DASHBOARD_BITACTORA_DE_INSIDENCIAS")
    ruta_salida = os.getenv("RUTA_SALIDA")
    # Convertir a CSV
    nombre_archivo = os.path.splitext(os.path.basename(ruta_archivo))[0] + ".csv"
    ruta_csv = os.path.join(ruta_salida, nombre_archivo)
    excel_a_csv(ruta_archivo, ruta_csv)

    if not ruta_csv:
        raise ValueError("No se encontró la ruta del archivo en el .env")

    try:
        df = pd.read_csv(ruta_csv)
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
            afectacion=fila.get('afectacion'),
            descripcion=fila.get('descripcion')
        )
        bitacoras.append(bitacora)

    return bitacoras