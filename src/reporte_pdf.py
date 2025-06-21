from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
from informe_pdf_generator import InformePDFGenerator 
import io
import calendar
from src.schema import Reporte

def generar_pdf(reporte: Reporte) -> bytes:
    mes = datetime.now().month
    ano = datetime.now().year
    mes_nombre = calendar.month_name[mes].capitalize()
    buffer = io.BytesIO()
    generador = InformePDFGenerator(mes, mes_nombre, ano, f"informe_movil_{mes_nombre}_{ano}.pdf") 
    
    buffer = generador.generar_reporte(reporte)

    #buffer.seek(0)
    return buffer