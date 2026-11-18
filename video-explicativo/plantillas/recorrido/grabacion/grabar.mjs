// Motor de grabación del recorrido (genérico: NO se edita por proyecto; lo propio de la app va en tomas.mjs).
//
//   node grabar.mjs --toma <nombre>     graba una toma (un proceso por toma: si se cuelga, la siguiente sigue)
//   node grabar.mjs --listar            imprime las tomas en el orden de proyecto.json
//
// Audio primero: cada escena dura ENTRADA + voz + SALIDA (voz/informe.json), así la imagen espera a la voz por construcción.
// Captura CDP directa (Page.startScreencast, JPEG) en vez de recordVideo: sin franja gris ni VP8 de 1 Mbps.
// Salida en salida/<toma>/: frames/*.jpg, frames.json [{n,t}], escenas.json {toma, escenas:[{id,t0,t1,voz,focos}]}, grabar.log.
// Las cargas de página quedan FUERA de las escenas: el montaje solo usa lo que pasa entre t0 y t1 de cada escena.
import { chromium } from "playwright";
import { appendFileSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import TOMAS, { preparar } from "./tomas.mjs";

const PROY = JSON.parse(readFileSync(new URL("../proyecto.json", import.meta.url)));
const G = PROY.grabacion;
const BASE = PROY.url_base;
const W = G.ancho, H = G.alto;
const ENTRADA = G.entrada_s, SALIDA = G.salida_s;

const argv = process.argv.slice(2);
if (argv.includes("--listar")) {
  const vistas = [];
  for (const c of PROY.capitulos) if (!vistas.includes(c.toma)) vistas.push(c.toma);
  console.log(vistas.join(" "));
  process.exit(0);
}
const TOMA = argv[argv.indexOf("--toma") + 1];
if (!argv.includes("--toma") || !TOMAS[TOMA]) {
  console.error(`Uso: node grabar.mjs --toma <${Object.keys(TOMAS).join("|")}>`);
  process.exit(2);
}
const INFORME = new URL("../voz/informe.json", import.meta.url);
if (!existsSync(INFORME)) { console.error("Falta voz/informe.json: corre voz.py antes de grabar (audio primero)."); process.exit(2); }
const VOZ = JSON.parse(readFileSync(INFORME));

const DIR = join("salida", TOMA);
rmSync(DIR, { recursive: true, force: true });
mkdirSync(join(DIR, "frames"), { recursive: true });
const LOG = join(DIR, "grabar.log");
const log = (...a) => { const l = a.join(" "); console.log(l); appendFileSync(LOG, l + "\n"); };
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
const ahora = () => Date.now() / 1000;

// ---------- navegador + captura CDP ----------
// angle "metal": GPU real (mapas deck.gl, WebGL). "swiftshader": por software (maquetas 3D que con metal no dibujan).
const ARGS = G.angle === "swiftshader"
  ? ["--enable-unsafe-swiftshader", "--use-angle=swiftshader", "--hide-scrollbars"]
  : ["--use-angle=metal", "--ignore-gpu-blocklist", "--enable-gpu-rasterization", "--hide-scrollbars"];
const browser = await chromium.launch({ channel: "chrome", args: ARGS });
const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: 1, locale: G.locale, timezoneId: G.zona });
// Cursor visible y pulso en cada clic, dibujados en la página (salen en la captura sin post-edición).
await ctx.addInitScript((acento) => {
  const iniciar = () => {
    if (document.getElementById("__cur")) return;
    const est = document.createElement("style");
    est.textContent = `nextjs-portal{display:none!important}
      #__cur{position:fixed;left:0;top:0;z-index:2147483647;pointer-events:none;width:30px;height:30px;will-change:transform;filter:drop-shadow(0 2px 3px rgba(0,0,0,.55))}
      .__pulso{position:fixed;z-index:2147483646;pointer-events:none;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;border:3px solid ${acento};animation:__p .6s ease-out forwards}
      @keyframes __p{from{transform:scale(.6);opacity:1}to{transform:scale(3.4);opacity:0}}`;
    document.head.appendChild(est);
    const cur = document.createElement("div");
    cur.id = "__cur";
    cur.innerHTML = '<svg viewBox="0 0 24 24" width="30" height="30"><path d="M3 2l7.2 18 2.6-7.4L20.4 10z" fill="#fff" stroke="#0f1b2d" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    document.documentElement.appendChild(cur);
    const pos = (x, y) => { cur.style.transform = `translate(${x - 4}px,${y - 3}px)`; };
    try { const p = JSON.parse(sessionStorage.getItem("__pos") || "null"); if (p) pos(p.x, p.y); else pos(-60, -60); } catch { pos(-60, -60); }
    addEventListener("mousemove", (e) => { pos(e.clientX, e.clientY); try { sessionStorage.setItem("__pos", JSON.stringify({ x: e.clientX, y: e.clientY })); } catch {} }, true);
    addEventListener("mousedown", (e) => {
      const d = document.createElement("div"); d.className = "__pulso"; d.style.left = e.clientX + "px"; d.style.top = e.clientY + "px";
      document.documentElement.appendChild(d); setTimeout(() => d.remove(), 750);
    }, true);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar); else iniciar();
}, PROY.marca.acento);
const page = await ctx.newPage();
page.setDefaultTimeout(G.espera_ms ?? 15000);
const errores = [];
page.on("pageerror", (e) => errores.push(String(e).slice(0, 160)));
const cdp = await ctx.newCDPSession(page);
const frames = [];
cdp.on("Page.screencastFrame", (f) => {
  const n = frames.length;
  writeFileSync(join(DIR, "frames", `f${String(n).padStart(6, "0")}.jpg`), Buffer.from(f.data, "base64"));
  frames.push({ n, t: ahora() });
  cdp.send("Page.screencastFrameAck", { sessionId: f.sessionId }).catch(() => {});
});
await cdp.send("Page.startScreencast", { format: "jpeg", quality: 90, maxWidth: W, maxHeight: H, everyNthFrame: 1 });

// ---------- escenas ----------
const escenas = [];
let actual = null;
// Una escena = una línea del guion. fn hace las acciones; la escena se sostiene hasta ENTRADA + voz + SALIDA (o `minimo`).
async function escena(id, fn, { minimo = 0 } = {}) {
  const voz = VOZ[id]?.duracion_s;
  if (!voz) throw new Error(`sin voz para ${id} (¿está en guion.json y corrió voz.py?)`);
  actual = { id, t0: ahora(), voz, focos: [] };
  log(`  ▶ ${id} (${voz.toFixed(1)} s)`);
  try { await fn(); } catch (e) { log(`  ⚠ ${id}: ${String(e.message || e).split("\n")[0].slice(0, 160)}`); }
  const fin = actual.t0 + Math.max(ENTRADA + voz + SALIDA, minimo);
  while (ahora() < fin) await dormir(60);
  escenas.push({ ...actual, t1: ahora() });
  actual = null;
}
// Espera hasta la fracción `f` (0–1) de la voz de la escena en curso.
async function a(f) {
  const t = actual.t0 + ENTRADA + f * actual.voz;
  while (ahora() < t) await dormir(40);
}
// Espera hasta que la voz dice `palabra` (la n-ésima vez si se repite). Más exacto que a(f): usa voz/<id>.palabras.json.
const sinTildes = (t) => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().replace(/[^\w]/g, "");
async function aPalabra(palabra, n = 1) {
  const p = new URL(`../voz/${actual.id}.palabras.json`, import.meta.url);
  const ws = existsSync(p) ? JSON.parse(readFileSync(p)) : [];
  const meta = sinTildes(palabra);
  const hits = ws.filter((w) => sinTildes(w.w).startsWith(meta));
  if (hits.length < n) { log(`  ⚠ ${actual.id}: la voz no dice «${palabra}» (${n}ª vez); sigo sin esperar`); return; }
  const t = actual.t0 + ENTRADA + hits[n - 1].s;
  while (ahora() < t) await dormir(40);
}
// Acción que puede fallar sin tumbar la escena. Devuelve true/valor si salió, null si no (y lo anota en el log).
async function intento(que, fn) {
  try { return (await fn()) ?? true; } catch (e) { log(`  ⚠ ${que}: ${String(e.message || e).split("\n")[0].slice(0, 160)}`); return null; }
}

// ---------- cursor y acciones ----------
let posX = W / 2, posY = H / 2;
async function moverA(x, y, ms = 650) {
  const pasos = Math.max(14, Math.round(ms / 20));
  const x0 = posX, y0 = posY;
  for (let i = 1; i <= pasos; i++) {
    const t = i / pasos, e = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
    await page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e);
    await dormir(ms / pasos);
  }
  posX = x; posY = y;
}
async function caja(loc) {
  const l = loc.filter({ visible: true }).first();   // paneles ocultos repiten textos: solo el visible
  await l.scrollIntoViewIfNeeded({ timeout: 8000 });
  await dormir(150);
  const b = await l.boundingBox();
  if (!b) throw new Error("sin caja");
  return b;
}
async function señalar(loc, ms = 650) {
  const b = await caja(loc);
  await moverA(b.x + Math.min(b.width / 2, 120), b.y + b.height / 2, ms);
  return b;
}
async function clic(loc, pausa = 350) {
  await señalar(loc);
  await dormir(180);
  await page.mouse.down(); await dormir(70); await page.mouse.up();
  await dormir(pausa);
}
async function clicEn(x, y, pausa = 300) {
  await moverA(x, y, 500); await dormir(120);
  await page.mouse.down(); await dormir(60); await page.mouse.up(); await dormir(pausa);
}
async function escribir(loc, texto, retardo = 55) {
  await clic(loc, 150);
  await page.keyboard.press("Meta+A"); await page.keyboard.press("Backspace");
  await page.keyboard.type(texto, { delay: retardo });
  await dormir(200);
}
async function desplazar(px, ms = 1400) {
  const pasos = Math.round(ms / 30);
  for (let i = 0; i < pasos; i++) { await page.mouse.wheel(0, px / pasos); await dormir(ms / pasos); }
  await dormir(200);
}
async function listo(extra = 800) {
  await page.waitForLoadState("domcontentloaded").catch(() => {});
  await page.waitForLoadState("networkidle", { timeout: 12000 }).catch(() => {});
  await page.evaluate(() => document.fonts.ready).catch(() => {});
  await dormir(extra);
}
async function ir(ruta, extra = 1500) {
  await page.goto(BASE + ruta, { waitUntil: "domcontentloaded", timeout: 180000 });
  await listo(extra);
}
// Lleva un texto al borde superior de su contenedor con scroll (suave), p. ej. una sección dentro de un panel.
async function aTexto(contenedor, texto, arriba = 70) {
  const el = contenedor.getByText(texto, { exact: false }).filter({ visible: true }).first();
  await el.evaluate((e, arriba) => {
    let p = e.parentElement;
    while (p && !(p.scrollHeight > p.clientHeight + 4 && getComputedStyle(p).overflowY !== "visible")) p = p.parentElement;
    if (!p) { e.scrollIntoView({ behavior: "smooth", block: "start" }); return; }
    const objetivo = p.scrollTop + e.getBoundingClientRect().top - p.getBoundingClientRect().top - arriba;
    p.scrollTo({ top: objetivo, behavior: "smooth" });
  }, arriba);
  await dormir(900);
}
// Marca un foco para el montaje: acercamiento suave (zoom) sobre la caja del elemento y, si anillo, un recuadro que se dibuja.
// Úsalo en lo que la voz nombra y hay que LEER (una cifra, un botón chico). Pocos por escena: una cámara que sube y baja marea.
async function foco(loc, { seg = 3.5, zoom = 1.35, anillo = true, pad = 10, mover = true } = {}) {
  const b = await caja(loc);
  if (mover) await moverA(b.x + Math.min(b.width / 2, 120), b.y + b.height / 2, 500);
  actual?.focos.push({ t: ahora(), dur: seg, x: b.x - pad, y: b.y - pad, w: b.width + 2 * pad, h: b.height + 2 * pad, zoom, anillo });
  return b;
}

const h = { page, ctx, browser, BASE, W, H, escena, a, aPalabra, intento, moverA, señalar, clic, clicEn, escribir, desplazar, listo, ir, aTexto,
  foco, caja, dormir, log };

// ======================================================================
const t0 = ahora();
log(`toma ${TOMA} · ${new Date().toISOString()}`);
try {
  if (preparar) await preparar(h);
  await TOMAS[TOMA](h);
} catch (e) {
  log(`✖ ${String(e.message || e).split("\n")[0].slice(0, 200)}`);
}
await dormir(600);
await cdp.send("Page.stopScreencast").catch(() => {});
writeFileSync(join(DIR, "frames.json"), JSON.stringify(frames));
writeFileSync(join(DIR, "escenas.json"), JSON.stringify({ toma: TOMA, escenas }, null, 1));
const esperadas = PROY.capitulos.filter((c) => c.toma === TOMA).flatMap((c) => c.escenas);
const faltan = esperadas.filter((id) => !escenas.some((s) => s.id === id));
log(`fin: ${escenas.length} escenas, ${frames.length} cuadros, ${(ahora() - t0).toFixed(0)} s · faltan: ${JSON.stringify(faltan)} · ` +
    `errores de página: ${JSON.stringify(errores.slice(0, 3))}`);
await Promise.race([browser.close(), dormir(8000)]);   // cerrar con la página animándose puede colgarse
process.exit(faltan.length ? 1 : 0);
