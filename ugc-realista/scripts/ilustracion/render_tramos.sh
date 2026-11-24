#!/usr/bin/env bash
# Renderiza el video por tramos (disco interno casi lleno), une el video sin recodificar y mezcla el audio aparte.
# Salidas: $SALIDA/video_con_musica.mp4 y $SALIDA/video_sin_musica.mp4
set -euo pipefail

P="$(cd "$(dirname "$0")/.." && pwd)"
HF="$P/hyperframes"
SALIDA="${SALIDA:?Define SALIDA con la carpeta de salida del render}"
export TMPDIR="${TMPDIR_RENDER:-$PWD/_tmp_render}"
mkdir -p "$SALIDA" "$TMPDIR"

MIN_ARRANQUE_KB=$((1100 * 1024))   # 1,1 GB libres para empezar un tramo
MIN_VIGIA_KB=$((700 * 1024))       # por debajo de 700 MB se detiene el tramo
CORTES=(0 15 30 45 60 75)
DURACION=75

libre_kb() { df -k /System/Volumes/Data | awk 'NR==2 {print $4}'; }

esperar_espacio() {
  local intentos=0
  while [ "$(libre_kb)" -lt "$MIN_ARRANQUE_KB" ]; do
    intentos=$((intentos + 1))
    if [ "$intentos" -gt 60 ]; then echo "ERROR: el disco no recuperó 1,1 GB en 5 min" >&2; exit 3; fi
    sleep 5
  done
}

cd "$HF"
: > "$SALIDA/lista.txt"
for i in $(seq 0 4); do
  ini=${CORTES[$i]}; fin=${CORTES[$((i + 1))]}
  tramo="$SALIDA/tramo_$i.mp4"
  echo "$tramo" | sed "s/^/file '/; s/$/'/" >> "$SALIDA/lista.txt"
  if [ -s "$tramo" ]; then echo "tramo $i ya existe, se salta"; continue; fi
  esperar_espacio
  echo "tramo ${i}: ${ini}–${fin} s · libres $(( $(libre_kb) / 1024 )) MB"
  npx -y hyperframes render --start "$ini" --end "$fin" --workers 1 --quality looks -o "$tramo" > "$SALIDA/tramo_$i.log" 2>&1 &
  pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    if [ "$(libre_kb)" -lt "$MIN_VIGIA_KB" ]; then
      echo "VIGIA: disco bajo ($(( $(libre_kb) / 1024 )) MB), se detiene el tramo ${i}" >&2
      pkill -P "$pid" 2>/dev/null || true; kill "$pid" 2>/dev/null || true
      rm -f "$tramo"; exit 4
    fi
    sleep 2
  done
  wait "$pid" || { echo "ERROR: falló el tramo $i (ver tramo_$i.log)" >&2; exit 5; }
done

ffmpeg -v error -y -f concat -safe 0 -i "$SALIDA/lista.txt" -an -c:v copy "$SALIDA/video_mudo.mp4"

VOZ="$HF/assets/voz.wav"; MUS="$HF/assets/musica.mp3"
ffmpeg -v error -y -i "$VOZ" -i "$MUS" -filter_complex \
  "[0:a]aresample=48000,apad=whole_dur=$DURACION[v];[1:a]aresample=48000,volume=0.14,afade=t=out:st=72.5:d=2.5,atrim=0:$DURACION[m];[v][m]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000[a]" \
  -map "[a]" -t "$DURACION" -c:a pcm_s16le "$SALIDA/audio_con_musica.wav"
ffmpeg -v error -y -i "$VOZ" -af "aresample=48000,apad=whole_dur=$DURACION,loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000" -t "$DURACION" -c:a pcm_s16le "$SALIDA/audio_sin_musica.wav"

for v in con sin; do
  ffmpeg -v error -y -i "$SALIDA/video_mudo.mp4" -i "$SALIDA/audio_${v}_musica.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
    -movflags +faststart -shortest "$SALIDA/video_${v}_musica.mp4"
done
echo "LISTO"; ls -la "$SALIDA"/video_*.mp4
