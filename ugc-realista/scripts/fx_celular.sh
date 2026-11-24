#!/bin/bash
# Hace que el audio de un video suene grabado con el micrófono frontal de un celular.
# Uso: ./fx_celular.sh entrada.mp4 salida.mp4 [nivel_ruido_dB=-46]
# Cadena: recorte de graves y agudos del micro del celular, voz algo más cerca de 3 kHz,
# compresión tipo control automático de ganancia, sala pequeña, ruido ambiente suave, normalizado.
set -eu
in="$1"; out="$2"; ruido="${3:--46}"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
ffmpeg -v error -y -i "$in" -f lavfi -i "anoisesrc=color=pink:amplitude=0.5:duration=${dur}:sample_rate=48000" \
 -filter_complex "[0:a]aresample=48000,highpass=f=120,lowpass=f=7200,equalizer=f=250:t=q:w=1:g=-2.5,equalizer=f=3000:t=q:w=1.2:g=3,acompressor=threshold=-24dB:ratio=3.5:attack=5:release=90:makeup=5,aecho=0.9:0.9:14|27:0.16|0.09,asoftclip=type=tanh:threshold=0.9[v];[1:a]highpass=f=80,lowpass=f=5000,volume=${ruido}dB[n];[v][n]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=7[a]" \
 -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k "$out"
