from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
from src.informe_pdf_generator import InformePDFGenerator 
import io
import locale
from src.schema import Reporte

def generar_pdf(reporte: Reporte) -> bytes:
    #locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

    mes = datetime.now().month
    ano = datetime.now().year
    mes_nombre = datetime.now().strftime('%B').capitalize()
 
    buffer = io.BytesIO()
    generador = InformePDFGenerator(mes, mes_nombre, ano, f"informe_movil_{mes_nombre}_{ano}.pdf") 
    
    buffer = generador.generar_reporte(reporte)

    #buffer.seek(0)
    return buffer