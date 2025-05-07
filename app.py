import os
from dotenv import load_dotenv
from flask import Flask, redirect, request, render_template, session
import google.generativeai as genai
from db import init_db, guardar_historial, obtener_historial

# Carga variables de entorno y configura la API
load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Inicializa Flask y base de datos
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'cambiame')
init_db()

@app.route('/', methods=['GET'])
def index():
    historial = obtener_historial(limit=20)
    return render_template('index.html', historial=historial)


@app.route('/predict', methods=['POST'])
def predict():
    prompt = request.form.get('prompt')
    if not prompt:
        return render_template('index.html', error="El campo de texto no puede estar vacío.", historial=obtener_historial(limit=20))

    # Leer el contenido de la base de conocimiento
    try:
        with open("base_conocimiento.txt", "r", encoding="utf-8") as f:
            base_conocimiento = f.read()
    except Exception:
        return render_template('index.html', error="No se pudo cargar la base de conocimiento.", historial=obtener_historial(limit=20))



    # Recuperar historial reciente
    historial = obtener_historial(limit=10)
    contexto = ""
    for user_msg, bot_msg in historial:
        contexto += f"Usuario: {user_msg}\nAsistente: {bot_msg}\n"

    # Construir el prompt con contexto y base de conocimiento
    prompt_con_contexto = f"""
Eres un asistente virtual profesional y empático de Glowbank. Tu función es ayudar a los usuarios usando exclusivamente la información contenida en el siguiente documento. Evita responder con información que no esté en el documento. 

Si el usuario menciona algo como "gloaming", "gloming", "glowmind" o cualquier variación parecida, pregunta de forma amable si se refiere al servicio del banco llamado "Glowbank" o "Glowmind", ya que a veces el sistema puede confundir los términos.
Si el usuario hace preguntas que no están relacionadas con los servicios de Glowbank (por ejemplo: si tienes hambre, si quieres una idea, si puedes ayudarle a hacer un cálculo genérico, etc.), responde con amabilidad y explica que solo puedes responder sobre el banco Glowbank.

- Si el usuario pregunta cosas como "¿tienes hambre?" o "¿quieres una idea?", responde agradeciendo, pero aclara que eres un asistente virtual y estás enfocado en ayudar con temas bancarios.

- Si el usuario pide ayuda con cálculos, primero verifica si se trata de algo relacionado con servicios financieros. Si no es así, aclara que no puedes ayudar en temas fuera del banco.
Cuando el usuario haga una pregunta negativa, sarcástica, ofensiva o malintencionada, responde con cortesía, mantén la profesionalidad y redirige la conversación hacia temas relacionados con los servicios de Glowbank.

Simplifica las respuestas para que no sean tan largas, a menos que el usuario solicite más detalles, las respuestas para que sean breves, claras y útiles. Evita repetir la misma información y prioriza la comprensión.
Evita decir "Hola" en todas las respuestas. Solo saluda al inicio de una conversación o si el usuario te saluda. El resto del tiempo, responde de forma directa, clara y amable.
Cuando no sepas la respuesta o el tema esté fuera de tu alcance, responde con comprensión y ofrece redirigir la conversación a temas bancarios. Asegúrate de que el usuario se sienta escuchado y valorado, incluso si no puedes ayudar directamente.
Haz que el usuario se sienta acompañado y satisfecho, incluso si no obtiene lo que buscaba. Usa frases suaves como:

- “Entiendo lo que dices, aunque en este momento solo puedo ayudarte con temas de Glowbank.”
- “Gracias por tu comentario, aunque no puedo opinar sobre eso, estaré encantado de ayudarte con tus dudas bancarias.”
- “Qué interesante, aunque como asistente de Glowbank me enfoco en ayudarte con nuestros servicios. ¿Te gustaría saber más sobre tu cuenta o algún trámite?”
Si el usuario da una respuesta negativa o no desea continuar con un tema, acepta su decisión. Si el usuario responde negativamente por segunda vez, no insistas más y cierra el tema de forma respetuosa. Usa frases como:

- "Está bien, si necesitas algo más de Glowbank, aquí estaré para ayudarte."
- "No hay problema, estaré disponible si decides consultarme algo más."

Evita hacer más preguntas después de dos negativas consecutivas, a menos que el usuario reinicie la conversación.
si responde que no puedes ayudar en nada responde: que mal, estoy aqui para ayudarte en todo lo que corresponde a Glowbank.
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

    historial_actualizado = obtener_historial(limit=20)
    return render_template('index.html', prompt=prompt, response_html=response_text, historial=historial_actualizado)

@app.route('/history', methods=['GET'])
def history():
    import sqlite3
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'historial.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT prompt, respuesta, fecha FROM historial ORDER BY fecha DESC")
    entries = cursor.fetchall()
    conn.close()
    return render_template('history.html', history=entries)



@app.route("/limpiar", methods=["POST"])
def limpiar():
    try:
        session.pop("historial", None)
        return redirect("/")
    except Exception as e:
        return f"Ocurrió un error: {e}", 500



if __name__ == '__main__':
    app.run(debug=True)
