# Trampas conocidas (con su arreglo)

## Voz
- **Instalación (una vez).**
  - `uv venv --python 3.12 ~/.venvs/kokoro` y luego `uv pip install --python ~/.venvs/kokoro/bin/python kokoro-onnx soundfile`.
  - Modelo y `synth-v*.py`: `npx --yes hyperframes@0.9.63 tts "hola" --voice ef_dora`, que los deja en `~/.cache/hyperframes/tts/`.
  - Whisper: `mlx_whisper` en `~/.local/bin`.
- **El `tts` de la CLI de HyperFrames en español cecea** porque solo pasa `es`. Por eso `voz.py` llama al sintetizador con `es-419`.
- **`mlx_whisper` corta el nombre de salida en el primer punto.** Las tomas se llaman `a1_toma1.wav`, nunca `a1.toma1.wav`.
- **Siglas y anglicismos:**
  - el TTS lee «curva IV» como «Ive» y «PVsol» como «pede sol». Escríbelas como se pronuncian y vuelve a pasar Whisper;
  - Whisper también se equivoca de oído («cada cargo» → «cara a cargo»). Si la duda persiste, reescribe la frase.
- **Kokoro habla rápido**, a ~2,9 palabras/s, y bajar la velocidad a 0,88 apenas alarga un 6 %. Mide antes de prometer duraciones.
- **Al cambiar una voz cambia su duración:** hay que volver a grabar la toma de esa escena.

## Grabación
- **Usa la captura CDP, no `recordVideo`.** `recordVideo` deja una franja gris de 88 px y graba en VP8 a 1 Mbps.
- **Una página quieta no emite cuadros.** `montar.py` sostiene el último. Si «falta» el final de una escena, es eso.
- **`intento()` devuelve `?? true`** porque `clic` devuelve `undefined`. Sin eso, la lógica que dependía del intento saltaba escenas.
- **Login:** espera `networkidle` antes de llenar los campos, o la página no termina de cargar.
- **La sesión puede vencer a mitad de una toma.** Una cookie guardada para `localhost` no vale en `127.0.0.1`, y una cookie `Secure` no viaja por http.
- **El 3D o el mapa sale «Cargando…»:** precaliéntalo fuera de escena.
  - Con `angle: metal` dibuja deck.gl; con `swiftshader`, las maquetas Three.js que no salen con `metal`.
- **Un tooltip queda pegado** tras pasar el cursor: mueve el cursor a una zona neutra antes de la escena siguiente.
- **Agregar elementos con clics en un mapa falla** (marcadores de Google, zoom distinto al del ensayo). Hazlo desde el buscador.
- **Cerrar el navegador con la página animándose puede colgarse.** El motor guarda los JSON antes y cierra con tope.
- **Server Actions de Next responden RSC:** `page.route` no las finge. Para «guardar» sin tocar producción, usa la copia local con base de ejemplo.
- **`next start` puede marcar la cookie como `Secure`:** por http no hay sesión. Graba contra la copia local configurada sin `Secure`.
- **Con el Chrome real del usuario** (no Playwright) sale la burbuja «¿Guardar la contraseña?» y el brillo naranja de la extensión. Por eso se graba con Playwright headless.

## Montaje y HyperFrames
- **`check` cuenta cada `<span>` por letra como una palabra** (`line_unread` falso). Anima por palabra, no por letra.
- **Un hilo de chat que crece** se ancla abajo con CSS (`flex-direction: column` + `justify-content: flex-end` + `min-height: 100%`). Medir `offsetTop` en el script da alturas falsas.
- **El ffmpeg de Homebrew no trae `drawtext` ni `subtitles`.** Los subtítulos y rótulos van en el HTML, nunca en filtros.
- **ImageMagick `montage` sin `-font` falla** con «unable to read font». Los scripts ya pasan Helvetica.
- **`ffmpeg … -c:v copy -shortest` recorta el video** al audio más corto. Usa `-t <duración>` y `apad`.
- **Música sintetizada con senoidales suena a PowerPoint 95.** Usa música con licencia o ninguna.
- **Un `fromTo` de GSAP pinta su estado inicial desde el segundo 0**, aunque arranque después. Si ese estado es visible (un anillo a 0,9), queda quieto en pantalla hasta que empieza. Pasa `immediateRender: false`. Le pasó al anillo del logo de la intro.

## Música
- **De dónde sale:**
  - el catálogo de HeyGen, con la skill `media-use` (`resolve --type bgm`). Requiere haber iniciado sesión en HeyGen;
  - o una pista con licencia comercial que traiga el usuario.
  - MusicGen local sirve solo para uso interno: sus pesos son CC-BY-NC 4.0. Si el video va a redes o a pauta, cámbiala. Dilo en el LEEME.
- **Más corta que el video:** `realzar.py` avisa. Alárgala con un cruce entre dos copias y recórtala:
  `ffmpeg -i m.wav -i m.wav -filter_complex "[0][1]acrossfade=d=4:c1=tri:c2=tri" -t <duración + 1> video/assets/musica/fondo.wav`.
  Que la unión caiga bajo una voz, donde la música va baja. Con `-stream_loop` el corte se oye.
- **Si la voz queda tapada**, baja `MUSICA_VOL` en `realzar.py`. No subas la voz: `render_tramos.sh` normaliza todo a −16 LUFS.

## Render
- **Vista previa y render del mismo proyecto a la vez:** se pisan en `video/.transcode-cache` y el render falla con `ENOENT … .tmp-…part…mp4`. Parece un problema de disco, pero es concurrencia. Apaga la vista previa por su puerto antes de renderizar.
- **Disco interno bajo:**
  - la swap crece mientras Chrome captura y tumba el render;
  - `render_tramos.sh` corre un proceso por tramo, espera a tener 1,1 GB libres y corta si quedan menos de 700 MB;
  - antes de renderizar, mira `df -h /System/Volumes/Data` y `sysctl vm.swapusage`;
  - nunca borres nada para hacer espacio sin preguntar.
- **TMPDIR dentro del proyecto rompe el render:** HyperFrames se copia a sí mismo hasta dar `ENAMETOOLONG`. El script lo pone al lado del proyecto.
- **Al unir tramos con `-c copy`, el audio se corre** 20 a 40 ms por tramo. El script recorta el audio de cada tramo a la duración de su video.

## Revisión
- **`revisar.py` usa el FIN de cada palabra para ubicar las voces,** porque Whisper pega el inicio de la primera palabra al inicio del segmento.
- **Whisper large-v3-turbo alucina «Gracias.»** sobre la música de una tarjeta final. Si una voz sale baja, oye ese tramo con `--clip-timestamps`.
- **Un estado vacío filmado como si fuera la función** («No hay reglas pendientes», «0/0») pasa todos los checks. Lo encuentra solo la revisión de espectador.
