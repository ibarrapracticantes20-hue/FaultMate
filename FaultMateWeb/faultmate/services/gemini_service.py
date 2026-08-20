import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent"


def _rol_gemini(rol):
    """Convierte el rol guardado en tu base de datos ('user'/'assistant')
    al formato que espera la API de Gemini ('user'/'model')."""
    return "model" if rol == "assistant" else "user"


def consultar_gemini(falla):
    """
    Le pide a la IA de Gemini un diagnostico para la falla recibida.
    Devuelve el texto de la respuesta (o un mensaje de error si algo falla).
    """
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY no está configurada en el .env"

    prompt = f"""
    Eres Faultmate, un experto en mantenimiento industrial.

    Analizar esta falla:

    {falla}

    Responde:
    Diagnóstico probable:
    Posible causa:
    Acción recomendada:
    """

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
    except requests.RequestException as exc:
        return f"Error de conexión con Gemini: {exc}"

    try:
        result_json = response.json()
    except ValueError:
        return "Error: respuesta inválida de Gemini"

    if "candidates" in result_json and len(result_json["candidates"]) > 0:
        return result_json["candidates"][0]["content"]["parts"][0]["text"]

    if "error" in result_json:
        return f"Error de Gemini: {result_json['error'].get('message', 'sin detalle')}"

    return "Error: no se pudo obtener respuesta de Gemini"


def consultar_gemini_agente(agente, mensaje_usuario, historial=None):
    """
    Envía el mensaje del usuario a Gemini, usando el prompt y la configuración
    del agente (temperatura, tokens) y el historial de la conversación,
    y devuelve el texto de respuesta como string.
    """
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY no está configurada en el .env"

    contents = []

    # Instrucciones/prompt del agente, como primer turno de la conversación
    if getattr(agente, "prompt", None):
        contents.append({
            "role": "user",
            "parts": [{"text": agente.prompt}]
        })
        contents.append({
            "role": "model",
            "parts": [{"text": "Entendido, seguiré esas instrucciones en mis respuestas."}]
        })

    # Historial previo del chat (si existe)
    for mensaje in (historial or []):
        contents.append({
            "role": _rol_gemini(mensaje.get("rol")),
            "parts": [{"text": mensaje.get("contenido", "")}]
        })

    # Mensaje actual del usuario
    contents.append({
        "role": "user",
        "parts": [{"text": mensaje_usuario}]
    })

    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": getattr(agente, "temperatura", 0.5),
            "maxOutputTokens": getattr(agente, "tokens", 800),
        }
    }

    try:
        response = requests.post(
            f"{GEMINI_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
    except requests.RequestException as exc:
        return f"Error de conexión con Gemini: {exc}"

    # Deja estos prints mientras pruebas; quítalos cuando ya funcione bien
    print("Status code:", response.status_code)
    print("Respuesta cruda:", response.text)

    try:
        result_json = response.json()
    except ValueError:
        return "Error: respuesta inválida de Gemini"

    if "candidates" in result_json and len(result_json["candidates"]) > 0:
        return result_json["candidates"][0]["content"]["parts"][0]["text"]

    if "error" in result_json:
        return f"Error de Gemini: {result_json['error'].get('message', 'sin detalle')}"

    return "Error: no se pudo obtener respuesta de Gemini"
