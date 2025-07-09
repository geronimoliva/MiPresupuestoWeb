from nomenclatura import obtener_departamento, obtener_localidad, obtener_pedania

def generar_contenido(cliente, tarea, reparticiones, designacion_inmueble):
    if len(designacion_inmueble) == 12:
        designacion_texto = f"N° de Cuenta {designacion_inmueble[0:2]}-{designacion_inmueble[2:4]}-{designacion_inmueble[4:11]}/{designacion_inmueble[11]}"
    elif len(designacion_inmueble) == 16:
        designacion_texto = "Nomenclatura Catastral"
    elif any(char.isalpha() for char in designacion_inmueble) and any(char.isdigit() for char in designacion_inmueble):
        designacion_texto = "designado como"
    else:
        designacion_texto = "designación desconocida"

    departamento = obtener_departamento(designacion_inmueble)
    pedania = obtener_pedania(designacion_inmueble)
    localidad = obtener_localidad(designacion_inmueble)

    if len(designacion_inmueble) == 12:
        contenido = (
            f"<b>A solicitud de {cliente}</b><br />"
            f"<br />Presupuesto por tarea de <b>{tarea}</b>, confección de Planos, Informes, "
            f"estudio de antecedentes legales y tramitación ante {reparticiones}, "
            f"el Colegio de Agrimensores, de inmueble con {designacion_texto}, "
            f"ubicado en pedanía {pedania}, departamento {departamento}, provincia de CÓRDOBA.<br />"
            "<br />Se incluyen en el monto total los honorarios profesionales, los aportes previsionales según Ley 8.470, las tasas correspondientes al Colegio de Agrimensores Ley 7.455 y los "
            "gastos operativos."
        )
    else:
        contenido = (
            f"<b>A solicitud de {cliente}</b><br />"
            f"<br />Presupuesto por tarea de <b>{tarea}</b>, confección de Planos, Informes, "
            f"estudio de antecedentes legales y tramitación ante {reparticiones} y "
            f"el Colegio de Agrimensores, de inmueble con {designacion_texto} {designacion_inmueble}, "
            f"ubicado en la localidad de {localidad}, pedanía {pedania}, departamento {departamento}, provincia de CÓRDOBA.<br />"
            "<br />Se incluyen en el monto total los honorarios profesionales, los aportes previsionales según Ley 8.470, las tasas correspondientes al Colegio de Agrimensores Ley 7.455 y los "
            "gastos operativos."
        )

    return contenido
