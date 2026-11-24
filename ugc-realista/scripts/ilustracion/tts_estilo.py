"""Genera voz con gemini-3.8-flash-tts pasando el estilo en speech_metadata (no dentro del texto).

`gemini-api tts` no expone el campo de estilo; aquí se arma la petición completa y se envía con
`gemini-api agent run --body`. La clave la toma gemini-api del llavero; este script nunca la ve.

Uso: python3 -I tts_estilo.py --voz Charon --texto-archivo guion.txt --salida voz.wav [--estilo "..."]
"""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MODELO = "gemini-3.8-flash-tts"
IDIOMA = "es-419"
ESTILO_POR_DEFECTO = (
    "Narrador masculino de documental de divulgación en español latinoamericano neutro (no de España). "
    "Voz cálida, clara y cercana. Ritmo ágil y natural, como un video de redes sociales, sin pausas largas entre frases."
)
TIEMPO_MAXIMO_S = 240


def armar_peticion(texto: str, voz: str, estilo: str) -> dict:
    return {
        "model": MODELO,
        "input": [{
            "type": "user_input",
            "content": [{
                "type": "text",
                "text": texto,
                "annotations": [{"type": "speech_metadata", "style": estilo}],
            }],
        }],
        "generation_config": {"speech_config": [{"voice": voz, "language": IDIOMA}]},
        "response_format": {"type": "audio"},
        "store": False,
    }


def extraer_wav(respuesta: dict) -> bytes:
    if respuesta.get("status") != "completed":
        raise RuntimeError(f"La interacción no terminó: status={respuesta.get('status')!r}")
    for paso in respuesta.get("steps", []):
        for parte in paso.get("content", []):
            if parte.get("type") == "audio" and parte.get("data"):
                return base64.b64decode(parte["data"])
    raise RuntimeError("La respuesta no trae audio.")


def generar(texto: str, voz: str, estilo: str, salida: Path) -> Path:
    peticion = armar_peticion(texto, voz, estilo)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(peticion, f, ensure_ascii=False)
        ruta_peticion = f.name
    resultado = subprocess.run(
        ["gemini-api", "agent", "run", "--body", f"@{ruta_peticion}", "--stream=false",
         "-o", "json", "--no-interactive"],
        capture_output=True, text=True, timeout=TIEMPO_MAXIMO_S,
    )
    Path(ruta_peticion).unlink(missing_ok=True)
    if resultado.returncode != 0:
        raise RuntimeError(f"gemini-api salió con {resultado.returncode}: {resultado.stderr.strip()[:400]}")
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_bytes(extraer_wav(json.loads(resultado.stdout)))
    return salida


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--voz", required=True)
    p.add_argument("--texto-archivo", required=True, type=Path)
    p.add_argument("--salida", required=True, type=Path)
    p.add_argument("--estilo", default=ESTILO_POR_DEFECTO)
    a = p.parse_args()
    texto = a.texto_archivo.read_text(encoding="utf-8").strip()
    if not texto:
        print("El archivo de texto está vacío.", file=sys.stderr)
        return 2
    print(generar(texto, a.voz, a.estilo, a.salida))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
