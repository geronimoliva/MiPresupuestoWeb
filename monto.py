def formatear_numero(valor):
    try:
        valor_float = float(valor)

        numero_formateado = "{:,.2f}".format(valor_float).replace(",", "_").replace(".", ",").replace("_", ".")

        return numero_formateado
    except ValueError:
        return "Error: Ingresa un número válido"