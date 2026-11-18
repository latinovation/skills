"""Revisión del RENDER FINAL antes de entregar: lo medible, más las hojas para mirarlo completo como espectador.

    python3 revisar.py <video.mp4> <carpeta_revision> [linea-de-tiempo.json]

Hace: ffprobe (duración contra la línea de tiempo, 1920×1080/1080×1920, 30 fps, audio), hojas a 2 cuadros/s (12,5 s por hoja),
una tira por escena (20 %, 55 %, 90 %), cuadros negros, volumen integrado (LUFS) y, si hay voces, Whisper sobre el audio final:
cada voz debe oírse en su lugar (similitud por palabras con el guion). Escribe <carpeta>/informe.md con la tabla y la
lista de preguntas de espectador que hay que contestar MIRANDO las hojas (eso no lo mide ningún script).
"""
import difflib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

WHISPER = Path.home() / ".local" / "bin" / "mlx_whisper"
try:   # recorrido: el guion trae cifras en palabras y Whisper las escribe con dígitos; voz.py sabe pasarlas a palabras
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from voz import numeros_a_letras as a_letras
except Exception:
    def a_letras(t: str) -> str:
        return t
FUENTE = "/System/Library/Fonts/Helvetica.ttc"   # sin -font, ImageMagick de Homebrew falla con «unable to read font»


def correr(args: list[str]) -> str:
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"falló {' '.join(args[:3])}…:\n{r.stderr[-600:]}")
    return r.stdout + r.stderr


def sondear(video: Path) -> dict:
    datos = json.loads(correr(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(video)]))
    v = next(s for s in datos["streams"] if s["codec_type"] == "video")
    audio = any(s["codec_type"] == "audio" for s in datos["streams"])
    num, den = v["r_frame_rate"].split("/")
    return {"dur": float(datos["format"]["duration"]), "w": v["width"], "h": v["height"], "fps": round(int(num) / int(den), 2),
            "audio": audio, "mb": round(int(datos["format"]["size"]) / 1e6, 1)}


def hojas(video: Path, out: Path, ancho: int) -> list[str]:
    correr(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-vf", f"fps=2,scale={ancho}:-1,tile=5x5:padding=4",
            str(out / "hoja-%02d.jpg")])
    return sorted(p.name for p in out.glob("hoja-*.jpg"))


def tiras(video: Path, out: Path, escenas: list[dict], ancho: int) -> None:
    (out / "escenas").mkdir(exist_ok=True)
    for s in escenas:
        cuadros = []
        for k, f in enumerate((0.2, 0.55, 0.9)):
            t = s["inicio"] + f * (s["fin"] - s["inicio"])
            p = out / "escenas" / f".{s['id']}-{k}.jpg"
            correr(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
                    "-vf", f"scale={ancho}:-1", str(p)])
            cuadros.append(str(p))
        correr(["magick", "montage", *cuadros, "-font", FUENTE, "-title", s["id"], "-tile", "3x", "-geometry", "+3+3", "-background", "#888",
                str(out / "escenas" / f"{s['id']}.jpg")])
        for c in cuadros:
            Path(c).unlink()


def negros(video: Path) -> list[str]:
    txt = correr(["ffmpeg", "-hide_banner", "-i", str(video), "-vf", "blackdetect=d=0.1:pix_th=0.05", "-an", "-f", "null", "-"])
    return re.findall(r"black_start:([\d.]+)", txt)


def lufs(video: Path) -> float | None:
    txt = correr(["ffmpeg", "-hide_banner", "-i", str(video), "-vn", "-af", "ebur128=framelog=quiet", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt)
    return float(m[-1]) if m else None


def palabras(t: str) -> list[str]:
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^\w ]+", " ", t).split()


def voces_oidas(video: Path, out: Path, voces: list[dict], idioma: str) -> list[dict]:
    wav = out / "audio_final.wav"
    correr(["ffmpeg", "-loglevel", "error", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
    correr([str(WHISPER), str(wav), "--language", idioma, "--model", "mlx-community/whisper-large-v3-turbo",
            "--word-timestamps", "True", "--condition-on-previous-text", "False", "--output-format", "json",
            "--output-dir", str(out)])
    ws = [w for seg in json.loads((out / "audio_final.json").read_text())["segments"] for w in seg.get("words", [])]
    filas = []
    for v in voces:
        # Por el FIN de la palabra: Whisper suele pegar el inicio de la primera palabra al inicio del segmento.
        oido = " ".join(w["word"] for w in ws if w["end"] > v["t"] + 0.05 and w["start"] < v["t"] + v["dur"] + 0.3)
        sim = difflib.SequenceMatcher(None, palabras(v["texto"]), palabras(a_letras(oido)), autojunk=False).ratio()
        filas.append({"id": v["id"], "t": v["t"], "sim": round(sim, 2), "oido": oido.strip()})
    wav.unlink()
    return filas


def main() -> None:
    video, out = Path(sys.argv[1]), Path(sys.argv[2])
    linea = json.loads(Path(sys.argv[3]).read_text()) if len(sys.argv) > 3 else {}
    out.mkdir(parents=True, exist_ok=True)
    p = sondear(video)
    ancho = 384 if p["w"] >= p["h"] else 216
    formato_ok = (p["w"], p["h"]) in ((1920, 1080), (1080, 1920)) and p["fps"] == 30
    lineas = [f"# Revisión de {video.name}", "",
              f"- {p['w']}×{p['h']} · {p['fps']} fps {'✅' if formato_ok else '⚠️ (se espera 1920×1080 o 1080×1920 a 30 fps)'}"
              f" · {p['dur']:.2f} s · {p['mb']} MB · audio: {'sí ✅' if p['audio'] else 'NO ⚠️'}"]
    esperado = linea.get("total_s")
    if esperado:
        dif = p["dur"] - esperado
        lineas.append(f"- Duración esperada {esperado:.2f} s → diferencia {dif:+.2f} s {'✅' if abs(dif) < 0.2 else '⚠️'}")
    hs = hojas(video, out, ancho)
    lineas.append(f"- Hojas a 2 cuadros/s: {', '.join(hs)} (cada hoja = 12,5 s; la hoja N empieza en {{(N-1)×12,5}} s)")
    if linea.get("escenas"):
        tiras(video, out, linea["escenas"], ancho)
        lineas.append(f"- Tiras por escena (20/55/90 %): escenas/<id>.jpg ({len(linea['escenas'])})")
    ng = negros(video)
    lineas.append(f"- Cuadros negros: {', '.join(ng) + ' s ⚠️' if ng else 'ninguno ✅'}")
    if p["audio"]:
        li = lufs(video)
        lineas.append(f"- Volumen integrado: {li} LUFS {'✅' if li is not None and abs(li + 16) <= 1.5 else '⚠️ (objetivo −16)'}")
    if linea.get("voces"):
        filas = voces_oidas(video, out, linea["voces"], linea.get("idioma", "es"))
        malas = [f for f in filas if f["sim"] < 0.85]
        lineas += ["", f"## Voces en el audio final ({len(filas) - len(malas)}/{len(filas)} con similitud ≥ 0,85)", "",
                   "| id | t (s) | similitud | Whisper oyó |", "|---|---|---|---|"]
        lineas += [f"| {f['id']} | {f['t']:.1f} | {f['sim']}{' ⚠️' if f['sim'] < 0.85 else ''} | {f['oido'][:90]} |" for f in filas]
    lineas += ["", "## Veredicto de espectador (contestar MIRANDO las hojas y las tiras, no con métricas)", "",
               "1. ¿Se ve lo que promete cada frase (de la voz o del texto en pantalla) en ese segundo? (con voz: cruzar con la tabla)",
               "2. ¿Algún rótulo, subtítulo, chip, anillo o panel tapa algo que importa?",
               "3. ¿Cada cifra (dicha o escrita) es la de la fuente y, si se dice, está en pantalla ≥ 1,5 s antes?",
               "4. ¿Hay estados vacíos, errores, cargas eternas, «0 kW», datos de prueba o datos personales a la vista?",
               "5. Pasada de significado: leer cada texto escrito por nosotros (títulos, capítulos, rótulos, resumen) y "
               "preguntar si es CIERTO para este periodo y este cliente.",
               "6. Incoherencias que quedan (con su segundo) → al LEEME de la entrega.", ""]
    (out / "informe.md").write_text("\n".join(lineas))
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
