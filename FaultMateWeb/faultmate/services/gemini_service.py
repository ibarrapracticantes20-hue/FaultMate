# Este archivo se encarga de "hablar" con la IA de Google (Gemini).
# La idea es tener en un solo lugar todo lo relacionado con la IA, para
# que dashboard/views.py solo tenga que llamar a consultar_gemini(falla).
import os

from dotenv import load_dotenv
from google import genai

# Carga las variables del archivo .env (por ejemplo GEMINI_API_KEY).
load_dotenv()

# Proyecto escolar: clave hardcodeada de forma directa.
# Reemplaza el valor por tu clave real de Gemini.
GEMINI_API_KEY = "PEGA_AQUI_TU_API_KEY"

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

    respuesta = cliente.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return respuesta.text
