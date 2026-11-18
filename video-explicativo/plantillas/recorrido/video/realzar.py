"""Realce opcional del recorrido: apertura y cierre con motion, fondo de marca en las tarjetas, efectos y música bajo la voz.

    (cd video && python3 montar.py && python3 realzar.py)    # SIEMPRE después de montar.py: montar.py lo pisa

Se configura en ../proyecto.json → "realce" (todo opcional; campos en referencias/recorrido.md):
- intro: `logo` (blanco, horizontal), `bajada` (imagen bajo el logo; sin ella va intro.sub en texto), `pilares`
  [[palabra que dice la voz, texto del chip], …] que entran cuando la voz dice esa palabra, y `palabra_titulo` (la
  palabra con la que entra intro.titulo).
- cierre: `logo` (completo, blanco). El lema es cierre.titulo y la cápsula de abajo, cierre.sub.
- `motivo`: "hexagonos" (campo de hexágonos en los tonos del acento) o "ninguno". La cuadrícula animada va siempre.
- `efectos`: whoosh en cada tarjeta de capítulo y golpe suave en cada logo (sonidos de la skill media-use).
- Música: video/assets/musica/fondo.* si existe; baja a 0,3 mientras habla la voz.
Todo es función del tiempo de la línea de tiempo: sin azar, sin red, sin relojes. Se puede correr varias veces.
Salió de un video real de presentación de una app (nov-2026).
"""
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
import montar as m  # noqa: E402  (estilos comunes, subtítulos, marca y duraciones de voz)

LINEA = json.loads((RAIZ / "linea-de-tiempo.json").read_text())
REALCE = m.PROY.get("realce", {})
SFX_ORIGEN = Path.home() / ".agents/skills/media-use/audio/assets/sfx"
SFX = ("whoosh-short.mp3", "impact-bass-1.mp3", "whoosh.mp3")
INI = m.VOZ_TARJETA          # la voz de la intro y del cierre entra aquí (igual que en montar.py)
MUSICA_VOL, MUSICA_BAJO = 0.42, 0.3


# ---------------------------------------------------------------- color
def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgba(h: str, a: float) -> str:
    r, g, b = _rgb(h)
    return f"rgba({r},{g},{b},{a})"


def mezclar(a: str, b: str, t: float) -> str:
    """Color entre `a` (t=0) y `b` (t=1)."""
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(_rgb(a), _rgb(b)))


CLARO = mezclar(m.ACENTO, "#ffffff", 0.45)
TONOS = [mezclar(m.FONDO, m.ACENTO, t) for t in (0.3, 0.48, 0.66, 0.83)] + [m.ACENTO, CLARO]


# ---------------------------------------------------------------- voz
def t_palabra(id_: str, prefijo: str) -> float:
    """Momento (en la composición) en que la voz `id_` dice la palabra que empieza por `prefijo`."""
    norm = lambda t: re.sub(r"[^\w]", "", t.lower().translate(str.maketrans("áéíóúüñ", "aeiouun")))
    ws = json.loads((m.PROY_DIR / "voz" / f"{id_}.palabras.json").read_text())
    for w in ws:
        if norm(w["w"]).startswith(norm(prefijo)):
            return INI + w["s"]
    raise SystemExit(f"realce: la voz {id_} no dice «{prefijo}». Dice: {' '.join(w['w'] for w in ws)}")


# ---------------------------------------------------------------- piezas
def marca(cid: str, sufijo: str, ruta: str | None, texto: str, clase: str) -> str:
    """Imagen de marca, o el texto si no hay ruta. Una ruta configurada que no existe es un error."""
    if ruta:
        if not (RAIZ / ruta).exists():
            raise SystemExit(f"realce: no existe video/{ruta}")
        return f'<img id="{cid}-{sufijo}" class="{clase}" src="{m.e(ruta)}" alt="{m.e(texto)}" />'
    return f'<div id="{cid}-{sufijo}" class="{clase} texto">{m.e(texto)}</div>'


def hexagonos(cid: str, cx0: float, cy0: float, radio: int, lado: float) -> tuple[str, list[str]]:
    """Campo de hexágonos (axial) con tono e intensidad deterministas; entran del centro hacia afuera."""
    if REALCE.get("motivo", "hexagonos") == "ninguno":
        return "", []
    polys, js = [], []
    w, h = math.sqrt(3) * lado, 1.5 * lado
    n = 0
    for q in range(-radio, radio + 1):
        for rr in range(max(-radio, -q - radio), min(radio, -q + radio) + 1):
            x, y = cx0 + w * (q + rr / 2), cy0 + h * rr
            dist = (abs(q) + abs(rr) + abs(q + rr)) / 2
            semilla = (q * 73856093 ^ rr * 19349663) & 0xFFFF
            if semilla % 7 == 0 or dist > radio - 0.5 and semilla % 3 == 0:
                continue   # huecos: que no sea un panal perfecto
            tono = TONOS[min(len(TONOS) - 1, int((1 - dist / (radio + 1)) * 4 + (semilla % 3)))]
            op = 0.22 + 0.55 * (1 - dist / (radio + 1)) * (0.6 + 0.4 * ((semilla >> 3) % 5) / 4)
            pts = " ".join(f"{x + (lado - 2) * math.cos(math.radians(60 * k - 30)):.1f},"
                           f"{y + (lado - 2) * math.sin(math.radians(60 * k - 30)):.1f}" for k in range(6))
            polys.append(f'<polygon id="{cid}-h{n}" points="{pts}" fill="{tono}" opacity="0" />')
            js.append(f'tl.fromTo("#{cid}-h{n}", {{ opacity: 0, scale: 0.55, svgOrigin: "{x:.0f} {y:.0f}" }}, '
                      f'{{ opacity: {op:.2f}, scale: 1, duration: 0.6, ease: "power2.out" }}, {0.25 + dist * 0.07 + (semilla % 5) * 0.02:.2f});')
            n += 1
    svg = f'<svg id="{cid}-hex" class="hexes" viewBox="0 0 1920 1080" width="1920" height="1080">{"".join(polys)}</svg>'
    return svg, js


def base_css(cid: str, ancho_brillo: int, alto_brillo: int) -> str:
    a, a2, f = m.ACENTO, m.ACENTO2, m.FONDO
    return m.css_comun() + f"""
    .grid {{ position: absolute; inset: 0; pointer-events: none; opacity: var(--g-op, 1);
      background-image: linear-gradient({rgba(a, 0.10)} 1px, transparent 1px), linear-gradient(90deg, {rgba(a, 0.10)} 1px, transparent 1px);
      background-size: 72px 72px; background-position: var(--g-x, 0px) var(--g-y, 0px); }}
    .glow-fondo {{ position: absolute; inset: 0; background: radial-gradient(1100px 680px at 80% 22%, {a2}40, transparent 62%),
      radial-gradient(900px 600px at 10% 95%, {a}26, transparent 60%), {f}; }}
    .vineta {{ position: absolute; inset: 0; background: radial-gradient(1400px 900px at 50% 50%, transparent 55%, rgba(4,8,16,0.55)); }}
    #{cid}-hex {{ position: absolute; left: 0; top: 0; }}
    #{cid}-marca {{ position: relative; }}
    #{cid}-glow {{ position: absolute; border-radius: 50%; pointer-events: none; opacity: 0;
      left: calc(50% - {ancho_brillo // 2}px); top: calc(50% - {alto_brillo // 2}px); width: {ancho_brillo}px; height: {alto_brillo}px;
      background: radial-gradient(circle, {rgba(a, 0.42)} 0%, {rgba(a2, 0.14)} 38%, {rgba(f, 0)} 70%); }}
    #{cid}-anillo {{ position: absolute; border-radius: 50%; border: 3px solid {a}; opacity: 0; pointer-events: none;
      left: calc(50% - 100px); top: calc(50% - 100px); width: 200px; height: 200px; }}
    .texto {{ color: #fff; font-weight: 800; letter-spacing: -0.02em; white-space: nowrap; }}"""


def destello(cid: str, t: float, escala: float) -> list[str]:
    """Brillo y anillo detrás del logo (registry: logo-outro / logo-sting).
    El anillo lleva immediateRender: false: si no, GSAP lo deja visible (0,9) desde el segundo 0 hasta que arranca."""
    return [f'tl.fromTo("#{cid}-glow", {{ opacity: 0, scale: 0.5 }}, {{ opacity: 1, scale: {escala}, duration: 0.45, ease: "power2.out" }}, {m.r(t)});',
            f'tl.to("#{cid}-glow", {{ opacity: 0.35, scale: {escala + 0.45}, duration: 1.4, ease: "power2.out" }}, {m.r(t + 0.45)});',
            f'tl.fromTo("#{cid}-anillo", {{ opacity: 0.9, scale: 0.4 }}, {{ opacity: 0, scale: {escala + 0.95}, duration: 0.9, ease: "power2.out", immediateRender: false }}, {m.r(t + 0.05)});']


def pagina(cid: str, css: str, cuerpo: str, js: list[str], voz: str | None) -> None:
    subs = m.subtitulos(f"{cid}-s", voz, INI, 0.3) if voz else []
    tl_js = (chr(10) + "    ").join(js)
    (m.COMP / f"{cid}.html").write_text(f"""<template>
  <style>{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="1920" data-height="1080" data-layout-allow-overlap>
    <div class="glow-fondo"></div>
    <div id="{cid}-grid" class="grid"></div>
{cuerpo}
{chr(10).join(subs)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {tl_js}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
""")


def pilares_conf() -> list[tuple[str, str]]:
    pil = REALCE.get("intro", {}).get("pilares", [])
    if not all(isinstance(p, list) and len(p) == 2 and all(isinstance(x, str) for x in p) for p in pil):
        raise SystemExit('realce.intro.pilares: va como [["palabra que dice la voz", "texto del chip"], …]')
    return [(a, b) for a, b in pil]


# ---------------------------------------------------------------- intro y cierre
def comp_intro(dur: float) -> None:
    cid, conf, voz = "intro", REALCE.get("intro", {}), m.PROY["intro"].get("voz")
    hex_svg, js_hex = hexagonos(cid, 1530, 470, 5, 46)
    pilares = pilares_conf()
    if pilares and not voz:
        raise SystemExit("realce: los pilares entran con la voz, y la intro no tiene voz (intro.voz)")
    logo = marca(cid, "logo", conf.get("logo") or m.MARCA.get("logo"), m.PROY["nombre"], "")
    bajada = marca(cid, "bajada", conf.get("bajada"), m.PROY["intro"]["sub"], "")
    chips = "\n".join(f'        <div id="{cid}-p{k}" class="pilar"><i></i>{m.e(t)}</div>' for k, (_, t) in enumerate(pilares))
    js = [f'tl.to("#{cid}-grid", {{ "--g-x": "72px", "--g-y": "-144px", duration: {m.r(dur)}, ease: "none" }}, 0);',
          f'tl.fromTo("#{cid}-grid", {{ "--g-op": 0 }}, {{ "--g-op": 1, duration: 1.2, ease: "power1.out" }}, 0);',
          *js_hex,
          f'tl.to("#{cid}-hex", {{ y: -26, duration: {m.r(dur)}, ease: "none" }}, 0);' if hex_svg else "",
          f'tl.fromTo("#{cid}-logo", {{ clipPath: "inset(0% 100% 0% 0%)", x: -30 }}, {{ clipPath: "inset(0% 0% 0% 0%)", x: 0, duration: 1.1, ease: "power4.out" }}, 0.15);',
          *destello(cid, 1.05, 1.15),
          f'tl.fromTo("#{cid}-bajada", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }}, 1.25);',
          f'tl.fromTo("#{cid}-raya", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.8, ease: "expo.out" }}, 1.45);']
    t_ult = 1.45
    for k, (pal, _) in enumerate(pilares):
        t_ult = t_palabra(voz, pal) - 0.08
        js.append(f'tl.fromTo("#{cid}-p{k}", {{ opacity: 0, y: 22, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.45, ease: "back.out(1.6)" }}, {m.r(t_ult)});')
    pal_t = conf.get("palabra_titulo")
    t_titulo = t_palabra(voz, pal_t) - 0.1 if pal_t and voz else t_ult + 0.6
    js += [f'tl.fromTo("#{cid}-t", {{ opacity: 0, y: 26, filter: "blur(8px)" }}, {{ opacity: 1, y: 0, filter: "blur(0px)", duration: 0.7, ease: "power3.out" }}, {m.r(t_titulo)});',
           f'tl.to("#{cid}-logo, #{cid}-bajada", {{ scale: 1.025, duration: {m.r(dur - 1.3)}, ease: "none" }}, 1.3);']
    css = base_css(cid, 760, 560) + f"""
    #{cid}-col {{ position: absolute; left: 150px; top: 0; bottom: 96px; width: 1180px; display: flex; flex-direction: column;
      justify-content: center; align-items: flex-start; }}
    #{cid}-logo {{ display: block; width: 780px; max-height: 230px; object-fit: contain; object-position: left center; transform-origin: 0 50%; }}
    #{cid}-logo.texto {{ width: auto; font-size: 96px; line-height: 1; }}
    #{cid}-bajada {{ display: block; margin-top: 16px; width: 780px; max-height: 80px; object-fit: contain; object-position: left center; transform-origin: 0 50%; }}
    #{cid}-bajada.texto {{ width: auto; font-size: 36px; font-weight: 600; letter-spacing: 0; color: rgba(255,255,255,0.78); }}
    #{cid}-raya {{ margin-top: 34px; width: 320px; height: 8px; border-radius: 8px; flex: none;
      background: linear-gradient(90deg, {m.ACENTO2}, {m.ACENTO}); transform-origin: 0 50%; }}
    #{cid}-pilares {{ margin-top: 46px; display: flex; flex-wrap: wrap; gap: 18px; }}
    .pilar {{ position: relative; height: 62px; padding: 0 26px 0 20px; display: flex; align-items: center; gap: 14px;
      border-radius: 999px; background: {rgba(m.ACENTO, 0.13)}; border: 1.5px solid {rgba(CLARO, 0.40)};
      color: #fff; font-size: 30px; font-weight: 700; white-space: nowrap; }}
    .pilar i {{ width: 14px; height: 14px; border-radius: 50%; background: {m.ACENTO}; box-shadow: 0 0 14px {m.ACENTO}; }}
    #{cid}-t {{ margin-top: 58px; width: 1100px; color: #fff; font-size: 74px; font-weight: 800; letter-spacing: -0.02em; line-height: 1.05; }}"""
    cuerpo = f"""    {hex_svg}
    <div class="vineta"></div>
    <div id="{cid}-col">
      <div id="{cid}-marca">
        <div id="{cid}-glow"></div>
        <div id="{cid}-anillo"></div>
        {logo}
      </div>
      {bajada}
      <div id="{cid}-raya"></div>
      <div id="{cid}-pilares">
{chips}
      </div>
      <div id="{cid}-t">{m.e(m.PROY["intro"]["titulo"])}</div>
    </div>"""
    pagina(cid, css, cuerpo, [j for j in js if j], voz)


def comp_cierre(dur: float) -> None:
    cid, conf, voz = "cierre", REALCE.get("cierre", {}), m.PROY["cierre"].get("voz")
    hex_svg, js_hex = hexagonos(cid, 960, 430, 7, 40)
    logo = marca(cid, "logo", conf.get("logo") or m.MARCA.get("logo"), m.PROY["nombre"], "")
    js = [f'tl.to("#{cid}-grid", {{ "--g-x": "-72px", "--g-y": "-144px", duration: {m.r(dur)}, ease: "none" }}, 0);',
          *js_hex,
          f'tl.to("#{cid}-hex", {{ opacity: 0.45, duration: 1.2, ease: "power1.inOut" }}, 1.6);' if hex_svg else "",
          f'tl.fromTo("#{cid}-logo", {{ clipPath: "inset(0% 50% 0% 50%)", scale: 0.94 }}, {{ clipPath: "inset(0% 0% 0% 0%)", scale: 1, duration: 1.2, ease: "power4.out" }}, 0.2);',
          *destello(cid, 1.0, 1.2),
          f'tl.fromTo("#{cid}-lema", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.9, ease: "power3.out" }}, 2.0);',
          f'tl.fromTo("#{cid}-pill", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.7, ease: "power3.out" }}, 2.4);',
          f'tl.to("#{cid}-logo", {{ scale: 1.03, duration: {m.r(dur - 1.4)}, ease: "none" }}, 1.4);']
    css = base_css(cid, 800, 600) + f"""
    #{cid}-col {{ position: absolute; left: 0; top: 0; width: 1920px; bottom: 120px; display: flex; flex-direction: column;
      justify-content: center; align-items: center; }}
    #{cid}-logo {{ display: block; width: 920px; max-height: 320px; object-fit: contain; transform-origin: 50% 50%; }}
    #{cid}-logo.texto {{ width: auto; font-size: 112px; line-height: 1; }}
    #{cid}-lema {{ margin-top: 56px; color: #fff; font-size: 52px; font-weight: 800; letter-spacing: -0.01em; text-align: center; }}
    #{cid}-pill {{ margin-top: 30px; display: flex; justify-content: center; }}
    #{cid}-pill span {{ padding: 12px 30px; border-radius: 999px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.18);
      color: rgba(255,255,255,0.74); font-size: 28px; font-weight: 600; }}"""
    cuerpo = f"""    {hex_svg}
    <div class="vineta"></div>
    <div id="{cid}-col">
      <div id="{cid}-marca">
        <div id="{cid}-glow"></div>
        <div id="{cid}-anillo"></div>
        {logo}
      </div>
      <div id="{cid}-lema">{m.e(m.PROY["cierre"]["titulo"])}</div>
      <div id="{cid}-pill"><span>{m.e(m.PROY["cierre"]["sub"])}</span></div>
    </div>"""
    pagina(cid, css, cuerpo, [j for j in js if j], voz)


def fondo_tarjetas() -> tuple[int, int]:
    """Tarjetas de capítulo con el fondo de marca de la intro (cuadrícula y brillos, CSS estático). Devuelve (con fondo, total)."""
    nuevo = ("{{ position: absolute; inset: 0; z-index: 10; background-image: "
             "linear-gradient({g} 1px, transparent 1px), linear-gradient(90deg, {g} 1px, transparent 1px), "
             "radial-gradient(1100px 680px at 82% 20%, {a2}3d, transparent 62%), radial-gradient(900px 600px at 8% 96%, {a}24, transparent 60%); "
             "background-size: 72px 72px, 72px 72px, auto, auto; background-color: {f}; }}").format(
        g=rgba(m.ACENTO, 0.09), a=m.ACENTO, a2=m.ACENTO2, f=m.FONDO).replace("{{", "{").replace("}}", "}")
    hechas = total = 0
    for cap in LINEA["capitulos"][1:-1]:
        f = m.COMP / f"{cap['id']}.html"
        total += 1
        s = f.read_text()
        viejo = f"#{cap['id']}-card {{ position: absolute; inset: 0; background: {m.FONDO}; z-index: 10; }}"
        if viejo in s:
            f.write_text(s.replace(viejo, f"#{cap['id']}-card {nuevo}"))
        if f"#{cap['id']}-card {nuevo}" in f.read_text():
            hechas += 1
    return hechas, total


# ---------------------------------------------------------------- sonido
def envolvente(voces: list[tuple[float, float]], total: float) -> list[dict]:
    """Música a 1 sin voz, a MUSICA_BAJO bajo la voz (con rampas); los huecos de más de 1,6 s la dejan subir a 0,85."""
    voces = sorted(voces)
    pts = [{"t": 0, "v": 1}]
    for k, (a, b) in enumerate(voces):
        pts += [{"t": round(max(0.0, a - 0.35), 2), "v": 1 if k == 0 or a - voces[k - 1][1] > 1.6 else MUSICA_BAJO},
                {"t": round(a, 2), "v": MUSICA_BAJO}]
        sig = voces[k + 1][0] if k + 1 < len(voces) else total
        if sig - b > 1.6:
            pts += [{"t": round(b + 0.25, 2), "v": MUSICA_BAJO}, {"t": round(b + 0.75, 2), "v": 0.85}]
    limpio: list[dict] = []
    for p in pts:   # tiempos crecientes, sin duplicados (gana el volumen más bajo)
        if limpio and p["t"] <= limpio[-1]["t"]:
            limpio[-1] = {"t": limpio[-1]["t"], "v": min(limpio[-1]["v"], p["v"])}
            continue
        limpio.append(p)
    return limpio


def duracion(f: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def clip(id_: str, src: str, t: float, dur: float, vol: float, pista: int, extra: str = "") -> str:
    return (f'      <audio id="{id_}" class="clip" src="{src}" data-start="{m.r(t)}" data-duration="{m.r(dur)}" '
            f'data-volume="{vol}"{extra} data-track-index="{pista}"></audio>')


def efectos() -> list[str]:
    if not REALCE.get("efectos", True):
        return []
    faltan = [s for s in SFX if not (SFX_ORIGEN / s).exists()]
    if faltan:
        print(f"  ⚠ sin efectos: faltan {faltan} en {SFX_ORIGEN} (sonidos de la skill media-use)")
        return []
    dest = RAIZ / "assets" / "sfx"
    dest.mkdir(parents=True, exist_ok=True)
    for s in SFX:
        shutil.copyfile(SFX_ORIGEN / s, dest / s)
    caps = LINEA["capitulos"]
    out = [clip("sfx-logo-intro", "assets/sfx/impact-bass-1.mp3", 1.0, 1.6, 0.32, 11)]
    out += [clip(f"sfx-cap-{c['id']}", "assets/sfx/whoosh-short.mp3", c["inicio"] + 0.05, 0.57, 0.38, 12 + k % 2)
            for k, c in enumerate(caps[1:-1])]
    c = caps[-1]
    out += [clip("sfx-cierre", "assets/sfx/whoosh.mp3", c["inicio"], 0.57, 0.34, 11),
            clip("sfx-logo-cierre", "assets/sfx/impact-bass-1.mp3", c["inicio"] + 1.0, 1.6, 0.30, 14)]
    return out


def musica(total: float) -> list[str]:
    carpeta = RAIZ / "assets" / "musica"
    pistas = sorted(carpeta.glob("fondo.*")) if carpeta.exists() else []
    if not pistas:
        print("  · sin música: no hay video/assets/musica/fondo.* (se monta sin ella)")
        return []
    dur = duracion(pistas[0])
    if dur < total - 0.5:
        print(f"  ⚠ la música dura {dur:.1f} s y el video {total:.1f} s: alárgala (referencias/trampas.md → Música)")
    voces = [(v["t"], v["t"] + v["dur"]) for v in LINEA["voces"]]
    lane = json.dumps({"version": 1, "lanes": [{"target": "volume", "points": envolvente(voces, total)}]}).replace('"', "&quot;")
    return [clip("musica", f"assets/musica/{pistas[0].name}", 0, total, MUSICA_VOL, 10,
                 f' data-fade-in="0.6" data-fade-out="3.0" data-automation="{lane}"')]


# ---------------------------------------------------------------- principal
def main() -> None:
    caps = {c["id"]: c for c in LINEA["capitulos"]}
    if "intro" not in caps or "cierre" not in caps:
        raise SystemExit("realce: corre primero `python3 montar.py` (no hay intro y cierre en linea-de-tiempo.json)")
    comp_intro(caps["intro"]["fin"] - caps["intro"]["inicio"])
    comp_cierre(caps["cierre"]["fin"] - caps["cierre"]["inicio"])
    hechas, total = fondo_tarjetas()
    if hechas != total:
        print(f"  ⚠ fondo de marca en {hechas} de {total} tarjetas: cambió el CSS de la tarjeta en montar.py")
    idx = RAIZ / "index.html"
    s = re.sub(r'\n      <audio id="(sfx-[^"]+|musica)"[^\n]*</audio>', "", idx.read_text())   # idempotente
    fin_voces = s.rindex("</audio>") + len("</audio>")
    nuevas = efectos() + musica(LINEA["total_s"])
    s = s[:fin_voces] + "".join("\n" + x for x in nuevas) + s[fin_voces:]
    idx.write_text(s)
    n_sfx = s.count('id="sfx-')
    con_musica = "sí" if 'id="musica"' in s else "no"
    print(f"realce listo: intro {caps['intro']['fin']:.1f} s · cierre {caps['cierre']['fin'] - caps['cierre']['inicio']:.1f} s · "
          f"tarjetas {hechas}/{total} · {n_sfx} efectos · música: {con_musica}")


if __name__ == "__main__":
    main()
