"""Voz en off con Kokoro (local, gratis), verificada con Whisper.

Por cada línea de guion.json hace hasta len(velocidades) tomas (Kokoro repite la misma toma a la misma velocidad); cada toma
se transcribe con mlx_whisper large-v3-turbo y se acepta si la similitud con el guion llega a `similitud_minima`.
Escribe voz/<id>.wav, voz/<id>.palabras.json (tiempo de cada palabra del guion) y voz/informe.json.
Una línea cuyo texto no cambió y ya tiene su .wav no se vuelve a sintetizar (salvo que se pida por id).

Uso:  ~/.venvs/kokoro/bin/python voz.py            # todas las líneas nuevas o cambiadas
      ~/.venvs/kokoro/bin/python voz.py m2 m3      # solo esas (siempre se rehacen)
"""
import difflib
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
VOZ = AQUI / "voz"
PROY = json.loads((AQUI / "proyecto.json").read_text())
CONF = PROY["voz"]
IDIOMA = PROY.get("idioma", "es")
CACHE = Path.home() / ".cache" / "hyperframes" / "tts"
MODELO = CACHE / "models" / "kokoro-v1.0.onnx"
VOCES = CACHE / "voices" / "voices-v1.0.bin"
PYTHON = Path.home() / ".venvs" / "kokoro" / "bin" / "python"
WHISPER = Path.home() / ".local" / "bin" / "mlx_whisper"

UNIDADES = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once", "doce", "trece",
            "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte", "veintiuno", "veintidós",
            "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete", "veintiocho", "veintinueve"]
DECENAS = {30: "treinta", 40: "cuarenta", 50: "cincuenta", 60: "sesenta", 70: "setenta", 80: "ochenta", 90: "noventa"}
CENTENAS = {100: "ciento", 200: "doscientos", 300: "trescientos", 400: "cuatrocientos", 500: "quinientos", 600: "seiscientos",
            700: "setecientos", 800: "ochocientos", 900: "novecientos"}


def sintesis() -> Path:
    """El script de síntesis que instala HyperFrames (synth-v3.py, synth-v4.py…): el de versión más alta."""
    candidatos = sorted(CACHE.glob("synth-v*.py"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0))
    if not candidatos:
        sys.exit(f"No hay synth-v*.py en {CACHE}: corre una vez `npx --yes hyperframes@0.9.63 tts \"hola\" --voice ef_dora` para instalarlo.")
    return candidatos[-1]


def en_letras(n: int) -> str:
    if n < 30:
        return UNIDADES[n]
    if n < 100:
        d, u = divmod(n, 10)
        return DECENAS[d * 10] + ("" if u == 0 else f" y {UNIDADES[u]}")
    if n == 100:
        return "cien"
    if n < 1000:
        c, r = divmod(n, 100)
        return CENTENAS[c * 100] + ("" if r == 0 else " " + en_letras(r))
    if n < 1_000_000:
        m, r = divmod(n, 1000)
        return ("mil" if m == 1 else en_letras(m) + " mil") + ("" if r == 0 else " " + en_letras(r))
    m, r = divmod(n, 1_000_000)
    return ("un millón" if m == 1 else en_letras(m) + " millones") + ("" if r == 0 else " " + en_letras(r))


def numeros_a_letras(texto: str) -> str:
    """Whisper escribe cifras con dígitos; el guion las trae en palabras. Solo español."""
    if IDIOMA != "es":
        return texto

    def cambiar(m: re.Match) -> str:
        entero, _, decimal = m.group(0).replace(".", "").partition(",")
        palabras = en_letras(int(entero))
        return palabras + (f" coma {en_letras(int(decimal))}" if decimal else "")
    texto = texto.replace("%", " por ciento")
    return re.sub(r"\d[\d.]*(,\d+)?", cambiar, texto)


def norm(t: str) -> list[str]:
    t = unicodedata.normalize("NFC", numeros_a_letras(t).lower())
    return re.sub(r"[^\wáéíóúüñ ]+", " ", t).split()


def sin_tildes(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")


def sintetizar(texto: str, velocidad: float, salida: Path) -> float:
    r = subprocess.run([str(PYTHON), str(sintesis()), str(MODELO), str(VOCES), texto, CONF["id"], str(velocidad), str(salida),
                        CONF["fonemas"]], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Kokoro falló en {salida.name}:\n{r.stderr[-800:]}")
    return json.loads(r.stdout.strip().splitlines()[-1])["durationSeconds"]


def transcribir(wav: Path) -> tuple[str, list[dict]]:
    r = subprocess.run([str(WHISPER), str(wav), "--language", IDIOMA, "--model", "mlx-community/whisper-large-v3-turbo",
                        "--word-timestamps", "True", "--output-format", "json", "--output-dir", str(wav.parent)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Whisper falló en {wav.name}:\n{r.stderr[-800:]}")
    datos = json.loads(wav.with_suffix(".json").read_text())
    palabras = [{"w": w["word"].strip(), "s": w["start"], "e": w["end"]} for seg in datos["segments"] for w in seg["words"]]
    return datos["text"].strip(), palabras


def similitud(guion: str, oido: str) -> float:
    """Por palabras y sin autojunk: por carácter, difflib hunde el ratio en textos largos."""
    a = [sin_tildes(w) for w in norm(guion)]
    b = [sin_tildes(w) for w in norm(oido)]
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def alinear(texto: str, palabras_whisper: list[dict], duracion: float) -> list[dict]:
    """Tiempo de cada palabra del guion: la que Whisper reconoce toma su tiempo; el resto se interpola."""
    guion = texto.split()
    a = [sin_tildes(" ".join(norm(w))) for w in guion]
    b = [sin_tildes(" ".join(norm(w["w"]))) for w in palabras_whisper]
    tiempos: list = [None] * len(guion)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            w = palabras_whisper[blk.b + k]
            tiempos[blk.a + k] = (w["s"], w["e"])
    conocidos = [i for i, t in enumerate(tiempos) if t]
    for i, t in enumerate(tiempos):
        if t:
            continue
        prev = max([j for j in conocidos if j < i], default=None)
        nxt = min([j for j in conocidos if j > i], default=None)
        t0 = tiempos[prev][1] if prev is not None else 0.0
        t1 = tiempos[nxt][0] if nxt is not None else duracion
        huecos = (nxt if nxt is not None else len(guion)) - (prev if prev is not None else -1) - 1
        pos = i - (prev if prev is not None else -1) - 1
        paso = (t1 - t0) / max(huecos, 1)
        tiempos[i] = (round(t0 + pos * paso, 3), round(t0 + (pos + 1) * paso, 3))
    return [{"w": g, "s": round(t[0], 3), "e": round(t[1], 3)} for g, t in zip(guion, tiempos)]


def huella(texto: str) -> str:
    return hashlib.sha1(f"{CONF['id']}|{CONF['fonemas']}|{texto}".encode()).hexdigest()[:12]


def main() -> None:
    VOZ.mkdir(exist_ok=True)
    lineas = json.loads((AQUI / "guion.json").read_text())["lineas"]
    pedidas = set(sys.argv[1:])
    desconocidas = pedidas - {l["id"] for l in lineas}
    if desconocidas:
        sys.exit(f"Ids que no están en guion.json: {sorted(desconocidas)}")
    informe_p = VOZ / "informe.json"
    informe = json.loads(informe_p.read_text()) if informe_p.exists() else {}
    for linea in lineas:
        id_, texto = linea["id"], linea["texto"]
        if pedidas and id_ not in pedidas:
            continue
        previo = informe.get(id_)
        if not pedidas and previo and previo.get("huella") == huella(texto) and (VOZ / f"{id_}.wav").exists():
            continue
        mejor = None
        for k, vel in enumerate(CONF["velocidades"], 1):
            wav = VOZ / f"{id_}_toma{k}.wav"  # sin puntos: mlx_whisper corta el nombre de salida en el primero
            dur = sintetizar(texto, vel, wav)
            oido, palabras = transcribir(wav)
            sim = similitud(texto, oido)
            print(f"{id_} toma {k} ({vel}): {dur:.2f} s · similitud {sim:.3f} · «{oido}»", flush=True)
            if mejor is None or sim > mejor["sim"]:
                mejor = {"toma": k, "vel": vel, "wav": wav, "dur": dur, "sim": sim, "oido": oido, "palabras": palabras}
            if sim >= CONF["similitud_minima"]:
                break
        (VOZ / f"{id_}.wav").write_bytes(mejor["wav"].read_bytes())
        alineadas = alinear(texto, mejor["palabras"], mejor["dur"])
        (VOZ / f"{id_}.palabras.json").write_text(json.dumps(alineadas, ensure_ascii=False, indent=0))
        informe[id_] = {"toma": mejor["toma"], "velocidad": mejor["vel"], "duracion_s": mejor["dur"], "huella": huella(texto),
                        "similitud": round(mejor["sim"], 3), "oido": mejor["oido"],
                        "aceptada": mejor["sim"] >= CONF["similitud_minima"]}
        informe_p.write_text(json.dumps(informe, ensure_ascii=False, indent=1))
    sobran = set(informe) - {l["id"] for l in lineas}
    for id_ in sobran:
        del informe[id_]
    informe_p.write_text(json.dumps(informe, ensure_ascii=False, indent=1))
    malas = [k for k, v in informe.items() if not v["aceptada"]]
    print("RECHAZADAS (reescribir la frase, no cambiar la voz):", malas if malas else "ninguna")
    sys.exit(1 if malas else 0)


if __name__ == "__main__":
    main()
