"""Imágenes (nano-banana-2) y voz (elevenlabs/text-to-speech-multilingual-v2) en kie.ai, un trabajo a la vez.

Reutiliza `http` y `subir` de kie_tarea.py (mismo directorio). Se corre desde la carpeta del proyecto: cada trabajo
cobrado se anota en su gasto.tsv. La llave viene del entorno (KIE_API_KEY), nunca de un archivo leído aquí.
Campos según docs.kie.ai (market/google/nanobanana2.md y market/elevenlabs/text-to-speech-multilingual-v2.md, 25-oct-2026).

  python3 kie_lote.py imagen --prompt-file p.txt [--ref URL ...] --salida img.png --concepto "V1 S1 A"
  python3 kie_lote.py voz --texto-file t.txt --voz <voice_id> [--velocidad 1.0] --salida voz.mp3 --concepto "muestra"
"""
from __future__ import annotations

import argparse
import datetime
import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

KIE_TAREA = Path(__file__).resolve().parent / "kie_tarea.py"   # el cliente de la skill, junto a este archivo
_spec = importlib.util.spec_from_file_location("kie_tarea", KIE_TAREA)
kt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(kt)

GASTO = Path.cwd() / "gasto.tsv"   # se corre desde la carpeta del proyecto
ESPERA_MAX_S = 20 * 60
MODELOS_VOZ = {"turbo": "elevenlabs/text-to-speech-turbo-2-5", "multilingual": "elevenlabs/text-to-speech-multilingual-v2"}


def anotar(task_id: str, concepto: str, creditos: float, etapa: str) -> None:
    nuevo = not GASTO.exists()
    with GASTO.open("a") as f:
        if nuevo:
            f.write("fecha\tservicio\tid\tconcepto\tcreditos\tusd\tetapa\n")
        f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M}\tkie\t{task_id}\t{concepto}\t{creditos}\t{creditos * kt.USD_POR_CREDITO:.3f}\t{etapa}\n")


def ejecutar(cuerpo: dict, salida: str, concepto: str, etapa: str) -> None:
    d = kt.http("POST", f"{kt.API}/api/v1/jobs/createTask", cuerpo)
    task_id = (d.get("data") or {}).get("taskId")
    if not task_id:
        sys.exit(f"Sin taskId en la respuesta: {json.dumps(d)[:300]}")
    print(f"{concepto}: tarea {task_id}", flush=True)
    t0 = time.time()
    while time.time() - t0 < ESPERA_MAX_S:
        rec = kt.http("GET", f"{kt.API}/api/v1/jobs/recordInfo?taskId={task_id}").get("data") or {}
        estado = rec.get("state")
        if estado == "success":
            creditos = rec.get("creditsConsumed") or 0
            anotar(task_id, concepto, creditos, etapa)
            urls = json.loads(rec.get("resultJson") or "{}").get("resultUrls") or []
            if not urls:
                sys.exit(f"{concepto}: éxito sin resultUrls ({task_id})")
            subprocess.run(["curl", "-s", "-m", "300", "-o", salida, urls[0]], check=True)
            print(f"  ok {int(time.time() - t0)} s · {creditos} créditos · {salida}", flush=True)
            return
        if estado == "fail":
            anotar(task_id, f"{concepto} (FALLÓ: {rec.get('failMsg')})", rec.get("creditsConsumed") or 0, etapa)
            sys.exit(f"{concepto}: falló: {rec.get('failMsg')}")
        time.sleep(5)
    sys.exit(f"{concepto}: sin respuesta en {ESPERA_MAX_S // 60} min; consultar {task_id} antes de pagar otra.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    pi = sub.add_parser("imagen")
    pi.add_argument("--prompt-file", required=True)
    pi.add_argument("--ref", action="append", default=[])
    pi.add_argument("--resolucion", default="1K", choices=["1K", "2K", "4K"])
    pv = sub.add_parser("voz")
    pv.add_argument("--texto-file", required=True)
    pv.add_argument("--voz", required=True)
    pv.add_argument("--velocidad", type=float, default=1.0)
    pv.add_argument("--modelo", default="turbo", choices=sorted(MODELOS_VOZ))
    for sp in (pi, pv):
        sp.add_argument("--salida", required=True)
        sp.add_argument("--concepto", required=True)
        sp.add_argument("--etapa", default="etapa 1 (pendiente de aprobación)")
    a = p.parse_args()

    if a.cmd == "imagen":
        prompt = Path(a.prompt_file).read_text().strip()
        if len(a.ref) > 10:
            sys.exit("nano-banana-2: hasta 10 imágenes de referencia.")
        cuerpo = {"model": "nano-banana-2", "input": {"prompt": prompt, "image_input": a.ref, "aspect_ratio": "9:16",
                                                      "resolution": a.resolucion, "output_format": "png"}}
    else:
        texto = Path(a.texto_file).read_text().strip()
        if not 0.7 <= a.velocidad <= 1.2:
            sys.exit("ElevenLabs: velocidad 0,7 a 1,2.")
        # solo Turbo/Flash 2.5 aceptan forzar el idioma; Multilingual v2 da error si se envía
        inp = {"text": texto, "voice": a.voz, "stability": 0.5, "similarity_boost": 0.75, "style": 0, "speed": a.velocidad}
        if a.modelo == "turbo":
            inp["language_code"] = "es"
        cuerpo = {"model": MODELOS_VOZ[a.modelo], "input": inp}
    ejecutar(cuerpo, a.salida, a.concepto, a.etapa)


if __name__ == "__main__":
    main()
