
import os
import json
import time
import random
import threading
import urllib.request
import urllib.error

from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

app = Flask(__name__)

# Configuracion de DuckApps
TOKEN = os.environ.get("DUCKS_BOT_TOKEN")

API_URL = "https://bots.duckapps.com.br/bot/v1"



PUBLIC_KEY = Ed25519PublicKey.from_public_bytes(
    bytes.fromhex(
        "6c96e368eee0944b026356a7a2ede8fe"
        "fb20e6f16f2b0ebf402e4b131060ce94"
    )
)



# Respuestas aleatorias de Uvita
RESPUESTAS = [
    "Hola mi bb ;3",
    "Buenas...nalgas",
    "Ese hola suena a acoso bro...",
    "Hi cosita bella",
    "Saludos espanta viejas",
    "Welcome to Haití",
    "Bienvenido al club gay."
]


# Verificar la firma de DuckApps
def verificar_firma(headers, cuerpo):

    timestamp = headers.get("X-Ducks-Timestamp")
    firma = headers.get("X-Ducks-Signature")

    if not timestamp or not firma:
        return False

    try:
        if abs(time.time() - int(timestamp)) > 300:
            return False

        mensaje = timestamp.encode() + b"." + cuerpo

        PUBLIC_KEY.verify(
            bytes.fromhex(firma),
            mensaje
        )

        return True

    except (InvalidSignature, ValueError):
        return False


# Pagina principal
@app.route("/", methods=["GET"])
def inicio():
    return "Uvita está funcionando."


# Recibir eventos de DuckApps
@app.route("/webhook", methods=["POST"])
def webhook():

    cuerpo = request.get_data(cache=False)

    if not verificar_firma(request.headers, cuerpo):
        return jsonify({"error": "Firma no valida"}), 401

    evento = json.loads(cuerpo.decode("utf-8"))

    tipo = evento.get("type")
    datos = evento.get("data", {})

    # Verificacion del webhook
    if tipo == "ping":
        return jsonify({
            "nonce": datos.get("nonce")
        }), 200

    # Comandos del bot
    if tipo == "command":

        contenido = datos.get("content", "").strip().lower()

        if contenido.startswith("/"):
            contenido = contenido[1:]

        comando = contenido.split()[0] if contenido else ""

        if comando in ["hola", "ola", "oa", "hi"]:

            respuesta = random.choice(RESPUESTAS)

            return jsonify({
                "reply": {
                    "content": respuesta
                }
            }), 200

    return jsonify({}), 200


# Solicitar la verificacion a DuckApps


def verificar_webhook():

    print("DIAGNOSTICO: Iniciando verificacion...", flush=True)

    if not TOKEN:
        print("ERROR: Falta DUCKS_BOT_TOKEN", flush=True)
        return

    print("DIAGNOSTICO: Token encontrado.", flush=True)

    try:
        solicitud = urllib.request.Request(
            API_URL + "/webhook/verify",
            method="POST",
            headers={
                "Authorization": "Bot " + TOKEN,
                "User-Agent": "UvitaBot/1.0",
                "Accept": "application/json"
            }
        )

        print("DIAGNOSTICO: Enviando solicitud a DuckApps...", flush=True)

        with urllib.request.urlopen(solicitud, timeout=30) as respuesta:
            print(
                "Verificacion solicitada:",
                respuesta.status,
                flush=True
            )
            print(respuesta.read().decode("utf-8"), flush=True)

    except urllib.error.HTTPError as error:
        print("ERROR HTTP de DuckApps:", error.code, flush=True)
        print(error.read().decode("utf-8"), flush=True)

    except Exception as error:
        print("ERROR al verificar:", repr(error), flush=True)
        
        


# Iniciar servidor
if __name__ == "__main__":

    print("Iniciando Uvita...")

    # Esperar a que el servidor este disponible
    threading.Timer(10, verificar_webhook).start()

    puerto = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=puerto,
        debug=False
        )
    
