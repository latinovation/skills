"""Arma el proyecto HyperFrames del piloto en collage: imágenes de collage + tramos 3D de la toma de Wan + voz de Wan +
subtítulo de una palabra (tiempos de Whisper) + neón, tiras, barras y cierre.
Estilo `collage` (referencias/estilos/collage.md). PLANTILLA: es el script de un piloto real; se copia a <proyecto>/scripts/ y se editan VIDEOS, CORTE_VOZ, ENCIMA_HTML/js_encima, colores, LOGO y FUENTE.

Necesita: tomas/<v>_t1.mp4, img/<nombre>.png, revision/<v>_t1/<v>_t1.json (mlx_whisper --word-timestamps True
--output-format json), Pillow, ffmpeg y `npx hyperframes`.

  python3 -I scripts/montar_collage.py c1      → montaje/c1/ (index.html, compositions/, assets/)

Cada plano empieza donde la narración dice su frase (ancla) y dura hasta el siguiente. Cifras del ejemplo: SURMOUNT-1.
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
FONDO, ROSA, TURQUESA, TINTA = "#1F4E5A", "#E07A9A", "#2BB3B1", "#14303A"   # colores de ejemplo: pon los de tu marca
ANCHO, ALTO = 1080, 1920
CIERRE_S = 2.8          # duración de la tarjeta de cierre con el logo
DESTELLO_S = 0.16       # destello entre planos, como en el formato de referencia
FUENTE = "Fuentes: NEJM 2022 y 2023 · TRIUMPH-5 (NCT06662383)"

DESTACAR = {"glp-1", "gip", "tirzepatida", "retatrutida", "glucagón", "tres", "dos", "tercero", "cuidado", "curso",
            "médico", "mejor"}


@dataclass(frozen=True)
class Plano:
    id: str
    ancla: str                       # frase de la narración donde empieza el plano ("" = segundo 0)
    tipo: str                        # img | tiras | wan
    fuente: str = ""                 # img/tiras: nombre en img/; wan: vacío
    media_start: float = 0.0         # wan: segundo de la toma que se muestra al empezar el plano
    encima: str = ""                 # interrogantes | senal | neon_hormonas | etiqueta_estudio | barras
    destello: bool = False           # destello al entrar
    caja: bool = False               # fondo claro bajo los subtítulos: la palabra lleva caja oscura


VIDEOS = {
    # Ejemplo: sin imágenes nuevas; el gancho y «estudios distintos» van con escenas 3D de la toma
    "r7": (
        Plano("p1", "", "wan", media_start=0.0, encima="interrogantes"),
        Plano("p2", "la tirzepatida activa", "wan", media_start=3.3, encima="neon_hormonas", destello=True, caja=True),
        Plano("p3", "la retatrutida suma", "wan", media_start=9.0, encima="neon_glucagon", destello=True),
        Plano("p4", "suena a más", "wan", media_start=1.5, encima="senal", destello=True),
        Plano("p5", "comparar cifras", "wan", media_start=13.0, destello=True),
        Plano("p6", "porque cambian", "img", "r7_reloj", destello=True),
        Plano("p7", "el estudio que", "img", "r7_carrera", encima="etiqueta_estudio", destello=True),
        Plano("p8", "hasta entonces", "img", "r7_medico", destello=True),
    ),
    "c1": (
        Plano("p1", "", "img", "p1_retrato", encima="interrogantes"),
        Plano("p2", "falta de voluntad", "tiras", "p1_retrato", encima="senal", destello=True),
        Plano("p3", "el hambre se regula", "img", "p3_cerebro_estomago", destello=True),
        # superficie celular rosada bajo el subtítulo: «GIP» en rosa no se leía (captura a 10,9 s)
        Plano("p4", "la tirzepatida imita", "wan", media_start=6.0, encima="neon_hormonas", destello=True, caja=True),
        Plano("p5", "las dos señales", "wan", media_start=12.0),
        Plano("p6", "y bajan el apetito", "img", "p6_plato", destello=True),
        Plano("p7", "en surmount-1", "img", "p7_participantes", encima="etiqueta_estudio", destello=True),
        Plano("p8", "perdieron", "img", "p8_papel_datos", encima="barras", caja=True),
        Plano("p9", "siempre con fórmula", "img", "p9_medico", destello=True),
    ),
}
# fin de la última palabra del guion: después, Whisper oye «El tiempo de fórmula…» en 0,1 s y la cola suena a −17,5 dB en la
# banda de voz (la música sola, −37 dB). Como no se puede descartar que Wan añadiera palabras, la voz se corta ahí.
CORTE_VOZ = {"c1": 29.2, "r7": 29.2}   # r7: la voz termina en 28,8 s; la cola es música (−42,7 dB en banda de voz)


def norm(w: str) -> str:
    return re.sub(r"[^\wáéíóúñü%-]", "", w.lower())


def palabras(v: str, limite: float) -> list[dict]:
    d = json.loads((PROYECTO / f"revision/{v}_t1/{v}_t1.json").read_text())
    ws: list[dict] = []
    for s in d["segments"]:
        for w in s.get("words", []):
            if w["start"] >= limite or not w["word"].strip():
                continue
            if ws and not w["word"].startswith(" "):   # pieza pegada a la anterior («GLP» + «-1»)
                ws[-1] = {**ws[-1], "t": ws[-1]["t"] + w["word"].strip(), "e": w["end"]}
            else:
                ws.append({"t": w["word"].strip(), "s": w["start"], "e": w["end"]})
    fusion: list[dict] = []
    for w in ws:   # «Surmount uno» → «SURMOUNT-1»
        if fusion and norm(fusion[-1]["t"]) == "surmount" and norm(w["t"]) in ("uno", "1"):
            fusion[-1] = {"t": "SURMOUNT-1" + re.sub(r"^\w+", "", w["t"]), "s": fusion[-1]["s"], "e": w["e"]}
        else:
            fusion.append(w)
    fusion = [{**w, "t": re.sub(r"(\d)%", "\\1\u00a0%", w["t"])} for w in fusion]
    fusion = [{**w, "t": re.sub(r"(?i)tirsepatida", lambda m: "T" + "irzepatida" if m.group(0)[0] == "T" else "tirzepatida", w["t"])} for w in fusion]
    return fusion


def buscar(ws: list[dict], frase: str) -> int:
    objetivo = [norm(x) for x in frase.split()]
    for i in range(len(ws) - len(objetivo) + 1):
        if [norm(w["t"]) for w in ws[i:i + len(objetivo)]] == objetivo:
            return i
    sys.exit(f"No encontré «{frase}» en la transcripción")


def tiempos(planos: tuple[Plano, ...], ws: list[dict], cierre: float) -> list[tuple[Plano, float, float]]:
    inicios = [0.0 if not p.ancla else round(ws[buscar(ws, p.ancla)]["s"] - 0.06, 2) for p in planos]
    if inicios != sorted(inicios):
        sys.exit(f"Los planos no quedan en orden: {inicios}")
    fines = inicios[1:] + [cierre]
    return [(p, i, f) for p, i, f in zip(planos, inicios, fines)]


# ---------- lo que va encima de cada plano (vectores y texto: nada de esto lo genera un modelo) ----------

def svg_interrogante(n: int, x: int, y: int, giro: int, escala: float) -> str:
    return (f'<svg id="q{n}" class="q" style="left:{x}px;top:{y}px;transform:rotate({giro}deg) scale({escala})" width="120" height="180" '
            f'viewBox="0 0 120 180"><path id="q{n}-t" d="M24 52 C24 14 96 10 96 52 C96 80 60 84 60 116" fill="none" stroke="#fff" '
            f'stroke-width="12" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" opacity="0"/>'
            f'<circle id="q{n}-p" cx="60" cy="152" r="8" fill="#fff" opacity="0"/></svg>')


ENCIMA_HTML = {
    "interrogantes": "".join(svg_interrogante(n, x, y, g, e) for n, (x, y, g, e) in
                             enumerate([(120, 330, -14, 1.0), (840, 270, 12, 0.85), (880, 760, 8, 0.7), (70, 820, -8, 0.6)])),
    "senal": ('<svg id="senal" class="senal" width="420" height="320" viewBox="0 0 420 320">'
              + "".join(f'<path id="arco{n}" d="M{210 - r} 260 A{r} {r} 0 0 1 {210 + r} 260" fill="none" stroke="{ROSA}" '
                        f'stroke-width="14" stroke-linecap="round" opacity="0"/>' for n, r in enumerate((60, 120, 180)))
              + f'<circle id="arco-c" cx="210" cy="260" r="16" fill="{ROSA}" opacity="0"/></svg>'),
    # mismo color que la molécula que queda debajo en la toma de Wan: rosa a la izquierda, turquesa a la derecha
    "neon_hormonas": (f'<div class="neon-fila"><span id="neon-glp" class="neon" style="--c:{ROSA}">GLP-1</span>'
                      f'<span id="neon-gip" class="neon" style="--c:{TURQUESA}">GIP</span></div>'),
    "etiqueta_estudio": '<div class="etiqueta"><span id="etq-in" class="etq">TRIUMPH-5 · en curso</span></div>',
    "neon_glucagon": f'<div class="neon-fila"><span id="neon-glu" class="neon" style="--c:#E8C26A">GLUCAGÓN</span></div>',
    "barras": ('<div id="datos" class="datos"><div class="dt-cab">72 semanas</div><div class="dt-cols">'
               '<div class="dt-col"><div id="bar-a" class="dt-barra" style="height:560px;background:#E66F8C"></div>'
               '<div id="num-a" class="dt-num">−20,9\u00a0%<div class="dt-lab">Tirzepatida<br>dosis más alta</div></div></div>'
               '<div class="dt-col"><div id="bar-b" class="dt-barra" style="height:83px;background:#8C9A9C"></div>'
               '<div id="num-b" class="dt-num">−3,1\u00a0%<div class="dt-lab">Placebo</div></div></div></div></div>'),
}


def js_encima(clave: str, ini: float, fin: float, ws: list[dict]) -> list[str]:
    if clave == "interrogantes":
        out = []
        for n in range(4):
            t = ini + 0.15 + n * 0.22
            out.append(f'    tl.set("#q{n}-t", {{opacity: 1}}, {t:.2f});')   # oculto hasta trazarse: la punta redonda dejaba un punto
            out.append(f'    tl.fromTo("#q{n}-t", {{strokeDashoffset: 1}}, {{strokeDashoffset: 0, duration: 0.35, ease: "power2.out"}}, {t:.2f});')
            out.append(f'    tl.fromTo("#q{n}-p", {{opacity: 0}}, {{opacity: 1, duration: 0.08}}, {t + 0.35:.2f});')
        return out
    if clave == "senal":
        out = [f'    tl.fromTo("#arco-c", {{opacity: 0}}, {{opacity: 1, duration: 0.08}}, {ini + 0.05:.2f});']
        for ciclo in range(int((fin - ini) // 0.9) + 1):
            for n in range(3):
                t = ini + 0.1 + ciclo * 0.9 + n * 0.16
                if t + 0.3 < fin:
                    base = "" if ciclo == 0 else ", immediateRender: false"
                    out.append(f'    tl.fromTo("#arco{n}", {{opacity: 0.15}}, {{opacity: 1, duration: 0.12, ease: "none"{base}}}, {t:.2f});')
        return out
    if clave == "neon_hormonas":
        return [f'    tl.fromTo("#neon-glp", {{opacity: 0}}, {{opacity: 1, duration: 0.05, repeat: 3, yoyo: true}}, {ini + 0.9:.2f});',
                f'    tl.set("#neon-glp", {{opacity: 1}}, {ini + 1.15:.2f});',
                f'    tl.fromTo("#neon-gip", {{opacity: 0}}, {{opacity: 1, duration: 0.05, repeat: 3, yoyo: true}}, {ini + 1.6:.2f});',
                f'    tl.set("#neon-gip", {{opacity: 1}}, {ini + 1.85:.2f});']
    if clave == "neon_glucagon":
        return [f'    tl.fromTo("#neon-glu", {{opacity: 0}}, {{opacity: 1, duration: 0.05, repeat: 3, yoyo: true}}, {ini + 0.9:.2f});',
                f'    tl.set("#neon-glu", {{opacity: 1}}, {ini + 1.15:.2f});']
    if clave == "etiqueta_estudio":
        return [f'    tl.fromTo("#etq-in", {{opacity: 0, y: -20}}, {{opacity: 1, y: 0, duration: 0.3, ease: "power3.out"}}, {ini + 0.15:.2f});']
    if clave == "barras":   # cada barra crece cuando la voz dice su cifra
        t_a = ws[buscar(ws, "21%")]["s"]
        t_b = ws[buscar(ws, "placebo")]["s"]
        return [f'    tl.fromTo("#datos", {{opacity: 0}}, {{opacity: 1, duration: 0.2}}, {ini + 0.1:.2f});',
                f'    tl.fromTo("#bar-a", {{scaleY: 0}}, {{scaleY: 1, duration: 1.1, ease: "power2.out"}}, {t_a - 0.6:.2f});',
                f'    tl.fromTo("#num-a", {{opacity: 0}}, {{opacity: 1, duration: 0.25}}, {t_a:.2f});',
                f'    tl.fromTo("#bar-b", {{scaleY: 0}}, {{scaleY: 1, duration: 0.5, ease: "power2.out"}}, {t_b:.2f});',
                f'    tl.fromTo("#num-b", {{opacity: 0}}, {{opacity: 1, duration: 0.25}}, {t_b + 0.4:.2f});']
    return []


TIRAS = 6


def html_plano(p: Plano, ini: float, fin: float, ws: list[dict]) -> tuple[str, list[str]]:
    dur = fin - ini
    js: list[str] = []
    desborde = " data-layout-allow-overflow"   # el zoom lento (1,04) y las tiras se salen del cuadro a propósito
    if p.tipo == "img":
        fondo = f'<img id="{p.id}-img" class="foto" src="assets/{p.fuente}.png" alt="">'
        js += [f'    tl.fromTo("#{p.id}-img", {{scale: 1.07}}, {{scale: 1.0, duration: 0.3, ease: "power3.out"}}, {ini:.2f});',
               f'    tl.to("#{p.id}-img", {{scale: 1.04, duration: {max(dur - 0.3, 0.1):.2f}, ease: "none"}}, {ini + 0.3:.2f});']
    elif p.tipo == "tiras":
        alto = ALTO // TIRAS
        fondo = "".join(f'<div id="{p.id}-t{n}" class="tira" style="top:{n * alto}px;height:{alto}px;'
                        f'background-image:url(assets/{p.fuente}.png);background-position:0 -{n * alto}px"></div>' for n in range(TIRAS))
        for n in range(TIRAS):
            dx = (46 if n % 2 else -46) + (n * 7 % 13) - 6
            js.append(f'    tl.fromTo("#{p.id}-t{n}", {{x: 0}}, {{x: {dx}, duration: 0.14, ease: "power3.out"}}, {ini + 0.02 * n:.2f});')
    else:
        return "", []   # los tramos de Wan van como <video> en la raíz
    encima = ENCIMA_HTML.get(p.encima, "")
    js += js_encima(p.encima, ini, fin, ws)
    return (f'    <div id="{p.id}" class="clip plano" data-start="{ini:.2f}" data-duration="{dur:.2f}"{desborde}>{fondo}{encima}</div>', js)


def html_encima_wan(p: Plano, ini: float, fin: float, ws: list[dict]) -> tuple[str, list[str]]:
    encima = ENCIMA_HTML.get(p.encima, "")
    if not encima:
        return "", []
    return (f'    <div id="{p.id}-encima" class="clip plano-vacio" data-start="{ini:.2f}" data-duration="{fin - ini:.2f}">{encima}</div>',
            js_encima(p.encima, ini, fin, ws))


CSS_COMUN = """
  #root { position: absolute; inset: 0; font-family: Montserrat, sans-serif; }
"""


def html_planos(cortes: list[tuple[Plano, float, float]], cierre: float, ws: list[dict]) -> str:
    elems, js = [], []
    for p, ini, fin in cortes:
        h, j = html_plano(p, ini, fin, ws) if p.tipo != "wan" else html_encima_wan(p, ini, fin, ws)
        if h:
            elems.append(h)
            js += j
        if p.destello and ini > 0:
            t = ini - DESTELLO_S / 2
            elems.append(f'    <div id="{p.id}-dest" class="clip destello" data-start="{t:.2f}" data-duration="{DESTELLO_S:.2f}"><div id="{p.id}-dest-in" class="dest-in"></div></div>')
            js.append(f'    tl.fromTo("#{p.id}-dest-in", {{opacity: 0}}, {{opacity: 0.7, duration: {DESTELLO_S / 2:.2f}, yoyo: true, repeat: 1, ease: "none"}}, {t:.2f});')
    elems.append(f'    <div id="cierre" class="clip" data-start="{cierre:.2f}" data-duration="{CIERRE_S:.2f}"><div id="cierre-in" class="cierre-in">'
                 f'<div class="logo-caja"><img id="logo" src="assets/logo.png" alt="Logo de la marca"></div>'
                 f'<p class="cta">Consulta con tu médico</p><p class="edu">Contenido educativo · {html.escape(FUENTE)}</p></div></div>')
    js.append(f'    tl.fromTo("#cierre-in", {{opacity: 0, scale: 0.96}}, {{opacity: 1, scale: 1, duration: 0.45, ease: "power2.out"}}, {cierre:.2f});')
    return f"""<template>
  <style>{CSS_COMUN}
    .plano, .plano-vacio, .destello, #cierre {{ position: absolute; inset: 0; overflow: hidden; }}
    .plano {{ background: {FONDO}; }}
    .foto {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
    .tira {{ position: absolute; left: -60px; right: -60px; background-size: {ANCHO}px {ALTO}px; background-repeat: no-repeat;
            background-origin: content-box; padding-left: 60px; box-shadow: 0 6px 14px rgba(0,0,0,.35); }}
    .dest-in {{ position: absolute; inset: 0; background: #fff; opacity: 0; }}
    .q {{ position: absolute; overflow: visible; }}
    .senal {{ position: absolute; left: 620px; top: 110px; }}
    .senal path, .senal circle {{ filter: drop-shadow(0 0 10px {ROSA}) drop-shadow(0 0 22px {ROSA}); }}
    .neon-fila {{ position: absolute; left: 0; right: 0; top: 300px; display: flex; gap: 40px; justify-content: center; }}
    .neon {{ padding: 14px 34px; border: 5px solid var(--c); border-radius: 26px; color: #fff; font-weight: 800; font-size: 76px;
            letter-spacing: 2px; text-shadow: 0 0 12px var(--c), 0 0 28px var(--c); box-shadow: 0 0 18px var(--c), inset 0 0 18px var(--c); }}
    .etiqueta {{ position: absolute; left: 0; right: 0; top: 250px; text-align: center; }}
    .etq {{ display: inline-block; padding: 14px 32px; border-radius: 999px; background: {ROSA}; color: {TINTA};
           font-weight: 800; font-size: 44px; box-shadow: 0 8px 24px rgba(0,0,0,.35); }}
    .datos {{ position: absolute; left: 150px; right: 150px; top: 470px; text-align: center; color: {TINTA}; }}
    .dt-cab {{ font-weight: 800; font-size: 52px; letter-spacing: 1px; }}
    .dt-cols {{ margin-top: 34px; padding-top: 0; border-top: 6px solid {TINTA}; display: flex; justify-content: space-around; }}
    .dt-col {{ width: 300px; display: flex; flex-direction: column; align-items: center; }}
    .dt-barra {{ width: 190px; transform-origin: 50% 0; border-radius: 0 0 10px 10px; }}
    .dt-num {{ margin-top: 18px; font-weight: 800; font-size: 76px; letter-spacing: -2px; }}
    .dt-lab {{ margin-top: 6px; font-weight: 700; font-size: 34px; line-height: 1.15; }}
    #cierre {{ background: {FONDO}; }}
    .cierre-in {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center;
                 padding: 0 70px; text-align: center; }}
    .logo-caja {{ display: inline-block; padding: 40px 50px; border-radius: 36px; background: #fff; }}
    #logo {{ display: block; width: 560px; height: auto; }}
    .cta {{ margin: 40px 0 0; color: #fff; font-weight: 800; font-size: 60px; }}
    .edu {{ margin: 18px 0 0; color: rgba(255,255,255,.9); font-weight: 500; font-size: 28px; }}
  </style>
  <div id="root" data-composition-id="planos" data-width="{ANCHO}" data-height="{ALTO}">
{chr(10).join(elems)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
    window.__timelines["planos"] = tl;
  </script>
</template>
"""


def html_subtitulos(ws: list[dict], cierre: float, sobre_papel: list[tuple[float, float]]) -> str:
    """sobre_papel: tramos cuyo fondo es papel claro; ahí la palabra lleva caja oscura (sin ella, contraste 1,2:1)."""
    bloques, js = [], []
    for n, w in enumerate(ws):
        ini = max(0.05, w["s"] - 0.03)
        sig = ws[n + 1]["s"] - 0.03 if n + 1 < len(ws) else w["e"] + 0.3
        fin = min(sig if sig - w["e"] < 0.35 else w["e"] + 0.2, cierre - 0.05)
        t = w["t"].rstrip(".,;:¿?¡!").lstrip("¿¡").upper()
        clase = "cap-in hl" if norm(w["t"]).rstrip("-") in DESTACAR or norm(w["t"]) in DESTACAR or re.search(r"\d", w["t"]) else "cap-in"
        if any(a <= ini < b for a, b in sobre_papel):
            clase += " caja"
        bloques.append(f'    <div id="cap-{n}" class="clip cap" data-start="{ini:.2f}" data-duration="{fin - ini:.2f}">'
                       f'<span id="cap-{n}-in" class="{clase}">{html.escape(t)}</span></div>')
        js.append(f'    tl.fromTo("#cap-{n}-in", {{scale: 0.86}}, {{scale: 1, duration: 0.09, ease: "power2.out"}}, {ini:.2f});')
    return f"""<template>
  <style>{CSS_COMUN}
    .cap {{ position: absolute; left: 0; right: 0; top: 1390px; text-align: center; overflow: visible; }}
    .cap-in {{ display: inline-block; color: #fff; font-weight: 800; font-size: 74px; letter-spacing: -0.5px;
              text-shadow: 0 4px 0 rgba(0,0,0,.35), 0 6px 26px rgba(0,0,0,.75); }}
    .hl {{ color: {ROSA}; }}
    .caja {{ padding: 6px 26px; border-radius: 18px; background: {TINTA}; }}
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


def html_raiz(cortes: list[tuple[Plano, float, float]], dur: float, cierre: float) -> str:
    videos = [f'      <video id="{p.id}-wan" class="clip" src="assets/toma.mp4" muted playsinline data-start="{ini:.2f}" '
              f'data-duration="{fin - ini:.2f}" data-media-start="{p.media_start:.2f}" data-track-index="0" '
              f'style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:1"></video>'
              for p, ini, fin in cortes if p.tipo == "wan"]
    return f"""<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={ANCHO}, height={ALTO}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {ANCHO}px; height: {ALTO}px; overflow: hidden; background: {FONDO}; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur:.2f}" data-width="{ANCHO}" data-height="{ALTO}">
{chr(10).join(videos)}
      <audio id="voz" class="clip" src="assets/voz.m4a" data-start="0" data-duration="{dur:.2f}" data-track-index="1" data-volume="1"></audio>
      <div id="planos" data-composition-id="planos" data-composition-src="compositions/planos.html" data-start="0"
           data-duration="{dur:.2f}" data-track-index="2" data-track-kind="graphics" data-width="{ANCHO}" data-height="{ALTO}" style="z-index:2"></div>
      <div id="subtitulos" data-composition-id="subtitulos" data-composition-src="compositions/subtitulos.html" data-start="0"
           data-duration="{cierre:.2f}" data-track-index="3" data-track-kind="captions" data-width="{ANCHO}" data-height="{ALTO}" style="z-index:3"></div>
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


def duracion(archivo: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(archivo)],
                                capture_output=True, text=True, check=True).stdout)


def main() -> None:
    v = sys.argv[1]
    planos = VIDEOS[v]
    destino = PROYECTO / "montaje" / v
    (destino / "assets").mkdir(parents=True, exist_ok=True)
    (destino / "compositions").mkdir(exist_ok=True)
    recortar_logo(destino / "assets/logo.png")
    for nombre in {p.fuente for p in planos if p.fuente}:
        shutil.copy(PROYECTO / f"img/{nombre}.png", destino / f"assets/{nombre}.png")
    toma = PROYECTO / f"tomas/{v}_t1.mp4"
    shutil.copy(toma, destino / "assets/toma.mp4")
    corte = CORTE_VOZ.get(v, duracion(toma) - 0.6)
    ws = palabras(v, corte)
    fin_voz = ws[-1]["e"]
    cierre = round(fin_voz + 0.35, 2)
    dur = round(cierre + CIERRE_S, 2)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(toma), "-vn", "-af", f"afade=t=out:st={corte:.2f}:d=0.2,apad",
                    "-t", str(dur), "-c:a", "aac", "-b:a", "192k", str(destino / "assets/voz.m4a")], check=True)
    cortes = tiempos(planos, ws, cierre)
    sobre_papel = [(ini, fin) for p, ini, fin in cortes if p.caja]
    (destino / "compositions/planos.html").write_text(html_planos(cortes, cierre, ws))
    (destino / "compositions/subtitulos.html").write_text(html_subtitulos(ws, cierre, sobre_papel))
    (destino / "index.html").write_text(html_raiz(cortes, dur, cierre))
    print(f"{v}: {dur} s, voz hasta {fin_voz:.2f} s, {len(ws)} palabras, planos:")
    for p, ini, fin in cortes:
        print(f"  {p.id:3} {ini:6.2f}–{fin:6.2f}  {p.tipo:5} {p.fuente or f'toma desde {p.media_start:.2f} s'}")


if __name__ == "__main__":
    main()
