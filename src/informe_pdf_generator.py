from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import black, blue, gray, Color
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.platypus.flowables import HRFlowable
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgetbase import Widget
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from src.schema import Reporte, AntelMovilNoGlobal, AntelMovilGlobal, Incidencias, Incidencia, Reclamos, MotivosIZI611, MotivoIZI611
from src.schema import MotivosContacto, MotivoContacto, Whatsapp, Salientes, Automatismos
from datetime import datetime, timedelta
from collections import defaultdict

from io import BytesIO
import calendar



class InformePDFGenerator:
    def __init__(self, mes, mes_nombre, ano, filename="informe_movil.pdf"):
        self.filename = filename
        self.doc = SimpleDocTemplate(filename, pagesize=A4, 
                                   rightMargin=2*cm, leftMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
        self.styles = getSampleStyleSheet()
        self.story = []
        
        self.mes = mes
        self.mes_nombre = mes_nombre
        self.ano = ano
        # Definir estilos personalizados
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados para el documento"""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Title'],
            fontSize=16,
            spaceAfter=12,
            alignment=TA_CENTER,
            textColor=black
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading1'],
            fontSize=14,
            spaceAfter=6,
            spaceBefore=12,
            alignment=TA_LEFT,
            textColor=black
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
        
        # Texto pequeño
        self.styles.add(ParagraphStyle(
            name='TextoPequeno',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            alignment=TA_LEFT
        ))

    def agregar_titulo_principal(self):
        """Agregar título principal del informe"""
        
        titulo = f"Informe Mensual de Gestión<br/>Móvil – {self.mes_nombre} {self.ano}"
        self.story.append(Paragraph(titulo, self.styles['TituloPrincipal']))
        self.story.append(Spacer(1, 12))
        
        # Descripción del servicio
        descripcion = """Informe mensual de gestión de servicios de Accesa Contact Center para los servicios 
        0800 6611 y *611 de atención de clientes de Móvil Antel y 0800 2466, atención a 
        Agentes de Venta y Clientes Internos. El servicio se atiende todos los días del año de 
        0 a 24 horas."""
        self.story.append(Paragraph(descripcion, self.styles['TextoNormal']))
        self.story.append(Spacer(1, 18))

    def crear_tabla_indicadores_principales(self, antel_movil_no_global: AntelMovilNoGlobal, antel_movil_global: AntelMovilGlobal, mes:int, anio:int):
        """Crear tabla con indicadores principales"""
        self.story.append(Paragraph("Indicadores de Gestión de las Llamadas", self.styles['Subtitulo']))
        self.story.append(Paragraph("El cuadro a continuación refleja los principales indicadores del mes:", 
                                  self.styles['TextoNormal']))
        self.story.append(Spacer(1, 12))
        
        # Datos de la tabla corregir
        data = [
            ["ANTEL - MÓVIL 611", f"{calendar.month_name[mes]}-{anio}"],
            ["Llamadas al servicio", f"{antel_movil_global.llamadas_al_servicio_global:,}"],
            ["Llamadas atendidas totales", f"{antel_movil_global.llamadas_atendidas_totales_global:,}"],
            ["Llamadas abandonadas", f"{antel_movil_global.llamadas_abandonadas_global:.1f}"],
            ["% Llamadas no atendidas", f"{antel_movil_no_global.porcentaje_no_atendidas:.1f}%"],
            ["Cumplimiento Nivel de servicio 80/20", f"{antel_movil_no_global.cumplimient_nivel_de_servicio:.1f}%"],
            ["Índice de respuesta", f"{antel_movil_no_global.indice_de_respuesta:.1f}%"],
            ["TRSAC", f"{antel_movil_global.trsac}"],
            ["Promedio operación (segundos)", f"{antel_movil_global.promedio_operacion:.2f}"],
            ["Tiempo total atención (horas)", f"{antel_movil_global.atencion:,.2f}"],
            ["Congestión", f"{antel_movil_global.congestion:.2f}%"]
        ]
        
        # Crear tabla
        table = Table(data, colWidths=[12*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 12))
        
        # Promedio diario
        _, cantidad_dias = calendar.monthrange(self.ano, self.mes)
        promedio_diario = antel_movil_global.llamadas_al_servicio_global // cantidad_dias  
        self.story.append(Paragraph(f"El promedio de llamadas diarias ingresado al servicio en el mes fue de {promedio_diario:,}", 
                                  self.styles['TextoNormal']))
        self.story.append(Spacer(1, 12))

    def agregar_incidencias(self, incidencias: Incidencias):
        """Agregar sección de incidencias"""
        self.story.append(Paragraph("Incidencias que afectaron el servicio Móvil en el mes:", 
                                  self.styles['TextoNormal']))
        self.story.append(Spacer(1, 6))
        
        incidencias_por_fecha = defaultdict(list)
        for inc in incidencias.incidencias:
            if inc.responsabilidad == "Cliente":
                incidencias_por_fecha[inc.fecha].append(inc.descripcion)

        motivo_style = ParagraphStyle('MotivoIndentado', parent=self.styles['TextoPequeno'], leftIndent=15)

        for fecha, descripcion in sorted(incidencias_por_fecha.items()):
            if len(descripcion) == 1:
                texto = f"▪ {fecha} {descripcion[0]}"
                self.story.append(Paragraph(texto, self.styles['TextoPequeno']))
            else:
                self.story.append(Paragraph(f"▪ {fecha}", self.styles['TextoPequeno']))
                for motivo in descripcion:
                    self.story.append(Paragraph(f"• {motivo}", motivo_style))
                
        self.story.append(Spacer(1, 12))

    def agregar_frase_importante(self, lista: list[int]):
        if not lista:
            return

        dias_str = ", ".join(str(dia) for dia in sorted(lista))
        descripcion = f"""
        Para el cálculo de indicadores globales del mes se excluye el/los día/s {dias_str} ya que las llamadas 
        del día superaron en más de un 20% al promedio de las 4 semanas anteriores, por 
        tanto, se configura la condición de excepción establecida en el SLA vigente.
        """
        self.story.append(Paragraph(descripcion.strip(), self.styles['TextoNormal']))


    def agregar_indicadores_globales(self, antel_movil_no_global: AntelMovilNoGlobal, antel_movil_global: AntelMovilGlobal):
        
        """Agregar explicación de indicadores globales"""
        self.story.append(Paragraph("Los indicadores globales son los siguientes:", self.styles['TextoNormal']))
        
        indicadores = [ 
            f"● El % de llamadas no atendidas es {antel_movil_no_global.porcentaje_no_atendidas:.1f}%, el indicador global del mes fue {antel_movil_global.porcentaje_no_atendidas_global:.1f}%.",
            f"● El Nivel de Servicio 80/20 es {antel_movil_no_global.cumplimient_nivel_de_servicio:.1f}%, el indicador global del mes fue {antel_movil_global.porcentaje_cumplimiento_de_servicio_global:.1f}%.",
            f"● El TRSAC es de {antel_movil_global.trsac} segundos, el indicador global del mes fue {antel_movil_global.trsac} segundos.",
            f"● El índice de respuesta es de {antel_movil_no_global.indice_de_respuesta:.1f}%, el indicador global del mes fue de {antel_movil_global.indice_de_respuesta_global:.1f}%."
        ]
        
        for indicador in indicadores:
            self.story.append(Paragraph(indicador, self.styles['TextoPequeno']))
        
        self.story.append(Spacer(1, 18))

    def crear_seccion_reclamos(self, reclamos: Reclamos, motivos_izi: MotivosIZI611, mes:int, anio:int):
        """Crear sección del sistema de reclamos"""
        self.story.append(Paragraph("Gestión Sistema Reclamos", self.styles['Subtitulo']))
        
        descripcion = """Además de la atención de la línea los Agentes del servicio Móvil realizan la gestión de 
        la bandeja en el Sistema Reclamos de ANTEL. A dicha carpeta llegan las consultas de 
        clientes provenientes de Whatsapp, la App MiAntel, de la Web MiAntel y de las 
        Oficinas Comerciales."""
        self.story.append(Paragraph(descripcion, self.styles['TextoNormal']))
        self.story.append(Spacer(1, 12))
        
        # Tabla de reclamos
        self.story.append(Paragraph(f"Durante el mes se realizaron {reclamos.manejo:,} llamadas en dicha gestión. El cuadro a continuación refleja las interacciones realizadas durante el mes.", 
                                  self.styles['TextoNormal']))
        self.story.append(Spacer(1, 12))
        
        # Tabla resumen reclamos
        total_segundos = int(reclamos.manejo_total) // 1000

        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        segundos = total_segundos % 60

        data_reclamos = [
            ["Mes", "Campaña", "Total Llamadas", "Tiempo Total"],
            [f"{anio}-{mes}", "Reclamos_611", f"{reclamos.manejo:,}", f"{horas:02}:{minutos:02}:{segundos:02}"]
        ]
        
        table_reclamos = Table(data_reclamos, colWidths=[3*cm, 4*cm, 4*cm, 4*cm])
        table_reclamos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table_reclamos)
        self.story.append(Spacer(1, 18))
        
        # Motivos IZI 611
        #self.story.append(Paragraph("Motivos IZI 611", self.styles['TextoNormal']))
        #self.story.append(Spacer(1, 6))
        
        # Crear tabla de motivos
        data_motivos = [["Motivos IZI 611", "Cantidad"]]
        total_motivos = 0

        # Filtrar y convertir manejo a int
        motivos_filtrados = [
            motivo for motivo in motivos_izi.motivosIzi611
            if "ININ" not in motivo.nombre_de_codigo_de_conclusion
        ]


        # Ordenar por manejo numérico descendente
        motivos_ordenados = sorted(
            motivos_filtrados,
            key=lambda m: int(m.manejo),
            reverse=True
        )

        for motivo in motivos_ordenados:
            cantidad = int(motivo.manejo)
            data_motivos.append([motivo.nombre_de_codigo_de_conclusion, f"{cantidad:,}"])
            total_motivos += cantidad

                
        data_motivos.append(["Total", f"{total_motivos:,}"])
        
        table_motivos = Table(data_motivos, colWidths=[12*cm, 3*cm])
        table_motivos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table_motivos)
        self.story.append(Spacer(1, 18))

    def crear_seccion_whatsapp(self, whatsapp: Whatsapp, mes:int, anio:int):
        """Crear sección de WhatsApp"""
        self.story.append(Paragraph("Asistencia por Roaming vía WhatsApp (092611611 opción 7)", 
                                  self.styles['Subtitulo']))
        
        data_wa = [
            [f"{calendar.month_name[mes]}-{anio}", ""],
            ["Cantidad de mensajes entrantes", f"{whatsapp.entrantes:,}"],
            ["Cantidad de mensajes salientes", f"{whatsapp.salientes:,}"],
            ["Total de mensajes", f"{whatsapp.total:,}"],
            ["Promedio de mensajes por interacción", f"{whatsapp.promedio:.0f}"]
        ]
        
        table_wa = Table(data_wa, colWidths=[10*cm, 5*cm])
        table_wa.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table_wa)
        self.story.append(Spacer(1, 18))

    def crear_seccion_salientes(self, salientes: Salientes, mes:int, anio:int):
        """Crear sección de llamadas salientes"""
        self.story.append(Paragraph("Llamadas Salientes", self.styles['Subtitulo']))
        
        descripcion = f"""Durante el mes se realizaron {salientes.total} llamadas salientes a clientes que por distinta 
        casuística fue necesario contactar. El cuadro siguiente refleja la distribución por 
        habilidad."""
        self.story.append(Paragraph(descripcion, self.styles['TextoNormal']))
        self.story.append(Spacer(1, 12))
        
        data_salientes = [
            [f"{calendar.month_name[mes]}-{anio}", ""],
            ["Campaña", "Total"],
            ["MOVIL_Contratos", f"{salientes.movil_contratos}"],
            ["MOVIL_Prepagos", f"{salientes.movil_prepagos}"],
            #["MOVIL_Prioritarios", f"{salientes.movil_prioritarios}"],
            ["Salientes_Movil", f"{salientes.salientes_movil}"],
            ["Total Llamadas", f"{salientes.total}"]
        ]
        
        table_salientes = Table(data_salientes, colWidths=[8*cm, 4*cm])
        table_salientes.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (1, 1), (1, 1), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'), #chk
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, 1), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table_salientes)
        self.story.append(Spacer(1, 12))

    def crear_seccion_motivos_contacto(self, motivos: MotivosContacto, total_llamadas_atendidas: int):
        """Crear sección de motivos de contacto"""
        self.story.append(Paragraph("Motivos de los contactos", self.styles['Subtitulo']))
        
        motivos_filtrados = [
            m for m in motivos.motivos_contactos
            if m.nombre_de_codigo_de_conclusion not in {
                "ININ-WRAP-UP-DELETED",
                "Default Wrap-up Code",
                "ININ-WRAP-UP-TIMEOUT"
            }
        ]

        total_motivos = sum([m.manejo for m in motivos_filtrados])
        porcentaje = (total_motivos / total_llamadas_atendidas) * 100
        
        descripcion = f"Durante el mes se registraron {total_motivos:,} motivos, lo que corresponde al {porcentaje:.2f}% de las llamadas atendidas."
        self.story.append(Paragraph(descripcion, self.styles['TextoNormal']))
        self.story.append(Spacer(1, 12))
        
        # Agrupar por campaña
        campanas = {}
        for motivo in motivos_filtrados:
            if motivo.nombre_cola not in campanas:
                campanas[motivo.nombre_cola] = []
            campanas[motivo.nombre_cola].append(motivo)
        
        # Crear tabla para cada campaña
        data_motivos = [["Campaña", "Descripción", "Cantidad"]]

        for campana, motivos_campana in sorted(campanas.items()):
            # Ordenar motivos por cantidad descendente
            motivos_ordenados = sorted(motivos_campana, key=lambda x: x.manejo, reverse=True)
            
            for motivo in motivos_ordenados:
                data_motivos.append([campana, motivo.nombre_de_codigo_de_conclusion, f"{motivo.manejo:,}"])
            
            # Subtotal
            subtotal = sum([m.manejo for m in motivos_campana])
            data_motivos.append([f"Sub Total {campana}:", "", f"{subtotal:,}"])
            data_motivos.append(["", "", ""])  # Línea en blanco para separación
        
        # Eliminar última línea vacía y agregar total
        if data_motivos[-1] == ["", "", ""]:
            data_motivos.pop()
        data_motivos.append(["Total", "", f"{total_motivos:,}"])
        
        table_motivos = Table(data_motivos, colWidths=[4*cm, 8*cm, 3*cm])
        
        # Aplicar estilos más sofisticados
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]
        
        # Resaltar subtotales
        for i, row in enumerate(data_motivos):
            if row[0].startswith("Sub Total"):
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.lightyellow))
                table_style.append(('FONTNAME', (0, i), (-1, i), 'Helvetica-Bold'))
        
        table_motivos.setStyle(TableStyle(table_style))
        
        self.story.append(table_motivos)
        self.story.append(Spacer(1, 18))


    def crear_seccion_automatismos(self, automatismos: Automatismos):
        """Crear sección de automatismos"""
        self.story.append(Paragraph("Automatismos", self.styles['Subtitulo']))
        
        descripcion = """El uso de automatismos libera recursos para la atención de otras consultas más complejas.
        Actualmente está operativa una automatización permanente para el servicio brindado a Móvil Antel."""
        self.story.append(Paragraph(descripcion, self.styles['TextoNormal']))
        self.story.append(Spacer(1, 12))
        
        data_auto = [
            [f"Tarjeta Móvil Agencias - {self.mes_nombre} {self.ano}", "Cantidad", "Porcentaje"],
            ["Total éxito", f"{automatismos.exito:,}", f"{automatismos.pexito:.2%}"],
            ["Total errores", f"{automatismos.error:,}", f"{automatismos.perror:.2%}"],
            ["Total:", f"{automatismos.total:,}", f"{automatismos.ptotal:.2%}"]
        ]
        
        table_auto = Table(data_auto, colWidths=[8*cm, 4*cm, 3*cm])
        table_auto.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        self.story.append(table_auto)
        self.story.append(Spacer(1, 12))
        
        nota = """Las horas incurridas en los automatismos no se computan como horas de operación mensual."""
        self.story.append(Paragraph(nota, self.styles['TextoPequeno']))
        self.story.append(Spacer(1, 18))

    def agregar_footer_personalizado(self):
        """Agregar información de pie de página personalizada"""
        # Información de contacto
        contacto = """<b>Accesa Contact Center</b><br/>
        Vilardebó 1498, Montevideo<br/>
        Email: accesa@accesa.com.uy<br/>
        Tel: +598 2208 2815<br/>
        Web: www.accesa.com.uy"""
        
        self.story.append(Spacer(1, 12))
        self.story.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.lightgrey))
        self.story.append(Spacer(1, 6))
        self.story.append(Paragraph(contacto, self.styles['TextoPequeno']))
        
        # Fecha de generación del reporte
        fecha_generacion = datetime.now().strftime("%d/%m/%Y %H:%M")
        fecha_texto = f"<i>Reporte generado el {fecha_generacion}</i>"
        
        # Estilo para fecha de generación
        estilo_fecha = ParagraphStyle(
            name='FechaGeneracion',
            parent=self.styles['Normal'],
            fontSize=8,
            spaceAfter=0,
            alignment=TA_RIGHT,
            textColor=colors.grey
        )
        
        self.story.append(Spacer(1, 12))
        self.story.append(Paragraph(fecha_texto, estilo_fecha))

    def generar_reporte(self, reporte: Reporte) -> bytes:
        """Generar el reporte completo"""
        
        # Agregar todas las secciones
        self.agregar_titulo_principal() 
        self.crear_tabla_indicadores_principales(reporte.antel_movil_no_global, reporte.antel_movil_global, reporte.mes, reporte.anio)
        self.agregar_incidencias(reporte.incidencias)
        self.agregar_frase_importante(reporte.lista_dias)
        self.agregar_indicadores_globales(reporte.antel_movil_no_global, reporte.antel_movil_global)
        self.crear_seccion_reclamos(reporte.reclamos, reporte.motivosIzi611, reporte.mes, reporte.anio)
        self.crear_seccion_whatsapp(reporte.whatsapp, reporte.mes, reporte.anio)
        self.crear_seccion_salientes(reporte.salientes, reporte.mes, reporte.anio)
        self.crear_seccion_motivos_contacto(reporte.motivos_contacto, reporte.antel_movil_global.llamadas_atendidas_totales_global)
        self.crear_seccion_automatismos(reporte.automatismos)
        self.agregar_footer_personalizado()
        
        # Crear un buffer en memoria para el PDF
        with BytesIO() as buffer:
            # Recrear el documento con el buffer como destino
            self.doc = SimpleDocTemplate(buffer, pagesize=self.doc.pagesize)
        
            # Generar el PDF en el buffer
            self.doc.build(self.story)
        
            # Obtener los bytes del PDF
            pdf_bytes = buffer.getvalue()
    
        print(f"Reporte generado en memoria ({len(pdf_bytes)} bytes)")

        #Guardar manualmente donde quieras
        with open(self.filename, "wb") as f:
            f.write(pdf_bytes)

        return pdf_bytes

