from flask import Flask, render_template, request, send_file
from pdf_generator import generar_pdf
from nomenclatura import obtener_localidad
import io
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def obtener_profesional_y_logo(nombre_profesional):
    if nombre_profesional == "OA":
        return {
            "nps": "Gerónimo Oliva",
            "tpps": "Ingeniero Agrimensor",
            "matps": "M.P. 1557/1",
            "emailps": "geronimo.oliva@gmail.com",
            "telps": "Tel.: 351 340-9228"
        }, os.path.join(BASE_DIR, 'logos', 'logo1.png')
    elif nombre_profesional == "OG":
        return {
            "nps": "OG Estudio de Agrimensura",
            "tpps": "Agrimensura Legal y Topografía",
            "matps": "",
            "emailps": "ogagrimensura@gmail.com",
            "telps": "Tel.: 351 340-9228"
        }, os.path.join(BASE_DIR, 'logos', 'logo2.png')
    elif nombre_profesional == "YG":
        return {
            "nps": "Yair Gantus",
            "tpps": "Ingeniero Agrimensor",
            "matps": "M.P. 1566/1",
            "emailps": "gantusyair@gmail.com",
            "telps": "Tel.: 3571 325179"
        }, os.path.join(BASE_DIR, 'logos', 'logo3.png')
    elif nombre_profesional == "MCRM":
        return {
            "nps": "María Camila Romero Molinero",
            "tpps": "Ingeniera Agrimensora",
            "matps": "M.P. 1584/1",
            "emailps": "mcrmolinero@gmail.com",
            "telps": "Tel.: 3546 539610"
        }, os.path.join(BASE_DIR, 'logos', 'logo4.png')

# Página inicial con botón para ir al formulario en misma ventana
@app.route("/")
def home():
    return render_template("formulario.html")

# Página formulario (GET para mostrar, POST para procesar)
@app.route("/formulario", methods=["GET", "POST"])
def formulario():
    if request.method == "POST":
        cliente = request.form.get("cliente")
        monto_str = request.form.get("monto", "0")
        try:
            monto = float(monto_str)
        except ValueError:
            return "<p>El monto ingresado no es válido.</p>"

        tarea = request.form.get("tarea")
        designacion = request.form.get("designacion")
        reparticiones = request.form.get("reparticiones")

        profesional_key = request.form.get("profesional")
        tipo_zona = request.form.get("tipo_zona")
        nr = request.form.get("nr")
        info_formas_pago = request.form.get("formas_pago", "")
        mensaje_zona_nr = request.form.get("mensaje_zona_nr", "")

        profesional, logo_path = obtener_profesional_y_logo(profesional_key)

        # Reemplazos en mensaje_zona_nr si se necesita
        localidad = obtener_localidad(designacion)
        mensaje_zona_nr = mensaje_zona_nr.replace("NombreLocalidad", localidad)

        buffer = io.BytesIO()
        generar_pdf(
            cliente,
            tarea,
            designacion,
            reparticiones,
            profesional,
            logo_path,
            monto,
            nr == "fe",
            nr == "posesion",
            tipo_zona,
            info_formas_pago,
            mensaje_zona_nr,
            buffer
        )
        buffer.seek(0)

        # (3) Devolver el PDF directamente como descarga
        safe_cliente = "".join(c for c in cliente if c.isalnum() or c in (" ", "_")).rstrip()
        filename = f"Presupuesto de {safe_cliente}.pdf"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    return render_template("formulario.html")

if __name__ == "__main__":
    import threading
    import webbrowser

    def abrir_navegador():
        webbrowser.open_new("http://127.0.0.1:5000")

    threading.Timer(1.0, abrir_navegador).start()
    app.run(debug=False)
