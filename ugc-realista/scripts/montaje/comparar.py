"""Compara la narración transcrita por Whisper con el texto exacto del prompt de Wan (lo que va entre comillas tras
«nothing removed:» y antes de «Under»). Se copia a <proyecto>/scripts/; lee prompts/wan/<v>.txt y
revision/<v>_t1/<v>_t1.json. CIFRAS traduce las cifras que escribe Whisper a las palabras del guion: agregar las que falten.

  python3 -I scripts/comparar.py v3
"""
import difflib
import json
import re
import sys
from pathlib import Path

PROYECTO = Path(__file__).resolve().parent.parent
# Whisper escribe cifras; el guion las tiene en letras
CIFRAS = {"1": "uno", "2": "dos", "11": "once", "12": "doce", "15": "quince", "28": "veintiocho", "30": "treinta",
          "42": "cuarenta y dos", "80": "ochenta", "100": "cien", "104": "ciento cuatro", "2026": "dos mil veintiséis",
          "%": " por ciento", "3": "tres", "5": "cinco", "6": "seis", "14": "catorce", "20": "veinte", "21": "veintiuno",
          "72": "setenta y dos", "2500": "dos mil quinientas", "2.500": "dos mil quinientas"}


def palabras(texto: str) -> list[str]:
    t = texto.lower()
    t = re.sub(r"\d+(?:\.\d+)?|%", lambda m: f" {CIFRAS.get(m.group(0), m.group(0))} ", t)
    return re.sub(r"[^\wáéíóúñü ]", " ", t).split()


def main() -> None:
    v = sys.argv[1]
    prompt = (PROYECTO / f"prompts/wan/{v}.txt").read_text()
    guion = re.search(r'nothing removed: "(.+?)" Under', prompt, re.S).group(1)
    d = json.loads((PROYECTO / f"revision/{v}_t1/{v}_t1.json").read_text())
    oido = " ".join(s["text"].strip() for s in d["segments"])
    a, b = palabras(guion), palabras(oido)
    dif = [x for x in difflib.ndiff(a, b) if x[0] in "+-"]
    fin = max((s["end"] for s in d["segments"] if s["text"].strip()), default=0)
    print(f"{v}: guion {len(a)} palabras, transcrito {len(b)}, diferencias {dif or 'ninguna'}, la voz termina en {fin:.1f} s")


if __name__ == "__main__":
    main()
