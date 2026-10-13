import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para calcular dinámicamente el número total de páginas y encabezados."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            # Encabezado superior
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#1E3A8A"))
            self.drawString(36, 812, "DWH Transfermarkt")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(125, 812, "|   Bases de Datos Avanzadas   |   Documento de Sustentación Técnica")
            self.drawRightString(559, 812, "Modelo de Constelación (Kimball)")
            
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(36, 806, 559, 806)

            # Pie de página inferior
            self.line(36, 36, 559, 36)
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(36, 26, "Universidad Popular del Cesar  |  Ingeniería de Sistemas  |  5to Semestre")
            self.drawRightString(559, 26, f"Página {self._pageNumber} de {page_count}")
            self.restoreState()

def build_pdf(filename="docs/Documento_Sustentacion_DWH_Transfermarkt.pdf"):
    # Configuración de documento A4 (595.28 x 841.89 pt) con márgenes de 36 pt (ancho útil = 523.28 pt)
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()
    
    # Paleta de colores profesional
    c_primary = colors.HexColor("#1E3A8A")     # Azul marino institucional
    c_secondary = colors.HexColor("#0D9488")   # Teal analítico
    c_dark = colors.HexColor("#1E293B")        # Texto principal
    c_muted = colors.HexColor("#64748B")       # Texto secundario
    c_bg_light = colors.HexColor("#F8FAFC")    # Fondo cajas
    c_border = colors.HexColor("#E2E8F0")      # Bordes suaves
    c_accent = colors.HexColor("#B45309")      # Ámbar de énfasis

    # Estilos tipográficos
    style_cover_super = ParagraphStyle('CoverSuper', fontName='Helvetica-Bold', fontSize=10, textColor=c_secondary, leading=14, spaceAfter=8)
    style_cover_title = ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=24, textColor=c_primary, leading=28, spaceAfter=10)
    style_cover_sub = ParagraphStyle('CoverSub', fontName='Helvetica', fontSize=11, textColor=c_muted, leading=16, spaceAfter=20)
    
    style_chap_num = ParagraphStyle('ChapNum', fontName='Helvetica-Bold', fontSize=9, textColor=c_secondary, leading=12, spaceAfter=2)
    style_chap_title = ParagraphStyle('ChapTitle', fontName='Helvetica-Bold', fontSize=15, textColor=c_primary, leading=18, spaceAfter=4, keepWithNext=True)
    style_chap_sub = ParagraphStyle('ChapSub', fontName='Helvetica-Oblique', fontSize=8.5, textColor=c_muted, leading=11, spaceAfter=10, keepWithNext=True)
    
    style_sec_title = ParagraphStyle('SecTitle', fontName='Helvetica-Bold', fontSize=10.5, textColor=c_primary, leading=14, spaceBefore=8, spaceAfter=4, keepWithNext=True)
    style_subsec_title = ParagraphStyle('SubSecTitle', fontName='Helvetica-Bold', fontSize=9, textColor=c_dark, leading=12, spaceBefore=6, spaceAfter=3, keepWithNext=True)
    
    style_body = ParagraphStyle('Body', fontName='Helvetica', fontSize=8, textColor=c_dark, leading=11, spaceAfter=5)
    style_body_bold = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=8, textColor=c_dark, leading=11, spaceAfter=5)
    style_bullet = ParagraphStyle('Bullet', fontName='Helvetica', fontSize=8, textColor=c_dark, leading=11, leftIndent=12, spaceAfter=3)
    
    style_callout = ParagraphStyle('Callout', fontName='Helvetica', fontSize=8, textColor=c_dark, leading=11)
    style_code = ParagraphStyle('Code', fontName='Courier', fontSize=6.8, textColor=colors.HexColor("#0F172A"), leading=8.5)
    
    style_th = ParagraphStyle('TH', fontName='Helvetica-Bold', fontSize=7.5, textColor=colors.white, leading=9.5, alignment=1)
    style_td = ParagraphStyle('TD', fontName='Helvetica', fontSize=7, textColor=c_dark, leading=8.8)
    style_td_bold = ParagraphStyle('TDBold', fontName='Helvetica-Bold', fontSize=7, textColor=c_dark, leading=8.8)
    style_td_center = ParagraphStyle('TDCenter', fontName='Helvetica', fontSize=7, textColor=c_dark, leading=8.8, alignment=1)

    story = []

    def callout_box(text, bg="#F1F5F9", border="#CBD5E1"):
        p = Paragraph(text, style_callout)
        t = Table([[p]], colWidths=[523.28])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg)),
            ('BOX', (0,0), (-1,-1), 0.8, colors.HexColor(border)),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        return t

    def code_box(code_text):
        p = Paragraph(code_text.replace('\n', '<br/>').replace(' ', '&nbsp;'), style_code)
        t = Table([[p]], colWidths=[523.28])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        return t

    # =========================================================================
    # PÁGINA 1: PORTADA INSTITUCIONAL
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("PROYECTO INTEGRADOR &nbsp;|&nbsp; BASES DE DATOS AVANZADAS", style_cover_super))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Data Warehouse del<br/>Ecosistema Futbolístico<br/>Transfermarkt", style_cover_title))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "<b>PostgreSQL 16</b> &nbsp;|&nbsp; <b>Arquitectura Medallón (Bronce, Plata, Oro)</b><br/>"
        "<b>Modelo de Constelación de Hechos (Kimball Bus Architecture)</b><br/>"
        "Pipeline ETL en Python &nbsp;|&nbsp; Analítica Multidimensional en Power BI",
        style_cover_sub
    ))
    
    story.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=10, spaceAfter=20))
    
    callout_portada = (
        "<b>DOCUMENTO DE SUSTENTACIÓN TÉCNICA Y GUÍA DE DEFENSA ORAL</b><br/><br/>"
        "Este documento técnico consolida los fundamentos arquitectónicos, el modelo dimensional de "
        "Constelación de Hechos, la metodología de calidad EDA, el pipeline de ingeniería de datos, "
        "las optimizaciones físicas en PostgreSQL y la estrategia analítica del proyecto integrador, "
        "diseñado para procesar y analizar más de <b>10,5 millones de registros</b> con tiempos de respuesta sub-segundo."
    )
    story.append(callout_box(callout_portada, bg="#EFF6FF", border="#93C5FD"))
    
    story.append(Spacer(1, 140))
    
    meta_box = [
        [Paragraph("<b>Programa:</b> Ingeniería de Sistemas", style_body), Paragraph("<b>Asignatura:</b> Bases de Datos Avanzadas", style_body)],
        [Paragraph("<b>Semestre:</b> 5to Semestre Académico", style_body), Paragraph("<b>Institución:</b> Universidad Popular del Cesar", style_body)],
        [Paragraph("<b>Integrantes:</b> Juan Sebastián Rincón Farelo y equipo", style_body), Paragraph("<b>Docente:</b> Docente Titular de la Cátedra", style_body)],
        [Paragraph("<b>Fecha:</b> Octubre de 2026", style_body), Paragraph("<b>Ubicación:</b> Valledupar, Cesar, Colombia", style_body)],
    ]
    t_meta = Table(meta_box, colWidths=[261.64, 261.64])
    t_meta.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: TABLA DE CONTENIDO (ÍNDICE)
    # =========================================================================
    story.append(Paragraph("ÍNDICE GENERAL DE CONTENIDO", style_chap_title))
    story.append(Paragraph("Estructura capitular del documento de sustentación", style_chap_sub))
    story.append(Spacer(1, 10))

    toc_data = [
        [Paragraph("<b>Capítulo</b>", style_th), Paragraph("<b>Título del Capítulo y Alcance Temático</b>", style_th), Paragraph("<b>Pág.</b>", style_th)],
        [Paragraph("1", style_td_center), Paragraph("<b>Resumen ejecutivo y contexto:</b> Problema, solución OLAP, alcance y cronograma.", style_td), Paragraph("3", style_td_center)],
        [Paragraph("2", style_td_center), Paragraph("<b>Objetivos y requerimientos:</b> Objetivo general, específicos, matriz RF01–RF10 y RNF01–RNF09.", style_td), Paragraph("4", style_td_center)],
        [Paragraph("3", style_td_center), Paragraph("<b>Volumetría y dimensionamiento físico:</b> Métricas reales (10,56 M), consumo en disco y SLAs.", style_td), Paragraph("6", style_td_center)],
        [Paragraph("4", style_td_center), Paragraph("<b>La base de datos de origen:</b> Las 7 entidades de Transfermarkt y contraste OLTP vs OLAP.", style_td), Paragraph("7", style_td_center)],
        [Paragraph("5", style_td_center), Paragraph("<b>Diseño del modelo de constelación de hechos:</b> Justificación Kimball, matriz de bus, DDLs.", style_td), Paragraph("9", style_td_center)],
        [Paragraph("6", style_td_center), Paragraph("<b>Arquitectura Medallón:</b> Roles por capa (Bronce, Plata, Oro, Meta) y stack tecnológico.", style_td), Paragraph("12", style_td_center)],
        [Paragraph("7", style_td_center), Paragraph("<b>Reglas del proceso EDA:</b> Catálogo E01–E10, calidad de datos y auditoría en meta.etl_rejected.", style_td), Paragraph("14", style_td_center)],
        [Paragraph("8", style_td_center), Paragraph("<b>Proceso ETL:</b> Flujo masivo por chunks con COPY, SQL set-based y expansión sintética.", style_td), Paragraph("15", style_td_center)],
        [Paragraph("9", style_td_center), Paragraph("<b>Capa Oro: agregaciones, índices y particiones:</b> Vistas materializadas concurrentes y partición.", style_td), Paragraph("17", style_td_center)],
        [Paragraph("10", style_td_center), Paragraph("<b>Dashboard Power BI y storytelling:</b> 4 páginas de negocio, medidas DAX y narrativa.", style_td), Paragraph("18", style_td_center)],
        [Paragraph("11", style_td_center), Paragraph("<b>Guía por diapositiva:</b> Resumen técnico y discurso de defensa para las 13 diapositivas.", style_td), Paragraph("20", style_td_center)],
        [Paragraph("12", style_td_center), Paragraph("<b>Banco de preguntas para la sustentación:</b> 15 respuestas directas y de alta rigurosidad.", style_td), Paragraph("23", style_td_center)],
        [Paragraph("13", style_td_center), Paragraph("<b>Puntos de atención y lista de verificación:</b> Checklist previo a la evaluación final.", style_td), Paragraph("25", style_td_center)],
    ]
    t_toc = Table(toc_data, colWidths=[35, 445, 43.28])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 20))

    callout_toc = (
        "<b>Nota sobre la evolución arquitectónica:</b> Este documento refleja la evolución definitiva "
        "desde el modelo estrella original hacia un <b>Modelo de Constelación de Hechos (Kimball Bus Architecture)</b>, "
        "con entidades en español en la capa Gold (<i>dim_*</i>, <i>hecho_*</i>, <i>agg_*</i>) y validación "
        "empírica de 10.565.092 registros con 55 pruebas automatizadas pasando al 100%."
    )
    story.append(callout_box(callout_toc, bg="#FEF3C7", border="#F59E0B"))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: CAPÍTULO 1 - RESUMEN EJECUTIVO Y CONTEXTO
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 1", style_chap_num))
    story.append(Paragraph("Resumen ejecutivo y contexto", style_chap_title))
    story.append(Paragraph("Qué problema se resuelve, qué se construye y cronograma de entrega", style_chap_sub))

    story.append(Paragraph(
        "El fútbol profesional moderno toma decisiones críticas de reclutamiento (scouting), valorización "
        "de activos y planteamiento táctico fundamentándose en analítica de datos a gran escala. La plataforma "
        "Transfermarkt representa una de las fuentes abiertas más ricas a nivel global, abarcando competencias, "
        "clubes, perfiles de futbolistas, partidos, valoraciones de mercado y eventos detallados minuto a minuto. "
        "No obstante, explotar analíticamente estos datos sobre un esquema transaccional (OLTP) normalizado ocasiona "
        "consultas lentas, cuellos de botella por múltiples JOINs costosos y bloqueos con las escrituras operacionales.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Solución implementada:</b> Se construyó un Data Warehouse (OLAP) de alto rendimiento en <b>PostgreSQL 16</b> "
        "utilizando la <b>Arquitectura Medallón</b> dividida en esquemas especializados: <b>Bronze</b> (ingesta cruda en texto "
        "con metadatos de linaje), <b>Silver</b> (limpieza, normalización relacional, tipado fuerte y reglas de calidad EDA E01–E10) "
        "y <b>Gold</b> (modelo multidimensional de Constelación de Hechos bajo la metodología Kimball y vistas materializadas). "
        "La orquestación se realiza mediante un pipeline modular en Python (procesamiento por bloques con COPY masivo) "
        "y el consumo analítico se canaliza hacia <b>Power BI</b> mediante tableros ejecutivos orientados a la toma de decisiones.",
        style_body
    ))

    story.append(Paragraph("1.1 Alcance del proyecto en una frase", style_sec_title))
    callout_c1 = (
        "<b>Alcance Global:</b> Consolidar y procesar <b>10.565.092 registros</b> del ecosistema Transfermarkt en un "
        "Data Warehouse en PostgreSQL con <b>Modelo de Constelación de Hechos</b>, completamente auditado, idempotente y "
        "con tiempos de respuesta analítica sub-segundo (&lt; 0,39 s), dando respuesta integral a 11 requerimientos "
        "funcionales de negocio a través de Power BI."
    )
    story.append(callout_box(callout_c1, bg="#EFF6FF", border="#93C5FD"))

    story.append(Paragraph("1.2 Cronograma y entregables del curso", style_sec_title))
    crono_data = [
        [Paragraph("<b>Fecha</b>", style_th), Paragraph("<b>Hito de Entrega</b>", style_th), Paragraph("<b>Contenido Técnico Exigido</b>", style_th), Paragraph("<b>Capítulo</b>", style_th)],
        [Paragraph("28 sep", style_td_center), Paragraph("Presentación inicial (5 min)", style_td), Paragraph("Introducción al dominio, objetivo general, específicos, requerimientos y volumetría preliminar.", style_td), Paragraph("Cap. 1, 2, 3", style_td_center)],
        [Paragraph("30 sep", style_td_center), Paragraph("Sustentación de modelo", style_td), Paragraph("Diseño del modelo dimensional, justificación de granos y separación en constelación de hechos.", style_td), Paragraph("Cap. 5", style_td_center)],
        [Paragraph("07 oct", style_td_center), Paragraph("Calidad y Arquitectura", style_td), Paragraph("Arquitectura Medallón, reglas EDA E01–E10, tipado, normalización y linaje técnico.", style_td), Paragraph("Cap. 6, 7", style_td_center)],
        [Paragraph("12 oct", style_td_center), Paragraph("Pipeline ETL y expansión", style_td), Paragraph("Implementación ETL en Python, carga por chunks, expansión controlada a 10,5M y validaciones.", style_td), Paragraph("Cap. 8, 9", style_td_center)],
        [Paragraph("14 oct", style_td_center), Paragraph("Sustentación final y BI", style_td), Paragraph("Dashboard en Power BI, storytelling, benchmarks de consulta OLAP y defensa del proyecto.", style_td), Paragraph("Cap. 10, 11, 12", style_td_center)],
    ]
    t_crono = Table(crono_data, colWidths=[45, 120, 308.28, 50])
    t_crono.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_crono)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINAS 4-5: CAPÍTULO 2 - OBJETIVOS Y REQUERIMIENTOS
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 2", style_chap_num))
    story.append(Paragraph("Objetivos y requerimientos del sistema", style_chap_title))
    story.append(Paragraph("Qué se debe lograr y cómo se demuestra técnicamente su cumplimiento", style_chap_sub))

    story.append(Paragraph("2.1 Objetivo General", style_sec_title))
    story.append(Paragraph(
        "Diseñar, implementar y validar un Data Warehouse en PostgreSQL bajo Arquitectura Medallón y un Modelo "
        "de Constelación de Hechos (Kimball Bus Architecture) con dimensiones conformadas compartidas, procesando "
        "más de 10,5 millones de registros de Transfermarkt para soportar análisis multidimensional en Power BI "
        "con tiempos de respuesta inferiores a 3 segundos (SLA cumplido en &lt; 0,39 s).",
        style_body
    ))

    story.append(Paragraph("2.2 Objetivos Específicos", style_sec_title))
    story.append(Paragraph("<b>1. Ingesta masiva y linaje (Bronce):</b> Aterrizar los 7 datasets CSV mediante COPY por bloques de 100.000 filas, preservando texto crudo y metadatos de auditoría (_load_id, _loaded_at, _source_file, _row_id).", style_bullet))
    story.append(Paragraph("<b>2. Depuración e integridad (Plata):</b> Aplicar reglas EDA E01–E10 para tipar datos, imputar nulos canónicamente y verificar 0 huérfanos con claves primarias y foráneas estrictas.", style_bullet))
    story.append(Paragraph("<b>3. Modelado dimensional (Oro):</b> Estructurar una Constelación con 7 dimensiones conformadas y 3 tablas de hechos independientes según su grano analítico.", style_bullet))
    story.append(Paragraph("<b>4. Expansión controlada de volumen:</b> Escalar el volumen desde 3,62 M reales hasta 10.565.092 registros sintéticos deterministas, trazables y 100% reversibles sin contaminar la analítica.", style_bullet))
    story.append(Paragraph("<b>5. Optimización física:</b> Particionar por rango anual la tabla masiva de eventos (1990–2035) y crear índices B-Tree y Hash para maximizar partition pruning.", style_bullet))
    story.append(Paragraph("<b>6. Explotación analítica:</b> Precalcular vistas materializadas concurrentes y diseñar un dashboard de 4 páginas en Power BI conectado vía PostgreSQL.", style_bullet))

    story.append(Paragraph("2.3 Matriz de Requerimientos Funcionales (RF01 – RF10)", style_sec_title))
    rf_data = [
        [Paragraph("<b>ID</b>", style_th), Paragraph("<b>Requerimiento Funcional de Negocio</b>", style_th), Paragraph("<b>Entidad Gold / Resolución Técnica</b>", style_th)],
        [Paragraph("RF01", style_td_center), Paragraph("Top goleadores y asistidores por temporada y liga.", style_td), Paragraph("gold.hecho_rendimiento_jugador + gold.agg_jugador_temporada_liga", style_td)],
        [Paragraph("RF02", style_td_center), Paragraph("Rendimiento comparativo por posición y rol en el campo.", style_td), Paragraph("gold.hecho_rendimiento_jugador + gold.dim_jugador(posicion, sub_posicion)", style_td)],
        [Paragraph("RF03", style_td_center), Paragraph("Evolución temporal del rendimiento de jugadores a lo largo de los años.", style_td), Paragraph("gold.hecho_rendimiento_jugador + gold.dim_fecha(temporada)", style_td)],
        [Paragraph("RF04", style_td_center), Paragraph("Tabla de posiciones y puntos por club y temporada (3, 1, 0 pts).", style_td), Paragraph("gold.dim_partido(goles_local, goles_visitante) + gold.agg_club_temporada", style_td)],
        [Paragraph("RF05", style_td_center), Paragraph("Relación y correlación estadística entre valor de plantilla y puntos.", style_td), Paragraph("gold.hecho_valoraciones_mercado + gold.agg_club_temporada (corr() en PG)", style_td)],
        [Paragraph("RF06", style_td_center), Paragraph("Disciplina arbitral: promedio de tarjetas por partido y por 90 min.", style_td), Paragraph("gold.hecho_eventos_partido + gold.agg_disciplina_arbitro", style_td)],
        [Paragraph("RF07", style_td_center), Paragraph("Distribución temporal de goles y tarjetas por franjas de 15 minutos.", style_td), Paragraph("gold.hecho_eventos_partido(franja_15min) + gold.agg_eventos_15min", style_td)],
        [Paragraph("RF08", style_td_center), Paragraph("Módulo de scouting de promesas Sub-23 (rendimiento vs tasación).", style_td), Paragraph("gold.hecho_rendimiento_jugador + gold.dim_jugador(fecha_nacimiento)", style_td)],
        [Paragraph("RF09", style_td_center), Paragraph("Balance local vs visitante: porcentaje de victorias y goles.", style_td), Paragraph("gold.dim_partido + gold.agg_local_visitante", style_td)],
        [Paragraph("RF10", style_td_center), Paragraph("Precalculo y aceleración OLAP mediante vistas materializadas.", style_td), Paragraph("5 vistas gold.agg_* con UNIQUE INDEX y REFRESH CONCURRENTLY", style_td)],
    ]
    t_rf = Table(rf_data, colWidths=[35, 230, 258.28])
    t_rf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_rf)
    story.append(PageBreak())

    # CONTINUACIÓN CAPÍTULO 2 (PÁGINA 5): REQUERIMIENTOS NO FUNCIONALES
    story.append(Paragraph("2.4 Matriz de Requerimientos No Funcionales (RNF01 – RNF09)", style_sec_title))
    rnf_data = [
        [Paragraph("<b>ID</b>", style_th), Paragraph("<b>Requerimiento No Funcional</b>", style_th), Paragraph("<b>Mecanismo de Implementación y Evidencia Técnica</b>", style_th)],
        [Paragraph("RNF01", style_td_center), Paragraph("Carga por bloques (Chunk Size)", style_td), Paragraph("Ingesta masiva en Python con pandas y comando COPY de PostgreSQL por chunks de 100.000 filas.", style_td)],
        [Paragraph("RNF02", style_td_center), Paragraph("Integridad referencial estricta", style_td), Paragraph("Restricciones FK en Silver y Gold. Cero registros huérfanos verificado por consultas de validación.", style_td)],
        [Paragraph("RNF03", style_td_center), Paragraph("SLA de consulta analítica &lt; 3 s", style_td), Paragraph("Benchmarks en PostgreSQL: todas las consultas clave responden entre 0,001 s y 0,386 s (meta &lt; 3,0 s).", style_td)],
        [Paragraph("RNF04", style_td_center), Paragraph("Vistas materializadas actualizables", style_td), Paragraph("Índices únicos en todas las vistas gold.agg_* permitiendo REFRESH MATERIALIZED VIEW CONCURRENTLY.", style_td)],
        [Paragraph("RNF05", style_td_center), Paragraph("Estandarización de fechas", style_td), Paragraph("Conversión uniforme a DATE ISO-8601 mediante función en PL/pgSQL meta.to_date.", style_td)],
        [Paragraph("RNF06", style_td_center), Paragraph("Imputación controlada de nulos", style_td), Paragraph("Reglas E01 (métricas a 0), E02 (valor de mercado a NULL) y E03 (textos a 'Desconocido').", style_td)],
        [Paragraph("RNF07", style_td_center), Paragraph("Idempotencia y reejecución", style_td), Paragraph("TRUNCATE en Bronce y UPSERT (INSERT ... ON CONFLICT DO UPDATE) en Silver y Gold; reejecutar no duplica.", style_td)],
        [Paragraph("RNF08", style_td_center), Paragraph("Particionamiento físico por rango", style_td), Paragraph("Tabla masiva gold.hecho_eventos_partido particionada anualmente por fecha_key (1990–2035).", style_td)],
        [Paragraph("RNF09", style_td_center), Paragraph("Tolerancia a fallos de codificación", style_td), Paragraph("Intento inicial en UTF-8 con fallback automático a Latin-1 y conteo con csv.reader sin falsos descartes.", style_td)],
    ]
    t_rnf = Table(rnf_data, colWidths=[38, 170, 315.28])
    t_rnf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_rnf)
    story.append(Spacer(1, 15))

    callout_rnf = (
        "<b>Verificación de Cumplimiento:</b> La suite automatizada de pruebas con <b>pytest (55 pruebas)</b> "
        "y el script de diagnóstico <b>scripts/validate.py</b> evalúan sistemáticamente cada uno de estos RNF, "
        "registrando 0 fallos de esquema, 0 violaciones de partición y 100% de integridad referencial."
    )
    story.append(callout_box(callout_rnf, bg="#ECFDF5", border="#10B981"))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 6: CAPÍTULO 3 - VOLUMETRÍA Y DIMENSIONAMIENTO FÍSICO
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 3", style_chap_num))
    story.append(Paragraph("Volumetría y dimensionamiento físico", style_chap_title))
    story.append(Paragraph("Auditoría real sobre pg_class, pg_relation_size() y tiempos de consulta en PostgreSQL", style_chap_sub))

    story.append(Paragraph("3.1 Resumen de Filas: Datos Reales vs Sintéticos", style_sec_title))
    vol_rows_data = [
        [Paragraph("<b>Tabla en Capa Silver</b>", style_th), Paragraph("<b>Filas Reales</b>", style_th), Paragraph("<b>Filas Sintéticas</b>", style_th), Paragraph("<b>Total Silver</b>", style_th), Paragraph("<b>Meta Propuesta</b>", style_th), Paragraph("<b>Estado</b>", style_th)],
        [Paragraph("silver.competitions", style_td), Paragraph("65", style_td_center), Paragraph("0", style_td_center), Paragraph("65", style_td_center), Paragraph("65", style_td_center), Paragraph("100.0%", style_td_center)],
        [Paragraph("silver.clubs", style_td), Paragraph("796", style_td_center), Paragraph("0", style_td_center), Paragraph("796", style_td_center), Paragraph("796", style_td_center), Paragraph("100.0%", style_td_center)],
        [Paragraph("silver.players", style_td), Paragraph("50.149", style_td_center), Paragraph("0", style_td_center), Paragraph("50.149", style_td_center), Paragraph("50.149", style_td_center), Paragraph("100.0%", style_td_center)],
        [Paragraph("silver.games", style_td), Paragraph("72.602", style_td_center), Paragraph("405.550", style_td_center), Paragraph("478.152", style_td_center), Paragraph("72.602", style_td_center), Paragraph("658.6%", style_td_center)],
        [Paragraph("silver.appearances", style_td), Paragraph("1.813.294", style_td_center), Paragraph("81.056", style_td_center), Paragraph("1.894.350", style_td_center), Paragraph("1.894.350", style_td_center), Paragraph("100.0%", style_td_center)],
        [Paragraph("silver.game_events", style_td), Paragraph("1.032.318", style_td_center), Paragraph("5.724.262", style_td_center), Paragraph("6.756.580", style_td_center), Paragraph("7.187.349", style_td_center), Paragraph("94.0%", style_td_center)],
        [Paragraph("silver.player_valuations", style_td), Paragraph("656.301", style_td_center), Paragraph("728.699", style_td_center), Paragraph("1.385.000", style_td_center), Paragraph("1.385.000", style_td_center), Paragraph("100.0%", style_td_center)],
        [Paragraph("<b>TOTAL CONSOLIDADO</b>", style_td_bold), Paragraph("<b>3.625.525</b>", style_td_center), Paragraph("<b>6.939.567</b>", style_td_center), Paragraph("<b>10.565.092</b>", style_td_center), Paragraph("<b>10.565.088</b>", style_td_center), Paragraph("<b>100.00% (+4)</b>", style_td_center)],
    ]
    t_vrows = Table(vol_rows_data, colWidths=[120, 75, 80, 85, 85, 78.28])
    t_vrows.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, c_bg_light]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EFF6FF")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_vrows)

    story.append(Paragraph("3.2 Consumo Físico en Disco (PostgreSQL) y Tiempos OLAP", style_sec_title))
    vol_disk_data = [
        [Paragraph("<b>Objeto en Base de Datos</b>", style_th), Paragraph("<b>Esquema</b>", style_th), Paragraph("<b>Registros</b>", style_th), Paragraph("<b>Datos (MB)</b>", style_th), Paragraph("<b>Índices (MB)</b>", style_th), Paragraph("<b>Total (MB)</b>", style_th)],
        [Paragraph("gold.hecho_eventos_partido (particiones)", style_td), Paragraph("gold", style_td_center), Paragraph("6.755.738", style_td_center), Paragraph("831,03", style_td_center), Paragraph("1.596,69", style_td_center), Paragraph("2.428,35", style_td_center)],
        [Paragraph("silver.game_events", style_td), Paragraph("silver", style_td_center), Paragraph("6.732.136", style_td_center), Paragraph("1.235,80", style_td_center), Paragraph("783,06", style_td_center), Paragraph("2.019,23", style_td_center)],
        [Paragraph("silver.appearances", style_td), Paragraph("silver", style_td_center), Paragraph("1.889.943", style_td_center), Paragraph("314,56", style_td_center), Paragraph("217,09", style_td_center), Paragraph("531,76", style_td_center)],
        [Paragraph("meta.etl_rejected", style_td), Paragraph("meta", style_td_center), Paragraph("1.018.618", style_td_center), Paragraph("406,22", style_td_center), Paragraph("29,84", style_td_center), Paragraph("436,20", style_td_center)],
        [Paragraph("gold.hecho_rendimiento_jugador", style_td), Paragraph("gold", style_td_center), Paragraph("1.894.350", style_td_center), Paragraph("160,69", style_td_center), Paragraph("230,39", style_td_center), Paragraph("391,14", style_td_center)],
        [Paragraph("silver.player_valuations", style_td), Paragraph("silver", style_td_center), Paragraph("1.385.000", style_td_center), Paragraph("140,61", style_td_center), Paragraph("75,45", style_td_center), Paragraph("216,12", style_td_center)],
        [Paragraph("gold.dim_partido", style_td), Paragraph("gold", style_td_center), Paragraph("478.152", style_td_center), Paragraph("106,88", style_td_center), Paragraph("89,47", style_td_center), Paragraph("196,42", style_td_center)],
        [Paragraph("gold.hecho_valoraciones_mercado", style_td), Paragraph("gold", style_td_center), Paragraph("1.385.000", style_td_center), Paragraph("82,77", style_td_center), Paragraph("112,57", style_td_center), Paragraph("195,40", style_td_center)],
        [Paragraph("gold.agg_jugador_temporada_liga", style_td), Paragraph("gold", style_td_center), Paragraph("167.477", style_td_center), Paragraph("16,94", style_td_center), Paragraph("7,04", style_td_center), Paragraph("24,01", style_td_center)],
        [Paragraph("gold.dim_jugador", style_td), Paragraph("gold", style_td_center), Paragraph("50.149", style_td_center), Paragraph("10,07", style_td_center), Paragraph("4,54", style_td_center), Paragraph("14,65", style_td_center)],
    ]
    t_vdisk = Table(vol_disk_data, colWidths=[175, 45, 75, 75, 75, 78.28])
    t_vdisk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(t_vdisk)
    story.append(Spacer(1, 8))

    bench_box = (
        "<b>Benchmarks OLAP Medidos:</b> Goleadores por temporada y liga: <b>0,017 s</b> | Tabla de posiciones: <b>0,001 s</b> | "
        "Eventos por franja 15 min: <b>0,302 s</b> | Disciplina arbitral: <b>0,002 s</b> | Local vs visitante: <b>0,000 s</b> | "
        "Join masivo eventos por competición (6,75 M filas): <b>0,386 s</b>. SLA exigido &lt; 3,0 s cumplido holgadamente."
    )
    story.append(callout_box(bench_box, bg="#EFF6FF", border="#93C5FD"))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINAS 7-8: CAPÍTULO 4 - LA BASE DE DATOS DE ORIGEN
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 4", style_chap_num))
    story.append(Paragraph("La base de datos de origen (Transfermarkt)", style_chap_title))
    story.append(Paragraph("Las 7 entidades de datos abiertos, su significado de negocio y contraste OLTP vs OLAP", style_chap_sub))

    story.append(Paragraph(
        "El origen de datos proviene del repositorio abierto <i>dcaribou/transfermarkt-datasets</i>, estructurado "
        "en 7 archivos CSV que modelan el ecosistema del fútbol profesional europeo y mundial:",
        style_body
    ))

    ent_data = [
        [Paragraph("<b>Archivo CSV / Entidad</b>", style_th), Paragraph("<b>Grano y Descripción del Negocio</b>", style_th), Paragraph("<b>Clave Natural</b>", style_th), Paragraph("<b>Dependencias Foráneas</b>", style_th)],
        [Paragraph("competitions.csv", style_td), Paragraph("Catálogo de competiciones nacionales e internacionales (ligas y copas).", style_td), Paragraph("competition_id", style_td_center), Paragraph("Ninguna (raíz)", style_td)],
        [Paragraph("clubs.csv", style_td), Paragraph("Clubes deportivos, estadios, valor neto y tamaño de nómina.", style_td), Paragraph("club_id", style_td_center), Paragraph("domestic_competition_id", style_td)],
        [Paragraph("players.csv", style_td), Paragraph("Perfiles de futbolistas, posición, fecha de nacimiento, altura y país.", style_td), Paragraph("player_id", style_td_center), Paragraph("current_club_id", style_td)],
        [Paragraph("games.csv", style_td), Paragraph("Encuentros deportivos disputados con marcadores, estadios y árbitros.", style_td), Paragraph("game_id", style_td_center), Paragraph("competition_id, home_club, away_club", style_td)],
        [Paragraph("appearances.csv", style_td), Paragraph("Alineación y rendimiento acumulado de un futbolista en un partido (90 min).", style_td), Paragraph("appearance_id", style_td_center), Paragraph("game_id, player_id, player_club_id", style_td)],
        [Paragraph("game_events.csv", style_td), Paragraph("Incidencias puntuales de partido ocurridas en un minuto (goles, tarjetas).", style_td), Paragraph("game_event_id", style_td_center), Paragraph("game_id, club_id, player_id", style_td)],
        [Paragraph("player_valuations.csv", style_td), Paragraph("Tasaciones periódicas históricas del valor de mercado del jugador.", style_td), Paragraph("(player_id, date)", style_td_center), Paragraph("player_id, current_club_id", style_td)],
    ]
    t_ent = Table(ent_data, colWidths=[105, 208.28, 90, 120])
    t_ent.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_ent)
    story.append(PageBreak())

    # CONTINUACIÓN CAPÍTULO 4 (PÁGINA 8): CONTRASTE OLTP VS OLAP
    story.append(Paragraph("4.1 Contraste Arquitectónico: Sistema OLTP vs Data Warehouse OLAP", style_sec_title))
    oltp_olap_data = [
        [Paragraph("<b>Aspecto Técnico</b>", style_th), Paragraph("<b>Sistema Operacional (OLTP de Origen)</b>", style_th), Paragraph("<b>Data Warehouse (OLAP en Capa Gold)</b>", style_th)],
        [Paragraph("Propósito principal", style_td_bold), Paragraph("Soportar operaciones diarias transaccionales de alta frecuencia.", style_td), Paragraph("Soportar análisis histórico multidimensional y toma de decisiones.", style_td)],
        [Paragraph("Diseño del modelo", style_td_bold), Paragraph("Normalizado en Tercera Forma Normal (3NF) para evitar redundancias.", style_td), Paragraph("Constelación de Hechos desnormalizada con dimensiones conformadas.", style_td)],
        [Paragraph("Naturaleza de consultas", style_td_bold), Paragraph("Puntuales, basadas en claves primarias, lecturas/escrituras de pocas filas.", style_td), Paragraph("Consultas complejas, agrupaciones masivas y agregaciones sobre millones de filas.", style_td)],
        [Paragraph("Costo de los JOINs", style_td_bold), Paragraph("Múltiples JOINs encadenados que penalizan el rendimiento analítico.", style_td), Paragraph("Esquema estrella/constelación con JOINs directos hacia dimensiones conformadas.", style_td)],
        [Paragraph("Estrategia de índices", style_td_bold), Paragraph("Índices mínimos para no ralentizar inserciones y actualizaciones.", style_td), Paragraph("Índices B-Tree en todas las FKs e índice Hash en columnas de alta selectividad.", style_td)],
        [Paragraph("Historial de tiempo", style_td_bold), Paragraph("Enfocado en el estado actual; el historial suele archivarse o depurarse.", style_td), Paragraph("Histórico inalterable con dimensión fecha (AAAAMMDD) y temporadas.", style_td)],
    ]
    t_olap = Table(oltp_olap_data, colWidths=[95, 214.14, 214.14])
    t_olap.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_olap)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINAS 9-11: CAPÍTULO 5 - DISEÑO DEL MODELO DE CONSTELACIÓN
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 5", style_chap_num))
    story.append(Paragraph("Diseño del modelo de constelación de hechos", style_chap_title))
    story.append(Paragraph("Metodología Ralph Kimball (Kimball Bus Architecture), separación de granos y DDLs en español", style_chap_sub))

    story.append(Paragraph("5.1 Justificación Arquitectónica: ¿Por qué Constelación y no una Estrella Simple?", style_sec_title))
    story.append(Paragraph(
        "En la propuesta inicial se consideró modelar una estrella única con <i>fact_events</i> en el centro. Sin embargo, "
        "en la práctica de ingeniería de datos y según los principios canónicos de Ralph Kimball, esa decisión adolecía "
        "de tres defectos graves de diseño:",
        style_body
    ))
    story.append(Paragraph("<b>1. Desajuste de Granularidad (Granularity Mismatch):</b> Un evento ocurre al minuto específico de un partido. Las alineaciones y el rendimiento físico (minutos jugados, kilómetros, asistencias) ocurren a nivel del partido completo (90 min). Forzar ambos en una sola tabla obligaba a inventar filas artificiales para futbolistas sin incidencias o a duplicar minutos por cada evento.", style_bullet))
    story.append(Paragraph("<b>2. Destrucción de la Aditividad:</b> <i>game_events</i> es una <i>Factless Fact Table</i> (tabla sin métricas numéricas acumulativas). Intentar calcular el total de goles o minutos de un jugador desde allí provocaba trampas de agregación (fan traps).", style_bullet))
    story.append(Paragraph("<b>3. Independencia de Procesos de Negocio:</b> La actuación en cancha, los incidentes cronometrados y las tasaciones financieras son tres procesos de negocio distintos que deben modelarse en tres tablas de hechos separadas.", style_bullet))

    story.append(Paragraph("5.2 Matriz de Bus de Arquitectura (Kimball Bus Matrix)", style_sec_title))
    bus_data = [
        [Paragraph("<b>Proceso de Negocio / Tabla de Hechos</b>", style_th), Paragraph("<b>dim_fecha</b>", style_th), Paragraph("<b>dim_competicion</b>", style_th), Paragraph("<b>dim_club</b>", style_th), Paragraph("<b>dim_jugador</b>", style_th), Paragraph("<b>dim_arbitro</b>", style_th), Paragraph("<b>dim_tipo_evento</b>", style_th), Paragraph("<b>dim_partido</b>", style_th)],
        [Paragraph("<b>Rendimiento Jugador</b> (hecho_rendimiento_jugador)", style_td), Paragraph("<b>X</b>", style_td_center), Paragraph("<b>X</b>", style_td_center), Paragraph("<b>X</b>", style_td_center), Paragraph("<b>X</b>", style_td_center), Paragraph("-", style_td_center), Paragraph("-", style_td_center), Paragraph("<b>X</b>", style_td_center)],
        [Paragraph("<b>Eventos de Partido</b> (hecho_eventos_partido)", style_td), Paragraph("<b>X</b>", style_td_center), Paragraph("<b>X</b>", style_td_center), Paragraph("<b>X</b>", style_td_center), Paragraph("<b>X</b>", style_td_center), Paragraph("<b>X</b>", style_td_center), Paragraph("<b>X</b>", style_td_center), Paragraph("<b>X</b>", style_td_center)],
        [Paragraph("<b>Valoraciones Mercado</b> (hecho_valoraciones_mercado)", style_td), Paragraph("<b>X</b>", style_td_center), Paragraph("-", style_td_center), Paragraph("<b>X</b>", style_td_center), Paragraph("<b>X</b>", style_td_center), Paragraph("-", style_td_center), Paragraph("-", style_td_center), Paragraph("-", style_td_center)],
    ]
    t_bus = Table(bus_data, colWidths=[155, 52, 53, 52, 53, 52, 53, 53.28])
    t_bus.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_bus)

    story.append(Paragraph("5.3 Diagrama Conceptual de la Constelación", style_sec_title))
    diagram_box = (
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[dim_fecha]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[dim_competicion]&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[dim_arbitro]<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br/>"
        "[dim_jugador] ──► [hecho_rendimiento_jugador] ──► [dim_partido] ──────► [dim_club]<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├────────► [hecho_eventos_partido] (partic.) ──┴───► [dim_tipo_evento]<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└────────► [hecho_valoraciones_mercado] (snapshot)"
    )
    story.append(code_box(diagram_box))
    story.append(PageBreak())

    # CONTINUACIÓN CAPÍTULO 5 (PÁGINA 10): DICCIONARIO DIMENSIONES Y HECHOS
    story.append(Paragraph("5.4 Diccionario de Entidades: 7 Dimensiones Conformadas y 3 Hechos", style_sec_title))
    dim_dict_data = [
        [Paragraph("<b>Tabla Dimensional</b>", style_th), Paragraph("<b>Clave Primaria</b>", style_th), Paragraph("<b>Atributos Relevantes</b>", style_th), Paragraph("<b>Jerarquías Analíticas</b>", style_th)],
        [Paragraph("gold.dim_fecha", style_td_bold), Paragraph("fecha_key (INT)", style_td_center), Paragraph("fecha_completa, anio, trimestre, mes, nombre_mes, semana, temporada", style_td), Paragraph("Día ──► Mes ──► Trimestre ──► Temporada (jul-jun)", style_td)],
        [Paragraph("gold.dim_competicion", style_td_bold), Paragraph("competicion_key (SERIAL)", style_td_center), Paragraph("competicion_id (UK), nombre, tipo (liga/copa), pais, confederacion", style_td), Paragraph("Competición ──► País ──► Confederación", style_td)],
        [Paragraph("gold.dim_club", style_td_bold), Paragraph("club_key (SERIAL)", style_td_center), Paragraph("club_id (UK), nombre, competicion_key (FK), estadio, tamanio_plantilla, edad_promedio", style_td), Paragraph("Club ──► Liga Doméstica ──► Confederación", style_td)],
        [Paragraph("gold.dim_jugador", style_td_bold), Paragraph("jugador_key (SERIAL)", style_td_center), Paragraph("jugador_id (UK), nombre, posicion, sub_posicion, fecha_nacimiento, pais, pie, altura", style_td), Paragraph("Jugador ──► Sub-Posición ──► Posición Principal", style_td)],
        [Paragraph("gold.dim_arbitro", style_td_bold), Paragraph("arbitro_key (SERIAL)", style_td_center), Paragraph("nombre_arbitro (TEXT UNIQUE)", style_td), Paragraph("Árbitro individual", style_td)],
        [Paragraph("gold.dim_tipo_evento", style_td_bold), Paragraph("tipo_evento_key (SERIAL)", style_td_center), Paragraph("nombre_tipo_evento (TEXT UNIQUE: Goals, Cards, Substitutions)", style_td), Paragraph("Incidencia ──► Categoría Disciplinaria / Gol", style_td)],
        [Paragraph("gold.dim_partido", style_td_bold), Paragraph("partido_key (SERIAL)", style_td_center), Paragraph("partido_id (UK), temporada, jornada, fecha_partido, goles_local, goles_visitante, arbitro", style_td), Paragraph("Partido ──► Jornada ──► Temporada", style_td)],
    ]
    t_dimdict = Table(dim_dict_data, colWidths=[105, 80, 195, 143.28])
    t_dimdict.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_dimdict)
    story.append(Spacer(1, 8))

    facts_dict_data = [
        [Paragraph("<b>Tabla de Hechos</b>", style_th), Paragraph("<b>Grano Analítico</b>", style_th), Paragraph("<b>Tipo Dimensional</b>", style_th), Paragraph("<b>Métricas / Atributos de Negocio</b>", style_th)],
        [Paragraph("gold.hecho_rendimiento_jugador", style_td_bold), Paragraph("Aparición de un futbolista en un partido específico (90 min).", style_td), Paragraph("Hecho Transaccional con Métricas Aditivas.", style_td), Paragraph("minutos_jugados, goles, asistencias, tarjetas_amarillas, tarjetas_rojas.", style_td)],
        [Paragraph("gold.hecho_eventos_partido", style_td_bold), Paragraph("Incidencia puntual ocurrida en un minuto determinado de partido.", style_td), Paragraph("Factless Fact Table particionada por rango anual.", style_td), Paragraph("minuto, franja_15min (0 a 6), es_local (booleano).", style_td)],
        [Paragraph("gold.hecho_valoraciones_mercado", style_td_bold), Paragraph("Tasación de mercado de un futbolista en una fecha dada.", style_td), Paragraph("Periodic Snapshot (Métrica Semi-Aditiva).", style_td), Paragraph("valor_mercado_eur (NUMERIC 14,2).", style_td)],
    ]
    t_factsdict = Table(facts_dict_data, colWidths=[130, 130, 120, 143.28])
    t_factsdict.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_factsdict)
    story.append(PageBreak())

    # CONTINUACIÓN CAPÍTULO 5 (PÁGINA 11): DDLS REALES DE LA CAPA ORO
    story.append(Paragraph("5.5 Definición DDL Real de la Capa Oro (Extracto sql/gold/04_dimensions_facts.sql)", style_sec_title))
    ddl_sample = (
        "-- 1. Dimensiones conformadas en español con llaves sustitutas y llaves naturales UNIQUE\n"
        "CREATE TABLE gold.dim_fecha (fecha_key INT PRIMARY KEY, fecha_completa DATE NOT NULL UNIQUE, ... temporada SMALLINT);\n"
        "CREATE TABLE gold.dim_jugador (jugador_key SERIAL PRIMARY KEY, jugador_id INT NOT NULL UNIQUE, nombre TEXT, posicion TEXT, ...);\n"
        "CREATE TABLE gold.dim_partido (partido_key SERIAL PRIMARY KEY, partido_id INT NOT NULL UNIQUE, competicion_key INT REFERENCES ...,\n"
        "  club_local_key INT, club_visitante_key INT, fecha_key INT, goles_local SMALLINT, goles_visitante SMALLINT, es_sintetico BOOLEAN);\n\n"
        "-- 2. Hecho 1: Rendimiento deportivo (Métricas Aditivas: goles, asistencias, minutos jugados)\n"
        "CREATE TABLE gold.hecho_rendimiento_jugador (\n"
        "  rendimiento_key BIGSERIAL PRIMARY KEY, aparicion_id VARCHAR(40) NOT NULL UNIQUE,\n"
        "  fecha_key INT REFERENCES gold.dim_fecha, partido_key INT REFERENCES gold.dim_partido,\n"
        "  jugador_key INT REFERENCES gold.dim_jugador, club_key INT REFERENCES gold.dim_club,\n"
        "  competicion_key INT REFERENCES gold.dim_competicion,\n"
        "  minutos_jugados INT, goles SMALLINT, asistencias SMALLINT, tarjetas_amarillas SMALLINT, tarjetas_rojas SMALLINT,\n"
        "  es_sintetico BOOLEAN NOT NULL DEFAULT FALSE\n"
        ");\n\n"
        "-- 3. Hecho 2: Eventos e incidencias discretas (Factless particionada por rango de fecha_key)\n"
        "CREATE TABLE gold.hecho_eventos_partido (\n"
        "  evento_key BIGSERIAL, evento_partido_id VARCHAR(64) NOT NULL,\n"
        "  fecha_key INT NOT NULL REFERENCES gold.dim_fecha, partido_key INT NOT NULL REFERENCES gold.dim_partido,\n"
        "  competicion_key INT NOT NULL REFERENCES gold.dim_competicion, club_key INT NOT NULL REFERENCES gold.dim_club,\n"
        "  jugador_key INT REFERENCES gold.dim_jugador, arbitro_key INT REFERENCES gold.dim_arbitro,\n"
        "  tipo_evento_key INT NOT NULL REFERENCES gold.dim_tipo_evento,\n"
        "  minuto SMALLINT, franja_15min SMALLINT, es_local BOOLEAN, es_sintetico BOOLEAN NOT NULL DEFAULT FALSE,\n"
        "  PRIMARY KEY (evento_key, fecha_key)\n"
        ") PARTITION BY RANGE (fecha_key);\n\n"
        "-- 4. Hecho 3: Valoraciones históricas de mercado (Periodic Snapshot)\n"
        "CREATE TABLE gold.hecho_valoraciones_mercado (\n"
        "  valoracion_key BIGSERIAL PRIMARY KEY, jugador_id INT NOT NULL, fecha_valoracion DATE NOT NULL,\n"
        "  fecha_key INT NOT NULL REFERENCES gold.dim_fecha, jugador_key INT NOT NULL REFERENCES gold.dim_jugador,\n"
        "  club_key INT REFERENCES gold.dim_club, valor_mercado_eur NUMERIC(14,2),\n"
        "  es_sintetico BOOLEAN NOT NULL DEFAULT FALSE, UNIQUE (jugador_id, fecha_valoracion)\n"
        ");"
    )
    story.append(code_box(ddl_sample))
    story.append(Spacer(1, 10))

    callout_c5 = (
        "<b>Ventaja frente a la estrella única:</b> Esta constelación permite que las consultas de "
        "goleadores (RF01) consulten directamente <i>hecho_rendimiento_jugador</i> sumando minutos y goles reales; "
        "mientras que las consultas de franjas horarias (RF07) consultan <i>hecho_eventos_partido</i> aprovechando "
        "el particionamiento anual por <i>fecha_key</i>, sin incurrir en interferencias de grano."
    )
    story.append(callout_box(callout_c5, bg="#ECFDF5", border="#10B981"))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINAS 12-13: CAPÍTULO 6 - ARQUITECTURA MEDALLÓN
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 6", style_chap_num))
    story.append(Paragraph("Arquitectura Medallón y gobernanza", style_chap_title))
    story.append(Paragraph("Capas Bronce, Plata, Oro y Meta: roles, responsabilidades y stack tecnológico", style_chap_sub))

    story.append(Paragraph("6.1 Estructura en Capas y Gobernanza Transversal", style_sec_title))
    medallion_data = [
        [Paragraph("<b>Capa / Esquema</b>", style_th), Paragraph("<b>Rol y Propósito Técnico</b>", style_th), Paragraph("<b>Estrategia de Carga e Idempotencia</b>", style_th), Paragraph("<b>Formato y Tipado</b>", style_th)],
        [Paragraph("<b>meta</b>", style_td_bold), Paragraph("Gobernanza, auditoría (etl_audit), registro de rechazos (etl_rejected) y funciones SQL.", style_td), Paragraph("Inserción append-only de eventos de auditoría y rechazos con run_id.", style_td), Paragraph("Metadatos técnicos y tablas de auditoría.", style_td)],
        [Paragraph("<b>bronze</b>", style_td_bold), Paragraph("Ingesta cruda de CSVs tal como vienen de la fuente. Preservación estricta de linaje.", style_td), Paragraph("TRUNCATE ... RESTART IDENTITY + inserción masiva por chunks con COPY.", style_td), Paragraph("Todas las columnas en TEXT + 4 columnas de auditoría técnica.", style_td)],
        [Paragraph("<b>silver</b>", style_td_bold), Paragraph("Datos limpios, tipados, deduplicados con PK/FK, CHECK y reglas EDA E01–E10.", style_td), Paragraph("UPSERT masivo (INSERT ... ON CONFLICT DO UPDATE). Idempotente y reejecutable.", style_td), Paragraph("Tipos nativos (INT, DATE, NUMERIC) + origin y synthetic_batch.", style_td)],
        [Paragraph("<b>gold</b>", style_td_bold), Paragraph("Modelo analítico de Constelación de Hechos en español para consumo en Power BI.", style_td), Paragraph("Resolución de llaves sustitutas, particiones físicas y vistas materializadas.", style_td), Paragraph("Dimensiones dim_*, hechos hecho_* y vistas agg_*.", style_td)],
    ]
    t_medallion = Table(medallion_data, colWidths=[65, 175, 150, 133.28])
    t_medallion.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_medallion)
    story.append(PageBreak())

    # CONTINUACIÓN CAPÍTULO 6 (PÁGINA 13): STACK TECNOLÓGICO Y HERRAMIENTAS
    story.append(Paragraph("6.2 Stack Tecnológico y Herramientas Utilizadas", style_sec_title))
    tech_data = [
        [Paragraph("<b>Herramienta / Tecnología</b>", style_th), Paragraph("<b>Versión</b>", style_th), Paragraph("<b>Rol Específico dentro del Proyecto</b>", style_th)],
        [Paragraph("PostgreSQL", style_td_bold), Paragraph("16 (Docker) / 18 local", style_td_center), Paragraph("Motor RDBMS del Data Warehouse. Aloja los esquemas meta, bronze, silver y gold.", style_td)],
        [Paragraph("Python", style_td_bold), Paragraph("3.12 / 3.13 (.venv)", style_td_center), Paragraph("Lenguaje principal para el pipeline ETL, transformaciones y scripts de validación.", style_td)],
        [Paragraph("pandas", style_td_bold), Paragraph("2.x / 3.x", style_td_center), Paragraph("Lectura por bloques (chunksize), normalización de encabezados y parsing CSV.", style_td)],
        [Paragraph("psycopg2-binary", style_td_bold), Paragraph("2.9.x", style_td_center), Paragraph("Driver de alto rendimiento en C para transacciones, COPY y consultas set-based.", style_td)],
        [Paragraph("pytest", style_td_bold), Paragraph("9.1.x", style_td_center), Paragraph("Batería de 55 pruebas automatizadas (esquema, FKs, checksums, idempotencia).", style_td)],
        [Paragraph("Docker & Compose", style_td_bold), Paragraph("2.x", style_td_center), Paragraph("Virtualización reproducible del motor PostgreSQL 16 sobre contenedor oficial.", style_td)],
        [Paragraph("DBeaver Community", style_td_bold), Paragraph("24.x", style_td_center), Paragraph("Cliente visual para administración, inspección de esquemas y diagramas ER.", style_td)],
        [Paragraph("Power BI Desktop", style_td_bold), Paragraph("2024 / 2026", style_td_center), Paragraph("Herramienta de Business Intelligence para tableros ejecutivos y DAX.", style_td)],
    ]
    t_tech = Table(tech_data, colWidths=[110, 85, 328.28])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_tech)
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 14: CAPÍTULO 7 - REGLAS DEL PROCESO EDA
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 7", style_chap_num))
    story.append(Paragraph("Reglas del proceso EDA y calidad de datos", style_chap_title))
    story.append(Paragraph("Catálogo exhaustivo de reglas E01 a E10 aplicadas antes de la capa Plata", style_chap_sub))

    eda_data = [
        [Paragraph("<b>Regla</b>", style_th), Paragraph("<b>Condición / Defecto Detectado</b>", style_th), Paragraph("<b>Acción Técnica de Calidad</b>", style_th), Paragraph("<b>Capa / Implementación</b>", style_th)],
        [Paragraph("<b>E01</b>", style_td_center), Paragraph("Nulos en métricas deportivas (goles, asistencias, tarjetas, minutos).", style_td), Paragraph("Imputar 0 mediante COALESCE(col, 0). Preserva sumatorias.", style_td), Paragraph("silver.appearances, game_events", style_td)],
        [Paragraph("<b>E02</b>", style_td_center), Paragraph("Nulos en valor de mercado.", style_td), Paragraph("Mantener NULL estrictamente. Imputar 0 distorsionaría promedios y correlación.", style_td), Paragraph("silver.player_valuations, players", style_td)],
        [Paragraph("<b>E03</b>", style_td_center), Paragraph("Nulos en campos de texto descriptivo (posiciones, nombres, estadios).", style_td), Paragraph("Imputar 'Desconocido' mediante función helper txt().", style_td), Paragraph("silver.*", style_td)],
        [Paragraph("<b>E04</b>", style_td_center), Paragraph("Fechas en formatos mixtos o fechas inválidas.", style_td), Paragraph("Normalizar a DATE ISO-8601 con meta.to_date(); si falla, rechazar fila.", style_td), Paragraph("silver.* (meta.to_date)", style_td)],
        [Paragraph("<b>E05</b>", style_td_center), Paragraph("Duplicados por clave natural de negocio.", style_td), Paragraph("Conservar el último registro cronológico con DISTINCT ON y deduplicar en destino.", style_td), Paragraph("silver.*", style_td)],
        [Paragraph("<b>E06</b>", style_td_center), Paragraph("Minutos fuera de rango [0, 130] o métricas deportivas negativas.", style_td), Paragraph("Rechazar la fila e insertar registro en meta.etl_rejected con motivo E06.", style_td), Paragraph("silver.game_events, appearances", style_td)],
        [Paragraph("<b>E07</b>", style_td_center), Paragraph("Registros huérfanos sin padre referencial en claves foráneas.", style_td), Paragraph("En FK obligatoria: rechazar fila. En FK opcional: colocar NULL y auditar.", style_td), Paragraph("silver.* (meta.etl_rejected)", style_td)],
        [Paragraph("<b>E08</b>", style_td_center), Paragraph("Codificación o caracteres corruptos en el archivo CSV de origen.", style_td), Paragraph("Reintento automático en Latin-1 si UTF-8 falla; conteo con csv.reader.", style_td), Paragraph("bronze.* (extract_bronze.py)", style_td)],
        [Paragraph("<b>E09</b>", style_td_center), Paragraph("Valores de texto no interpretables en columnas numéricas.", style_td), Paragraph("Conversión controlada a NULL mediante meta.to_int() y meta.to_num().", style_td), Paragraph("silver.*", style_td)],
        [Paragraph("<b>E10</b>", style_td_center), Paragraph("Clave natural de negocio nula o vacía (PK de negocio inexistente).", style_td), Paragraph("Rechazo inmediato de la fila y registro de auditoría en meta.etl_rejected.", style_td), Paragraph("silver.*", style_td)],
    ]
    t_eda = Table(eda_data, colWidths=[32, 160, 201.28, 130])
    t_eda.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_eda)
    story.append(Spacer(1, 10))

    callout_eda = (
        "<b>Auditoría en meta.etl_rejected:</b> Cada registro rechazado almacena el identificador del lote (<i>run_id</i>), "
        "la tabla afectada, el valor de la clave de negocio rechazada, el código de la regla infringida (E04, E06, E07, E10) "
        "y el motivo técnico del descarte, garantizando total trazabilidad y cero pérdida silenciosa de datos."
    )
    story.append(callout_box(callout_eda, bg="#EFF6FF", border="#93C5FD"))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINAS 15-16: CAPÍTULO 8 - PROCESO ETL
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 8", style_chap_num))
    story.append(Paragraph("Proceso ETL y pipeline de datos", style_chap_title))
    story.append(Paragraph("Herramientas, flujo secuencial, comandos CLI y expansión sintética controlada", style_chap_sub))

    story.append(Paragraph("8.1 Flujo Secuencial del Pipeline", style_sec_title))
    story.append(Paragraph(
        "El pipeline se ejecuta de manera modular mediante el orquestador central <code>etl.run_pipeline</code>, "
        "garantizando que cada fase sea transaccional, reejecutable y verificable:",
        style_body
    ))
    story.append(Paragraph("<b>1. Fase Bronze (extract_bronze.py):</b> Lee cada CSV en bloques configurables (100k filas) y los inserta con COPY en tablas de texto crudo, inyectando metadatos de linaje (_load_id, _loaded_at, _source_file, _row_id).", style_bullet))
    story.append(Paragraph("<b>2. Fase Silver (transform_silver.py):</b> Ejecuta sentencias SQL set-based dentro del motor PostgreSQL respetando el orden topológico de FKs (competitions ──► clubs ──► players ──► games ──► appearances ──► game_events ──► player_valuations).", style_bullet))
    story.append(Paragraph("<b>3. Fase Gold (load_gold.py):</b> Genera dim_fecha, carga dimensiones resolviendo llaves sustitutas enteras, carga las 3 tablas de hechos de la constelación y particiona por fecha_key.", style_bullet))
    story.append(Paragraph("<b>4. Fase Agregaciones (refresh_aggregations.py):</b> Ejecuta REFRESH MATERIALIZED VIEW CONCURRENTLY sobre las 5 vistas de negocio.", style_bullet))
    story.append(Paragraph("<b>5. Fase Expansión (expand_synthetic.py):</b> Clona deterministamente partidos y eventos hasta alcanzar 10.565.092 registros con origin='sintetico' y es_sintetico=TRUE.", style_bullet))

    story.append(Paragraph("8.2 Comandos CLI del Sistema", style_sec_title))
    cli_code = (
        "# 1) Creación de esquema físico, funciones PL/pgSQL y tablas de auditoría\n"
        "python scripts/setup_database.py\n\n"
        "# 2) Carga de datos reales (Bronze -> Silver -> Gold) por chunks de 100.000 filas\n"
        "python -m etl.run_pipeline --layer all --chunk-size 100000\n\n"
        "# 3) Expansión sintética controlada a 10,5 millones de registros\n"
        "python -m etl.run_pipeline --layer expand --target-total 10565088\n\n"
        "# 4) Validación integral de calidad, particiones y benchmarks analíticos\n"
        "python scripts/validate.py\n\n"
        "# 5) Batería automatizada de pruebas unitarias y de integración (55 pruebas)\n"
        "pytest -v\n\n"
        "# Reversión instantánea de datos sintéticos (Rollback total al estado real base)\n"
        "python -m etl.run_pipeline --layer expand --rollback"
    )
    story.append(code_box(cli_code))
    story.append(PageBreak())

    # CONTINUACIÓN CAPÍTULO 8 (PÁGINA 16): DETALLES DE IMPLEMENTACIÓN EN PYTHON
    story.append(Paragraph("8.3 Metodología de Expansión Sintética Controlada", style_sec_title))
    story.append(Paragraph(
        "Para superar la prueba de estrés de volumetría de 10,5 millones de registros sin distorsionar la realidad del fútbol:",
        style_body
    ))
    story.append(Paragraph("<b>Clonación de Partidos (silver.games):</b> Se clonaron partidos reales asignando IDs en un rango reservado no solapable (game_id &gt;= 900.000.000), preservando competición, clubes, árbitros, estadios y marcadores exactos.", style_bullet))
    story.append(Paragraph("<b>Clonación de Eventos (silver.game_events):</b> Se asociaron a los partidos clonados generando claves con prefijo 'SYN-{pase}-{id}', con perturbación acotada del minuto (+/- 3 min) acotada al rango [0, 130].", style_bullet))
    story.append(Paragraph("<b>Clonación de Apariciones (silver.appearances):</b> Claves con prefijo 'SYN-1-{id}', completando exactamente 1.894.350 filas en plata.", style_bullet))
    story.append(Paragraph("<b>Valoraciones Sintéticas (silver.player_valuations):</b> Generadas para futbolistas existentes en fechas quincenales no ocupadas previamente, respetando la PK compuesta (player_id, valuation_date) y aplicando un factor de hash en el rango [0.95, 1.05].", style_bullet))

    story.append(Paragraph("8.4 Trazabilidad y Aislamiento Analítico", style_sec_title))
    callout_expand = (
        "<b>Aislamiento Analítico Garantizado:</b><br/>"
        "• En la capa Silver, cada fila expandida lleva <code>origin = 'sintetico'</code> y su <code>synthetic_batch UUID</code>.<br/>"
        "• En la capa Gold, cada hecho expandido lleva <code>es_sintetico = TRUE</code>.<br/>"
        "• Las 5 vistas materializadas <code>gold.agg_*</code> filtran explícitamente <code>WHERE es_sintetico = FALSE</code>, "
        "garantizando que las estadísticas históricas y tableros en Power BI coincidan <b>bit a bit</b> con los datos reales."
    )
    story.append(callout_box(callout_expand, bg="#FEF3C7", border="#F59E0B"))
    story.append(Spacer(1, 10))

    story.append(Paragraph("8.5 Idempotencia y Reversibilidad (Rollback)", style_sec_title))
    story.append(Paragraph(
        "El comando <code>--rollback</code> ejecuta la eliminación en cascada de los registros sintéticos tanto en Silver "
        "como en Gold, refresca concurrentemente las vistas materializadas y restituye la base de datos exactamente "
        "a sus <b>3.625.525 registros reales originales</b> en menos de 25 segundos, verificado mediante checksums SHA/Hash.",
        style_body
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 17: CAPÍTULO 9 - CAPA ORO: AGREGACIONES, ÍNDICES Y PARTICIONES
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 9", style_chap_num))
    story.append(Paragraph("Capa Oro: agregaciones, índices y particiones", style_chap_title))
    story.append(Paragraph("Vistas materializadas con refresco concurrente, particionamiento anual e índices físicos", style_chap_sub))

    story.append(Paragraph("9.1 Las 5 Vistas Materializadas de Agregación (RF10)", style_sec_title))
    story.append(Paragraph(
        "Para responder consultas analíticas en milisegundos evitando escanear 6,75 millones de hechos por clic en Power BI, "
        "la capa Gold cuenta con 5 vistas materializadas con índice único para refresco concurrente:",
        style_body
    ))

    mv_data = [
        [Paragraph("<b>Vista Materializada</b>", style_th), Paragraph("<b>Grano de Agrupación</b>", style_th), Paragraph("<b>Métricas Precalculadas</b>", style_th), Paragraph("<b>RF</b>", style_th)],
        [Paragraph("gold.agg_jugador_temporada_liga", style_td_bold), Paragraph("(jugador_key, competicion_key, temporada)", style_td), Paragraph("Partidos, minutos, goles, asistencias, tarjetas, goles por 90, ranking goleador.", style_td), Paragraph("RF01, RF02, RF08", style_td_center)],
        [Paragraph("gold.agg_club_temporada", style_td_bold), Paragraph("(club_key, temporada)", style_td), Paragraph("Partidos, victorias, empates, derrotas, goles favor/contra, puntos, valor plantilla.", style_td), Paragraph("RF04, RF05", style_td_center)],
        [Paragraph("gold.agg_eventos_15min", style_td_bold), Paragraph("(competicion_key, temporada, franja_15min, tipo_evento_key)", style_td), Paragraph("Total de eventos por franja horaria (0 a 6) y porcentaje sobre el total del partido.", style_td), Paragraph("RF07", style_td_center)],
        [Paragraph("gold.agg_disciplina_arbitro", style_td_bold), Paragraph("(arbitro_key, temporada)", style_td), Paragraph("Partidos dirigidos, tarjetas amarillas/rojas, tarjetas por partido y tarjetas por 90 min.", style_td), Paragraph("RF06", style_td_center)],
        [Paragraph("gold.agg_local_visitante", style_td_bold), Paragraph("(competicion_key, temporada)", style_td), Paragraph("Victorias locales, empates, victorias visitantes, pct victoria local, promedio goles.", style_td), Paragraph("RF09", style_td_center)],
    ]
    t_mv = Table(mv_data, colWidths=[130, 140, 203.28, 50])
    t_mv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_mv)

    story.append(Paragraph("9.2 Particionamiento Físico por Rango Anual (RNF08)", style_sec_title))
    story.append(Paragraph(
        "La tabla <code>gold.hecho_eventos_partido</code> (6,75 M de filas) implementa particionamiento declarativo "
        "por rango sobre <code>fecha_key</code> (formato AAAAMMDD). Se crearon 46 particiones físicas anuales desde 1990 "
        "hasta 2035 (ej: <code>hecho_eventos_partido_2023</code> para valores entre 20230101 y 20240101) más una partición default. "
        "La auditoría demostró que la partición default contiene exactamente <b>0 filas</b>.",
        style_body
    ))

    story.append(Paragraph("9.3 Estrategia de Índices B-Tree y Hash", style_sec_title))
    callout_idx = (
        "• <b>Índices B-Tree:</b> Presentes en todas las dimensiones y en todas las claves foráneas de las tres tablas de hechos "
        "(fecha_key, partido_key, jugador_key, club_key, competicion_key, arbitro_key). Maximizan el <i>partition pruning</i>.<br/>"
        "• <b>Índice Hash:</b> Implementado en <code>gold.hecho_eventos_partido USING HASH (tipo_evento_key)</code>, acelerando "
        "búsquedas exactas por tipo de incidencia (Goals, Cards, Substitutions) con un ahorro de espacio del 40% frente a B-Tree.<br/>"
        "• <b>Índices Únicos en Vistas:</b> Habilitan <code>REFRESH MATERIALIZED VIEW CONCURRENTLY</code> sin bloqueos de lectura."
    )
    story.append(callout_box(callout_idx, bg="#EFF6FF", border="#93C5FD"))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINAS 18-19: CAPÍTULO 10 - DASHBOARD POWER BI Y STORYTELLING
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 10", style_chap_num))
    story.append(Paragraph("Dashboard Power BI y storytelling", style_chap_title))
    story.append(Paragraph("Estructura de las 4 páginas de negocio, medidas DAX y narrativa orientada a la decisión", style_chap_sub))

    story.append(Paragraph("10.1 Estructura del Tablero Analítico", style_sec_title))
    pbi_data = [
        [Paragraph("<b>Página del Tablero</b>", style_th), Paragraph("<b>Pregunta de Decisión de Negocio</b>", style_th), Paragraph("<b>Visuales y Componentes Analíticos</b>", style_th), Paragraph("<b>RF</b>", style_th)],
        [Paragraph("1. Resumen Ejecutivo", style_td_bold), Paragraph("¿Cuál es el panorama competitivo y económico general de la temporada?", style_td), Paragraph("Tarjetas KPI (goles totales, partidos, promedio gol, valor de mercado), gráfico de barras por torneo.", style_td), Paragraph("RF01, RF04", style_td_center)],
        [Paragraph("2. Rankings y Scouting Sub-23", style_td_bold), Paragraph("¿Quiénes son los talentos jóvenes más eficientes antes de su encarecimiento?", style_td), Paragraph("Top N dinámico de goleadores/asistidores, dispersión valor de mercado vs goles por 90 min, filtro Sub-23.", style_td), Paragraph("RF01, RF02, RF08", style_td_center)],
        [Paragraph("3. Desempeño Clubes y Factor Cancha", style_td_bold), Paragraph("¿Cuánto pesa la localía y cuánto explica la nómina los puntos obtenidos?", style_td), Paragraph("Tabla de posiciones con puntos calculados (3, 1, 0), dispersión valor plantilla vs puntos, matriz local/visita.", style_td), Paragraph("RF04, RF05, RF09", style_td_center)],
        [Paragraph("4. Disciplina y Rigor Arbitral", style_td_bold), Paragraph("¿Qué árbitros condicionan más los partidos y en qué minutos hay más tarjetas?", style_td), Paragraph("Ranking de colegiados por tarjetas cada 90 min, gráfico de calor de eventos por franjas de 15 min.", style_td), Paragraph("RF06, RF07", style_td_center)],
    ]
    t_pbi = Table(pbi_data, colWidths=[105, 140, 233.28, 45])
    t_pbi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_pbi)

    story.append(Paragraph("10.2 Medidas DAX Implementadas sobre la Capa Gold", style_sec_title))
    dax_code = (
        "// 1. Rendimiento deportivo acumulado (desde hecho_rendimiento_jugador)\n"
        "Goles Totales = SUM(hecho_rendimiento_jugador[goles])\n"
        "Minutos Jugados = SUM(hecho_rendimiento_jugador[minutos_jugados])\n"
        "Goles Por 90 = DIVIDE([Goles Totales] * 90, [Minutos Jugados], 0)\n\n"
        "// 2. Disciplina arbitral\n"
        "Tarjetas Por 90 = DIVIDE((SUM(hecho_rendimiento_jugador[tarjetas_amarillas]) + \n"
        "                         SUM(hecho_rendimiento_jugador[tarjetas_rojas])) * 90, [Minutos Jugados], 0)\n\n"
        "// 3. Valoración económica y scouting\n"
        "Valor Plantilla EUR = SUM(hecho_valoraciones_mercado[valor_mercado_eur])\n"
        "Es Promesa Sub23 = IF(DATEDIFF(MAX(dim_jugador[fecha_nacimiento]), TODAY(), YEAR) < 23, \"Sub-23\", \"Senior\")"
    )
    story.append(code_box(dax_code))
    story.append(PageBreak())

    # CONTINUACIÓN CAPÍTULO 10 (PÁGINA 19): STORYTELLING
    story.append(Paragraph("10.3 Narrativa de Storytelling Analítico (Los 4 Actos)", style_sec_title))
    story.append(Paragraph(
        "El tablero no presenta datos aislados; acompaña al tomador de decisiones (director deportivo o analista de scouting) "
        "a través de una narrativa secuencial estructurada:",
        style_body
    ))

    story_data = [
        [Paragraph("<b>Acto Narrativo</b>", style_th), Paragraph("<b>Mensaje Central de la Historia</b>", style_th), Paragraph("<b>Evidencia en el Tablero</b>", style_th), Paragraph("<b>Acción de Decisión Recomendada</b>", style_th)],
        [Paragraph("<b>1. Situación</b>", style_td_bold), Paragraph("La brecha económica entre ligas se amplía, pero el talento joven marca diferencias.", style_td), Paragraph("KPIs ejecutivos y valor global de mercado por confederación.", style_td), Paragraph("Monitorear ligas medianas donde el costo por gol es más eficiente.", style_td)],
        [Paragraph("<b>2. Complicación</b>", style_td_bold), Paragraph("Fichar por nombre o reputación pasada es ineficiente y riesgoso.", style_td), Paragraph("Gráfico de dispersión: jugadores caros con bajo rendimiento por 90 min.", style_td), Paragraph("Descartar fichajes de alto valor salarial con métricas decrecientes.", style_td)],
        [Paragraph("<b>3. Descubrimiento</b>", style_td_bold), Paragraph("Existen perfiles Sub-23 con métricas de élite a una fracción del costo de mercado.", style_td), Paragraph("Cuadrante superior izquierdo en dispersión (alto gol/90, baja tasación).", style_td), Paragraph("Priorizar scouting presencial en jóvenes con más de 900 min disputados.", style_td)],
        [Paragraph("<b>4. Resolución</b>", style_td_bold), Paragraph("La ventaja de campo y el rigor arbitral condicionan los puntos de campeonato.", style_td), Paragraph("Matriz local/visitante (60% victorias locales) y franjas de fatiga (min 75–90+).", style_td), Paragraph("Ajustar rotaciones en tramos finales y adaptar alineaciones según el árbitro.", style_td)],
    ]
    t_story = Table(story_data, colWidths=[90, 140, 145, 148.28])
    t_story.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_secondary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_story)
    story.append(Spacer(1, 15))

    callout_story = (
        "<b>Modo de Conexión:</b> Power BI se conecta a PostgreSQL mediante el conector nativo en modo <b>Import (VertiPaq)</b>, "
        "lo que comprime los 10,5 millones de registros en memoria a ~180–220 MB y garantiza que todos los filtros cruzados, "
        "segmentadores de edad y cambios de liga respondan en <b>menos de 0,5 segundos</b>."
    )
    story.append(callout_box(callout_story, bg="#EFF6FF", border="#93C5FD"))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINAS 20-22: CAPÍTULO 11 - GUÍA POR DIAPOSITIVA (DEFENSA ORAL)
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 11", style_chap_num))
    story.append(Paragraph("Guía técnica por diapositiva para la sustentación", style_chap_title))
    story.append(Paragraph("Qué muestra cada diapositiva de la presentación, cómo explicarla y preguntas probables", style_chap_sub))

    story.append(Paragraph("Diapositiva 1. Introducción y Planteamiento del Problema", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> Presenta el ecosistema de Transfermarkt, el crecimiento del fútbol basado en datos y la ineficiencia de procesar analítica sobre bases OLTP transaccionales normalizadas.", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Comienza con la frase de apertura: <i>'Hoy los clubes deciden con datos'</i>. Explica que un OLTP colapsa con agregaciones sobre millones de filas y que por ello se diseñó un DWH OLAP en PostgreSQL con Arquitectura Medallón.", style_bullet))

    story.append(Paragraph("Diapositiva 2. Objetivos y Alcance del Proyecto", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> Objetivo general y los 6 objetivos específicos estructurados según el ciclo de vida del dato.", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Destaca las tres ideas clave: arquitectura escalable por capas, modelo de constelación de hechos Kimball y volumen superior a 10,5 millones de registros.", style_bullet))

    story.append(Paragraph("Diapositiva 3. Requerimientos Funcionales y No Funcionales", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> La matriz RF01–RF10 y los 9 requerimientos no funcionales de rendimiento y calidad.", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Resalta que cada requerimiento funcional tiene una tabla de hechos o vista materializada específica en la capa Gold, y que los RNF (SLA &lt; 3 s, 0 huérfanos) se verifican con pruebas automatizadas.", style_bullet))

    story.append(Paragraph("Diapositiva 4. Arquitectura de Origen (Transfermarkt)", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> Las 7 entidades del dataset abierto, sus relaciones de negocio y el contraste técnico OLTP vs OLAP.", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Menciona que games, appearances y game_events concentran el 90% del volumen, y explica por qué la estructura de origen no era apta para consumo analítico directo sin antes pasar por el ETL.", style_bullet))

    story.append(Paragraph("Diapositiva 5. Volumetría Real y Pruebas Físicas", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> La medición real en disco en PostgreSQL: 10.565.092 filas, 2,4 GB en la tabla masiva particionada, 6,8 GB totales en disco y benchmarks sub-segundo (&lt; 0,39 s).", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Enfatiza que los índices representan el 32-35% del espacio pero son los responsables directos de que las consultas analíticas respondan 150 veces más rápido que el SLA exigido.", style_bullet))
    story.append(Paragraph("• <b>Pregunta probable del docente:</b> <i>¿De dónde salen esas cifras de almacenamiento?</i> Respuesta: <i>'De consultas directas a los catálogos del sistema de PostgreSQL utilizando pg_relation_size(), pg_indexes_size() y pg_total_relation_size()'</i>.", style_bullet))
    story.append(PageBreak())

    # CONTINUACIÓN CAPÍTULO 11 (PÁGINA 21): DIAPOSITIVAS 6 A 10
    story.append(Paragraph("Diapositiva 6. Modelo Dimensional: Constelación de Hechos (Defensa Clave)", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> El diagrama de la Constelación de Hechos con 7 dimensiones conformadas y 3 tablas de hechos independientes.", style_bullet))
    story.append(Paragraph("• <b>Cómo defenderla ante el docente:</b> <i>'Profesor, originalmente se consideró una estrella única con los eventos en el centro, pero al analizar los requerimientos y la literatura de Ralph Kimball detectamos un desajuste de grano: un evento ocurre al minuto específico, mientras que la actuación y los minutos jugados del futbolista son métricas aditivas de los 90 minutos del partido. Fusionarlos en una sola tabla destruía la aditividad o generaba duplicados artificiales. Por eso evolucionamos el diseño a una Constelación de Hechos con dimensiones conformadas compartidas, lo que garantiza rigor metodológico y exactitud en las métricas.'</i>", style_bullet))
    story.append(Paragraph("• <b>Pregunta probable:</b> <i>¿Por qué no usar copo de nieve?</i> Respuesta: <i>'Porque el copo de nieve normaliza las dimensiones agregando JOINs innecesarios. En analítica preferimos dimensiones conformadas desnormalizadas para maximizar la velocidad de lectura en Power BI.'</i>", style_bullet))

    story.append(Paragraph("Diapositiva 7. Arquitectura Medallón: Capa Bronce", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> Ingesta cruda, campos en TEXT, carga masiva por chunks de 100k con COPY y metadatos de linaje técnico.", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Explica que Bronce es un aterrizaje fiel que nunca corrige datos, garantizando que siempre se pueda auditar el dato original ante cualquier duda.", style_bullet))

    story.append(Paragraph("Diapositiva 8. Arquitectura Medallón: Capa Plata", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> Normalización relacional, tipado fuerte (INT, DATE, NUMERIC), restricciones CHECK y trazabilidad (origin).", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Cuenta que Plata es donde se asegura la calidad del dato: aquí se resuelven las dependencias foráneas y se descartan o aíslan los registros huérfanos.", style_bullet))

    story.append(Paragraph("Diapositiva 9. Arquitectura Medallón: Capa Oro", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> El modelo de constelación en español (dim_*, hecho_*, agg_*), llaves sustitutas y particionamiento anual.", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Resalta que Oro es la única capa que ve el negocio y Power BI; los nombres están en español profesional para facilitar la creación de métricas y la comprensión del analista.", style_bullet))

    story.append(Paragraph("Diapositiva 10. Stack Tecnológico e Infraestructura", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> El ecosistema de herramientas: PostgreSQL 16 en Docker, Python 3.12+, pandas, psycopg2, pytest y Power BI.", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Explica que Docker garantiza que el entorno sea reproducible en cualquier máquina sin depender de configuraciones locales de PostgreSQL.", style_bullet))
    story.append(PageBreak())

    # CONTINUACIÓN CAPÍTULO 11 (PÁGINA 22): DIAPOSITIVAS 11 A 13
    story.append(Paragraph("Diapositiva 11. Calidad de Datos y Reglas EDA (E01 a E10)", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> El catálogo de reglas de calidad, diferenciación entre imputación a 0 y preservación de NULL, y auditoría en meta.etl_rejected.", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Da el ejemplo emblemático de la regla E02: <i>'En valor de mercado conservamos NULL y nunca imputamos 0, porque un futbolista sin tasación no vale 0 euros; asignarle 0 distorsionaría por completo la correlación con los puntos de la plantilla.'</i>", style_bullet))

    story.append(Paragraph("Diapositiva 12. Pipeline ETL: Flujo y Expansión Controlada", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> El flujo de datos entre capas, el procesamiento por chunks, y el mecanismo de clonación sintética controlada.", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Narra el recorrido de los datos: cómo un archivo de 1,8 M de filas se lee en memoria en bloques de 100k filas sin saturar la RAM, se limpia en Plata con SQL set-based y se carga en Oro resolviendo llaves sustitutas.", style_bullet))

    story.append(Paragraph("Diapositiva 13. Dashboard Power BI, Storytelling y Conclusiones", style_sec_title))
    story.append(Paragraph("• <b>Qué muestra:</b> Capturas del tablero de Power BI de 4 páginas, las medidas DAX clave y los 4 actos de la narrativa analítica.", style_bullet))
    story.append(Paragraph("• <b>Cómo explicarla:</b> Cierra demostrando que el tablero responde las preguntas estratégicas de negocio: encontrar talento Sub-23 eficiente y evaluar el impacto del rigor arbitral en los resultados deportivos.", style_bullet))

    story.append(Spacer(1, 15))
    callout_defensa = (
        "<b>Estrategia de Cierre de la Presentación:</b><br/>"
        "1. Concluir afirmando que se cumplió el 100% de los requerimientos funcionales y no funcionales.<br/>"
        "2. Destacar que el proyecto cuenta con <b>55 pruebas automatizadas pasando en verde</b>.<br/>"
        "3. Ofrecer abrir en vivo DBeaver o Power BI para ejecutar cualquier consulta analítica que el docente solicite."
    )
    story.append(callout_box(callout_defensa, bg="#ECFDF5", border="#10B981"))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINAS 23-24: CAPÍTULO 12 - BANCO DE PREGUNTAS PARA LA SUSTENTACIÓN
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 12", style_chap_num))
    story.append(Paragraph("Banco de preguntas para la sustentación", style_chap_title))
    story.append(Paragraph("15 respuestas cortas, directas y técnicamente blindadas para la defensa oral", style_chap_sub))

    q_data = [
        ("1. ¿Qué es un Data Warehouse y en qué se diferencia de una base de datos operacional?",
         "Un DWH es un repositorio integrado, temático, histórico y no volátil optimizado para lectura y análisis (OLAP). Una base operacional (OLTP) está optimizada para transacciones atómicas frecuentes (escrituras) y consultas puntuales normalizadas."),
        ("2. ¿Qué es la Arquitectura Medallón y qué ventajas aporta?",
         "Es un patrón de ingeniería de datos en capas: Bronce almacena el dato crudo con linaje, Plata lo limpia y normaliza relacionalmente, y Oro lo modela dimensionalmente para negocio. Aporta trazabilidad, reprocesamiento seguro y calidad incremental."),
        ("3. ¿Por qué un modelo de constelación de hechos y no una estrella simple?",
         "Porque en el negocio coexisten procesos con granos incompatibles: el evento puntual al minuto (factless), la actuación acumulada de 90 min (aditiva) y la tasación periódica (snapshot). Unirlos en una sola tabla generaría fan traps y duplicaciones."),
        ("4. ¿Cuál es el grano de cada tabla de hechos?",
         "• hecho_rendimiento_jugador: La actuación de un futbolista en un partido (90 min).\n• hecho_eventos_partido: Una incidencia ocurrida en un minuto puntual.\n• hecho_valoraciones_mercado: La tasación económica de un futbolista en una fecha."),
        ("5. ¿Qué son las llaves sustitutas y por qué usarlas en las dimensiones?",
         "Son enteros generados artificialmente (SERIAL) propios del DWH. Independizan el modelo de los cambios en los IDs de origen, manejan claves compuestas o nulas elegantemente y aceleran sustancialmente los JOINs en el motor relacional."),
        ("6. ¿Cómo garantizan que no hay registros huérfanos?",
         "Mediante restricciones FOREIGN KEY estrictas en Silver y Gold, y pruebas automatizadas de LEFT JOIN con WHERE IS NULL en pytest y en scripts/validate.py que certifican 0 filas huérfanas en todas las relaciones."),
        ("7. ¿Cómo logran que el pipeline ETL sea 100% idempotente?",
         "Con TRUNCATE ... RESTART IDENTITY en la ingesta Bronce, y sentencias UPSERT (INSERT ... ON CONFLICT DO UPDATE) en Silver y Gold. Reejecutar el pipeline 10 veces seguidas deja la base de datos exactamente en el mismo estado."),
        ("8. ¿Por qué procesar la ingesta en chunks con COPY?",
         "Para no desbordar la memoria RAM. Procesar en bloques de 100.000 filas con el comando nativo COPY de PostgreSQL transfiere datos binariamente en milisegundos, siendo hasta 50 veces más rápido que INSERTs fila a fila."),
    ]

    for q, a in q_data:
        story.append(Paragraph(f"<b>{q}</b>", style_sec_title))
        story.append(Paragraph(a.replace('\n', '<br/>'), style_body))
        story.append(Spacer(1, 2))
    story.append(PageBreak())

    # CONTINUACIÓN CAPÍTULO 12 (PÁGINA 24): PREGUNTAS 9 A 15
    q_data_2 = [
        ("9. ¿Cómo garantizan que las consultas analíticas tarden menos de 3 segundos?",
         "Mediante tres capas de optimización: 1) Vistas materializadas con agregaciones precalculadas, 2) Particionamiento físico anual por rango en hechos de eventos, y 3) Índices B-Tree en FKs e índice Hash en tipo de evento. Benchmark real: &lt; 0,39 s."),
        ("10. ¿Por qué los índices representan el 32-35% del almacenamiento y por qué es aceptable?",
         "Porque en un Data Warehouse la carga de trabajo es 95% lectura analítica. Pagar un tercio del espacio en índices es una decisión de diseño deliberada para reducir los tiempos de respuesta de minutos a milisegundos."),
        ("11. ¿Cómo calculan los puntos de campeonato y la correlación valor-puntos?",
         "Se asignan 3, 1 y 0 puntos por victoria, empate y derrota a partir de los goles de dim_partido. Se totalizan por club y temporada en gold.agg_club_temporada y se correlacionan con la función estadística corr() de PostgreSQL."),
        ("12. ¿Cómo se calcula la métrica de tarjetas por 90 minutos?",
         "Fórmula: ((tarjetas_amarillas + tarjetas_rojas) * 90) / minutos_jugados. Se aplica solo a futbolistas con más de 900 minutos disputados para filtrar distorsiones estadísticas de jugadores con pocos minutos."),
        ("13. ¿Cómo trataron los valores nulos y por qué el valor de mercado no se imputó a 0?",
         "Métricas deportivas a 0 (E01), textos a 'Desconocido' (E03). El valor de mercado se conservó en NULL (E02) porque un futbolista sin tasación no vale 0 euros; imputar 0 distorsionaría las medias de valor de nómina."),
        ("14. ¿Cómo llegaron a 10,5 millones de registros sin contaminar los datos reales?",
         "Mediante clonación controlada determinista con semilla fija. Se marcaron con origin='sintetico' en Silver y es_sintetico=TRUE en Gold. Las vistas agregadas filtran estrictamente es_sintetico=FALSE, aislando los datos reales al 100%."),
        ("15. ¿Cómo implementaron el particionamiento físico y qué beneficio aporta?",
         "Particionamiento por rango anual en gold.hecho_eventos_partido sobre fecha_key (1990–2035). PostgreSQL descarta particiones completas que no coincidan con la fecha consultada (partition pruning), reduciendo lecturas de disco drásticamente."),
    ]

    for q, a in q_data_2:
        story.append(Paragraph(f"<b>{q}</b>", style_sec_title))
        story.append(Paragraph(a.replace('\n', '<br/>'), style_body))
        story.append(Spacer(1, 2))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 25: CAPÍTULO 13 - PUNTOS DE ATENCIÓN Y LISTA DE VERIFICACIÓN
    # =========================================================================
    story.append(Paragraph("CAPÍTULO 13", style_chap_num))
    story.append(Paragraph("Puntos de atención y lista de verificación final", style_chap_title))
    story.append(Paragraph("Alertas sobre el alcance del dataset y checklist exhaustivo previo a la sustentación", style_chap_sub))

    story.append(Paragraph("13.1 Alertas sobre el Alcance del Dataset Abierto", style_sec_title))
    story.append(Paragraph(
        "<b>Métricas Técnicas de Partido (RF02 / RF04):</b> El enunciado académico menciona métricas como pases precisos, "
        "recuperaciones o tiros a puerta. Es fundamental aclarar con honestidad técnica que en la versión pública oficial de "
        "Transfermarkt esas métricas especializadas (propias de proveedores cerrados como Opta o Wyscout) no existen. "
        "En su lugar, el proyecto resolvió el rendimiento con goles, asistencias, tarjetas y minutos jugados.",
        style_body
    ))
    story.append(Paragraph(
        "<b>Trazabilidad de la Expansión (10,5 M de Filas):</b> Si el docente pregunta sobre el volumen expandido, se debe "
        "destacar la total transparencia del sistema: los datos reales (3,62 M) están intactos y validados por checksums hash, "
        "mientras que los datos sintéticos están etiquetados de forma permanente y pueden revertirse en segundos con <code>--rollback</code>.",
        style_body
    ))

    story.append(Paragraph("13.2 Checklist de Verificación Previo a la Sustentación", style_sec_title))
    chk_data = [
        [Paragraph("<b>Componente a Verificar</b>", style_th), Paragraph("<b>Criterio de Aceptación</b>", style_th), Paragraph("<b>Comando o Acción de Comprobación</b>", style_th), Paragraph("<b>Estado</b>", style_th)],
        [Paragraph("Contenedor PostgreSQL", style_td), Paragraph("Contenedor postgres:16 activo y escuchando en puerto 5432.", style_td), Paragraph("docker compose ps (o servicio local)", style_td), Paragraph("OK", style_td_center)],
        [Paragraph("Volumetría Expandida", style_td), Paragraph("Exactamente 10.565.092 filas en la capa Silver.", style_td), Paragraph("python scripts/validate.py (Sección 1)", style_td), Paragraph("OK", style_td_center)],
        [Paragraph("Integridad Referencial", style_td), Paragraph("0 huérfanos en todas las claves foráneas de Silver y Gold.", style_td), Paragraph("python scripts/validate.py (Sección 4)", style_td), Paragraph("OK", style_td_center)],
        [Paragraph("Partición Default", style_td), Paragraph("Exactamente 0 filas en hecho_eventos_partido_default.", style_td), Paragraph("SELECT count(*) FROM gold.hecho_eventos_partido_default;", style_td), Paragraph("OK", style_td_center)],
        [Paragraph("Vistas Materializadas", style_td), Paragraph("5 vistas pobladas y con índices únicos listos para refresco.", style_td), Paragraph("python -m etl.run_pipeline --layer gold", style_td), Paragraph("OK", style_td_center)],
        [Paragraph("Tiempos de Consulta", style_td), Paragraph("Todas las consultas benchmark respondiendo en &lt; 0,5 s.", style_td), Paragraph("python scripts/validate.py (Sección 6)", style_td), Paragraph("OK", style_td_center)],
        [Paragraph("Batería de Pruebas", style_td), Paragraph("55 de 55 pruebas unitarias y de integración pasando en verde.", style_td), Paragraph("pytest -v", style_td), Paragraph("OK", style_td_center)],
        [Paragraph("Tablero Power BI", style_td), Paragraph("Archivo .pbix con 4 páginas conectadas a las tablas Gold.", style_td), Paragraph("Abrir Power BI Desktop y verificar actualización", style_td), Paragraph("OK", style_td_center)],
    ]
    t_chk = Table(chk_data, colWidths=[105, 170, 203.28, 45])
    t_chk.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_chk)
    story.append(Spacer(1, 15))

    callout_final = (
        "<b>Proyecto Listo para Sustentación:</b> Todos los componentes arquitectónicos, scripts de base de datos, "
        "pipelines ETL, documentación técnica y modelo de sustentación se encuentran completamente alineados, "
        "probados y validados empíricamente para la defensa final."
    )
    story.append(callout_box(callout_final, bg="#EFF6FF", border="#93C5FD"))

    # Construir documento
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Documento generado exitosamente en: {filename}")

if __name__ == "__main__":
    out_path = "docs/Documento_Sustentacion_DWH_Transfermarkt.pdf"
    if len(sys.argv) > 1:
        out_path = sys.argv[1]
    build_pdf(out_path)
