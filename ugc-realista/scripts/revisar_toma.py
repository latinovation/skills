#!/usr/bin/env python3
"""Control de calidad de una toma de video generada (UGC realista). Mide lo que se puede medir y deja una hoja
de fotogramas para lo que hay que mirar (manos, anillos, etiqueta, naturalidad).

Uso:
  python revisar_toma.py calibrar <carpeta_poses>
      Parecido entre las poses del personaje (misma persona) -> <carpeta_poses>/calibracion.json.
  python revisar_toma.py toma <video.mp4> [--poses <carpeta>] [--texto "lo que debe decir"]
                         [--criticas "MiMarca,gomitas"] [--idioma es] [--salida <carpeta>]
      Cara contra las poses, diálogo contra el guion (Whisper), palabras críticas, ritmo, formato y hoja.
  python revisar_toma.py comparar <carpeta_poses> <imagen...>
      Parecido de imágenes sueltas contra las poses (p. ej. para comprobar que otra persona queda por debajo).
  python revisar_toma.py hoja <video.mp4> [--salida <carpeta>]
      Solo la hoja de fotogramas (un cuadro cada 0,5 s).

Resultado de `toma`, de peor a mejor:
  FALLA       algo medido quedó fuera de umbral: se descarta la toma.
  INCOMPLETO  nada falló pero algo quedó sin medir: no se puede entregar como verificado.
  REVISAR     el diálogo pasa el umbral pero alguna palabra no coincide: confirmar con otro modelo o que la
              persona lo escuche (una sola vocal cambiada ya cambia el sentido).
  PASA        todo medido y dentro de umbral.

Dependencias: numpy, opencv-python-headless (>=4.8), ffmpeg y ffprobe en el PATH. Whisper (uno de): mlx_whisper
(Mac), faster-whisper u openai-whisper; siempre el modelo large-v3-turbo, con el que se calibró el umbral.
Modelos de cara (se bajan solos a ~/ugc-realista/modelos y se verifican por SHA-256): YuNet (MIT) y SFace
(Apache-2.0) de github.com/opencv/opencv_zoo, aptos para uso comercial."""
import argparse
import difflib
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path.home() / "ugc-realista"
MODELOS = {
    "yunet": ("face_detection_yunet_2023mar.onnx", "face_detection_yunet",
              "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"),
    "sface": ("face_recognition_sface_2021dec.onnx", "face_recognition_sface",
              "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79"),
}
FPS_CARA = 2
CARA_MIN_PX = 60          # caras más chicas no se comparan: el parecido sale con ruido
DIALOGO_MIN = 0.93        # similitud por palabras con el guion, calibrada con Whisper large-v3-turbo
# Ritmo medido (oct-2026): la toma «robot» rechazada iba a 1,72 palabras/s y la aprobada a 2,64. Entre ambas no
# hay mediciones: por debajo de 2,2 falla; de 2,2 a 2,6 y por encima de 3,8 solo avisa (que la persona escuche).
RITMO_FALLA = 2.2
RITMO_OK = (2.6, 3.8)
# Parecido SFace medido en 42 tomas de video de 2 personajes: misma persona 0,565–0,776 de media; otra persona
# 0,337–0,411. El percentil 10 se cruza entre ambos grupos (giros de perfil), por eso solo avisa.
CARA_MEDIA_MIN = 0.50
CARA_P10_AVISO = 0.30
POSES_MEDIA_MIN = 0.60    # poses de un mismo personaje entre sí: 0,72 y 0,83 en los dos kits medidos
POSE_ATIPICA = 0.50       # una pose que en promedio se parece menos que esto a las demás: revisar o quitar
EXTS_IMAGEN = {".png", ".jpg", ".jpeg", ".webp"}


class SinModelo(Exception):
    pass


def modelo(clave):
    nombre, carpeta, sha = MODELOS[clave]
    ruta = RAIZ / "modelos" / nombre
    if not ruta.exists():
        ruta.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://github.com/opencv/opencv_zoo/raw/main/models/{carpeta}/{nombre}"
        print(f"bajando {nombre}…", file=sys.stderr)
        tmp = ruta.with_suffix(".part")
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                tmp.write_bytes(r.read())
        except (urllib.error.URLError, OSError) as e:
            tmp.unlink(missing_ok=True)
            raise SinModelo(f"no se pudo bajar {nombre} de github.com ({e}); copiarlo a mano a {ruta}") from e
        tmp.rename(ruta)
    if hashlib.sha256(ruta.read_bytes()).hexdigest() != sha:
        ruta.unlink()
        raise SinModelo(f"{nombre} no coincide con su SHA-256 (se borró); volver a correr")
    return str(ruta)


class Caras:
    def __init__(self):
        self.det = cv2.FaceDetectorYN.create(modelo("yunet"), "", (320, 320), 0.7, 0.3, 5000)
        self.rec = cv2.FaceRecognizerSF.create(modelo("sface"), "")

    def vector(self, img):
        """Vector de identidad de la cara más grande de la imagen, o None si no hay cara usable."""
        if img is None:
            return None
        h, w = img.shape[:2]
        self.det.setInputSize((w, h))
        _, caras = self.det.detect(img)
        if caras is None or len(caras) == 0:
            return None
        # Las manos abiertas y los tejidos dan falsos positivos con recuadro grande: primero las más seguras, luego la más grande
        seguras = [c for c in caras if c[-1] >= caras[:, -1].max() - 0.05]
        cara = max(seguras, key=lambda c: c[2] * c[3])
        if min(cara[2], cara[3]) < CARA_MIN_PX:
            return None
        v = self.rec.feature(self.rec.alignCrop(img, cara)).flatten().astype(np.float64)
        return v / np.linalg.norm(v)


def leer(ruta):
    return cv2.imdecode(np.fromfile(str(ruta), dtype=np.uint8), cv2.IMREAD_COLOR)  # admite rutas con tildes en Windows


def escribir(ruta, img):
    ok, buf = cv2.imencode(Path(ruta).suffix, img)
    if not ok:
        raise OSError(f"no se pudo codificar {ruta}")
    buf.tofile(str(ruta))  # cv2.imwrite falla en silencio con rutas no ASCII en Windows


def imagenes(carpeta):
    return sorted(p for p in Path(carpeta).iterdir() if p.suffix.lower() in EXTS_IMAGEN and not p.name.startswith("."))


def vectores_poses(caras, carpeta):
    vs, sin_cara = {}, []
    for p in imagenes(carpeta):
        v = caras.vector(leer(p))
        if v is None:
            sin_cara.append(p.name)
        else:
            vs[p.name] = v
    return vs, sin_cara


def calibrar(carpeta):
    caras = Caras()
    vs, sin_cara = vectores_poses(caras, carpeta)
    if len(vs) < 3:
        sys.exit(f"ERROR: hacen falta al menos 3 poses con la cara visible; hay {len(vs)} (sin cara: {sin_cara}).")
    nombres = list(vs)
    sims = [float(vs[a] @ vs[b]) for i, a in enumerate(nombres) for b in nombres[i + 1:]]
    media = float(np.mean(sims))
    atipicas = {a: round(float(np.mean([vs[a] @ vs[b] for b in nombres if b != a])), 3) for a in nombres}
    atipicas = {a: s for a, s in atipicas.items() if s < POSE_ATIPICA}
    res = {
        "poses_con_cara": len(vs), "sin_cara": sin_cara, "atipicas": atipicas,
        "entre_poses": {"media": round(media, 3), "min": round(min(sims), 3), "p10": round(float(np.percentile(sims, 10)), 3)},
        "umbral_media": CARA_MEDIA_MIN, "aviso_p10": CARA_P10_AVISO,
        "kit_valido": media >= POSES_MEDIA_MIN and not atipicas,
    }
    (Path(carpeta) / "calibracion.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False))
    if media < POSES_MEDIA_MIN:
        print(f"AVISO: las poses se parecen poco entre sí ({media:.2f} < {POSES_MEDIA_MIN}); quizá no son la misma cara. "
              "Rehacer el kit antes de generar video.", file=sys.stderr)
    if atipicas:
        print(f"AVISO: poses atípicas {atipicas}: otra cara, cara muy chica, tapada o de perfil completo. "
              "Quitarlas de la carpeta (un perfil puede ir como referencia de la generación, no de la medición).", file=sys.stderr)


def comparar(carpeta, rutas):
    caras = Caras()
    vs, _ = vectores_poses(caras, carpeta)
    for r in rutas:
        v = caras.vector(leer(r))
        print(Path(r).name, "sin cara" if v is None else round(float(np.mean([v @ p for p in vs.values()])), 3))


def fotogramas(video, carpeta, fps):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", f"fps={fps}", str(carpeta / "f_%04d.png")], check=True)
    return sorted(carpeta.glob("f_*.png"))


def hoja(frames, destino, paso):
    """Un cuadro cada `paso` segundos, 8 por fila, con el tiempo escrito."""
    ims = []
    for i, f in enumerate(frames):
        im = leer(f)
        im = cv2.resize(im, (180, 320) if im.shape[0] >= im.shape[1] else (320, 180))
        cv2.putText(im, f"{i * paso:.1f}s", (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
        ims.append(im)
    if not ims:
        return False
    cols = 8
    filas = [ims[i:i + cols] + [np.zeros_like(ims[0])] * (cols - len(ims[i:i + cols])) for i in range(0, len(ims), cols)]
    escribir(destino, np.vstack([np.hstack(f) for f in filas]))
    return True


def formato(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(video)],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    if not d.get("streams"):
        sys.exit(f"ERROR: {video} no tiene video legible.")
    s = d["streams"][0]
    audio = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0",
                            str(video)], capture_output=True, text=True).stdout.strip()
    try:
        dur = round(float(d.get("format", {}).get("duration")), 2)
    except (TypeError, ValueError):
        dur = None
    return {"ancho": s.get("width"), "alto": s.get("height"), "fps": s.get("r_frame_rate"), "duracion_s": dur, "audio": bool(audio)}


def normalizar(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", t).split()


def whisper_hijo(wav, idioma):
    """Corre en un proceso aparte: faster-whisper trae PyAV, que choca con las librerías de video de OpenCV si se
    cargan juntos. El audio entra ya decodificado (wav 16 kHz mono) para no depender de PyAV, cuyas versiones nuevas
    rompen faster-whisper 1.2 («unexpected keyword argument 'metadata_errors'»)."""
    import wave
    from faster_whisper import WhisperModel
    with wave.open(wav) as w:
        audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    segs, _ = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8").transcribe(
        audio, language=idioma, word_timestamps=True, condition_on_previous_text=False)
    pals = [(w.word, w.start, w.end) for s in segs for w in (s.words or [])]
    print(json.dumps({"texto": "".join(p[0] for p in pals).strip(), "palabras": pals}))


def whisper_cli(exe, wav, idioma):
    if exe == "mlx_whisper":
        args = ["--model", "mlx-community/whisper-large-v3-turbo", "--word-timestamps", "True", "--output-format", "json",
                "--condition-on-previous-text", "False", "--output-dir", str(wav.parent)]
    else:
        args = ["--model", "turbo", "--word_timestamps", "True", "--output_format", "json",
                "--condition_on_previous_text", "False", "--output_dir", str(wav.parent)]
    subprocess.run([exe, str(wav), "--language", idioma, *args], capture_output=True, text=True)
    js = wav.parent / f"{wav.stem}.json"
    if not js.exists():
        return None
    d = json.loads(js.read_text(encoding="utf-8"))
    pals = [(w["word"], w["start"], w["end"]) for s in d.get("segments", []) for w in s.get("words", [])]
    return d.get("text", "").strip(), pals


def transcribir(wav, idioma):
    """(texto, palabras con tiempos, motor, error) con el primer Whisper que funcione; todos con large-v3-turbo."""
    errores = []
    if shutil.which("mlx_whisper"):
        r = whisper_cli("mlx_whisper", wav, idioma)
        if r:
            return (*r, "mlx_whisper large-v3-turbo", None)
        errores.append("mlx_whisper instalado pero no transcribió")
    if importlib.util.find_spec("faster_whisper"):
        p = subprocess.run([sys.executable, __file__, "_whisper", str(wav), idioma], capture_output=True, text=True,
                           encoding="utf-8")
        if p.returncode == 0:
            d = json.loads(p.stdout.strip().splitlines()[-1])
            return d["texto"], [tuple(x) for x in d["palabras"]], "faster-whisper large-v3-turbo", None
        ultima = (p.stderr.strip().splitlines() or ["sin detalle"])[-1]
        errores.append(f"faster-whisper instalado pero falló (¿descarga del modelo de 1,55 GB?): {ultima}")
    if shutil.which("whisper"):
        r = whisper_cli("whisper", wav, idioma)
        if r:
            return (*r, "openai-whisper turbo", None)
        errores.append("openai-whisper instalado pero no transcribió")
    return None, [], None, "; ".join(errores) or "no hay Whisper instalado (mlx_whisper, faster-whisper u openai-whisper)"


def cambios(esperado, oido):
    """Palabras del guion que no se oyeron y palabras oídas que no estaban, para ver una sustitución de un vistazo."""
    a, b = normalizar(esperado), normalizar(oido)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op != "equal":
            out.append(f"«{' '.join(a[i1:i2])}» → «{' '.join(b[j1:j2])}»")
    return out


def dialogo(video, esperado, criticas, idioma, tmp):
    wav = tmp / "audio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)], check=True)
    oido, pals, motor, error = transcribir(wav, idioma)
    if oido is None:
        return {"medido": False, "motivo": error}
    res = {"medido": True, "motor": motor, "oido": oido}
    if esperado:
        res["similitud"] = round(difflib.SequenceMatcher(None, normalizar(esperado), normalizar(oido), autojunk=False).ratio(), 3)
        res["cambios"] = cambios(esperado, oido)
    if criticas:
        texto_oido = " " + " ".join(normalizar(oido)) + " "
        res["criticas_faltan"] = [c for c in criticas if " " + " ".join(normalizar(c)) + " " not in texto_oido]
    if len(pals) >= 4:
        habla = pals[-1][2] - pals[0][1]
        res["palabras_por_s"] = round(len(pals) / habla, 2) if habla > 0 else None
    return res


def toma(video, poses, texto, criticas, idioma, salida):
    video = Path(video)
    salida = Path(salida or video.parent / "revision")
    salida.mkdir(parents=True, exist_ok=True)
    res = {"toma": video.name, "formato": formato(video)}
    fallos, avisos, sin_medir, revisar = [], [], [], []
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        frames = fotogramas(video, tmp, FPS_CARA)
        ruta_hoja = salida / f"{video.stem}_hoja.jpg"
        if not hoja(frames, ruta_hoja, 1 / FPS_CARA):
            fallos.append("no se pudo sacar ningún fotograma")
        if poses:
            medir_cara(poses, frames, res, fallos, avisos, sin_medir)
        else:
            sin_medir.append("cara (no se pasaron --poses)")
        if res["formato"]["audio"]:
            res["dialogo"] = dialogo(video, texto, criticas, idioma, tmp)
            evaluar_dialogo(res["dialogo"], texto, fallos, avisos, sin_medir, revisar)
        elif texto:
            fallos.append("la toma no tiene audio y debía decir un texto")
    if fallos:
        res["automatico"] = "FALLA: " + "; ".join(fallos)
    elif sin_medir:
        res["automatico"] = "INCOMPLETO: sin medir " + "; ".join(sin_medir)
    elif revisar:
        res["automatico"] = "REVISAR: " + "; ".join(revisar)
    else:
        res["automatico"] = "PASA"
    res["revisar"] = revisar
    res["avisos"] = avisos
    res["sin_medir"] = sin_medir
    res["falta_mirar"] = f"{ruta_hoja} con la lista visual (manos, anillos, etiqueta, texto, celular, naturalidad)"
    (salida / f"{video.stem}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1))


def medir_cara(poses, frames, res, fallos, avisos, sin_medir):
    cal_ruta = Path(poses) / "calibracion.json"
    if not cal_ruta.exists():
        sys.exit(f"ERROR: falta {cal_ruta}. Correr primero: revisar_toma.py calibrar {poses}")
    if not json.loads(cal_ruta.read_text(encoding="utf-8")).get("kit_valido", False):
        sin_medir.append("cara: el kit de poses no pasó la calibración (quitar poses atípicas y recalibrar)")
        return
    try:
        caras = Caras()
    except SinModelo as e:
        sin_medir.append(f"cara: {e}")
        return
    refs, _ = vectores_poses(caras, poses)
    sims = [float(np.mean([v @ r for r in refs.values()])) for v in (caras.vector(leer(f)) for f in frames) if v is not None]
    res["cara"] = {"fotogramas": len(frames), "con_cara": len(sims)}
    if not sims:
        fallos.append("no se detectó la cara en ningún fotograma")
        return
    res["cara"].update({"media": round(float(np.mean(sims)), 3), "p10": round(float(np.percentile(sims, 10)), 3),
                        "umbral_media": CARA_MEDIA_MIN})
    if res["cara"]["media"] < CARA_MEDIA_MIN:
        fallos.append(f"cara media {res['cara']['media']} < {CARA_MEDIA_MIN}: probablemente otra persona")
    if res["cara"]["p10"] < CARA_P10_AVISO:
        avisos.append(f"cara p10 {res['cara']['p10']}: hay fotogramas que se parecen poco (giro o cara cambiada); mirarlos")


def evaluar_dialogo(d, texto, fallos, avisos, sin_medir, revisar):
    if not d["medido"]:
        sin_medir.append("diálogo: " + d["motivo"])
        return
    if not texto:
        sin_medir.append("diálogo contra el guion (no se pasó --texto)")
    elif d["similitud"] < DIALOGO_MIN:
        fallos.append(f"diálogo {d['similitud']} < {DIALOGO_MIN}: {', '.join(d['cambios'])}")
    elif d["cambios"]:
        revisar.append(f"el diálogo no coincide palabra por palabra ({', '.join(d['cambios'])}): confirmar con otro "
                       "modelo de Whisper o que la persona lo escuche")
    if d.get("criticas_faltan"):
        fallos.append(f"palabras críticas que no se oyeron: {d['criticas_faltan']}")
    ppm = d.get("palabras_por_s")
    if ppm is None:
        sin_medir.append("ritmo (muy pocas palabras)")
    elif ppm < RITMO_FALLA:
        fallos.append(f"ritmo {ppm} palabras/s < {RITMO_FALLA}: habla lenta, suena a robot")
    elif not RITMO_OK[0] <= ppm <= RITMO_OK[1]:
        avisos.append(f"ritmo {ppm} palabras/s fuera de {RITMO_OK[0]}–{RITMO_OK[1]}: que la persona lo escuche")


def main():
    for flujo in (sys.stdout, sys.stderr):
        flujo.reconfigure(encoding="utf-8", errors="replace")  # consolas de Windows en cp1252
    if len(sys.argv) == 4 and sys.argv[1] == "_whisper":
        return whisper_hijo(sys.argv[2], sys.argv[3])
    for exe in ("ffmpeg", "ffprobe"):
        if not shutil.which(exe):
            sys.exit(f"ERROR: falta {exe} en el PATH. Instalarlo (Mac: brew install ffmpeg · Windows: winget install ffmpeg).")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("calibrar").add_argument("poses")
    c = sub.add_parser("comparar")
    c.add_argument("poses")
    c.add_argument("imagenes", nargs="+")
    t = sub.add_parser("toma")
    t.add_argument("video")
    t.add_argument("--poses")
    t.add_argument("--texto")
    t.add_argument("--criticas", help="palabras que tienen que oírse, separadas por coma (marca, producto, cifras)")
    t.add_argument("--idioma", default="es")
    t.add_argument("--salida")
    h = sub.add_parser("hoja")
    h.add_argument("video")
    h.add_argument("--salida")
    a = ap.parse_args()
    try:
        if a.cmd == "calibrar":
            calibrar(a.poses)
        elif a.cmd == "comparar":
            comparar(a.poses, a.imagenes)
        elif a.cmd == "toma":
            criticas = [x.strip() for x in a.criticas.split(",") if x.strip()] if a.criticas else []
            toma(a.video, a.poses, a.texto, criticas, a.idioma, a.salida)
        else:
            video = Path(a.video)
            salida = Path(a.salida or video.parent / "revision")
            salida.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory() as tmp:
                hoja(fotogramas(video, Path(tmp), FPS_CARA), salida / f"{video.stem}_hoja.jpg", 1 / FPS_CARA)
            print(salida / f"{video.stem}_hoja.jpg")
    except SinModelo as e:
        sys.exit(f"ERROR: {e}")


if __name__ == "__main__":
    main()
