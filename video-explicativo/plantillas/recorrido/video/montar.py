"""Monta el recorrido en HyperFrames desde la grabación y la voz verificada (genérico: se configura en ../proyecto.json).

    python3 montar.py              # todo
    SOLO=cap1,cap2 python3 montar.py   # solo esos capítulos (toma de humo)

Lee ../grabacion/salida/<toma>/{frames.json, escenas.json, frames/}, ../voz/<id>.wav|.palabras.json, ../guion.json.
Escribe assets/partes/<toma>.mp4 (30 fps, tiempo real), assets/voz/*.wav, compositions/<capítulo>.html, index.html,
package.json (HyperFrames fijado) y linea-de-tiempo.json (dónde cae cada escena y cada voz en el video final).
Cuadro: la grabación va enmarcada arriba (1728×972) y los subtítulos viven en la franja de abajo, sin tapar la app.
Focos (foco() en tomas.mjs): acercamiento suave dentro del marco + anillo que se dibuja; la cámara vuelve a 1× al salir.
"""
import html
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
PROY_DIR = RAIZ.parent
GRAB = PROY_DIR / "grabacion" / "salida"
COMP = RAIZ / "compositions"
PROY = json.loads((PROY_DIR / "proyecto.json").read_text())
LINEAS = {l["id"]: l for l in json.loads((PROY_DIR / "guion.json").read_text())["lineas"]}
INFORME = json.loads((PROY_DIR / "voz" / "informe.json").read_text())
VOZ_DUR = {k: v["duracion_s"] for k, v in INFORME.items()}
MARCA = PROY["marca"]
CAPITULOS = PROY["capitulos"]

ENTRADA = PROY["grabacion"]["entrada_s"]   # la voz entra igual que en la grabación
CARTON = 2.6                               # tarjeta de capítulo
VOZ_TARJETA = 0.8                          # la voz de la intro y del cierre entra aquí (realzar.py la usa igual)
VX, VY, VW, VH = 96, 12, 1728, 972         # marco de la grabación dentro de 1920×1080
FRANJA_Y = VY + VH                         # la franja de subtítulos empieza aquí
ESC = VW / PROY["grabacion"]["ancho"]      # px de grabación → px de marco
ZOOM_MAX = 1.4                             # 1600 px de grabación × 1,08 × 1,4 ≈ 1,5×: más, y el texto se ablanda
FONDO, ACENTO, ACENTO2 = MARCA["fondo"], MARCA["acento"], MARCA["acento2"]
FUENTE = MARCA["fuente"]
DEBILES = {"el", "la", "los", "las", "de", "del", "y", "o", "su", "sus", "un", "una", "en", "con", "por", "para", "a", "al", "que",
           "se", "lo", "the", "a", "an", "of", "and", "or", "to", "in", "on", "for", "with", "your", "its"}


def e(t: str) -> str:
    return html.escape(t, quote=True)


def r(x: float) -> str:
    return f"{x:.3f}".rstrip("0").rstrip(".")


def logo_o_nombre(cid: str, clase: str) -> str:
    logo = MARCA.get("logo")
    if logo and (RAIZ / logo).exists():
        return f'<img id="{cid}-logo" class="{clase}" src="{e(logo)}" alt="{e(PROY["nombre"])}" />'
    return f'<div id="{cid}-logo" class="{clase} nombre">{e(PROY["nombre"])}</div>'


# ---------------------------------------------------------------- tomas → MP4
def armar_toma(toma: str) -> tuple[float, dict]:
    """MP4 de 30 fps con tiempo real; devuelve el origen (t del primer cuadro) y las escenas por id."""
    d = GRAB / toma
    if not (d / "frames.json").exists():
        raise SystemExit(f"Falta la toma {toma}: corre `bash grabacion/grabar-todo.sh {toma}`")
    frames = json.loads((d / "frames.json").read_text())
    escenas = {s["id"]: s for s in json.loads((d / "escenas.json").read_text())["escenas"]}
    destino = RAIZ / "assets" / "partes" / f"{toma}.mp4"
    if not destino.exists() or destino.stat().st_mtime < (d / "frames.json").stat().st_mtime:
        fin = max(s["t1"] for s in escenas.values()) + 0.3   # una página quieta no emite cuadros: se sostiene el último
        lineas = []
        for a, b in zip(frames, frames[1:] + [None]):
            dur = (b["t"] - a["t"]) if b else max(0.5, fin - a["t"])
            lineas.append(f"file 'frames/f{a['n']:06d}.jpg'\nduration {dur:.4f}")
        lineas.append(f"file 'frames/f{frames[-1]['n']:06d}.jpg'")
        (d / "concat.txt").write_text("\n".join(lineas) + "\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "concat.txt",
                        "-vf", f"fps=30,scale={VW}:{VH}:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-crf", "16",
                        "-preset", "medium", "-g", "30", "-movflags", "+faststart", str(destino)], cwd=d, check=True)
        print(f"  {toma}.mp4 listo")
    return frames[0]["t"], escenas


# ---------------------------------------------------------------- subtítulos
def partir(ws: list[dict], tope: int = 14) -> list[list[dict]]:
    """Parte una frase larga en la coma más cercana al medio; sin coma, cerca del medio sin dejar al final una palabra débil."""
    if len(ws) <= tope:
        return [ws]
    medio = len(ws) / 2
    comas = [k for k, w in enumerate(ws[:-1]) if w["w"].endswith((",", ":", ";")) and 3 <= k + 1 <= len(ws) - 3]
    if comas:
        k = min(comas, key=lambda k: abs(k + 1 - medio)) + 1
    else:
        k = int(medio)
        while k > 3 and ws[k - 1]["w"].lower().strip(",.:;") in DEBILES:
            k -= 1
    return partir(ws[:k], tope) + partir(ws[k:], tope)


def en_pantalla(texto: str) -> str:
    """La voz lee las cifras en palabras; el subtítulo las muestra con números (proyecto.json → pantalla).
    Solo palabras completas («dos» no toca «pedidos»); sin distinguir mayúsculas al inicio de frase."""
    for voz, pantalla in PROY.get("pantalla", []):
        texto = re.sub(rf"(?<!\w){re.escape(voz)}(?!\w)", lambda _m, p=pantalla: p, texto, flags=re.IGNORECASE)
    return texto


def trozos(id_: str) -> list[dict]:
    """Trozos legibles de una línea: por frases, luego las largas en su coma central; tiempos de las palabras de la voz."""
    palabras = json.loads((PROY_DIR / "voz" / f"{id_}.palabras.json").read_text())
    frases, actual = [], []
    for i, w in enumerate(palabras):
        actual.append(w)
        if w["w"].endswith((".", ":", ";", "?", "!")) or i == len(palabras) - 1:
            frases.append(actual)
            actual = []
    out = [{"texto": " ".join(x["w"] for x in p), "s": p[0]["s"], "e": p[-1]["e"]} for f in frases for p in partir(f)]
    # Un trozo que no alcanza a leerse (0,5 s + 0,3 s por palabra) se une al siguiente si caben en dos líneas (≤ 24 palabras).
    unidos: list[dict] = []
    for t in out:
        if unidos:
            prev = unidos[-1]
            n_prev = len(prev["texto"].split())
            if prev["e"] - prev["s"] < 0.5 + 0.3 * n_prev and n_prev + len(t["texto"].split()) <= 24:
                unidos[-1] = {"texto": prev["texto"] + " " + t["texto"], "s": prev["s"], "e": t["e"]}
                continue
        unidos.append(t)
    for a, b in zip(unidos, unidos[1:]):   # cada trozo dura hasta que empieza el siguiente: la franja no parpadea
        a["e"] = max(a["e"], b["s"] - 0.02)
    return [{**t, "texto": en_pantalla(t["texto"])} for t in unidos]


def subtitulos(pref: str, id_: str, inicio: float, cola: float) -> list[str]:
    ts = trozos(id_)
    out = []
    for k, tr in enumerate(ts):
        a = inicio + tr["s"]
        b = inicio + tr["e"] + (cola if k == len(ts) - 1 else 0)
        out.append(f'    <div id="{pref}-{k}" class="clip sub" data-start="{r(a)}" data-duration="{r(max(0.4, b - a))}" '
                   f'data-track-index="3">{e(tr["texto"])}</div>')
    return out


# ---------------------------------------------------------------- cámara (focos)
def camara(cid: str, focos: list[dict], ini: float, fin: float, n0: int) -> tuple[list[str], list[str]]:
    """Tweens de cámara del escenario y anillos SVG para los focos de UNA escena (tiempos ya en la composición)."""
    js, svgs = [], []
    focos = sorted(focos, key=lambda f: f["L"])
    for i, f in enumerate(focos):
        X, Y, W, H = (f[k] * ESC for k in ("x", "y", "w", "h"))
        X, Y = max(0.0, X), max(0.0, Y)
        W, H = min(W, VW - X), min(H, VH - Y)
        z = min(f["zoom"], 0.88 * VW / W, 0.80 * VH / H, ZOOM_MAX)
        z = 1.0 if z < 1.08 else z
        cx, cy = X + W / 2, Y + H / 2
        tx = min(0.0, max(VW - VW * z, VW / 2 - cx * z))
        ty = min(0.0, max(VH - VH * z, VH / 2 - cy * z))
        t_in = max(f["L"], ini + 0.3)
        if t_in + 0.9 > fin:
            continue
        t_fin = min(f["L"] + f["dur"], fin - 0.7)
        sig = focos[i + 1] if i + 1 < len(focos) else None
        encadena = sig is not None and sig["L"] - t_fin < 1.5 and sig["L"] + 0.9 < fin
        js.append(f'tl.to("#{cid}-stage", {{ scale: {r(z)}, x: {r(tx)}, y: {r(ty)}, duration: 0.7, ease: "power2.inOut" }}, {r(t_in)});')
        t_sale = None
        if not encadena:
            t_sale = min(max(t_in + 1.3, t_fin), fin - 0.65)
            js.append(f'tl.to("#{cid}-stage", {{ scale: 1, x: 0, y: 0, duration: 0.6, ease: "power2.inOut" }}, {r(t_sale)});')
        a0, a1 = t_in + 0.55, (t_sale if t_sale is not None else max(sig["L"], t_in + 0.9))
        if f.get("anillo") and a1 - a0 > 0.7:
            n = n0 + len(svgs)
            sw, rx = 3.2 / z, 10 / z
            svgs.append(f'      <svg id="{cid}-r{n}" class="clip ring" data-start="{r(a0)}" data-duration="{r(a1 - a0)}" '
                        f'data-track-index="2" style="left:{r(X)}px;top:{r(Y)}px;width:{r(W)}px;height:{r(H)}px" '
                        f'viewBox="0 0 {r(W)} {r(H)}"><rect id="{cid}-r{n}-k" x="{r(sw / 2)}" y="{r(sw / 2)}" '
                        f'width="{r(W - sw)}" height="{r(H - sw)}" rx="{r(rx)}" pathLength="100" fill="none" '
                        f'stroke="{ACENTO}" stroke-width="{r(sw)}" stroke-dasharray="100 120" stroke-dashoffset="110"/></svg>')
            js.append(f'tl.fromTo("#{cid}-r{n}-k", {{ attr: {{ "stroke-dashoffset": 110 }} }}, '
                      f'{{ attr: {{ "stroke-dashoffset": 0 }}, duration: 0.5, ease: "power2.out" }}, {r(a0)});')
    return js, svgs


# ---------------------------------------------------------------- composiciones
def css_comun() -> str:
    return f"""
    @font-face {{ font-family: "{FUENTE}"; font-style: normal; font-weight: 200 800; src: url("{MARCA['archivo_fuente']}") format("woff2"); }}
    #root {{ position: absolute; inset: 0; overflow: hidden; background: {FONDO}; font-family: "{FUENTE}", sans-serif; }}
    .marco {{ position: absolute; left: {VX}px; top: {VY}px; width: {VW}px; height: {VH}px; border-radius: 14px; overflow: hidden;
      box-shadow: 0 18px 50px rgba(0,0,0,0.45); background: #e9edf2; }}
    .stage {{ position: absolute; left: 0; top: 0; width: {VW}px; height: {VH}px; transform-origin: 0 0; }}
    .stage video {{ position: absolute; left: 0; top: 0; width: {VW}px; height: {VH}px; }}
    .stage .ring {{ position: absolute; overflow: visible; }}
    .sub {{ position: absolute; left: {VX}px; width: {VW}px; top: {FRANJA_Y + 14}px; height: 70px; display: flex; align-items: center;
      justify-content: center; text-align: center; color: #ffffff; font-size: 31px; font-weight: 600; line-height: 1.18; }}
    .chip {{ position: absolute; right: {1920 - VX - VW + 18}px; top: {VY + 18}px; padding: 8px 18px; border-radius: 999px;
      background: rgba(11,18,32,0.86); color: #ffffff; font-size: 28px; font-weight: 700; }}
    .chip b {{ color: {ACENTO}; font-weight: 800; margin-right: 8px; }}
    .nombre {{ color: #ffffff; font-weight: 800; letter-spacing: -0.02em; }}"""


def carton(cid: str, n: int, titulo: str) -> tuple[str, str, list[str]]:
    """Tarjeta de capítulo (índice con el capítulo actual resaltado): CSS, HTML y tweens."""
    indice = "\n".join(f'          <li class="{"hoy" if i == n else "ya" if i < n else ""}">{e(c["titulo"])}</li>'
                       for i, c in enumerate(CAPITULOS, start=1))
    css = f"""
    #{cid}-card {{ position: absolute; inset: 0; background: {FONDO}; z-index: 10; }}
    #{cid}-card-in {{ position: absolute; inset: 0; }}
    .logo {{ position: absolute; left: 150px; top: 110px; width: 300px; }}
    .logo.nombre {{ width: auto; font-size: 44px; white-space: nowrap; }}
    .k {{ position: absolute; left: 150px; top: 380px; color: {ACENTO}; font-size: 30px; font-weight: 800; letter-spacing: 0.18em; }}
    .t {{ position: absolute; left: 146px; top: 432px; color: #ffffff; font-size: 104px; font-weight: 800; letter-spacing: -0.02em; line-height: 1.04; width: 1600px; }}
    .bar {{ position: absolute; left: 150px; top: 590px; width: 260px; height: 8px; border-radius: 8px; background: linear-gradient(90deg, {ACENTO2}, {ACENTO}); transform-origin: 0 50%; }}
    .idx {{ position: absolute; left: 150px; bottom: 110px; width: 1620px; display: flex; flex-wrap: wrap; gap: 10px 30px; list-style: none;
      font-size: 28px; font-weight: 600; color: rgba(255,255,255,0.62); }}
    .idx li.ya {{ color: rgba(255,255,255,0.36); }}
    .idx li.hoy {{ color: {ACENTO}; font-weight: 800; }}"""
    html_ = f"""    <div id="{cid}-card" class="clip" data-start="0" data-duration="{r(CARTON)}" data-track-index="5">
      <div id="{cid}-card-in">
        {logo_o_nombre(cid, "logo")}
        <div id="{cid}-k" class="k">CAPÍTULO {n} DE {len(CAPITULOS)}</div>
        <div id="{cid}-t" class="t">{e(titulo)}</div>
        <div id="{cid}-bar" class="bar"></div>
        <ol id="{cid}-idx" class="idx">
{indice}
        </ol>
      </div>
    </div>"""
    js = [f'tl.fromTo("#{cid}-k", {{ opacity: 0, y: 18 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, 0.15);',
          f'tl.fromTo("#{cid}-t", {{ opacity: 0, y: 26 }}, {{ opacity: 1, y: 0, duration: 0.55, ease: "power3.out" }}, 0.3);',
          f'tl.fromTo("#{cid}-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "expo.out" }}, 0.55);',
          f'tl.to("#{cid}-card-in", {{ opacity: 0, duration: 0.35, ease: "power2.in" }}, {r(CARTON - 0.35)});']
    return css, html_, js


def comp_capitulo(n: int, cap: dict, voces: list, escenas_out: list) -> float:
    """Tarjeta + escenas del capítulo. Devuelve su duración; agrega (id, inicio relativo) de cada voz y de cada escena."""
    cid = cap["id"]
    origen, escenas = armar_toma(cap["toma"])
    css_c, html_c, js = carton(cid, n, cap["titulo"])
    cuerpo, rings, subs = [], [], []
    L = CARTON
    for j, id_ in enumerate(cap["escenas"]):
        s = escenas.get(id_)
        if s is None:
            print(f"  ⚠ {id_}: no está en la toma {cap['toma']}; se omite (¿falló la escena? ver grabar.log)")
            continue
        dur = s["t1"] - s["t0"]
        cuerpo.append(f'        <video id="{cid}-v{j}" class="clip" src="assets/partes/{cap["toma"]}.mp4" data-start="{r(L)}" '
                      f'data-duration="{r(dur)}" data-media-start="{r(s["t0"] - origen)}" data-track-index="1" muted playsinline></video>')
        if j > 0:
            js.append(f'tl.set("#{cid}-stage", {{ scale: 1, x: 0, y: 0 }}, {r(L)});')
        focos = [{**f, "L": L + (f["t"] - s["t0"])} for f in s.get("focos", [])]
        cj, svgs = camara(cid, focos, L, L + dur, len(rings))
        js += cj
        rings += svgs
        voces.append((id_, L + ENTRADA))
        escenas_out.append((id_, L, L + dur))
        subs += subtitulos(f"{cid}-s{j}", id_, L + ENTRADA, 0.35)
        L += dur
    js.append(f'tl.fromTo("#{cid}-chip", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.4 }}, {r(CARTON + 0.3)});')
    js.append(f'tl.to("#{cid}-chip", {{ opacity: 0, duration: 0.4 }}, {r(CARTON + 4.5)});')
    tl_js = (chr(10) + "    ").join(js)
    html_ = f"""<template>
  <style>{css_comun()}{css_c}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080">
    <div id="{cid}-marco" class="marco">
      <div id="{cid}-stage" class="stage">
{chr(10).join(cuerpo + rings)}
      </div>
    </div>
{chr(10).join(subs)}
    <div id="{cid}-chip" class="clip chip" data-start="{r(CARTON)}" data-duration="{r(L - CARTON)}" data-track-index="4"><b>{n}</b>{e(cap["titulo"])}</div>
{html_c}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {tl_js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""
    (COMP / f"{cid}.html").write_text(html_)
    print(f"  {n}. {cap['titulo']}: {len(cuerpo)} escenas · {len(rings)} anillos · {L:.1f} s")
    return L


def comp_tarjeta(cid: str, conf: dict, voces: list) -> float:
    """Apertura o cierre: logo (o nombre), título y subtítulo sobre el fondo de marca, con su voz y sus subtítulos."""
    id_voz = conf.get("voz")
    dur = VOZ_TARJETA + (VOZ_DUR[id_voz] if id_voz else 2.2) + conf.get("extra_s", 1.8)
    subs = []
    if id_voz:
        voces.append((id_voz, VOZ_TARJETA))
        subs = subtitulos(f"{cid}-s", id_voz, VOZ_TARJETA, 0.3)
    html_ = f"""<template>
  <style>{css_comun()}
    #{cid}-fondo {{ position: absolute; inset: 0; background: radial-gradient(1200px 700px at 78% 18%, {ACENTO2}47, transparent 60%),
      radial-gradient(900px 600px at 12% 92%, {ACENTO}29, transparent 60%), {FONDO}; }}
    #{cid}-logo {{ position: absolute; left: 160px; top: 250px; width: 760px; transform-origin: 0 50%; }}
    #{cid}-logo.nombre {{ top: 400px; width: auto; font-size: 96px; white-space: nowrap; }}
    #{cid}-t {{ position: absolute; left: 166px; top: 540px; color: #ffffff; font-size: 64px; font-weight: 800; letter-spacing: -0.015em; }}
    #{cid}-x {{ position: absolute; left: 168px; top: 630px; color: rgba(255,255,255,0.72); font-size: 32px; font-weight: 600; }}
    #{cid}-bar {{ position: absolute; left: 168px; top: 712px; width: 300px; height: 8px; border-radius: 8px; background: linear-gradient(90deg, {ACENTO2}, {ACENTO}); transform-origin: 0 50%; }}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080">
    <div id="{cid}-fondo"></div>
    {logo_o_nombre(cid, "")}
    <div id="{cid}-t">{e(conf["titulo"])}</div>
    <div id="{cid}-x">{e(conf["sub"])}</div>
    <div id="{cid}-bar"></div>
{chr(10).join(subs)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#{cid}-logo", {{ scale: 0.97 }}, {{ scale: 1.03, duration: {r(dur)}, ease: "none" }}, 0);
    tl.fromTo("#{cid}-t", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.55, ease: "power3.out" }}, 0.45);
    tl.fromTo("#{cid}-x", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, 0.65);
    tl.fromTo("#{cid}-bar", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.7, ease: "expo.out" }}, 0.8);
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""
    (COMP / f"{cid}.html").write_text(html_)
    return dur


def host(cid: str, start: float, dur: float) -> str:
    return (f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
            f'data-start="{r(start)}" data-duration="{r(dur)}" data-track-index="1" data-track-kind="graphics" '
            f'data-width="1920" data-height="1080"></div>')


def escribir_raiz(hosts: list[str], audios: list[tuple], total: float) -> None:
    for v, _ in audios:
        shutil.copyfile(PROY_DIR / "voz" / f"{v}.wav", RAIZ / "assets" / "voz" / f"{v}.wav")
    pistas = "\n".join(f'      <audio id="voz-{v}" class="clip" src="assets/voz/{v}.wav" data-start="{r(s)}" '
                       f'data-duration="{r(VOZ_DUR[v])}" data-track-index="9"></audio>' for v, s in audios)
    (RAIZ / "index.html").write_text(f"""<!doctype html>
<html lang="{PROY.get('idioma', 'es')}" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: {FONDO}; }}
      #root {{ width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{r(total)}" data-width="1920" data-height="1080">
{chr(10).join(hosts)}
{pistas}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")
    v = PROY["hyperframes"]
    (RAIZ / "package.json").write_text(json.dumps({"name": "video-recorrido", "private": True, "type": "module", "scripts": {
        "dev": f"npx --yes hyperframes@{v} preview", "check": f"npx --yes hyperframes@{v} check",
        "render": f"npx --yes hyperframes@{v} render", "snapshot": f"npx --yes hyperframes@{v} snapshot"}}, indent=2) + "\n")


def main() -> None:
    malas = [k for k, v in INFORME.items() if not v["aceptada"]]
    if malas:
        raise SystemExit(f"Voces rechazadas por Whisper: {malas}. Reescribe esas frases y corre voz.py antes de montar.")
    for d in (COMP, RAIZ / "assets" / "partes", RAIZ / "assets" / "voz"):
        d.mkdir(parents=True, exist_ok=True)
    solo = set(filter(None, os.environ.get("SOLO", "").split(",")))
    hosts, audios, escenas, caps, t = [], [], [], [], 0.0

    def agregar(cid: str, dur: float, voces: list, esc: list) -> None:
        nonlocal t
        hosts.append(host(cid, t, dur))
        audios.extend((v, t + s) for v, s in voces)
        escenas.extend({"id": i, "capitulo": cid, "inicio": round(t + a, 2), "fin": round(t + b, 2)} for i, a, b in esc)
        caps.append({"id": cid, "inicio": round(t, 2), "fin": round(t + dur, 2)})
        t += dur

    voces: list = []
    agregar("intro", comp_tarjeta("intro", PROY["intro"], voces), voces, [])
    for n, cap in enumerate(CAPITULOS, start=1):
        if solo and cap["id"] not in solo:
            continue
        voces, esc = [], []
        agregar(cap["id"], comp_capitulo(n, cap, voces, esc), voces, esc)
    voces = []
    agregar("cierre", comp_tarjeta("cierre", PROY["cierre"], voces), voces, [])
    escribir_raiz(hosts, audios, t)
    linea = {"total_s": round(t, 2), "idioma": PROY.get("idioma", "es"), "capitulos": caps, "escenas": escenas,
             "voces": [{"id": v, "t": round(s, 2), "dur": VOZ_DUR[v], "texto": LINEAS[v]["texto"]} for v, s in audios]}
    (RAIZ / "linea-de-tiempo.json").write_text(json.dumps(linea, ensure_ascii=False, indent=1))
    print(f"total {t:.1f} s ({int(t // 60)}:{int(t % 60):02d}) · {len(audios)} voces")


if __name__ == "__main__":
    main()
