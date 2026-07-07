from google import genai

cliente = genai.Client(
    api_key="AQ.Ab8RN6L5AdGlQbwh1DVCuLRTvcLiEQeywvz4dsUe7EgI39SYKw"
)

def consultar_gemini(falla):

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
