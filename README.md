# Skills de Latinovation

Skills para agentes de código (Claude Code y Codex). Cada carpeta es una skill: un `SKILL.md` con sus instrucciones y los
scripts y plantillas que usa.

| Skill | Qué hace |
|---|---|
| [`video-explicativo`](video-explicativo/) | Videos que explican una webapp o lo que pasó con ella, hechos con HyperFrames y motion de GSAP. Tiene dos modos. En **recorrido**, la app se graba con Playwright y se narra con voz de Kokoro verificada con Whisper; puede llevar intro y cierre animados, efectos y música. En **historia**, chats reales de un periodo se cuentan como chats animados, en 16:9 y 9:16. |

## Instalación

Copia la carpeta de la skill en la carpeta de skills de tu agente:

```bash
git clone https://github.com/latinovation/skills.git
cp -R skills/video-explicativo ~/.claude/skills/    # Claude Code
cp -R skills/video-explicativo ~/.agents/skills/    # Codex
```

En Codex se invoca nombrándola: `$video-explicativo`.

## Requisitos de `video-explicativo`

Corre en local; no funciona en sandboxes web como Claude.ai o ChatGPT web.

- macOS con Apple Silicon, porque Whisper corre con `mlx_whisper`.
- Node.js con `npx`. HyperFrames va fijado en `0.9.63`.
- Python 3, `uv`, `ffmpeg` e ImageMagick (`magick`).
- Kokoro en `~/.venvs/kokoro` y `mlx_whisper` en `~/.local/bin`. Los pasos de instalación están en
  [`referencias/trampas.md`](video-explicativo/referencias/trampas.md) → Voz.
- Los sonidos salen de la skill `media-use` de HyperFrames, en `~/.agents/skills/media-use`.

## Licencia

El código y las instrucciones van con licencia [MIT](LICENSE). La plantilla trae además la fuente Manrope, que
conserva su licencia SIL Open Font License 1.1 ([`video-explicativo/OFL-Manrope.txt`](video-explicativo/OFL-Manrope.txt)).
