#!/bin/bash
# Render de un proyecto HyperFrames por tramos, cada uno en su propio proceso, con vigilante de disco interno.
# Une los tramos sin deriva de audio y normaliza el volumen (-16 LUFS).
#
#   bash render_tramos.sh <carpeta_hyperframes> <salida.mp4> [segundos_por_tramo=60] [calidad=delivery]
#
# Por qué: con el disco interno casi lleno, la memoria virtual (swap) crece mientras Chrome captura y tumba un render
# largo a mitad. Cada tramo libera memoria al terminar. Los temporales van junto al proyecto (TMPDIR), fuera de él.
# Retoma: los tramos que ya existen no se vuelven a renderizar (borra salida.tramos/ para empezar de cero).
set -u
DIR=$(cd "$1" && pwd) || exit 2
mkdir -p "$(dirname "$2")"
SALIDA="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"   # absoluta: cada tramo corre con cd al proyecto
TRAMO=${3:-60}
CALIDAD=${4:-delivery}
MIN_INICIO_MB=${MIN_INICIO_MB:-1100}   # espera este espacio libre antes de cada tramo
MIN_CORTE_MB=${MIN_CORTE_MB:-700}      # por debajo de esto detiene el tramo en curso
FPS=30

VER=$(python3 -c "import json,re,sys; s=json.load(open('$DIR/package.json'))['scripts']['render']; print(re.search(r'hyperframes@([\w.\-]+)', s).group(1))" 2>/dev/null)
[ -z "$VER" ] && { echo "package.json sin versión fijada de hyperframes (scripts.render)"; exit 2; }
TOTAL=$(python3 -c "import re; t=open('$DIR/index.html').read(); print(re.search(r'data-composition-id=\"main\"[^>]*data-duration=\"([\d.]+)\"', t).group(1))")
OUTD="${SALIDA%.mp4}.tramos"
# TMPDIR FUERA del proyecto (si queda dentro, HyperFrames lo copia dentro de sí mismo hasta ENAMETOOLONG) y en el mismo
# disco del proyecto (el externo), no en el interno.
TMPR="$(dirname "$DIR")/.tmp-render-$(basename "$DIR")"
mkdir -p "$OUTD" "$TMPR"
export TMPDIR="$TMPR/"

# Cortes en múltiplos exactos de cuadro (si no, cada tramo arrastra medio cuadro y el audio se corre).
CORTES=$(python3 -c "
fps=$FPS; tot=round($TOTAL*fps); paso=round($TRAMO*fps)
c=list(range(0, tot, paso)) + [tot]
if len(c) > 2 and c[-1]-c[-2] < fps*5: c.pop(-2)   # último tramo de menos de 5 s: se une al anterior
print(' '.join(f'{x/fps:.4f}' for x in c))")
set -- $CORTES
N=$(($# - 1))
libre_mb() { df -m /System/Volumes/Data | awk 'NR==2{print $4}'; }
echo "hyperframes@$VER · $TOTAL s en $N tramo(s) · libre $(libre_mb) MB · swap: $(sysctl -n vm.swapusage | awk '{print $6}') usados"

i=1
CORTES_ARR=($CORTES)
while [ $i -le $N ]; do
  S=${CORTES_ARR[$((i - 1))]}; E=${CORTES_ARR[$i]}
  F="$OUTD/t$i.mp4"
  if [ -s "$F" ]; then echo "tramo $i ya existe"; i=$((i + 1)); continue; fi
  while [ "$(libre_mb)" -lt "$MIN_INICIO_MB" ]; do echo "esperando espacio: $(libre_mb) MB"; sleep 20; done
  echo "tramo $i/$N: $S → $E s ($(date +%H:%M:%S), libre $(libre_mb) MB)"
  ( cd "$DIR" && npx --yes "hyperframes@$VER" render --quality "$CALIDAD" --workers 1 --start "$S" --end "$E" -o "$F" > "$OUTD/t$i.log" 2>&1 ) &
  RP=$!
  while kill -0 $RP 2>/dev/null; do
    if [ "$(libre_mb)" -lt "$MIN_CORTE_MB" ]; then
      echo "DISCO BAJO ($(libre_mb) MB): detengo el tramo $i. Libera espacio (o reinicia) y vuelve a correr: retoma aquí."
      pkill -P $RP
      kill $RP 2>/dev/null
      pkill -f "hyperframes.*render.*--start $S --end $E"
      rm -f "$F"
      exit 3
    fi
    sleep 5
  done
  wait $RP; RC=$?
  if [ $RC -ne 0 ] || [ ! -s "$F" ]; then echo "tramo $i falló (rc $RC):"; tail -8 "$OUTD/t$i.log"; exit 4; fi
  i=$((i + 1))
done

# Unión: video con -c copy; el audio de cada tramo se recorta a la duración exacta de su video antes de concatenar
# (el AAC de cada tramo sale 20-40 ms más largo y, sin recortar, el retraso se acumula tramo a tramo).
LIST="$OUTD/lista.txt"; : > "$LIST"
ARGS=(); FILT=""; LBL=""
for i in $(seq 1 $N); do
  F="$OUTD/t$i.mp4"
  ffmpeg -loglevel error -y -i "$F" -map 0:v -c copy "$OUTD/v$i.mp4"
  echo "file '$OUTD/v$i.mp4'" >> "$LIST"
  CUADROS=$(ffprobe -v error -select_streams v:0 -count_packets -show_entries stream=nb_read_packets -of csv=p=0 "$F")
  DUR=$(python3 -c "print($CUADROS/$FPS)")
  ARGS+=(-i "$F")
  FILT+="[$((i - 1)):a]apad,atrim=0:$DUR,asetpts=PTS-STARTPTS[a$i];"
  LBL+="[a$i]"
done
ffmpeg -loglevel error -y -f concat -safe 0 -i "$LIST" -map 0:v -c:v copy "$OUTD/video.mp4" || exit 5
ffmpeg -loglevel error -y "${ARGS[@]}" -filter_complex "${FILT}${LBL}concat=n=$N:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
  -map "[a]" -ar 48000 -c:a aac -b:a 192k "$OUTD/audio.m4a" || exit 5
ffmpeg -loglevel error -y -i "$OUTD/video.mp4" -i "$OUTD/audio.m4a" -map 0:v -map 1:a -c copy -movflags +faststart "$SALIDA" || exit 5
rm -rf "$TMPR"
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of compact "$SALIDA"
echo "listo: $SALIDA (esperado $TOTAL s). Los tramos quedan en $OUTD (bórralos al entregar)."
