import requests
import os 
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def diagnosticar_falla(texto):
    texto = texto.lower()

    if not texto:
        return "No se ingersó ninguna falla"

    if "motor" in texto and "no arranca" in texto:
        return "Posible causa: capacitor o contactor dañado"
    
    elif "sobrecalentamiento" in texto:
        return "Posible causa: ventilación bloqueada o sobrecarga"
    
    elif "presión" in texto:
        return "Posible causa: fuga o bomba desgastada"
    
    elif "no prende" in texto:
        return "Posible causa: falla eléctrica o sin energía"
    
    elif "vibración" in texto:
        return "Posible causa: desbalance o rodamiento dañado"
    
    else:
        return "Falla no reconocida"
    

@app.route("/test")
def test():
    return jsonify({
        "estado": "ok",
        "mensaje" : "FaultMate conecatado"
    })


@app.route("/diagnosticar", methods=["POST"])
def diagnosticar():
    falla = request.form.get("falla", "")
    resultado = diagnosticar_falla(falla)

    return render_template(
        "resultado.html",
         falla=falla, 
         resultado=resultado
    )



@app.route("/ia", methods=["POST"])
def ia():

    print("Entro A /ia")

    data = request.json or {}
    falla = data.get("falla", "")

    print("Falla:", falla)

    prompt = f"""
Eres un experto en mantenimiento industrial.
Analiza esta falla:

{falla}

Devuelve:
- Posible causa raíz
- Diagnóstico
- Acción correctiva
"""
    

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
    )

    resultado = "Error: no se pudo obtener respuesta de Gemini"

    try:
        result_json = response.json()

        if "candidates" in result_json and len(result_json["candidates"]) > 0:
            resultado = result_json["candidates"][0]["content"]["parts"][0]["text"]
        
    except Exception:
        resultado = "Error: respuesta inválida de Gemini"

    return jsonify({
        "respuesta": str(resultado)
    })


if __name__== "__main__":
    app.run(debug=True)