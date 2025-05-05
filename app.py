



import os
from dotenv import load_dotenv
from flask import Flask, request, render_template
import google.generativeai as genai
from db import init_db, guardar_historial, obtener_historial

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, funciona para dev y PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
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


{prompt}
 
"""

if __name__ == '__main__':
   app.run(debug=True)
