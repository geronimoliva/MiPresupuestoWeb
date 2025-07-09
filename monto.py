from num2words import num2words

def formatear_numero(valor):
    try:
        valor_float = float(valor)

        numero_formateado = "{:,.2f}".format(valor_float).replace(",", "_").replace(".", ",").replace("_", ".")

        return numero_formateado
    except ValueError:
        return "Error: Ingresa un número válido"
    


def monto_a_letras(monto):
    entero = int(float(monto))
    centavos = int(round((float(monto) - entero) * 100))
    
    texto_entero = num2words(entero, lang='es')
    if centavos > 0:
        texto_centavos = num2words(centavos, lang='es')
        resultado = f"{texto_entero} con {texto_centavos} centavos"
    else:
        resultado = f"{texto_entero} con cero centavos"
    return resultado.lower()
