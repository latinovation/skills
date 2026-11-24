# Skills de Latinovation

Skills para agentes de código (Claude Code y Codex). Cada carpeta es una skill: un `SKILL.md` con sus instrucciones y los
scripts y plantillas que usa.

| Skill | Qué hace |
|---|---|
| [`video-explicativo`](video-explicativo/) | Videos que explican una webapp o lo que pasó con ella, hechos con HyperFrames y motion de GSAP. Tiene dos modos. En **recorrido**, la app se graba con Playwright y se narra con voz de Kokoro verificada con Whisper; puede llevar intro y cierre animados, efectos y música. En **historia**, chats reales de un periodo se cuentan como chats animados, en 16:9 y 9:16. |
| [`ugc-realista`](ugc-realista/) | Videos con IA que no parecen hechos con IA, en siete estilos: UGC, documental, 3D médico de cristal, 3D animado de personaje, collage editorial, ilustración animada y presentadora de TV. Cotiza antes de gastar, revisa cada toma (parecido de la cara, diálogo, manos y producto), mira el video final como espectador y guarda en un cuaderno lo que aprende de tus videos. Trabaja con tu cuenta de Higgsfield, kie.ai o Comfy Cloud. |

## Instalación

Copia la carpeta de la skill en la carpeta de skills de tu agente:

```bash
git clone https://github.com/latinovation/skills.git
cp -R skills/video-explicativo ~/.claude/skills/    # Claude Code
cp -R skills/video-explicativo ~/.agents/skills/    # Codex
cp -R skills/ugc-realista ~/.claude/skills/         # Claude Code
cp -R skills/ugc-realista ~/.agents/skills/         # Codex
```

En Codex se invoca nombrándola: `$video-explicativo` o `$ugc-realista`.

## Requisitos de `video-explicativo`

Corre en local; no funciona en sandboxes web como Claude.ai o ChatGPT web.

- macOS con Apple Silicon, porque Whisper corre con `mlx_whisper`.
- Node.js con `npx`. HyperFrames va fijado en `0.9.63`.
- Python 3, `uv`, `ffmpeg` e ImageMagick (`magick`).
- Kokoro en `~/.venvs/kokoro` y `mlx_whisper` en `~/.local/bin`. Los pasos de instalación están en
  [`referencias/trampas.md`](video-explicativo/referencias/trampas.md) → Voz.
- Los sonidos salen de la skill `media-use` de HyperFrames, en `~/.agents/skills/media-use`.

## Requisitos de `ugc-realista`

Corre en local, en Claude Code o Codex (Mac, Linux o Windows). En Codex no se ha probado con un pedido real.

- `python3` y `ffmpeg`. La primera vez, la skill crea `~/ugc-realista/.venv` con `opencv-python-headless`, `numpy` y
  `faster-whisper` para revisar las tomas.
- Una cuenta propia en un servicio de video: Higgsfield (`npm install -g @higgsfield/cli`), kie.ai o Comfy Cloud. Las
  llaves las guardas tú en `~/ugc-realista/.env`; nunca se pegan en el chat.
- Según el estilo:
  - Node.js con `npx` para HyperFrames (documental, 3D de cristal, collage, presentadora e ilustración);
  - `mlx_whisper` (Mac con Apple Silicon) para las plantillas de montaje;
  - `uv` para `medir_voces.py`;
  - `gemini-api` con prepago de Google AI Studio para la ilustración animada.
- Las fichas de cada estilo traen costos y fallas medidos en proyectos reales. Las entregas y los proyectos que citan no
  vienen en este repositorio.

## Licencia

El código y las instrucciones van con licencia [MIT](LICENSE). La plantilla trae además la fuente Manrope, que
conserva su licencia SIL Open Font License 1.1 ([`video-explicativo/OFL-Manrope.txt`](video-explicativo/OFL-Manrope.txt)).
