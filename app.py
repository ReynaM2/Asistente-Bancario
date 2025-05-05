"""
Aplicación web basada en Flask que utiliza el modelo 'gemini-1.5-flash' de Google Gemini para generar respuestas
a partir de entradas del usuario. La aplicación almacena el historial de conversaciones y utiliza Markdown
para formatear las respuestas generadas.

Requisitos:
- Flask y Flask-Session instalados.
- Paquete `google.generativeai` instalado.
- Configurar la variable de entorno `GEMINI_API_KEY` con la clave de acceso a la API de Gemini.

Características:
1. Muestra una página inicial donde el usuario puede interactuar con el modelo.
2. Permite gestionar un historial limitado de interacciones entre usuario y modelo.
3. Formatea las respuestas en Markdown antes de mostrarlas.
"""
import os
import sys

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona para dev y PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# import os

# import google.generativeai as genai
# import markdown
# import requests
# from flask import Flask, request, render_template, session
# from dotenv import load_dotenv
# from flask_session import Session

# # Configuración de la aplicación Flask
# app = Flask(__name__)

# # Configuración de sesiones
# app.secret_key = "clave_secreta_para_sesiones"  # Cambia esto en producción
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# load_dotenv()
# # Configuración del modelo Gemini
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])
# model = genai.GenerativeModel("gemini-1.5-flash")

# # Constante para limitar el historial de interacciones
# MAX_HISTORY = 4


# @app.route("/")
# def home():
#     """
#     Ruta principal de la aplicación. Muestra la interfaz inicial y el historial de interacciones previas,
#     si existe alguno.
#     """
#     if "history" not in session:
#         session["history"] = []  # Inicializar el historial si no está presente
#     return render_template("index.html", history=session["history"])


# @app.route("/predict", methods=["POST"])
# def predict():
#     """
#     Procesa la entrada del usuario, genera una respuesta utilizando el modelo Gemini,
#     y actualiza el historial con la interacción actual.

#     Returns:
#         str: Renderiza la página principal con la nueva respuesta y el historial actualizado.
#     """
#     # Obtener el texto ingresado por el usuario
#     prompt = request.form.get("prompt")

#     if not prompt:
#         # Manejar el caso de entrada vacía
#         return render_template("index.html", error="Por favor, ingresa un texto válido.")

#     # Construir el contexto con el historial de interacciones
#     history = session.get("history", [])
#     context = ""
#     for item in history[-MAX_HISTORY:]:
#         context += f"Usuario: {item['prompt']}\nModelo: {item['response_raw']}\n"
#     context += f"Usuario: {prompt}\n"

#     try:
#         # Generar la respuesta utilizando el modelo
#         response = model.generate_content(context).text

#         # Formatear la respuesta en HTML utilizando Markdown
#         output_html = markdown.markdown(response)

#         # Actualizar el historial con la interacción actual
#         history.append({
#             "prompt": prompt,
#             "response_raw": response,
#             "response_html": output_html
#         })
#         session["history"] = history

#         # Renderizar la página con la nueva respuesta
#         return render_template("index.html", prompt=prompt, response_html=output_html, history=history)

#     except requests.exceptions.RequestException as e:
#         # Manejar errores de conexión o solicitudes
#         return render_template("index.html", error=f"Error al conectarse a Gemini: {e}")


# if __name__ == "__main__":
#     app.run(debug=True)






#####hace lo que ella digo
# import os
# from dotenv import load_dotenv
# from flask import Flask, request, render_template
# import google.generativeai as genai
# from db import init_db, guardar_historial, obtener_historial

# # Carga variables de entorno y configura la API
# load_dotenv()
# genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# # Inicializa Flask y BD
# app = Flask(__name__)
# app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'cambiame')
# init_db()

# @app.route('/', methods=['GET'])
# def index():
#     return render_template('index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     prompt = request.form.get('prompt')
#     if not prompt:
#         return render_template('index.html', error="El campo de texto no puede estar vacío.")

#     # Recupera últimas interacciones para contexto (no se muestra al usuario)
#     historial = obtener_historial(limit=5)
#     contexto = ""
#     for user_msg, bot_msg in historial:
#         contexto += f"Usuario: {user_msg}\nAsistente: {bot_msg}\n"
#     prompt_con_contexto = f"{contexto}Usuario: {prompt}\nAsistente:"

#     # Genera la respuesta
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     resp = model.generate_content(prompt_con_contexto)
#     response_text = resp.text.strip()



#     # Guarda la interacción
#     guardar_historial(prompt, response_text)

#     # Muestra solo la entrada y respuesta actuales
#     return render_template('index.html', prompt=prompt, response_html=response_text)

# @app.route('/history', methods=['GET'])
# def history():
#     import sqlite3
#     conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'historial.db'))
#     cursor = conn.cursor()
#     cursor.execute("SELECT prompt, respuesta, fecha FROM historial ORDER BY fecha DESC")
#     entries = cursor.fetchall()
#     conn.close()
#     return render_template('history.html', history=entries)

# if __name__ == '__main__':
#     app.run(debug=True)




import os
from dotenv import load_dotenv
from flask import Flask, request, render_template
import google.generativeai as genai
from db import init_db, guardar_historial, obtener_historial

# Carga variables de entorno y configura la API
load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Inicializa Flask y BD
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'cambiame')
init_db()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    prompt = request.form.get('prompt')
    if not prompt:
        return render_template('index.html', error="El campo de texto no puede estar vacío.")

    # Leer el contenido de la base de conocimiento
    try:
        with open("base_conocimiento.txt", "r", encoding="utf-8") as f:
            base_conocimiento = f.read()
    except Exception as e:
        return render_template('index.html', error="No se pudo cargar la base de conocimiento.")

    # Recuperar historial reciente
    historial = obtener_historial(limit=5)
    contexto = ""
    for user_msg, bot_msg in historial:
        contexto += f"Usuario: {user_msg}\nAsistente: {bot_msg}\n"

    # Construir el prompt con contexto y base de conocimiento
    prompt_con_contexto = f"""
Eres un asistente de Glowbank que responde únicamente utilizando el contenido del siguiente documento.
trata de no salir de contexto pero cuando te quieran hacer salir de contexto responde con 
amabilidad y diles que estas en hora de trabajo y no puedes comentar sobre esos temas.
simplifica las respuestas para que no se an tan largas 
cuando te digan algo parecido a gloaming, gloming o glowmind, pregunta si se refiere al servicio del banco

Documento de referencia:
\"\"\"
{base_conocimiento}
\"\"\"

Historial reciente de conversación:
{contexto}

Nueva pregunta del usuario:
{prompt}

Tu respuesta:
"""

    # Generar la respuesta
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(prompt_con_contexto)
    response_text = resp.text.strip()

    # Guardar en la base de datos
    guardar_historial(prompt, response_text)
    
    return render_template('index.html', prompt=prompt, response_html=response_text)

@app.route('/history', methods=['GET'])
def history():
    import sqlite3
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'historial.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT prompt, respuesta, fecha FROM historial ORDER BY fecha DESC")
    entries = cursor.fetchall()
    conn.close()
    return render_template('history.html', history=entries)

 if __name__ == '__main__':
   app.run(debug=True)


