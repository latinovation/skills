"""Arma un proyecto HyperFrames por video: toma de Wan + subtítulos (tiempos de Whisper) + tarjetas de cifras + cierre.
Estilos `3d-cristal` y `documental` (referencias/estilos/). PLANTILLA: es el script de una serie real de explicativos de salud,
tal como funcionó; se copia a <proyecto>/scripts/ y se editan VIDEOS, LOGO, colores y FUENTE.
Por tarjeta: arriba (pared), bajo (bajo el subtítulo, sobre el torso) o abajo (sobre el subtítulo), con tiempos fijos en
los cortes de escena (ffmpeg select=gt(scene,0.25)). Por video: etiqueta, corte_voz (corta lo que Wan añade y conserva la
cola congelada) y acercar (acerca el cuadro desde arriba en un tramo para sacar un defecto del borde de abajo).

Necesita: tomas/<v>_t1.mp4, revision/<v>_t1/<v>_t1.json (mlx_whisper --word-timestamps True --output-format json),
Pillow, ffmpeg y `npx hyperframes`.

  python3 -I scripts/montar_explicativo.py t1      → montaje/t1/ (index.html, compositions/, assets/)
"""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PROYECTO = Path(__file__).resolve().parent.parent
LOGO = Path("assets/logo-marca.png")   # el logo de tu marca (cuadrado, por ejemplo 1080×1080)
ROSA, TURQUESA = "#E07A9A", "#2BB3B1"   # colores de ejemplo: pon los de tu marca
ANCHO, ALTO = 1080, 1920
CIERRE_S = 2.8          # duración de la tarjeta de cierre con el logo
CONGELAR_S = 2.6        # cola de último cuadro que se añade a las tomas de 30 s para que quepa el cierre
FUENTE = ""
ETIQUETA = "TIRZEPATIDA"
MAX_PALABRAS = 5

DESTACAR = {"glp-1", "gip", "tirzepatida", "retatrutida", "surmount-1", "surmount-4", "placebo", "mitad", "apnea",
            "hígado", "grasa", "músculo", "proteína", "fuerza", "náuseas", "rodilla", "médico", "dolor", "glucagón"}


@dataclass(frozen=True)
class Tarjeta:
    ancla: str          # palabras (normalizadas) donde aparece la tarjeta
    cuerpo: str         # HTML interno ya escapado
    fin_ancla: str | None = None   # si no, dura hasta la siguiente tarjeta o el cierre
    arriba: bool = False   # en un video real, subirla cuando la cara del plano está a media altura
    inicio_t: float | None = None   # tiempos fijos (corte de escena) en lugar del ancla
    fin_t: float | None = None
    bajo: bool = False   # debajo del subtítulo (torso): cuando la cara del plano ocupa el centro del cuadro


@dataclass(frozen=True)
class Video:
    titulo: str
    tarjetas: tuple[Tarjeta, ...]
    corte_voz: float | None = None   # p. ej. cortar la última frase
    duracion_v1: float | None = None
    fuente: bool = True
    ignorar_desde: float | None = None   # palabras que Whisper inventa sobre el silencio final («¡Gracias!»)
    fuente_texto: str = ""   # vacío: FUENTE
    tarjeta_abajo: bool = False   # videos reales: la tarjeta se apoya sobre el subtítulo para no tapar caras
    etiqueta: str = ETIQUETA   # la píldora del título: el medicamento del video
    acercar: tuple[tuple[float, float, float], ...] = ()   # (desde, hasta, factor): acerca el cuadro desde arriba


def pegar(texto: str) -> str:
    """Escapa y une cada cifra con su unidad («12 mg», «30 %») para que no se partan en dos líneas."""
    return re.sub(r"(\d) (mg|%|semanas)", "\\1\u00a0\\2", html.escape(texto))


def dato(cifra: str, texto: str, comparacion: str = "") -> str:
    comp = f'<div class="comp">{pegar(comparacion)}</div>' if comparacion else ""
    return f'<div class="cifra">{pegar(cifra)}</div><div class="texto">{pegar(texto)}</div>{comp}'


def chips(*pares: tuple[str, str], pie: str) -> str:
    c = "".join(f'<span class="chip" style="background:{color}">{html.escape(t)}</span>' for t, color in pares)
    return f'<div class="chips">{c}</div><div class="texto">{html.escape(pie)}</div>'


# Cifras verificadas el 30-oct-2026 con su cita textual (PLAN.md). Las anclas se ajustan a la transcripción de cada toma.
VIDEOS = {
    "t7": Video("Apnea del sueño", (
        Tarjeta("en dos estudios", dato("469", "adultos · 52 semanas", "obesidad y apnea moderada a grave")),
        Tarjeta("redujo las pausas", dato("−25,3", "pausas respiratorias por hora (estudio 1)",
                                          "estudio 2: −29,3 · placebo: −5,3 y −5,5"), fin_ancla="desde diciembre"),
        Tarjeta("desde diciembre", chips(("FDA · dic. 2024", TURQUESA), pie="apnea moderada a grave con obesidad, en EE. UU."),
                fin_ancla="si roncas"),
    ), fuente_texto="Fuentes: SURMOUNT-OSA (NEJM 2024) · FDA, 20-dic-2024"),
    "r5": Video("Hígado graso", (
        Tarjeta("en un estudio pequeño", dato("98", "adultos · fase 2a", "obesidad e hígado graso")),
        Tarjeta("bajó más de", dato("−82,4 %", "grasa del hígado a las 24 semanas (12 mg)", "8 mg: −81,4 % · placebo: +0,3 %")),
        Tarjeta("de cada 10", dato("86 %", "llegó a grasa hepática normal (12 mg)", "8 mg: 79 % · placebo: 0 %"),
                fin_ancla="son resultados"),
    ), fuente_texto="Fuente: Sanyal et al., Nature Medicine 2024", etiqueta="RETATRUTIDA"),
    "r6": Video("Rodillas y artrosis", (
        Tarjeta("en un estudio de fase", dato("445", "adultos · 68 semanas", "sobrepeso u obesidad y artrosis de rodilla")),
        Tarjeta("quienes siguieron", dato("−28,7 %", "peso con 12 mg, quienes siguieron el tratamiento",
                                          "placebo: −2,1 % · contando a todos: −23,7 %"), fin_ancla="y su dolor", bajo=True),
        # cortes de la toma: 12,93 calle · 20,57 consulta · 27,33 descanso de la escalera
        Tarjeta("y su dolor", dato("−4,5", "puntos de dolor de rodilla (WOMAC, 9 mg)", "12 mg: −4,4 · placebo: −2,4"), bajo=True,
                fin_t=20.5),
        Tarjeta("y su dolor", dato("−4,5", "puntos de dolor de rodilla (WOMAC, 9 mg)", "12 mg: −4,4 · placebo: −2,4"), arriba=True,
                inicio_t=20.6),
        Tarjeta("hasta 18", dato("18,2 %", "lo dejó por efectos adversos (12 mg)", "9 mg: 12,2 % · placebo: 4,0 %"),
                arriba=True, fin_t=27.28),
    ), tarjeta_abajo=True, fuente_texto="Fuente: Lilly, TRIUMPH-4 (comunicado, 11-dic-2025)", etiqueta="RETATRUTIDA",
       # Wan añadió «ser un costo» tras «Lilly» (29,22–30,0 s, −17,4 dB en banda de voz); silencio en 29,26–29,56
       corte_voz=29.3, ignorar_desde=29.22),
    # toma 2 (con zapatos pedidos): cortes 4,27 cocina · 13,97 sala · 23,07 consulta · 27,57 calle. Wan lo dejó descalzo
    # en la sala y en la consulta: se acerca el cuadro desde arriba (12 y 15 %) para sacar los pies
    "t6": Video("No todo es grasa", (
        Tarjeta("en un subestudio", dato("160", "personas medidas con DXA · 72 semanas", "subestudio de SURMOUNT-1")),
        Tarjeta("tres cuartas partes", dato("≈ 75 %", "del peso perdido fue grasa", "≈ 25 % masa magra"), fin_t=13.9),
        Tarjeta("con placebo", chips(("Igual con placebo", TURQUESA), pie="la proporción fue la misma"), bajo=True, fin_t=17.4),
        Tarjeta("cuatro sociedades", chips(("Proteína", TURQUESA), ("Fuerza", "#E8A23A"), pie="recomiendan 4 sociedades científicas"),
                bajo=True, fin_t=23.0),
        Tarjeta("cuatro sociedades", chips(("Proteína", TURQUESA), ("Fuerza", "#E8A23A"), pie="recomiendan 4 sociedades científicas"),
                arriba=True, inicio_t=23.1, fin_t=27.4),
    ), tarjeta_abajo=True, fuente_texto="Fuentes: Look et al., Diabetes Obes Metab 2025 · ACLM, ASN, OMA y TOS, 2025",
       acercar=((13.97, 23.07, 1.12), (23.07, 27.57, 1.15), (27.57, 31.0, 1.12))),
    "t5": Video("¿Y si lo dejo?", (
        Tarjeta("surmount-4", dato("670", "adultos · 88 semanas", "SURMOUNT-4")),
        # en la calle (13–19 s) su cara queda a la altura de la tarjeta normal: va bajo el subtítulo
        Tarjeta("primero", dato("−20,9 %", "de peso en 36 semanas", "todos con tirzepatida"), bajo=True),
        Tarjeta("quienes la dejaron", dato("+14,0 %", "de peso con placebo (semana 36 a 88)", "quienes siguieron: −5,5 %")),
        # consulta (desde 25,0 s): las dos caras a media altura, la tarjeta sube a la pared
        Tarjeta("cualquier cambio", dato("−25,3 %", "desde el inicio, quienes siguieron", "quienes la dejaron: −9,9 %"), arriba=True),
    ), tarjeta_abajo=True, fuente_texto="Fuente: SURMOUNT-4 (JAMA 2024)"),
}


def norm(w: str) -> str:
    return re.sub(r"[^\wáéíóúñü%-]", "", w.lower())


def palabras(v: str, limite: float | None) -> list[dict]:
    d = json.loads((PROYECTO / f"revision/{v}_t1/{v}_t1.json").read_text())
    ws: list[dict] = []
    for s in d["segments"]:
        for w in s.get("words", []):
            if limite is not None and w["start"] >= limite or not w["word"].strip():
                continue
            if ws and not w["word"].startswith(" "):   # pieza pegada a la anterior («GLP» + «-1»)
                ws[-1] = {**ws[-1], "t": ws[-1]["t"] + w["word"].strip(), "e": w["end"]}
            else:
                ws.append({"t": w["word"].strip(), "s": w["start"], "e": w["end"]})
    fusion: list[dict] = []
    for w in ws:   # «Triumph uno» → «TRIUMPH-1»
        if fusion and norm(fusion[-1]["t"]) == "triumph" and norm(w["t"]) in ("uno", "1"):
            fusion[-1] = {"t": "TRIUMPH-1" + w["t"].lstrip("uno1"), "s": fusion[-1]["s"], "e": w["e"]}
        elif fusion and norm(fusion[-1]["t"]) == "surmount" and norm(w["t"]) in ("uno", "1", "cuatro", "4", "cinco", "5"):
            n = {"uno": "1", "cuatro": "4", "cinco": "5"}.get(norm(w["t"]), norm(w["t"]))
            fusion[-1] = {"t": f"SURMOUNT-{n}" + re.sub(r"^\w+", "", w["t"]), "s": fusion[-1]["s"], "e": w["e"]}
        elif norm(w["t"]) == "triunfuno":   # así transcribe Whisper «Triumph uno» dicho de corrido
            fusion.append({**w, "t": "TRIUMPH-1" + w["t"][len("Triunfuno"):]})
        elif fusion and norm(fusion[-1]["t"]) == "reta" and norm(w["t"]) == "trutida":   # Whisper parte la palabra
            fusion[-1] = {"t": fusion[-1]["t"] + w["t"], "s": fusion[-1]["s"], "e": w["e"]}
        else:
            fusion.append(w)
    fusion = [{**w, "t": re.sub(r"(\d)%", "\\1\u00a0%", w["t"].replace("Triumph", "TRIUMPH"))} for w in fusion]
    # «promedia»: Whisper (o Wan) concordó en femenino; el guion dice «pérdida promedio»
    fusion = [{**w, "t": re.sub(r"^promedia\b", "promedio", w["t"])} for w in fusion]
    # serie 3: Whisper (tres modelos) oye «modeada» y «doces»; el subtítulo dice lo que dice el guion
    fusion = [{**w, "t": re.sub(r"^modeada\b", "moderada", re.sub(r"^doces\b", "dosis", w["t"]))} for w in fusion]
    fusion = [{**w, "t": re.sub(r"^Lili\b", "Lilly", w["t"])} for w in fusion]
    fusion = [{**w, "t": re.sub(r"(?i)tirsepatida", lambda m: "T" + "irzepatida" if m.group(0)[0] == "T" else "tirzepatida", w["t"])} for w in fusion]
    if fusion:   # Whisper a veces deja en minúscula la primera palabra
        fusion[0] = {**fusion[0], "t": fusion[0]["t"][:1].upper() + fusion[0]["t"][1:]}
    return fusion


def buscar(ws: list[dict], frase: str) -> int:
    objetivo = [norm(x) for x in frase.split()]
    for i in range(len(ws) - len(objetivo) + 1):
        if [norm(w["t"]) for w in ws[i:i + len(objetivo)]] == objetivo:
            return i
    sys.exit(f"No encontré «{frase}» en la transcripción")


def grupos(ws: list[dict]) -> list[list[dict]]:
    out, actual = [], []
    for i, w in enumerate(ws):
        actual.append(w)
        pausa = i + 1 < len(ws) and ws[i + 1]["s"] - w["e"] >= 0.15
        if len(actual) >= MAX_PALABRAS or re.search(r"[.:;?!]$", w["t"]) or (re.search(r",$", w["t"]) and len(actual) >= 2) or pausa:
            out.append(actual); actual = []
    out += [actual] if actual else []
    pegados: list[list[dict]] = []
    for g in out:   # una palabra sola que cierra la frase se pega al grupo anterior
        if len(g) == 1 and pegados and not re.search(r"[.:;?!]$", pegados[-1][-1]["t"]) and g[0]["s"] - pegados[-1][-1]["e"] < 0.3:
            pegados[-1] = pegados[-1] + g
        else:
            pegados.append(g)
    return pegados


def preparar_toma(v: str, cfg: Video, destino: Path) -> float:
    toma = PROYECTO / f"tomas/{v}_t1.mp4"
    if cfg.corte_voz is not None and cfg.duracion_v1 is None:
        # serie 3: se corta la voz (Wan añadió palabras) pero se conserva la cola congelada para el cierre
        dur_toma = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(toma)],
                                        capture_output=True, text=True, check=True).stdout)
        dur = round(dur_toma + CONGELAR_S, 2)
        args = ["-vf", f"tpad=stop_mode=clone:stop_duration={CONGELAR_S}", "-af", f"afade=t=out:st={cfg.corte_voz}:d=0.15,apad",
                "-t", str(dur)]
    elif cfg.corte_voz is not None:
        filtro_a = f"afade=t=out:st={cfg.corte_voz}:d=0.35"
        args = ["-t", str(cfg.duracion_v1), "-af", filtro_a]
        dur = cfg.duracion_v1
    else:
        dur_toma = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(toma)],
                                        capture_output=True, text=True, check=True).stdout)
        filtro_v = f"tpad=stop_mode=clone:stop_duration={CONGELAR_S}"
        for n, (desde, hasta, f) in enumerate(cfg.acercar):   # p. ej. sacar del cuadro un defecto en el borde de abajo
            filtro_v = (f"split[base{n}][z{n}];[z{n}]crop=iw/{f}:ih/{f}:(iw-iw/{f})/2:0,scale=iw*{f}:ih*{f}[zz{n}];"
                        f"[base{n}][zz{n}]overlay=0:0:enable='between(t,{desde},{hasta})'," + filtro_v)
        args = ["-filter_complex", f"[0:v]{filtro_v}[v]", "-map", "[v]", "-map", "0:a",
                "-af", f"afade=t=out:st={dur_toma - 0.4}:d=0.4,apad"]
        dur = round(dur_toma + CONGELAR_S, 2)
        args += ["-t", str(dur)]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(toma), *args, "-c:v", "libx264", "-crf", "16", "-g", "30",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(destino)], check=True)
    return dur


CSS_COMUN = f"""
  #root {{ position: absolute; inset: 0; font-family: Montserrat, sans-serif; }}
"""


def html_subtitulos(gs: list[list[dict]]) -> str:
    bloques, js = [], []
    for n, g in enumerate(gs):
        ini, fin = max(0.1, g[0]["s"] - 0.05), g[-1]["e"] + 0.12
        if n + 1 < len(gs):   # que dos grupos seguidos no se vean a la vez (aviso de HyperFrames, 30-oct)
            fin = min(fin, max(0.1, gs[n + 1][0]["s"] - 0.05) - 0.02)
        texto = " ".join(
            f'<span class="hl">{html.escape(w["t"].rstrip(".,;:"))}</span>' if norm(w["t"]).rstrip("-") in DESTACAR or norm(w["t"]) in DESTACAR or re.search(r"\d", w["t"])
            else html.escape(w["t"].rstrip(".,;:")) for w in g)
        bloques.append(f'    <div id="cap-{n}" class="clip cap" data-start="{ini:.2f}" data-duration="{fin - ini:.2f}">'
                       f'<span id="cap-{n}-in" class="cap-in">{texto}</span></div>')
        js.append(f'    tl.fromTo("#cap-{n}-in", {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: 0.14, ease: "power2.out"}}, {ini:.2f});')
    return f"""<template>
  <style>{CSS_COMUN}
    .cap {{ position: absolute; left: 0; right: 0; top: 1130px; text-align: center; overflow: visible; }}
    .cap-in {{ display: inline-block; max-width: 900px; padding: 14px 28px; border-radius: 22px; background: rgba(6, 12, 28, 0.62);
              color: #fff; font-weight: 800; font-size: 60px; line-height: 1.15; letter-spacing: -0.5px; }}
    .hl {{ color: {ROSA}; }}
  </style>
  <div id="root" data-composition-id="subtitulos" data-width="{ANCHO}" data-height="{ALTO}">
{chr(10).join(bloques)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    window.__timelines["subtitulos"] = tl;
  </script>
</template>
"""


def html_tarjetas(cfg: Video, ws: list[dict], dur: float) -> str:
    cierre = dur - CIERRE_S
    tiempos = []
    for t in cfg.tarjetas:
        ini = t.inicio_t if t.inicio_t is not None else ws[buscar(ws, t.ancla)]["s"] - 0.1
        tiempos.append((t, ini))
    elems, js = [], []
    titulo_fin = min(2.6, tiempos[0][1] - 0.2) if tiempos else 2.6
    elems.append(f'    <div id="titulo" class="clip" data-start="0" data-duration="{titulo_fin:.2f}"><div id="titulo-in" class="titulo-in">'
                 f'<span class="eyebrow">{cfg.etiqueta}</span><h1>{html.escape(cfg.titulo)}</h1></div></div>')
    js.append('    tl.fromTo("#titulo-in", {opacity: 1, y: 0}, {opacity: 0, y: -16, duration: 0.3, ease: "power2.in"}, '
              f'{titulo_fin - 0.32:.2f});')
    for n, (t, ini) in enumerate(tiempos):
        if t.fin_t is not None:
            fin = t.fin_t
        elif t.fin_ancla:
            fin = ws[buscar(ws, t.fin_ancla)]["s"] - 0.15
        elif n + 1 < len(tiempos):
            fin = tiempos[n + 1][1] - 0.15
        else:
            fin = cierre - 0.1
        lugar = "bajo" if t.bajo else "arriba" if t.arriba or not cfg.tarjeta_abajo else "abajo"
        elems.append(f'    <div id="tj-{n}" class="clip tj {lugar}" data-start="{ini:.2f}" data-duration="{fin - ini:.2f}">'
                     f'<div id="tj-{n}-in" class="tj-in">{t.cuerpo}</div></div>')
        js.append(f'    tl.fromTo("#tj-{n}-in", {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: 0.4, ease: "power2.out"}}, {ini:.2f});')
        js.append(f'    tl.to("#tj-{n}-in", {{opacity: 0, duration: 0.3, ease: "power2.in"}}, {fin - 0.32:.2f});')
    fuente_txt = html.escape(cfg.fuente_texto or FUENTE).replace("NEJM ", "NEJM\u00a0")
    fuente = f'<p class="fuente">{fuente_txt}</p>' if cfg.fuente else ""
    elems.append(f'    <div id="cierre" class="clip" data-start="{cierre:.2f}" data-duration="{CIERRE_S:.2f}"><div id="cierre-in" class="cierre-in">'
                 f'<div class="logo-caja"><img id="logo" src="assets/logo.png" alt="Logo de la marca"></div>'
                 f'<p class="edu">Contenido educativo</p>{fuente}</div></div>')
    js.append(f'    tl.fromTo("#cierre-in", {{opacity: 0, scale: 0.96}}, {{opacity: 1, scale: 1, duration: 0.45, ease: "power2.out"}}, {cierre:.2f});')
    return f"""<template>
  <style>{CSS_COMUN}
    #titulo, .tj, #cierre {{ position: absolute; left: 0; right: 0; }}
    #titulo {{ top: 250px; text-align: center; }}
    .titulo-in {{ display: inline-block; max-width: 920px; }}
    .eyebrow {{ display: inline-block; padding: 8px 22px; border-radius: 999px; background: {TURQUESA}; color: #04212a;
               font-weight: 800; font-size: 30px; letter-spacing: 4px; }}
    h1 {{ margin: 22px 0 0; color: #fff; font-weight: 800; font-size: 88px; line-height: 1.05; letter-spacing: -1.5px;
         text-shadow: 0 6px 30px rgba(0,0,0,.55); }}
    .tj {{ text-align: center; }}
    .tj.arriba {{ top: 300px; }}
    .tj.abajo {{ bottom: 810px; }}
    .tj.bajo {{ top: 1290px; }}
    .tj.abajo .tj-in, .tj.bajo .tj-in {{ padding: 24px 36px; }}
    .tj.bajo .cifra {{ font-size: 120px; }}
    .tj.bajo .texto {{ font-size: 40px; }}
    .tj.abajo .cifra {{ font-size: 120px; }}
    .tj.abajo .texto {{ font-size: 40px; }}
    .tj-in {{ display: inline-block; min-width: 560px; max-width: 900px; padding: 34px 44px; border-radius: 34px;
             background: rgba(8, 16, 34, 0.74); border: 2px solid rgba(255,255,255,.12); color: #fff; }}
    .cifra {{ font-weight: 800; font-size: 150px; line-height: 1; color: {ROSA}; letter-spacing: -3px; }}
    .texto {{ margin-top: 12px; font-weight: 700; font-size: 44px; line-height: 1.2; }}
    .comp {{ margin-top: 14px; font-weight: 600; font-size: 36px; color: {TURQUESA}; }}
    .chips {{ display: flex; gap: 18px; justify-content: center; flex-wrap: wrap; }}
    .chip {{ padding: 12px 28px; border-radius: 999px; color: #08121f; font-weight: 800; font-size: 44px; }}
    #cierre {{ top: 0; bottom: 0; display: flex; align-items: center; justify-content: center; }}
    .cierre-in {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;
                 padding: 0 70px; text-align: center; background: rgba(4, 10, 24, 0.55); }}
    .logo-caja {{ display: inline-block; padding: 40px 50px; border-radius: 36px; background: #fff; }}
    #logo {{ display: block; width: 560px; height: auto; }}
    .edu {{ margin: 34px 0 0; color: #fff; font-weight: 700; font-size: 40px; text-shadow: 0 4px 18px rgba(0,0,0,.6); }}
    .fuente {{ margin: 14px auto 0; max-width: 900px; color: rgba(255,255,255,.9); font-weight: 500; font-size: 28px; line-height: 1.3;
              text-shadow: 0 4px 18px rgba(0,0,0,.6); }}
  </style>
  <div id="root" data-composition-id="tarjetas" data-width="{ANCHO}" data-height="{ALTO}">
{chr(10).join(elems)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    window.__timelines["tarjetas"] = tl;
  </script>
</template>
"""


def html_raiz(dur: float, cierre: float) -> str:  # cierre: fin de los subtítulos
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={ANCHO}, height={ALTO}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {ANCHO}px; height: {ALTO}px; overflow: hidden; background: #000; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.2f}" data-width="{ANCHO}" data-height="{ALTO}">
      <video id="toma" class="clip" src="assets/toma.mp4" data-start="0" data-duration="{dur:.2f}" data-track-index="0"
             data-has-audio="true" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:0"></video>
      <div id="subtitulos" data-composition-id="subtitulos" data-composition-src="compositions/subtitulos.html" data-start="0"
           data-duration="{cierre:.2f}" data-track-index="2" data-track-kind="captions" data-width="{ANCHO}" data-height="{ALTO}" style="z-index:3"></div>
      <div id="tarjetas" data-composition-id="tarjetas" data-composition-src="compositions/tarjetas.html" data-start="0"
           data-duration="{dur:.2f}" data-track-index="3" data-track-kind="graphics" data-width="{ANCHO}" data-height="{ALTO}" style="z-index:2"></div>
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""


def recortar_logo(destino: Path, margen: int = 30) -> None:
    """El logo vertical viene centrado en 1080×1080 con mucho blanco: se recorta a su contenido."""
    from PIL import Image, ImageChops
    im = Image.open(LOGO).convert("RGB")
    caja = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if caja is None:
        sys.exit("El logo está en blanco")
    x0, y0, x1, y1 = caja
    im.crop((max(0, x0 - margen), max(0, y0 - margen), min(im.width, x1 + margen), min(im.height, y1 + margen))).save(destino)


def main() -> None:
    v = sys.argv[1]
    cfg = VIDEOS[v]
    destino = PROYECTO / "montaje" / v
    (destino / "assets").mkdir(parents=True, exist_ok=True)
    (destino / "compositions").mkdir(exist_ok=True)
    recortar_logo(destino / "assets/logo.png")
    dur = preparar_toma(v, cfg, destino / "assets/toma.mp4")
    cierre = round(dur - CIERRE_S, 2)
    limites = [x for x in (cfg.corte_voz, cfg.ignorar_desde) if x is not None]
    ws = palabras(v, min(limites) if limites else None)
    (destino / "compositions/subtitulos.html").write_text(html_subtitulos(grupos(ws)))
    (destino / "compositions/tarjetas.html").write_text(html_tarjetas(cfg, ws, dur))
    (destino / "index.html").write_text(html_raiz(dur, cierre))
    print(f"{v}: {dur} s, {len(grupos(ws))} grupos de subtítulos, {len(cfg.tarjetas)} tarjetas → {destino}")


if __name__ == "__main__":
    main()
