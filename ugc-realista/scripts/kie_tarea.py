#!/usr/bin/env python3
"""Cliente mínimo de kie.ai para la skill UGC realista: saldo, cotizar, crear una tarea de video y seguirla.

Uso (la llave se carga al entorno del comando, nunca se imprime ni se pega en el chat):
  ( set -a; . ~/ugc-realista/.env; set +a; python3 kie_tarea.py saldo )
  python3 kie_tarea.py crear --modelo wan3 --prompt-file p.txt --duracion 4 --resolucion 480P \
      --ratio 9:16 --ref-img https://.../a.png --ref-img https://.../b.png            # solo cotiza y muestra el cuerpo
  python3 kie_tarea.py crear ... --si --salida toma.mp4                              # envía, espera y baja el video
  python3 kie_tarea.py estado <taskId>
  python3 kie_tarea.py subir imagen.png audio.mp3                                     # sube a kie y devuelve las URLs para --ref-img / --ref-audio

Seguridad de gasto: `crear` SIN `--si` nunca envía nada: imprime el cuerpo y el costo estimado. Con `--si` la persona ya aprobó la cotización.
Modelos: `wan3` (wan/3-0-video) y `seedance` (bytedance/seedance-2-5). Tarifas de docs.kie.ai y kie.ai/blog (oct-2026); confirmar siempre en kie.ai/pricing.
OJO: en la API de kie, la resolución por defecto de Wan 3.0 es 1080P (4 veces el costo de 480P). Este script siempre envía la resolución, por defecto 480P.
HTTP con curl (el Python de framework de macOS falla con certificados)."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

API = "https://api.kie.ai"
UPLOAD = "https://kieai.redpandaai.co"
# créditos por segundo: wan3 480P/720P/1080P = 8/16/32 (kie.ai/wan3.0-video); seedance sin video de referencia 28/63/158 (blog de kie)
TARIFA = {"wan3": {"480P": 8, "720P": 16, "1080P": 32}, "seedance": {"480P": 28, "720P": 63, "1080P": 158}}
MODELOS = {"wan3": "wan/3-0-video", "seedance": "bytedance/seedance-2-5"}
USD_POR_CREDITO = 0.005
RATIOS_WAN = {"adaptive", "16:9", "4:3", "1:1", "3:4", "9:16"}


def clave() -> str:
    k = os.environ.get("KIE_API_KEY")
    if not k:
        sys.exit("Falta KIE_API_KEY en el entorno. Cárgala con: ( set -a; . ~/ugc-realista/.env; set +a; python3 kie_tarea.py ... )")
    return k


def config_clave() -> str:
    """Configuración de curl con la llave, para pasarla por la entrada estándar (`-K -`) y no en la línea de comando,
    donde otros procesos de la computadora la verían con `ps`."""
    k = clave()
    if any(c in k for c in '"\\\n\r'):
        sys.exit("KIE_API_KEY tiene caracteres no válidos (comillas, barras o saltos de línea).")
    return f'header = "Authorization: Bearer {k}"\n'


def http(metodo: str, url: str, cuerpo: dict | None = None) -> dict:
    cmd = ["curl", "-s", "-m", "300", "-K", "-", "-X", metodo, url, "-H", "Content-Type: application/json"]
    if cuerpo is not None:
        cmd += ["-d", json.dumps(cuerpo)]
    r = subprocess.run(cmd, input=config_clave(), capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        sys.exit(f"Respuesta no válida de kie ({r.returncode}): {r.stdout[:300]} {r.stderr[:200]}")
    if d.get("code") not in (200, None):   # kie responde HTTP 200 con el error dentro de `code`
        sys.exit(f"kie devolvió code={d.get('code')}: {d.get('msg')}")
    return d


def saldo() -> None:
    d = http("GET", f"{API}/api/v1/chat/credit")
    print("créditos:", d.get("data"))


def cuerpo_tarea(a: argparse.Namespace, prompt: str) -> dict:
    modelo = MODELOS[a.modelo]
    inp = {"prompt": prompt, "resolution": a.resolucion, "duration": a.duracion, "aspect_ratio": a.ratio}
    if a.modelo == "wan3":
        inp["audio"] = a.audio
        if a.primer_cuadro: inp["first_frame_url"] = a.primer_cuadro
        if a.ultimo_cuadro: inp["last_frame_url"] = a.ultimo_cuadro
        if a.ref_img: inp["reference_image_urls"] = a.ref_img
        if a.ref_video: inp["reference_video_urls"] = a.ref_video
        if a.ref_audio: inp["reference_audio_urls"] = a.ref_audio
    else:
        inp["generate_audio"] = a.audio
        inp["resolution"] = a.resolucion.lower()
        if a.ref_img: inp["reference_image_urls"] = a.ref_img
        if a.ref_video: inp["reference_video_urls"] = a.ref_video
        if a.ref_audio: inp["reference_audio_urls"] = a.ref_audio
    return {"model": modelo, "input": inp}


def validar(a: argparse.Namespace) -> None:
    if a.modelo == "wan3":
        if a.duracion != -1 and not 2 <= a.duracion <= 30: sys.exit("Wan 3.0: duración 2 a 30 s, o -1 (la elige el modelo).")
        if a.ratio not in RATIOS_WAN: sys.exit(f"Wan 3.0: ratio uno de {sorted(RATIOS_WAN)}.")
        if len(a.ref_img) > 10: sys.exit("Wan 3.0: hasta 10 imágenes de referencia.")
        if len(a.ref_video) > 5 or len(a.ref_audio) > 5: sys.exit("Wan 3.0: hasta 5 videos y 5 audios de referencia.")
        if (a.primer_cuadro or a.ultimo_cuadro) and (a.ref_img or a.ref_video or a.ref_audio):
            sys.exit("Wan 3.0: el primer/último cuadro NO se combina con referencias.")
        if a.ultimo_cuadro and not a.primer_cuadro: sys.exit("Wan 3.0: el último cuadro exige primer cuadro.")
    else:
        if a.duracion != -1 and not 4 <= a.duracion <= 30: sys.exit("Seedance 2.5: duración 4 a 30 s, o -1.")
        if a.ref_video and (a.ratio != "adaptive" or a.duracion != -1): sys.exit("Seedance 2.5 en edición exige --ratio adaptive y --duracion -1.")
    if a.resolucion not in ("480P", "720P", "1080P"): sys.exit("Resolución: 480P, 720P o 1080P.")


def costo(a: argparse.Namespace, seg_ref_video: float = 0) -> float | None:
    if a.duracion == -1:
        return None
    return TARIFA[a.modelo][a.resolucion] * (a.duracion + seg_ref_video)


def subir(archivos: list[str]) -> None:
    """Sube archivos locales al almacenamiento de kie (multipart) y escribe una URL por línea."""
    for ruta in archivos:
        nombre = f"{int(time.time())}_{os.path.basename(ruta)}"
        r = subprocess.run(["curl", "-s", "-m", "300", "-K", "-", "-X", "POST", f"{UPLOAD}/api/file-stream-upload",
                            "-F", f"file=@{ruta}", "-F", "uploadPath=ugc-realista", "-F", f"fileName={nombre}"],
                           input=config_clave(), capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
        except Exception:
            sys.exit(f"Respuesta no válida al subir {ruta}: {r.stdout[:300]}")
        if d.get("code") not in (200, None) or not d.get("success", True):
            sys.exit(f"kie no aceptó {ruta}: {d.get('code')} {d.get('msg')}")
        datos = d.get("data") or {}
        url = datos.get("downloadUrl") or datos.get("fileUrl")
        if not url:
            sys.exit(f"Subida sin URL en la respuesta: {json.dumps(d)[:300]}")
        print(url, flush=True)


def seguir(task_id: str, salida: str | None) -> None:
    t0 = time.time(); ultimo = None
    while time.time() - t0 < 45 * 60:
        rec = http("GET", f"{API}/api/v1/jobs/recordInfo?taskId={task_id}").get("data") or {}
        if rec.get("state") != ultimo:
            ultimo = rec.get("state"); print(f"  estado: {ultimo} ({int(time.time()-t0)} s)", flush=True)
        if ultimo == "success":
            urls = (json.loads(rec.get("resultJson") or "{}")).get("resultUrls") or []
            print("créditos consumidos:", rec.get("creditsConsumed"))
            if urls and salida:
                subprocess.run(["curl", "-s", "-m", "300", "-o", salida, urls[0]], check=True); print("guardado:", salida)
            else:
                print("resultUrls:", urls)
            return
        if ultimo == "fail":
            sys.exit(f"Falló: {rec.get('failMsg')} (créditos consumidos: {rec.get('creditsConsumed')})")
        time.sleep(15)
    sys.exit("Se acabó la espera de 45 min: revisa con `estado <taskId>` antes de pagar otra.")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest="cmd", required=True)
    s.add_parser("saldo")
    e = s.add_parser("estado"); e.add_argument("task_id"); e.add_argument("--salida")
    u = s.add_parser("subir"); u.add_argument("archivos", nargs="+")
    l = s.add_parser("lipsync", help="rehace la boca de un video para que siga un audio (volcengine/video-to-video-lip-sync)")
    l.add_argument("--video", required=True); l.add_argument("--audio", required=True)
    l.add_argument("--modo", choices=["lite", "basic"], default="lite", help="lite: una persona de frente; basic: escenas complejas")
    l.add_argument("--si", action="store_true"); l.add_argument("--salida")
    c = s.add_parser("crear")
    c.add_argument("--modelo", choices=list(MODELOS), required=True)
    g = c.add_mutually_exclusive_group(required=True); g.add_argument("--prompt"); g.add_argument("--prompt-file")
    c.add_argument("--duracion", type=int, default=4); c.add_argument("--resolucion", default="480P")
    c.add_argument("--ratio", default="9:16"); c.add_argument("--audio", action="store_true", help="por defecto SIN audio")
    c.add_argument("--primer-cuadro"); c.add_argument("--ultimo-cuadro")
    c.add_argument("--ref-img", action="append", default=[]); c.add_argument("--ref-video", action="append", default=[]); c.add_argument("--ref-audio", action="append", default=[])
    c.add_argument("--seg-ref-video", type=float, default=0, help="segundos de video de referencia (se cobran)")
    c.add_argument("--si", action="store_true", help="la persona aprobó la cotización: ENVÍA y cobra")
    c.add_argument("--salida")
    a = p.parse_args()
    if a.cmd == "saldo": return saldo()
    if a.cmd == "estado": return seguir(a.task_id, a.salida)
    if a.cmd == "subir": return subir(a.archivos)
    if a.cmd == "lipsync":
        cuerpo = {"model": "volcengine/video-to-video-lip-sync", "input": {"mode": a.modo, "video_url": a.video, "audio_url": a.audio}}
        print("cuerpo:", json.dumps(cuerpo)[:200], "\ncosto: sin tarifa publicada en la doc de kie; medir el saldo antes y después")
        if not a.si:
            print("Simulación: no se envió nada. Repite con --si."); return
        d = http("POST", f"{API}/api/v1/jobs/createTask", cuerpo); task = (d.get("data") or {}).get("taskId")
        if not task: sys.exit(f"No devolvió taskId: {d}")
        print("taskId:", task, flush=True); return seguir(task, a.salida)
    a.resolucion = a.resolucion.upper()
    validar(a)
    prompt = a.prompt if a.prompt else open(a.prompt_file, encoding="utf-8").read().strip()
    cuerpo = cuerpo_tarea(a, prompt)
    cr = costo(a, a.seg_ref_video)
    print("cuerpo:", json.dumps({**cuerpo, "input": {**cuerpo["input"], "prompt": prompt[:60] + ("..." if len(prompt) > 60 else "")}}, ensure_ascii=False))
    print("costo estimado:", "lo decide el modelo (duración -1)" if cr is None else f"{cr} créditos ≈ US${cr * USD_POR_CREDITO:.2f}")
    if not a.si:
        print("Simulación: no se envió nada. Con la cotización aprobada, repite el comando con --si."); return
    d = http("POST", f"{API}/api/v1/jobs/createTask", cuerpo)
    task = (d.get("data") or {}).get("taskId")
    if not task: sys.exit(f"No devolvió taskId: {d}")
    print("taskId:", task, flush=True)
    seguir(task, a.salida)


if __name__ == "__main__":
    main()
