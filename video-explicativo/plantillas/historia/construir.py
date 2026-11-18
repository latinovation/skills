"""Genera el video «historia con datos reales» (conversaciones de un asistente que terminaron en resultado) desde historia.json.

    python3 construir.py h     → film/   (1920×1080)
    python3 construir.py v     → film-v/ (1080×1920)

Cada capítulo = un caso real: ceja (fecha · lugar), nombre de pila, la pregunta del cliente en grande que «cae» al chat, el hilo
de mensajes apareciendo, un riel con los pasos que dio el asistente y la tarjeta del resultado. Luego un resumen con las cifras
(de una consulta, nunca a mano) y el cierre con el logo. Sin voz: el ritmo sale del largo de cada texto (tiempo de lectura).
Sonidos: tic en cada mensaje del cliente, pop en cada resultado y fila del resumen, whoosh entre escenas (assets/sfx/).
Escribe <film>/index.html, <film>/compositions/*.html, <film>/package.json y <film>/linea-de-tiempo.json.
"""
from __future__ import annotations

import html
import json
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
H = json.loads((RAIZ / "historia.json").read_text())
M = H["marca"]
AS = H["asistente"]
FPS = 30
# Sonidos de media-use (Pixabay, uso comercial): (archivo, pico en s, largo en s) medidos con `hyperframes audio`.
SFX = {"pop": ("assets/sfx/pop.mp3", 0.12, 0.72), "whoosh": ("assets/sfx/whoosh.mp3", 0.162, 0.575),
       "tick": ("assets/sfx/click.mp3", 0.073, 0.366)}
VOLUMEN = {"tick": 0.35, "pop": 0.7, "whoosh": 0.45}
LAYOUTS = {
    "h": {"dir": "film", "w": 1920, "h": 1080, "panel": (1100, 60, 700, 960), "rail_left": 120, "rail_w": 860,
          "rail_top": 92, "steps_top": 300, "q_top": 300, "result_bottom": 92, "name_px": 96, "q_px": 60, "q_px_long": 50,
          "step_px": 36, "msg_px": 28, "bg_pos": "50% 50%"},
    "v": {"dir": "film-v", "w": 1080, "h": 1920, "panel": (60, 880, 960, 980), "rail_left": 80, "rail_w": 920,
          "rail_top": 180, "steps_top": 370, "q_top": 370, "result_bottom": None, "name_px": 92, "q_px": 58, "q_px_long": 50,
          "step_px": 36, "msg_px": 30, "bg_pos": "100% 50%"},
}
FOTO_ICONO = ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="4.5" width="18" height="15" rx="2.5" fill="none" '
              'stroke="#FFFFFF" stroke-width="1.8"/><circle cx="8.5" cy="9.5" r="1.8" fill="#FFFFFF"/><path d="M4.5 17.5 L10 12 '
              'L13.5 15.5 L16 13 L19.5 16.5" fill="none" stroke="#FFFFFF" stroke-width="1.8" stroke-linejoin="round" '
              'stroke-linecap="round"/></svg>')


def rgba(hex_: str, a: float) -> str:
    h = hex_.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


def palabras(t: str) -> int:
    return len(re.findall(r"\S+", t))


def esc(t: str) -> str:
    return html.escape(t, quote=True)


def md(t: str) -> str:
    """**negrita** del texto real → <strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(t))


def resaltar(t: str) -> str:
    """**x** → color de resalte (para el cierre del resumen)."""
    return re.sub(r"\*\*(.+?)\*\*", r'<span class="acc">\1</span>', esc(t))


def sin_corte_guion(t: str) -> str:
    return re.sub(r"\b(\w+(?:-\w+)+)\b", r'<span style="white-space: nowrap">\1</span>', t)


def acento(t: str, palabra: str | None) -> str:
    out = esc(t)
    return out.replace(esc(palabra), f'<span class="acc">{esc(palabra)}</span>', 1) if palabra else out


def revisar_texto() -> None:
    blob = json.dumps(H["capitulos"], ensure_ascii=False) + json.dumps(H["resumen"], ensure_ascii=False) + json.dumps(H["intro"], ensure_ascii=False)
    for malo in H.get("texto_prohibido", []):
        if malo in blob:
            raise SystemExit(f"Texto prohibido por la marca en historia.json: «{malo}»")
    for cap in H["capitulos"]:
        if not any(m[2].get("result") for m in cap["mensajes"]):
            raise SystemExit(f"{cap['id']}: ningún mensaje lleva {{\"result\": true}}")


# ---------------------------------------------------------------- CSS común
def fuentes() -> str:
    return "".join(f'@font-face {{ font-family: "{f["familia"]}"; src: url("{f["archivo"]}"); font-weight: {f["peso"]}; }}\n'
                   for f in M["fuentes"])


def css_base(L: dict) -> str:
    px, py, pw, ph = L["panel"]
    m = L["msg_px"]
    T, TT = M["familia_texto"], M["familia_titulos"]
    F, S, P, O, I, R = M["fondo"], M["suave"], M["primario"], M["oscuro"], M["tinta"], M["resalte"]
    return fuentes() + f"""
#root {{ position: absolute; inset: 0; overflow: hidden; font-family: "{T}", sans-serif; background: {F}; }}
.bg {{ position: absolute; left: 0; top: 0; width: {L['w']}px; height: {L['h']}px; object-fit: cover; object-position: {L['bg_pos']}; }}
.scrim {{ position: absolute; inset: 0; background: {F}; opacity: 0.97; }}
.eyebrow {{ font-family: "{TT}"; font-weight: 600; font-size: 30px; letter-spacing: 0.06em; text-transform: uppercase; color: {S}; }}
.name {{ font-family: "{TT}"; font-weight: 600; font-size: {L['name_px']}px; line-height: 1; text-transform: uppercase; color: #FFFFFF; margin-top: 12px; }}
.acc {{ color: {R}; }}
.panel {{ position: absolute; left: {px}px; top: {py}px; width: {pw}px; height: {ph}px; background: rgba(255,255,255,0.80);
  backdrop-filter: blur(24px) saturate(1.4); border: 1px solid rgba(255,255,255,0.65); border-radius: 20px;
  box-shadow: 0 30px 70px rgba(12,24,30,0.45), inset 0 1px 0 rgba(255,255,255,0.85); overflow: hidden; display: flex; flex-direction: column; }}
.header {{ background: {rgba(O, 0.92)}; color: #FFFFFF; padding: 24px 28px; font-weight: 600; font-size: {m + 2}px; display: flex;
  align-items: center; gap: 16px; border-bottom: 1px solid rgba(255,255,255,0.18); }}
.dot {{ width: 14px; height: 14px; border-radius: 50%; background: {S}; box-shadow: 0 0 0 5px {rgba(S, 0.35)}; }}
.vp {{ flex: 1; position: relative; overflow: hidden; }}
.thread {{ position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: flex-end; }}
.stack {{ flex-shrink: 0; min-height: 100%; padding: 26px 24px 70px; display: flex; flex-direction: column; gap: 16px; }}
.stack > .msg, .stack > .card, .stack > .photo {{ display: none; }}
.hint {{ color: {I}; font-size: {m}px; line-height: 1.45; padding: 0 4px; }}
.msg {{ max-width: 85%; padding: 15px 22px; border-radius: 20px; font-size: {m}px; line-height: 1.42; white-space: pre-wrap; overflow-wrap: break-word; }}
.u {{ align-self: flex-end; background: {P}; color: #FFFFFF; box-shadow: 0 6px 18px {rgba(O, 0.2)}; transform-origin: right bottom; }}
.photo {{ display: none; align-self: flex-end; align-items: center; gap: 14px; background: {P}; color: #FFFFFF; border-radius: 20px;
  padding: 15px 22px; font-size: {m}px; font-weight: 600; transform-origin: right bottom; }}
.photo svg {{ width: {m + 10}px; height: {m + 10}px; flex-shrink: 0; }}
.a {{ align-self: flex-start; background: rgba(255,255,255,0.94); border: 2px solid {rgba(S, 0.7)}; color: {I}; transform-origin: left bottom; }}
.a strong {{ font-weight: 600; color: {O}; }}
.card {{ align-self: flex-start; max-width: 85%; border: 2px solid {rgba(S, 0.7)}; border-radius: 16px; padding: 18px 20px; background: rgba(255,255,255,0.94); transform-origin: left bottom; }}
.card-title {{ font-weight: 600; font-size: {m}px; color: {O}; margin-bottom: 12px; }}
.card-link {{ display: inline-block; font-size: {m}px; font-weight: 600; color: #FFFFFF; background: {P}; padding: 10px 20px; border-radius: 14px; }}
.typing {{ opacity: 0; position: absolute; left: 28px; bottom: 14px; font-size: {m}px; color: {P}; }}
.inrow {{ display: flex; gap: 14px; padding: 18px; border-top: 1px solid {rgba(S, 0.6)}; background: rgba(255,255,255,0.55); }}
.input {{ flex: 1; border: 2px solid {rgba(S, 0.8)}; border-radius: 16px; background: rgba(255,255,255,0.9); padding: 16px 20px; font-size: {m}px; color: {rgba(I, 0.6)}; }}
.send {{ border-radius: 16px; background: {P}; color: #FFFFFF; font-size: {m}px; font-weight: 600; padding: 16px 24px; }}
"""


def fondo_html() -> str:
    img = M.get("fondo_imagen")
    return (f'<img class="bg" src="{esc(img)}" alt="" />\n  ' if img else "") + '<div class="scrim"></div>'


def panel_html(pref: str, items: str) -> str:
    return f"""
  <div class="panel" id="{pref}-panel">
    <div class="header" data-layout-allow-occlusion><span class="dot"></span><span>{esc(AS['nombre'])}</span></div>
    <div class="vp" id="{pref}-vp" data-layout-allow-overflow>
      <div class="thread" id="{pref}-thread"><div class="stack" id="{pref}-stack">
        <p class="hint">{esc(AS['saludo'])}</p>{items}
      </div></div>
      <span class="typing" id="{pref}-typing">{esc(AS['escribiendo'])}</span>
    </div>
    <div class="inrow" data-layout-allow-occlusion><div class="input">{esc(AS['placeholder'])}</div><div class="send">{esc(AS['enviar'])}</div></div>
  </div>"""


def escena_doc(cid: str, L: dict, css: str, cuerpo: str, script: str) -> str:
    return f"""<template>
  <style>{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{L['w']}" data-height="{L['h']}">{cuerpo}
  </div>
  <script>{script}
  </script>
</template>
"""


# ---------------------------------------------------------------- capítulos
def tiempos_capitulo(cap: dict) -> tuple[list[dict], dict]:
    """Eventos con tiempo local y marcas (q_in, q_out, result, end). El ritmo sale del largo de cada texto."""
    q_pal = palabras(cap["pregunta"]) + (palabras(cap["pregunta_sub"]) if cap.get("pregunta_sub") else 0)
    q_in = 0.45
    t = q_in + min(4.4, 0.6 + 0.3 * q_pal)
    marcas = {"q_in": q_in, "q_out": t}
    eventos: list[dict] = []
    for i, (rol, texto, extra) in enumerate(cap["mensajes"]):
        if i == 0:
            t += 0.25   # la pregunta gigante «cae» al chat
        if rol == "a":
            eventos.append({"kind": "typing", "t": round(t, 3), "dur": 0.6})
            t += 0.6
        eventos.append({"kind": rol, "i": i, "t": round(t, 3)})
        n = palabras(texto)
        if rol in ("u", "photo"):
            espera = min(1.8, max(0.95, 0.6 + 0.08 * n))
        elif rol == "a":
            espera = min(2.9, max(1.35, 0.8 + 0.055 * n))
        else:
            espera = 1.3
        for clave in ("step", "step2"):
            if clave in extra:
                st = t + 0.3 + (0.9 if clave == "step2" else 0)
                eventos.append({"kind": "step", "i": extra[clave], "t": round(st, 3)})
                espera = max(espera, (st - t) + 1.1)
        if extra.get("result"):
            marcas["result"] = round(t + 0.5, 3)
            espera = max(espera, 0.5 + 3.8)
        t += espera
    marcas["end"] = round(t + 0.55, 2)
    return eventos, marcas


def capitulo_html(cap: dict, L: dict) -> tuple[str, float, list[tuple[str, float]]]:
    pref = cap["id"]
    eventos, marcas = tiempos_capitulo(cap)
    items = []
    for i, (rol, texto, _extra) in enumerate(cap["mensajes"]):
        if rol == "photo":
            items.append(f'\n        <div class="photo" id="{pref}-m{i}">{FOTO_ICONO}<span>{esc(texto)}</span></div>')
        elif rol == "card":
            items.append(f'\n        <div class="card" id="{pref}-m{i}"><div class="card-title">{esc(texto)}</div>'
                         f'<span class="card-link">{esc(AS["enlace"])}</span></div>')
        else:
            items.append(f'\n        <div class="msg {rol}" id="{pref}-m{i}">{md(texto)}</div>')
    pasos = "".join(f'\n      <div class="step" id="{pref}-s{k}"><span class="mark"></span><div class="lab">{esc(lab)}</div>'
                    f'<div class="txt">{acento(txt, acc)}</div></div>' for k, (lab, txt, acc) in enumerate(cap["pasos"]))
    q_px = L["q_px_long"] if palabras(cap["pregunta"]) > 8 else L["q_px"]
    sub = f'<div class="qsub">{esc(cap["pregunta_sub"])}</div>' if cap.get("pregunta_sub") else ""
    rlab, rtxt = cap["resultado"]
    left, rw = L["rail_left"], L["rail_w"]
    vertical = L["h"] > L["w"]
    pos_res = (f"left: {left}px; bottom: {L['result_bottom']}px;" if not vertical
               else f"left: {left}px; top: {(L['steps_top'] + L['panel'][1]) // 2 - 90}px;")
    S, P, O, TT = M["suave"], M["primario"], M["oscuro"], M["familia_titulos"]
    css = css_base(L) + f"""
.rail {{ position: absolute; left: {left}px; top: {L['rail_top']}px; width: {rw}px; }}
.q {{ position: absolute; left: {left}px; top: {L['q_top']}px; width: {rw}px; font-weight: 600; font-size: {q_px}px; line-height: 1.16; color: #FFFFFF; }}
.qsub {{ font-weight: 400; font-size: 40px; color: {S}; margin-top: 14px; }}
.steps {{ position: absolute; left: {left}px; top: {L['steps_top']}px; width: {rw}px; display: flex; flex-direction: column; gap: 20px; }}
.step {{ position: relative; padding-left: 40px; }}
.mark {{ position: absolute; left: 0; top: 8px; width: 16px; height: 16px; border-radius: 50%; background: {S}; }}
.step .lab {{ font-family: "{TT}"; font-weight: 600; font-size: 28px; letter-spacing: 0.06em; text-transform: uppercase; color: {S}; }}
.step .txt {{ font-weight: 600; font-size: {L['step_px']}px; line-height: 1.22; color: #FFFFFF; margin-top: 4px; }}
.result {{ position: absolute; {pos_res} width: {rw}px; background: #FFFFFF; border-radius: 4px; padding: 24px 32px 26px; border-left: 12px solid {P}; box-shadow: 0 18px 40px rgba(12,24,30,0.35); }}
.result .lab {{ font-family: "{TT}"; font-weight: 600; font-size: 30px; letter-spacing: 0.06em; text-transform: uppercase; color: {P}; }}
.result .txt {{ font-weight: 700; font-size: 42px; line-height: 1.15; color: {O}; margin-top: 6px; text-wrap: balance; }}
"""
    cuerpo = f"""
  {fondo_html()}
  <div class="rail" id="{pref}-rail">
    <div class="eyebrow" id="{pref}-eyebrow">{esc(cap['ceja'])}</div>
    <div class="name" id="{pref}-name">{esc(cap['nombre'])}</div>
  </div>
  <div class="q" id="{pref}-q" data-hold>{esc(cap['pregunta'])}{sub}</div>
  <div class="steps" id="{pref}-steps">{pasos}
  </div>
  <div class="result" id="{pref}-result" data-hold><div class="lab">{esc(rlab)}</div><div class="txt">{sin_corte_guion(esc(rtxt))}</div></div>
{panel_html(pref, ''.join(items))}"""
    plan = {"pref": pref, "events": eventos, "marks": marcas, "dur": marcas["end"], "vertical": vertical}
    sfx = [("tick", ev["t"]) for ev in eventos if ev["kind"] in ("u", "photo")] + [("pop", marcas["result"])]
    return escena_doc(pref, L, css, cuerpo, JS_CAPITULO.replace("__PLAN__", json.dumps(plan))), marcas["end"], sfx


JS_CAPITULO = r"""
const P = __PLAN__;
const $ = (s) => document.querySelector(s);
const tl = gsap.timeline({ paused: true });
const id = (s) => "#" + P.pref + "-" + s;
const M = P.marks;
tl.fromTo(id("eyebrow"), { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, 0.1);
tl.fromTo(id("name"), { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.22, ease: "power4.out" }, 0.22);
tl.fromTo(id("q"), { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, M.q_in);
// La pregunta viaja hacia el chat y se vuelve la primera burbuja.
tl.to(id("q"), { x: P.vertical ? 0 : 160, y: P.vertical ? 260 : 0, opacity: 0, filter: "blur(6px)", duration: 0.4, ease: "power3.in" }, M.q_out - 0.15);
const typing = $(id("typing"));
for (const ev of P.events) {
  if (ev.kind === "typing") { tl.set(typing, { opacity: 1 }, ev.t); tl.set(typing, { opacity: 0 }, ev.t + ev.dur); continue; }
  if (ev.kind === "step") {
    const s = id("s" + ev.i);
    tl.fromTo(s + " .mark", { scale: 0 }, { scale: 1, duration: 0.3, ease: "back.out(2)" }, ev.t);
    tl.fromTo(s + " .lab", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.out" }, ev.t);
    tl.fromTo(s + " .txt", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }, ev.t + 0.1);
    continue;
  }
  const el = id("m" + ev.i);
  tl.set(el, { display: ev.kind === "photo" ? "flex" : "block" }, ev.t);
  tl.fromTo(el, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.24, ease: "back.out(1.6)" }, ev.t);
}
for (let k = 0; k < 8; k++) {
  if (!$(id("s" + k))) break;
  tl.set(id("s" + k) + " .lab", { opacity: 0 }, 0);
  tl.set(id("s" + k) + " .txt", { opacity: 0 }, 0);
  tl.set(id("s" + k) + " .mark", { scale: 0 }, 0);
}
tl.fromTo(id("result"), { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 0.5, ease: "expo.out" }, M.result);
if (P.vertical) tl.to(id("steps"), { opacity: 0, duration: 0.25, ease: "power2.out" }, M.result - 0.1);
const out = P.dur - 0.5;
tl.to([id("rail"), id("steps"), id("result")], { opacity: 0, filter: "blur(8px)", duration: 0.3, ease: "power3.in" }, out);
tl.fromTo(id("stack"), { y: 0, opacity: 1 }, { y: -260, opacity: 0, duration: 0.4, ease: "power3.in", immediateRender: false }, out);
window.__timelines[P.pref] = tl;
"""


# ---------------------------------------------------------------- intro, resumen y cierre
def intro_html(L: dict) -> tuple[str, float, list[tuple[str, float]]]:
    """Clic en el botón del chat sobre el fondo; el color de marca inunda la pantalla desde ahí y entra el título."""
    vertical = L["h"] > L["w"]
    fx, fy = H["intro"].get("boton_v" if vertical else "boton_h") or [L["w"] - 50, L["h"] - 50]
    left, rw = L["rail_left"], L["rail_w"]
    top = 300 if not vertical else 290
    TT = M["familia_titulos"]
    it = H["intro"]
    # Tamaño del título por su largo (con una tipografía ancha, 132 px parte en 3 líneas un título de 20+ letras).
    n = len(it["titulo"])
    titulo_px = it.get("titulo_px") or (132 if n <= 16 else 104 if n <= 26 else 84) - (12 if vertical else 0)
    css = css_base(L) + f"""
.cam {{ position: absolute; inset: 0; transform-origin: {fx}px {fy}px; }}
.flood {{ position: absolute; inset: 0; background: {M['fondo']}; opacity: 0.97; clip-path: circle(0px at {fx}px {fy}px); }}
.cursor {{ position: absolute; left: {fx - 6}px; top: {fy - 4}px; width: 64px; height: 64px; }}
.t-block {{ position: absolute; left: {left}px; top: {top - 70}px; width: {rw}px; display: flex; flex-direction: column; }}
.t-title {{ margin-top: 30px; font-family: "{TT}"; font-weight: 600; font-size: {titulo_px}px; line-height: 0.98; text-transform: uppercase; color: #FFFFFF; }}
.t-sub {{ margin-top: 48px; width: {rw - 60}px; font-weight: 600; font-size: 44px; line-height: 1.25; color: #FFFFFF; }}
.t-note {{ margin-top: 40px; font-size: 30px; color: {M['suave']}; }}
.w {{ display: inline-block; }}
"""
    tw = " ".join(f'<span class="w" id="in-w{i}">{esc(w)}</span>' for i, w in enumerate(it["titulo"].split()))
    img = M.get("fondo_imagen")
    cuerpo = f"""
  <div class="cam" id="in-cam">{f'<img class="bg" src="{esc(img)}" alt="" />' if img else ''}</div>
  <div class="flood" id="in-flood"></div>
  <div class="t-block">
    <div class="eyebrow" id="in-eyebrow">{esc(it['ceja'])}</div>
    <div class="t-title" id="in-title" data-hold>{tw}</div>
    <div class="t-sub" id="in-sub">{esc(it['sub'])}</div>
    <div class="t-note" id="in-note">{esc(it['nota'])}</div>
  </div>
{panel_html('in', '')}
  <svg class="cursor" id="in-cursor" viewBox="0 0 24 24"><path d="M4 2 L4 19 L8.5 15 L11.5 22 L14.5 20.7 L11.6 14 L18 14 Z" fill="#FFFFFF" stroke="#2D2D2C" stroke-width="1.4" stroke-linejoin="round"/></svg>"""
    dur = 6.6
    script = f"""
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#in-cam", {{ scale: 1 }}, {{ scale: 1.35, duration: 1.2, ease: "power2.inOut" }}, 0.3);
tl.fromTo("#in-cursor", {{ x: 220, y: 160 }}, {{ x: 0, y: 0, duration: 0.9, ease: "expo.out" }}, 0.4);
tl.to("#in-cursor", {{ scale: 0.86, duration: 0.07, ease: "power2.in", transformOrigin: "10% 10%" }}, 1.42);
tl.to("#in-cursor", {{ scale: 1, duration: 0.12, ease: "power2.out" }}, 1.49);
tl.fromTo("#in-flood", {{ clipPath: "circle(0px at {fx}px {fy}px)" }}, {{ clipPath: "circle(2400px at {fx}px {fy}px)", duration: 0.8, ease: "power2.inOut" }}, 1.5);
tl.to("#in-cam", {{ scale: 1, duration: 0.8, ease: "power2.inOut" }}, 1.5);
tl.to("#in-cursor", {{ opacity: 0, duration: 0.2 }}, 1.7);
tl.fromTo("#in-panel", {{ opacity: 0, y: 40, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.6, ease: "expo.out", transformOrigin: "100% 100%" }}, 1.75);
tl.fromTo("#in-eyebrow", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 2.15);
gsap.utils.toArray("#in-title .w").forEach((w, i) => tl.fromTo(w, {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.16, ease: "power4.out" }}, 2.3 + i * 0.09));
tl.fromTo("#in-sub", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 2.9);
tl.fromTo("#in-note", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3, ease: "power2.out" }}, 3.3);
tl.to(["#in-eyebrow", "#in-title", "#in-sub", "#in-note"], {{ opacity: 0, filter: "blur(8px)", duration: 0.28, ease: "power3.in" }}, {dur - 0.45});
window.__timelines["intro"] = tl;
"""
    return escena_doc("intro", L, css, cuerpo, script), dur, [("tick", 1.45)]


def resumen_html(L: dict) -> tuple[str, float, list[tuple[str, float]]]:
    vertical = L["h"] > L["w"]
    left = L["rail_left"]
    ancho = L["w"] - 2 * left
    filas = H["resumen"]["filas"]
    TT = M["familia_titulos"]
    css = css_base(L) + f"""
.r-eyebrow {{ position: absolute; left: {left}px; top: {96 if not vertical else 200}px; }}
.rows {{ position: absolute; left: {left}px; top: {150 if not vertical else 260}px; width: {ancho}px; display: flex; flex-direction: column; }}
.row {{ display: grid; grid-template-columns: {'240px 1fr 1.2fr' if not vertical else 'auto 1fr'}; align-items: baseline; column-gap: 24px; row-gap: 2px; padding: {'13px 0' if not vertical else '16px 0'}; border-bottom: 2px solid {rgba(M['suave'], 0.35)}; }}
.row .n {{ font-family: "{TT}"; font-weight: 600; font-size: {46 if not vertical else 50}px; line-height: 1; text-transform: uppercase; color: #FFFFFF; }}
.row .p {{ font-size: {29 if not vertical else 28}px; color: {M['suave']}; }}
.row .o {{ font-weight: 600; font-size: {32 if not vertical else 34}px; color: #FFFFFF; {'grid-column: 1 / -1;' if vertical else ''} }}
.close {{ position: absolute; left: {left}px; top: {868 if not vertical else 1360}px; width: {ancho}px; font-weight: 700; font-size: {46 if not vertical else 52}px; line-height: 1.15; color: #FFFFFF; }}
"""
    filas_html = "".join(f'\n    <div class="row" id="rc-r{i}"><div class="n">{esc(n)}</div><div class="p">{esc(p)}</div><div class="o">{esc(o)}</div></div>'
                         for i, (n, p, o) in enumerate(filas))
    cuerpo = f"""
  {fondo_html()}
{panel_html('rc', '')}
  <div class="eyebrow r-eyebrow" id="rc-eyebrow">{esc(H['resumen']['ceja'])}</div>
  <div class="rows" id="rc-rows">{filas_html}
  </div>
  <div class="close" id="rc-close" data-hold>{resaltar(H['resumen']['cierre'])}</div>"""
    paso = 0.4
    cierre_t = 0.75 + len(filas) * paso + 0.35
    dur = round(cierre_t + 5.4, 2)
    script = f"""
const tl = gsap.timeline({{ paused: true }});
tl.fromTo("#rc-panel", {{ x: 0, opacity: 1 }}, {{ x: 900, opacity: 0, duration: 0.55, ease: "power3.in" }}, 0.05);
tl.fromTo("#rc-eyebrow", {{ opacity: 0, filter: "blur(6px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.2, ease: "power4.out" }}, 0.5);
for (let i = 0; i < {len(filas)}; i++) {{
  tl.fromTo("#rc-r" + i, {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.22, ease: "power4.out" }}, 0.75 + i * {paso});
}}
tl.fromTo("#rc-close", {{ opacity: 0, filter: "blur(8px)" }}, {{ opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power4.out" }}, {cierre_t});
tl.to(["#rc-eyebrow", "#rc-rows", "#rc-close"], {{ opacity: 0, filter: "blur(8px)", duration: 0.3, ease: "power3.in" }}, {dur - 0.45});
window.__timelines["recap"] = tl;
"""
    return escena_doc("recap", L, css, cuerpo, script), dur, [("pop", 0.75 + i * paso) for i in range(len(filas))]


def fin_html(L: dict) -> tuple[str, float, list[tuple[str, float]]]:
    vertical = L["h"] > L["w"]
    lw = 560 if not vertical else 640
    logo = M.get("logo")
    marca = (f'<img class="logo" id="end-logo" src="{esc(logo)}" alt="{esc(H["nombre"])}" />' if logo
             else f'<div class="logo nombre" id="end-logo">{esc(H["nombre"])}</div>')
    css = css_base(L) + f"""
.fin {{ position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 36px; padding: 0 {L['rail_left']}px; }}
.logo {{ width: {lw}px; }}
.logo.nombre {{ width: auto; text-align: center; color: #FFFFFF; font-family: "{M['familia_titulos']}"; font-weight: 600; font-size: {84 if len(H['nombre']) <= 18 else 60}px; line-height: 1.05; text-wrap: balance; }}
.tag {{ text-align: center; font-weight: 600; font-size: 40px; color: {M['suave']}; }}
"""
    cuerpo = f"""
  <div class="fin">
    {marca}
    <div class="tag" id="end-tag">{esc(H['fin']['lema'])}</div>
  </div>"""
    script = """
const tl = gsap.timeline({ paused: true });
tl.fromTo("#end-logo", { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 0.8, ease: "expo.out" }, 0.25);
tl.fromTo("#end-tag", { opacity: 0, filter: "blur(8px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.25, ease: "power4.out" }, 1.0);
window.__timelines["end"] = tl;
"""
    return escena_doc("end", L, css, cuerpo, script), 5.0, [("pop", 0.3)]


# ---------------------------------------------------------------- raíz
def construir(fmt: str) -> None:
    revisar_texto()
    L = LAYOUTS[fmt]
    out = RAIZ / L["dir"]
    (out / "compositions").mkdir(parents=True, exist_ok=True)
    if (out / "assets").exists():
        shutil.rmtree(out / "assets")
    shutil.copytree(RAIZ / "assets", out / "assets")
    shutil.copyfile(RAIZ / "hyperframes.json", out / "hyperframes.json")
    escenas = [("intro", *intro_html(L))]
    escenas += [(c["id"], *capitulo_html(c, L)) for c in H["capitulos"]]
    escenas += [("recap", *resumen_html(L)), ("end", *fin_html(L))]
    hosts, audio, linea, t, n_audio = [], [], [], 0.0, 0
    for z, (sid, doc, d, sfx) in enumerate(escenas):
        (out / "compositions" / f"{sid}.html").write_text(doc)
        d = round(round(d * FPS) / FPS, 4)   # escenas en cuadros enteros: las uniones caen en cuadro exacto
        hosts.append(f'      <div id="{sid}" class="clip" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" '
                     f'data-start="{t:.4f}" data-duration="{d}" data-track-index="1" data-track-kind="graphics" '
                     f'data-width="{L["w"]}" data-height="{L["h"]}" style="z-index:{z + 1}"></div>')
        for tipo, lt in ([("whoosh", 0.0)] if z > 0 else []) + list(sfx):
            src, pico, largo = SFX[tipo]
            n_audio += 1
            pista = 3 if tipo == "tick" else (2 if n_audio % 2 else 4)
            audio.append(f'      <audio id="sfx{n_audio}" class="clip" src="{src}" data-start="{max(0.0, t + lt + 1 / FPS - pico):.3f}" '
                         f'data-duration="{largo}" data-track-index="{pista}" data-volume="{VOLUMEN[tipo]}"></audio>')
        linea.append({"id": sid, "inicio": round(t, 2), "fin": round(t + d, 2)})
        t += d
    total = round(t, 3)
    (out / "index.html").write_text(f"""<!doctype html>
<html lang="{H.get('idioma', 'es')}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={L['w']}, height={L['h']}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {L['w']}px; height: {L['h']}px; overflow: hidden; background: {M['fondo']}; }}
      #root {{ position: relative; width: 100%; height: 100%; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="{L['w']}" data-height="{L['h']}">
{chr(10).join(hosts)}
{chr(10).join(audio)}
    </div>
    <script>
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
""")
    v = H["hyperframes"]
    (out / "package.json").write_text(json.dumps({"name": f"video-historia-{fmt}", "private": True, "type": "module", "scripts": {
        "dev": f"npx --yes hyperframes@{v} preview", "check": f"npx --yes hyperframes@{v} check",
        "render": f"npx --yes hyperframes@{v} render", "snapshot": f"npx --yes hyperframes@{v} snapshot"}}, indent=2) + "\n")
    (out / "linea-de-tiempo.json").write_text(json.dumps({"total_s": total, "idioma": H.get("idioma", "es"), "escenas": linea},
                                                         ensure_ascii=False, indent=1))
    print(f"{fmt}: {total:.1f} s · " + ", ".join(f"{e['id']} {e['fin'] - e['inicio']:.1f}" for e in linea))


if __name__ == "__main__":
    construir(sys.argv[1] if len(sys.argv) > 1 else "h")
