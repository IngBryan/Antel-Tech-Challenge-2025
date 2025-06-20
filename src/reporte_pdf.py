import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime

from src.schema import (
    Reporte, Incidencias, Incidencia, Reclamos,
    MotivosIZI611, MotivoIZI611, MotivosContacto, MotivoContacto,
    Whatsapp, Salientes, Automatismos
)

def generar_pdf(reporte: Reporte) -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 2*cm

    def write_line(text, offset=14, bold=False):
        nonlocal y
        if bold:
            c.setFont("Helvetica-Bold", 10)
        else:
            c.setFont("Helvetica", 10)
        c.drawString(2*cm, y, text)
        y -= offset

    # Encabezado
    write_line("REPORTE MENSUAL - ANTEL", bold=True)
    write_line(f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    write_line("-" * 80)

    # Antel Móvil
    write_line("ANTEL MÓVIL - 611", bold=True)
    am = reporte.antel_movil_global
    amNG = reporte.antel_movil_no_global
    write_line(f"Llamadas al servicio: {am.llamadas_al_servicio_global}")
    write_line(f"Llamadas atendidas: {am.llamadas_atendidas_totales_global}")
    write_line(f"Llamadas abandonadas: {am.llamadas_abandonadas_global}")
    write_line(f"%Llamadas no atendidas: {100-(amNG.indice_de_respuesta):.2f}%")
    write_line(f"Cumplimiento del servicio: {amNG.cumplimient_nivel_de_servicio:.2f}%")# este
    write_line(f"Índice de respuesta: {amNG.indice_de_respuesta:.2f}%")
    write_line(f"TRSAC: {am.trsac} segundos")
    write_line(f"Promedio operación (segundos): {am.promedio_operacion}")
    write_line(f"Tiempo total atención (horas) : {am.atencion}")
    write_line(f"Congestión: {am.congestion}")

    write_line("-" * 80)

    # Whatsapp
    write_line("WHATSAPP", bold=True)
    wa = reporte.whatsapp
    write_line(f"Entrantes: {wa.entrantes}")
    write_line(f"Salientes: {wa.salientes}")
    write_line(f"Total: {wa.total}")
    write_line(f"Promedio por interacción: {wa.promedio:.2f}")

    write_line("-" * 80)

    # Automatismos
    write_line("AUTOMATISMOS", bold=True)
    a = reporte.automatismos
    write_line(f"Total: {a.total}")
    write_line(f"Éxitos: {a.exito} ({a.pexito:.2%})")
    write_line(f"Errores: {a.error} ({a.perror:.2%})")

    # Incidencias
    write_line("-" * 80)
    write_line("INCIDENCIAS", bold=True)
    for inc in reporte.incidencias.incidencias:
        write_line(f"- {inc.fecha}: {inc.motivo}")

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer.read()