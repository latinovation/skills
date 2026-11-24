#!/usr/bin/env bash
# Renderiza un tramo en piezas cortas (menos memoria) y las une en tramo_<n>.mp4. Uso: render_subtramos.sh <n> <ini> <fin> <paso>
set -euo pipefail
N="$1"; INI="$2"; FIN="$3"; PASO="$4"
P="$(cd "$(dirname "$0")/.." && pwd)"
SALIDA="${SALIDA:?Define SALIDA con la carpeta de salida del render}"
export TMPDIR="${TMPDIR_RENDER:-$PWD/_tmp_render}"
MIN_ARRANQUE_KB=$((850 * 1024))
MIN_VIGIA_KB=$((520 * 1024))
libre_kb() { df -k /System/Volumes/Data | awk 'NR==2 {print $4}'; }

cd "$P/hyperframes"
: > "$SALIDA/sub_$N.txt"
a="$INI"; k=0
while [ "$a" -lt "$FIN" ]; do
  b=$((a + PASO)); [ "$b" -gt "$FIN" ] && b="$FIN"
  pieza="$SALIDA/sub_${N}_${k}.mp4"
  echo "file '$pieza'" >> "$SALIDA/sub_$N.txt"
  if [ ! -s "$pieza" ]; then
    espera=0
    while [ "$(libre_kb)" -lt "$MIN_ARRANQUE_KB" ]; do
      espera=$((espera + 1)); [ "$espera" -gt 90 ] && { echo "ERROR: sin espacio para la pieza ${k}" >&2; exit 3; }
      sleep 5
    done
    echo "pieza ${k}: ${a}–${b} s · libres $(( $(libre_kb) / 1024 )) MB"
    npx -y hyperframes render --start "$a" --end "$b" --workers 1 --quality looks -o "$pieza" > "$SALIDA/sub_${N}_${k}.log" 2>&1 &
    pid=$!
    while kill -0 "$pid" 2>/dev/null; do
      if [ "$(libre_kb)" -lt "$MIN_VIGIA_KB" ]; then
        echo "VIGIA: disco bajo ($(( $(libre_kb) / 1024 )) MB), se detiene la pieza ${k}" >&2
        pkill -P "$pid" 2>/dev/null || true; kill "$pid" 2>/dev/null || true; rm -f "$pieza"; exit 4
      fi
      sleep 2
    done
    wait "$pid" || { echo "ERROR: falló la pieza ${k}" >&2; exit 5; }
  fi
  a="$b"; k=$((k + 1))
done
ffmpeg -v error -y -f concat -safe 0 -i "$SALIDA/sub_$N.txt" -c copy "$SALIDA/tramo_$N.mp4"
echo "tramo_$N listo: $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$SALIDA/tramo_$N.mp4") cuadros"
