# Este archivo se encarga de "hablar" con la IA de Google (Gemini).
# La idea es tener en un solo lugar todo lo relacionado con la IA, para
# que dashboard/views.py solo tenga que llamar a consultar_gemini(falla).
from google import genai

# Configuracion solicitada: API key hardcodeada.
GEMINI_API_KEY = "AQ.Ab8RN6IaaoqSAuQ7FbV9FZgImFBxUreYTLyrx5Gmi_koU-1yoA"

# Si no hay clave configurada, "cliente" queda en None y avisamos con un
# mensaje claro en vez de que el programa se caiga con un error raro.
cliente = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def consultar_gemini(falla):
    """
    Le pide a la IA de Gemini un diagnostico para la falla recibida.
    Devuelve el texto de la respuesta (o un mensaje de error si algo falla).
    """
    if cliente is None:
        return (
            "Error: no se encontró GEMINI_API_KEY. "
            "Configura la variable de entorno en un archivo .env."
        )

    # El "prompt" son las instrucciones que le damos a la IA.
    prompt = f"""
    Eres Faultmate, un experto en mantenimiento industrial.

    Analizar esta falla:

    {falla}

    Responde:
    Diagnóstico probable:
    Posible causa:
    Acción recomendada:
    """

    try:
        respuesta = cliente.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return respuesta.text
    except Exception as e:
        return f"Error al consultar Gemini: {e}"


def consultar_gemini_agente(agente, mensaje_usuario, historial=None):
    """Consulta Gemini usando la configuracion/prompt de un agente y su historial."""
    if cliente is None:
        return (
            "Error: no se encontró GEMINI_API_KEY. "
            "Configura la variable de entorno o reemplaza PEGA_AQUI_TU_API_KEY."
        )

    historial = historial or []
    historial_texto = "\n".join(
        [f"{item['rol'].upper()}: {item['contenido']}" for item in historial[-12:]]
    )

    prompt_base = agente.prompt or (
        f"Eres {agente.nombre}, un agente especializado en mantenimiento industrial."
    )

    prompt = f"""
{prompt_base}

Historial reciente:
{historial_texto}

Mensaje actual del usuario:
{mensaje_usuario}

Responde en formato claro, tecnico y accionable.
"""

    try:
        respuesta = cliente.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return respuesta.text
    except Exception as e:
        return f"Error al consultar Gemini: {e}"
