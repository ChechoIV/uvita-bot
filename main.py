
import os
import time
import random
import json

from flask import Flask, request, jsonify
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

app = Flask(__name__)

# Clave publica oficial de DuckApps
CLAVE_PUBLICA = Ed25519PublicKey.from_public_bytes(
    bytes.fromhex(
        "6c96e368eee0944b026356a7a2ede8fefb20e6f16f2b0ebf402e4b131060ce94"
    )
)

SALUDOS = ["hola", "ola", "oa", "hi"]

RESPUESTAS = [
    "Hola mi bb ;3",
    "Buenas...nalgas",
    "Ese hola suena a acoso bro...",
    "Hi cosita bella",
    "Saludos espanta viejas",
    "Welcome to Haití",
    "Bienvenido al club gay."
]


def responder_saludo(mensaje):
    mensaje = mensaje.lower().strip()

    if mensaje in SALUDOS:
        return random.choice(RESPUESTAS)

    return None


def verificar_firma(headers, cuerpo):
    marca_tiempo = headers.get("X-Ducks-Timestamp")
    firma = headers.get("X-Ducks-Signature")

    if not marca_tiempo or not firma:
        return False

    try:
        if abs(time.time() - int(marca_tiempo)) > 300:
            return False

        mensaje = marca_tiempo.encode() + b"." + cuerpo

        CLAVE_PUBLICA.verify(
            bytes.fromhex(firma),
            mensaje
        )

        return True

    except (InvalidSignature, ValueError):
        return False


@app.route("/", methods=["GET"])
def inicio():
    return "Uvita está funcionando."


@app.route("/webhook", methods=["POST"])
def webhook():

    cuerpo = request.get_data()

    if not verificar_firma(request.headers, cuerpo):
        return "", 401

    evento = json.loads(cuerpo.decode("utf-8"))

    # Verificación de DuckApps
    if evento["type"] == "ping":
        return jsonify({
            "nonce": evento["data"]["nonce"]
        })

    # Cuando alguien escribe un comando
    if evento["type"] == "command":

        datos = evento["data"]
        contenido = datos["content"]

        if contenido.startswith("/"):
            contenido = contenido[1:]

        respuesta = responder_saludo(contenido)

        if respuesta is not None:
            return jsonify({
                "reply": {
                    "content": respuesta
                }
            })

    return jsonify({})


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=puerto)
      
