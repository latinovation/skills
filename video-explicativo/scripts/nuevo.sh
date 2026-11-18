#!/bin/bash
# Crea un proyecto de video desde la plantilla de la skill.
#
#   bash nuevo.sh recorrido <carpeta_destino>    grabación de la app + voz + montaje (proyecto.json, guion.json, tomas.mjs)
#   bash nuevo.sh historia  <carpeta_destino>    historia con datos reales animada (historia.json → construir.py)
#
# La carpeta va FUERA de Documents/ (iCloud vacía archivos y rompe git): ~/Developer/_<proyecto>-video-<fecha>/.
set -eu
MODO=${1:?modo: recorrido | historia}
DEST=${2:?carpeta destino}
SKILL=$(cd "$(dirname "$0")/.." && pwd)
SFX_SRC="$HOME/.agents/skills/media-use/audio/assets/sfx"

case "$DEST" in "$HOME/Documents"*|*"/Documents/"*) echo "No en Documents/ (iCloud): usa ~/Developer/_<proyecto>-video-<fecha>"; exit 2;; esac
[ -d "$SKILL/plantillas/$MODO" ] || { echo "modo desconocido: $MODO"; exit 2; }
if [ -e "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null)" ]; then echo "$DEST ya existe y no está vacía: no la piso"; exit 2; fi
mkdir -p "$DEST"
cp -R "$SKILL/plantillas/$MODO/." "$DEST/"
cp "$SKILL/scripts/render_tramos.sh" "$SKILL/scripts/revisar.py" "$DEST/"

if [ "$MODO" = recorrido ]; then
  (cd "$DEST/grabacion" && npm install --no-audit --no-fund --silent) || echo "⚠ npm install falló en grabacion/: córrelo a mano"
  for f in "$HOME/.venvs/kokoro/bin/python" "$HOME/.local/bin/mlx_whisper"; do [ -x "$f" ] || echo "⚠ falta $f (ver referencias/trampas.md → Voz)"; done
  ls "$HOME"/.cache/hyperframes/tts/synth-v*.py >/dev/null 2>&1 || echo "⚠ falta synth-v*.py: corre una vez npx --yes hyperframes@0.9.63 tts \"hola\" --voice ef_dora"
fi
if [ "$MODO" = historia ]; then
  mkdir -p "$DEST/assets/sfx"
  for s in pop whoosh click; do
    if [ -f "$SFX_SRC/$s.mp3" ]; then cp "$SFX_SRC/$s.mp3" "$DEST/assets/sfx/"; else echo "⚠ falta $SFX_SRC/$s.mp3 (sonidos de media-use)"; fi
  done
fi
echo "Proyecto creado en $DEST (modo $MODO). Sigue el paso a paso del SKILL.md."
