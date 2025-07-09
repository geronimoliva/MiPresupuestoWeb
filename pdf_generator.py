from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

import hashlib

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

from monto import monto_a_letras
import os
import io

from contenido import generar_contenido
from monto import formatear_numero

from nomenclatura import obtener_localidad

# generar ID del presupuesto

def generar_id_presupuesto(cliente, tarea, designacion_inmueble, reparticiones, profesional, monto, fecha_emision=None):
    if fecha_emision is None:
        fecha_emision = datetime.now().strftime("%Y-%m-%d")
    
    campos = [
        cliente or "",
        tarea or "",
        designacion_inmueble or "",
        str(monto) or "",
        profesional.get('nps', '') if isinstance(profesional, dict) else "",
        fecha_emision
    ]
    cadena = '_'.join(campos)
    print("Cadena para hash:", cadena)
    return hashlib.sha256(cadena.encode()).hexdigest()

# -----------------------------------------------------------------------------------------------------------------------------

def generar_pdf(
    cliente: str,
    tarea: str,
    designacion_inmueble: str,
    reparticiones: str,
    profesional: dict,
    logo_path: str,
    monto: float,
    formulario_e: bool,
    notarogacionsinprecalificacion: bool,
    tipo_zona: str,
    info_formas_pago: str,
    mensaje_zona_nr: str,
    destino
):
    from reportlab.lib.enums import TA_JUSTIFY

    # Crear el PDF
    c = canvas.Canvas(destino, pagesize=A4)
    ancho, alto = A4

    # Generar ID presupuesto
    id_presupuesto = generar_id_presupuesto(cliente, tarea, designacion_inmueble, reparticiones, profesional, monto)

    # ------------------- Definir estilos justo acá ------------------- #
    styles = getSampleStyleSheet()
    justified_style_mensaje = ParagraphStyle(
        'JustifiedMensaje',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        fontSize=10,
        leading=12,
        textColor='grey'
    )
    justified_style_contenido = ParagraphStyle(
        'JustifiedContenido',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        fontSize=11,
        leading=14,
    )
    justified_style_formulario = ParagraphStyle(
        'JustifiedFormulario',
        parent=styles['Normal'],
        alignment=TA_JUSTIFY,
        fontSize=11
    )
    # ------------------------------------------------------------------- #

    # ---------------------------- CABECERA ---------------------------- #
    c.drawImage(logo_path, 55, alto - 100, width=70, height=70)  # LOGO

    if profesional['nps'] == "OG Estudio de Agrimensura":
        c.setFont("Helvetica-Bold", 18)
        c.drawString(145, alto - 60, "OG ESTUDIO DE AGRIMENSURA")
        c.setFont("Helvetica", 9)
        c.drawString(145, alto - 75, f"{profesional['tpps']}")
        c.drawString(145, alto - 85, f"Contacto: {profesional['emailps']}")
    else:
        c.setFont("Helvetica-Bold", 18)
        c.drawString(145, alto - 60, profesional['nps'])
        c.setFont("Helvetica", 9)
        c.drawString(145, alto - 75, f"{profesional['tpps']} {profesional['matps']}")
        c.drawString(145, alto - 85, f"Contacto: {profesional['emailps']} | {profesional['telps']}")

    # ----------------------- CONTENIDO PRINCIPAL ----------------------- #

    # Dibuja mensaje final (mensaje_zona_nr) justificado y gris
    paragraph_formulario = Paragraph(mensaje_zona_nr.strip(), justified_style_mensaje)
    paragraph_formulario.wrap(470, 600)
    y_mensaje = 400
    paragraph_formulario.drawOn(c, 60, y_mensaje)

    # Posición para recuadro monto (debajo mensaje)
    pos_y_mensaje = y_mensaje - paragraph_formulario.height -10

    # Contenido principal justificado
    contenido = generar_contenido(cliente, tarea, reparticiones, designacion_inmueble)
    paragraph = Paragraph(contenido, justified_style_contenido)
    paragraph.wrap(470, 600)

    # Posición del contenido (por debajo de cabecera)
    pos_contenido_y = alto - 130 - paragraph.height
    paragraph.drawOn(c, 60, pos_contenido_y)


    # ---------------------------- MONTO ------------------------------- #

    def justificar_derecha(c, x, y, texto):
        ancho_pagina = c._pagesize[0]
        ancho_texto = c.stringWidth(texto, c._fontname, c._fontsize)
        nueva_posicion_x = ancho_pagina - x - ancho_texto
        c.drawString(nueva_posicion_x, y, texto)

    # El recuadro se ubica un poco más abajo del contenido
    poscuadro = pos_contenido_y - 60

    monto_texto = formatear_numero(monto)

    colores_monto = {
        "Gerónimo Oliva": (0.788, 0.851, 0.792),
        "OG Estudio de Agrimensura": (0.663, 0.82, 0.961),
        "Yair Gantus": (0.96, 0.96, 0.86),
        "María Camila Romero Molinero": (0.737, 0.733, 0.949)
    }

    color_rectangulo = colores_monto.get(profesional['nps'], (0.85, 0.85, 0.85))
    c.setFillColorRGB(*color_rectangulo)
    c.roundRect(60, poscuadro, 470, 40, radius=10, fill=1, stroke=0)

    posdineroy3 = poscuadro + 12
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(113, posdineroy3, "TOTAL:")
    justificar_derecha(c, 100, posdineroy3, "$ {}".format(monto_texto))

    resultadoenletras = monto_a_letras(monto)
    posdineroy4 = posdineroy3 - 30
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("Helvetica", 8)
    justificar_derecha(c, 100, posdineroy4, f"Son pesos {resultadoenletras}.")


    # ------------------------ MENSAJES CONDICIONALES ------------------- #

    mensaje_zona = ""
    if tipo_zona == "urbano":
        mensaje_zona = ("No se incluye en el presente presupuesto el monto correspondiente a tasas y/o derechos "
                    "de visación de la Municipalidad, el cual deberá abonarse al momento de la presentación "
                    "de la documentación en dicha repartición para la prosecución del trámite.")

    mensaje_formulario = ""
    if formulario_e:
        mensaje_formulario = ("Con el propósito de la Protocolización del Plano, es necesario gestionar ante un Escribano Público "
                            "la confección de la <i>Nota de Rogación con Precalificación de Antecedentes</i> y el "
                            "<i>Certificado de Dominio, Inhibición y Gravámenes</i>, los cuales se presentan "
                            "simultáneamente con el trámite en la Dirección General de Catastro. El costo de estos no está incluido en el presente presupuesto.")
    elif notarogacionsinprecalificacion:
        mensaje_formulario = ("Deberá gestionarse ante un Escribano Público la confección de la <i>Nota de Rogación sin Precalificación "
                            "de Antecedentes</i> y la <i>certificación de frimas</i>, la cual se presenta simultáneamente con el trámite "
                            "en la Dirección General de Catastro. El costo de estos no está incluido en el presente presupuesto.")

    mensajes_condicionales = ""
    if mensaje_zona:
        mensajes_condicionales += "<br /><br />" + mensaje_zona
    if mensaje_formulario:
        mensajes_condicionales += "<br /><br />" + mensaje_formulario

    if mensajes_condicionales.strip():
        paragraph_mensajes = Paragraph(mensajes_condicionales.strip(), justified_style_mensaje)
        paragraph_mensajes.wrap(470, 600)
        pos_mensajes = poscuadro - 120
        paragraph_mensajes.drawOn(c, 60, pos_mensajes)
        pos_formas_pago = pos_mensajes - paragraph_mensajes.height - 80
    else:
        pos_formas_pago = poscuadro - 160


    # ----------------------- INFO FORMAS DE PAGO ----------------------- #

    if info_formas_pago.strip():  # Solo si hay contenido real

        info_formas_pago = info_formas_pago.replace("\n\n", "<br /><br />").replace("\n", "<br />")
        info_formas_pago = info_formas_pago.replace("1 PAGO", "<b>1 PAGO</b>")
        info_formas_pago = info_formas_pago.replace("2 CUOTAS", "<b>2 CUOTAS</b>")
        info_formas_pago = info_formas_pago.replace("3 CUOTAS", "<b>3 CUOTAS</b>")

        titulo = "<b>FORMAS DE PAGO</b><br /><br />"
        info_formas_pago = titulo + info_formas_pago

        info_formas_pago_paragraph = Paragraph(info_formas_pago, justified_style_formulario)
        info_formas_pago_paragraph.wrap(470, 600)
        info_formas_pago_paragraph.drawOn(c, 60, pos_formas_pago)
    else:
        print("info_formas_pago está vacío. No se imprime en el PDF.")

    # ---------------------------- PIE DE PÁGINA ------------------------ #
    fecha_emision = datetime.now().strftime("%d/%m/%Y")
    c.setFont("Helvetica", 10)
    c.drawString(70, 50, fecha_emision)
    c.drawString(170, 50, f"#:{id_presupuesto}")

    # Guardar y cerrar PDF
    c.showPage()
    c.save()
