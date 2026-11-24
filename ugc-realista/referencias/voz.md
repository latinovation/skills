# Voz

**Claude no oye.** Puede medir (duración, ritmo, transcripción) pero el juicio de cómo suena —acento,
naturalidad, si «suena a robot»— es de la persona. Nunca decir «la voz suena natural»; decir qué se midió y pedir
que la escuche.

## Elegir la voz
1. Generar la MISMA frase del guion con 3–4 voces candidatas del idioma y acento pedidos (ver servicios en
   `proveedores.md`). Cuesta centavos.
2. La persona las escucha y elige. Anotarla en el kit (`voz.txt`).

## Qué hace cada modelo con la voz (medido el 22-oct-2026)
- **Seedance 2.5:** regenera la voz siguiendo la referencia; la boca queda sincronizada. Va siempre con voz de referencia.
- **Wan 3.0 con voz de referencia ajena:** deja el audio intacto (correlación 0,984) y solo mueve la boca hacia él; la persona vio que no cuadraba bien. No usar.
- **Wan 3.0 con voz propia** (sin audio de referencia, el texto entre comillas en el prompt): sincronizó bien y la persona la prefirió, pero puede añadir o quitar palabras. Comprobar el texto con la transcripción y repetir la toma si cambia.

## Preparar la voz de cada plano
Una línea de voz por plano, que va al modelo de video como **audio de referencia**. El modelo re-genera la voz
siguiendo esa referencia (conserva el tono y las palabras); no la copia tal cual.

Ritmo objetivo: **3–3,5 palabras por segundo, sin silencios internos largos** (personas mayores de 70: ≈ 2,5–2,8, con menos palabras en el guion y nunca pidiendo lentitud; las sílabas de un adulto mayor duran 20–25 % más; ver «Voz más joven que el personaje» en `senales-ia.md`). Una persona contando algo a
cámara va a ese ritmo. Medido en tomas de video: la rechazada por «robot» iba a 1,72 palabras/s y la aprobada a
2,64 (el modelo alarga la frase respecto a la voz de referencia). Receta probada:

```bash
# 1) recortar las pausas internas largas a 0,14 s y el silencio inicial
ffmpeg -y -i linea.mp3 -af "silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.14:stop_threshold=-45dB" linea_sin_pausas.wav
# 2) medir: palabras del texto / duración. Si da < 3,0, acelerar lo justo para llegar a 3,3:
#    atempo = duración × 3,3 / palabras   (no pasar de 1,3: más rápido se deforma)
ffmpeg -y -i linea_sin_pausas.wav -af "atempo=<valor>" linea_plano.wav
```
Luego transcribir `linea_plano.wav` para confirmar que no se comió palabras.

## Verificar lo que se dice (sin oído)
- Transcribir cada línea y cada toma con Whisper (large-v3-turbo) y comparar con el guion: similitud ≥ 0,93 y
  las palabras críticas presentes (marca, producto, cifras). `revisar_toma.py toma … --texto "…" --criticas
  "Marca,producto"` lo hace por toma y lista cada palabra que no coincide (resultado REVISAR).
- Los TTS fallan palabras **al azar**, no solo siglas: hasta 4 intentos por línea y quedarse con el que transcribe
  limpio.
- Un solo modelo de Whisper puede equivocarse: ante una palabra dudosa, confirmar con un segundo modelo o tamaño.
- Siglas, anglicismos y nombres raros: probar 2–3 grafías y quedarse con la que Whisper transcribe bien. Si
  ninguna sirve, **reescribir**: decir qué es («la simulación») y dejar la sigla en un rótulo.
- Si una palabra puede cambiar el sentido, explicitar el sujeto («para que *ella* lo haga…»).
- **Jerga técnica en español:** el modelo de video la pronuncia mal aunque la voz de referencia esté bien.
  Proponer desde el inicio que la persona (o un locutor) grabe el guion: ese audio real es la pista final y el
  modelo solo mueve los labios.

## Nombre de la marca en la voz
Medido el 22-oct-2026 con Inworld «Lupita (es)»: escrito con su grafía en inglés, la voz dijo mal la marca (la transcripción lo oyó así en tres tomas). Escrita como se pronuncia en español, la transcripción oyó la marca bien escrita. Regla: poner la grafía fonética en el texto de la voz, no en los subtítulos, y comprobar la marca con la transcripción antes de gastar en video (un video con la marca mal dicha obliga a pagar otra toma).

## Audio de celular
La voz de referencia o generada suena limpia y siempre al mismo tono, como de estudio. Se pueden pedir micrófono
o estilo UGC en el prompt (no probado) o **procesar el audio**; quien lo probó (22-oct-2026) prefirió procesar el
audio. `scripts/fx_celular.sh entrada.mp4 salida.mp4 [ruido_dB]` (necesita `ffmpeg`) hace en un comando:
- recorta graves (<120 Hz) y agudos (>7,2 kHz) como el micrófono frontal de un celular;
- baja 2,5 dB a 250 Hz y sube 3 dB a 3 kHz (la voz «más cerca»);
- comprime como el control automático de ganancia del celular;
- añade una sala pequeña (eco de 14 y 27 ms) y ruido ambiente rosa suave (por defecto −46 dB; −40 más ruido,
  −52 menos);
- normaliza a −16 LUFS; el video se copia sin tocar.

Cuándo: al montar, con el video ya unido y **antes** de transcribir el MP4 final. Entregar también el original.
Qué se midió: en una toma, la energía de 3–8 kHz pasó de 2,7 % a 9,3 % y el pico de 0,97 a 0,77, y la
transcripción siguió dando el mismo diálogo. **Cómo suena lo decide la persona escuchando** (Claude no oye); si
queda artificial, ajustar `ruido_dB` o cambiar la cadena.

## Montaje del audio
- Al armar el video, cortar cada plano a su voz (un respiro de 0,10–0,15 s antes y después).
- Música: con licencia, o ninguna. Nunca música sintetizada en el momento.
- No usar `ffmpeg … -shortest` para unir audio y video: recorta el video al audio más corto. Usar `-t <duración
  del video>` y `apad`.
- Transcribir también el audio del MP4 final: es lo que se entrega.
