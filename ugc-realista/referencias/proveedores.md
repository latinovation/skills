# Servicios de generación: lo medido (oct-2026)

Cada persona usa **sus** cuentas. Las llaves nunca se pegan en el chat: la persona las guarda ella misma en
`~/ugc-realista/.env` (una por línea, `NOMBRE=valor`, con `chmod 600`). Claude **nunca lee ni imprime ese
archivo**: lo carga al entorno de una subshell en el mismo comando que llama al servicio, para que la llave no
quede en la sesión (`( set -a; . ~/ugc-realista/.env; set +a; python3 mi_script.py )`), y el código toma la
llave de `os.environ`.
Antes de escribir código contra una API, leer su documentación vigente (si existe el comando `chub`,
`chub get <paquete>`); lo de abajo son mediciones reales con fecha, no la documentación. **Los precios cambian:
cotizar siempre con el servicio antes de pedir permiso.**

## Empezar con kie.ai (el camino para quien ensaya la skill por primera vez)
1. **Llave:** créala en kie.ai (página de llaves de API) y guárdala TÚ en `~/ugc-realista/.env` como `KIE_API_KEY=…` (`chmod 600`). Nunca la pegues en el chat. kie.ai da unos créditos de bienvenida a las cuentas nuevas (la página de Wan 3.0 menciona 80); la recarga está en kie.ai/pricing.
2. **Comprobar la conexión y el saldo:** `( set -a; . ~/ugc-realista/.env; set +a; python3 <carpeta de la skill>/scripts/kie_tarea.py saldo )`.
3. **Subir las referencias:** `kie_tarea.py subir imagen.png voz.mp3` devuelve una URL por archivo (imágenes de hasta 20 MB, audios de hasta 15 MB y 15 s).
4. **Cotizar:** `kie_tarea.py crear …` SIN `--si` no envía nada y muestra el cuerpo y el costo. Cuando la persona dice «sí», se repite con `--si`.
5. **Revisar la toma** con `revisar_toma.py` y mirando (ver `SKILL.md`).
- **Qué modelo usar para ensayar:** Wan 3.0 (`--modelo wan3`) a 480P cuesta US$0,04 por segundo (un plano de 8 s = 64 créditos, US$0,32) y a 720P US$0,08; con su voz propia y el texto verificado por transcripción. Seedance 2.5 (`--modelo seedance`) a 480p cuesta 28 créditos por segundo (8 s = 224 créditos, US$1,12) y va con voz de referencia: úsalo cuando el guion deba salir exacto.
- **Errores de kie:** responden con HTTP 200 y un `code`; «The server is busy» no cobra, se reintenta; un trabajo en espera se consulta con `kie_tarea.py estado <taskId>` antes de pagar otro. Más abajo, la sección kie.ai tiene la API completa.

## Higgsfield (CLI `higgsfield`)
- Instalar: `npm install -g @higgsfield/cli`. Entrar: `higgsfield auth login` (abre el navegador). Si dice «No
  workspace selected»: `higgsfield workspace list` y `higgsfield workspace set <id>`.
- Llamarlo `higgsfield` o `higgs`. `hf` puede ser otro programa (el de Hugging Face) si está antes en el PATH.
- Parámetros de un modelo: `higgsfield model get <modelo>`. Lista: `higgsfield model list --video|--audio|--image`.
- Saldo: `higgsfield account status`. Cotizar: `higgsfield generate cost <modelo> …` con los mismos parámetros
  (en `omni_reference` exige al menos un archivo de referencia).
- **Plano con personaje, producto y voz** (Seedance 2.5, medido: 8 s a 720p = 56 créditos, 7 créditos/s;
  1080p 12/s; hasta 30 imágenes de referencia; 4–30 s):
  ```bash
  higgsfield generate create seedance_2_5 --mode omni_reference --duration 8 --resolution 720p \
    --aspect_ratio 9:16 --prompt "$(cat plano1.txt)" "${REFS[@]}" --audio-references voz_plano1.mp3 \
    --wait --wait-timeout 25m --json > plano1_a.json
  ```
  `REFS` es un arreglo (`REFS=(--image-references poses/p1.png --image-references producto.png …)`); en zsh una
  variable sin comillas no se separa y el CLI responde «Too many positional args».
- **Imágenes** (pose maestra, poses, placa): elegir con `higgsfield model list --image`; una placa 2k con GPT
  Image 2.5 costó ≈ 2,75 créditos. Cotizar con `generate cost`.
- **Voz** (los flags cambian por modelo: siempre `higgsfield model get <modelo>` antes): `inworld_text_to_speech` (voz «Lupita (es)» aprobada en una prueba) y `text2speech_v2`
  (`--variant elevenlabs|minimax|seed_speech|… --voice-id … --voice-type preset|element`; ids en
  `higgsfield voices list`). Una línea cuesta ≈ 0,3 créditos. `qwen_audio_tts` no tiene español.
- **Cambiar persona u objeto dentro de un video:** `hf_mult_replace_object` (Object Swap) y
  `hf_mult_motion_control` (Motion Transfer): 1 `--video-references` + al menos 1 `--image-references`. Cobran como
  Seedance 2.5 (clip de 15 s: 45 créditos a 480p, 105 a 720p, 300 a 1080p).
- **Wan 3.0** (`wan3_0` y `wan3_0_prime`; prueba corta del 22-oct-2026, 8 s, 720p, 9:16): cuestan 14 y 24 créditos
  (Seedance 2.5: 56). Aceptan `--image-references`, `--audio-references`, `--video-references`,
  `--start-image`/`--end-image` (estas no se combinan con referencias), `generate_audio` y duración de 2 a 30 s
  o -1. Con audio de referencia, Wan deja la voz casi igual a la entregada (correlación 0,99 medida en
  `wan3_0`), a diferencia de Seedance, que la re-genera (0,23). Resultado con una toma por modelo, una marca de gomitas y una avatar:
  `wan3_0` salió bien según la persona; `wan3_0_prime` falló en lipsync y se movía menos (cara en movimiento
  4,2 contra 6,1). Es una muestra pequeña y el prompt cambió entre rondas: repetir antes de generalizar. Mismas
  revisiones que con cualquier modelo.
- **Gastos:** `higgsfield account transactions --size 20` lista cada cobro por modelo. En una cuenta que usan
  otras sesiones, el saldo baja por cobros ajenos (en la prueba, 78 de 182 créditos no eran del proyecto).
- **Fallos medidos:** con `--wait` puede salir HTTP 503 aunque el trabajo exista y se cobre → NO repetir;
  buscarlo con `higgsfield generate list --size 20 --json` y bajar `result_url`. Un trabajo puede quedarse
  «in_progress» ~30 min y terminar después: recuperarlo con `higgsfield generate get <id>` antes de pagar otro.
  Un error 520 al subir referencias es antes del cobro: reintentar. El CLI no borra nada (solo la web).
- Precio en dólares: depende del plan de cada persona. Preguntar cuánto paga por cuántos créditos; no adivinar.

## kie.ai (API, llave `KIE_API_KEY`)
- Modelo `bytedance/seedance-2-5`. Doc: docs.kie.ai (market › bytedance › seedance-2-5).
- **Tarifa (créditos por segundo; 1 crédito = US$0,005):** generar sin video de referencia 480p 28 · 720p 63 ·
  1080p 158. Con video de referencia 17 · 38 · 95, cobrados sobre (segundos del video subido + segundos
  generados). Imágenes y audio de referencia no cobran.
- **Edición (transformar):** exige `aspect_ratio: "adaptive"` y `duration: -1` (si no, falla sin cobro). Con
  `duration: -1` reserva créditos de la duración máxima al crear: dos tareas en paralelo → error 402. Encadenar.
  Límite 30 s por tarea. La salida pierde ~0,3 s al final y a 480p puede llegar sin audio.
- La API recibe **URLs** de los archivos: subirlos con el servicio de subida de archivos de kie (ver su doc
  vigente) o servirlos desde una URL pública temporal. Ambos caminos se usaron en el equipo.
- Generar desde cero: 8 s a 480p = 224 créditos exactos; la salida no se trunca. `first_frame_url` y
  `last_frame_url` no se mezclan con `reference_*_urls`.
- El filtro de derechos de autor juzga el parecido de la salida y falla sin cobro.

- **API (docs.kie.ai, leída el 22-oct-2026):** base `https://api.kie.ai`, cabecera `Authorization: Bearer <llave>`.
  Crear: `POST /api/v1/jobs/createTask` con `{"model": …, "input": {…}, "callBackUrl": opcional}`. Consultar:
  `GET /api/v1/jobs/recordInfo?taskId=…` → `data.state` (`waiting`, `queuing`, `generating`, `success`, `fail`),
  `data.resultJson` (texto JSON con `resultUrls`), `failMsg` y `creditsConsumed`. Saldo: `GET /api/v1/chat/credit`.
  Los errores llegan con HTTP 200 y un `code` distinto de 200: revisar `code`, no el estado HTTP. Subida de archivos
  (base `https://kieai.redpandaai.co`): `POST /api/file-url-upload` (campo `fileUrl`) y `/api/file-stream-upload`
  (multipart).
- **Cliente listo: `scripts/kie_tarea.py`** (`saldo`, `crear`, `estado`; llave desde el entorno). `crear` SIN `--si`
  nunca envía: valida los límites del modelo, muestra el cuerpo y el costo estimado. Con `--si` (cotización ya
  aprobada) crea la tarea, la sigue y baja el video. `subir` sube archivos locales y devuelve la URL (imágenes y audio hasta ~5 MB, probado con seis archivos). Probado el 22-oct: saldo, subida, simulaciones,
  validaciones y dos trabajos reales de Wan. Flags de `crear`: `--primer-cuadro`/`--ultimo-cuadro` (URL),
  `--ref-img`/`--ref-video`/`--ref-audio` (repetibles), `--audio`, `--resolucion`, `--ratio`, `--duracion`. Imágenes de
  Nano Banana 2 y voces de ElevenLabs: `scripts/kie_lote.py` (un trabajo a la vez; anota `gasto.tsv` de la carpeta
  desde la que se corre).
- **Wan 3.0 en kie** (`wan/3-0-video`; página del modelo y docs, 22-oct-2026). **Medido el 22-oct-2026 con 2 trabajos de 11 s a 720P: 176 créditos cada uno (16 por segundo, igual que la tarifa), 252 y 262 s de espera.** Con `reference_audio_urls` deja la voz de entrada casi intacta (correlación 0,984, sin desfase): la voz la pones tú, Wan no la inventa. Modo referencias con 5 imágenes (3 poses del personaje, el frasco y el lugar) y una voz: el personaje se conservó (parecido 0,80 contra el kit):
  8 / 16 / 32 créditos por segundo a 480P / 720P / 1080P, o sea US$0,04 / 0,08 / 0,16 por segundo. Se cobra
  duración de salida + segundos de video de referencia. Campos de `input`: `prompt` (hasta 20.000 caracteres),
  `first_frame_url` y `last_frame_url` (no se combinan con `reference_*`), `reference_image_urls` (hasta 10; en el
  prompt `Image1…`), `reference_video_urls` (hasta 5 de 1 a 15 s, 15 s en total; entrada más salida hasta 30 s),
  `reference_audio_urls` (hasta 5), `resolution`, `aspect_ratio` (`adaptive`, 16:9, 4:3, 1:1, 3:4, 9:16),
  `duration` (2 a 30, o -1 para que el modelo elija), `audio` y `seed`.
  🔴 **El valor por defecto de `resolution` es 1080P** (4 veces el costo de 480P): enviar siempre la resolución.
  Por defecto `audio` es true y `duration` es 5.
- **Sincronía de labios (medido el 22-oct-2026, mismo plano de 11 s de una marca de gomitas):** con Wan 3.0 y una voz de referencia, la persona vio que la boca no seguía bien la voz. Wan deja el audio intacto (correlación 0,984) y solo mueve la boca hacia él. Se probaron tres arreglos en kie:
  (A) **Seedance 2.5 con la misma voz como referencia**: 308 créditos a 480p (28 por segundo, como la tarifa); regenera la voz; texto 1,00 y marca bien dicha.
  (B) **Wan 3.0 sin audio de referencia** (la voz la inventa el modelo): 176 créditos; dijo bien el nombre de la marca pero **añadió palabras** («gigante, o sea» repetido), así que no respeta el guion.
  (C) **Pasada de sincronía de labios sobre el video ya hecho**, `volcengine/video-to-video-lip-sync` (`scripts/kie_tarea.py lipsync`): entra un video y un audio; modo `lite` para una persona de frente, `basic` para escenas complejas; la salida (MP4, 25 fps) dura lo que el audio, y con `align_audio` repite el video si el audio es más largo; 88 créditos por 11,9 s (≈ 7,4 créditos por segundo, US$0,037/s). Reemplaza la voz del video por la del audio. Texto 0,99 y marca bien dicha. Un error «The server is busy» no cobró: reintentar.
  **Veredicto de la persona (22-oct-2026, viendo y oyendo las tres):** A y B salieron muy bien; C salió mal. B dijo palabras de más, pero fue la opción que prefirió. La medida automática de la boca (apertura contra volumen de voz) dio ruido en las cuatro tomas, incluida Seedance, así que NO sirve para ordenarlas: el juicio es de la persona.
  **Cómo usarlo:** por defecto, Wan 3.0 con voz propia (B, 176 créditos a 720P) y **comprobar con la transcripción que el texto sea exacto, repitiendo la toma si añade o quita palabras**; Seedance 2.5 con voz de referencia (A, 308 créditos a 480p) cuando haga falta el guion palabra por palabra. No usar la pasada `lipsync` (C) sobre un video ya hecho como solución por defecto.
- **Modelos de video que lista kie** (market, 22-oct-2026): Seedance 2.5, Seedance 2, Wan 3.0, Veo 3.1, Grok Imagine
  1.5, Kling 4.0, Vidu Q4 y, en la página de documentación, Wan 2.2, 2.5, 2.6 y 2.7. No se midió ningún otro.
  `wan/2-2-animate-replace` dio «Internal Error» tres veces con 0 créditos (oct-2026): descartado.
- **Medido el 5-nov-2026 (sorteo con presentadora, 1.312 cr en total):**
  - `reference_image_urls` con «Image1 is MARIANA, the presenter: keep exactly…» e «Image2 is the studio…» conservó
    cara, ropa y set en tomas de 30 s (480P 240 cr, 720P 480 cr; 5–15 min); texto exacto 61/61 en 2 de 2 con voz propia.
    La persona se recorta SIN el objeto del set si el modelo de imagen le puso texto (balotas numeradas en el ancla).
  - `first_frame_url` (`kie_tarea.py crear --primer-cuadro URL`) con una imagen fija del set y un prompt de UN evento
    (5 s, 720P, 80 cr): 6/6 clips con la física exacta (mezcla, una sola balota, copa vacía → una balota). Es la salida
    para lo que Wan no hace en una toma larga: contar, conservar cantidades y sincronizar la acción con la voz.
  - **Nano Banana 2** (`nano-banana-2`, `scripts/kie_lote.py imagen`): 8 cr por imagen 1K 9:16; `--ref URL` (hasta 10,
    campo `image_input`) para que una imagen nueva siga el diseño de otra (fijas de máquina con la placa como referencia:
    2/2 iguales al set; sin referencia, 2/2 distintas). Un número grande en un inserto («printed with the black number
    23 facing the camera, printed once, crisp»): 7/7 exactos. Puede ignorar «no printed numbers» en objetos pequeños.
    «generate task timeout» (2 de 8) llega como fallo sin cobro: relanzar.
  - Errores: `402` «Credits insufficient» llega con HTTP 200 y no cobra. Una llave compartida con otras apps baja el
    saldo sin tarea de la sesión (320 cr en 10 min): `saldo` antes de cada etapa y anotar por `taskId` en `gasto.tsv`.

## Cuál conviene por costo (referencia, 4 s de video)
| Servicio y modelo | 480p | 720p | Origen de la cifra |
|---|---|---|---|
| kie.ai · Wan 3.0 | US$0,16 | US$0,32 | tarifa de su página; 720P medido (176 créditos por 11 s) |
| Comfy Cloud · Wan 3.0 | US$0,29 | sin medir | medido (28,6 ¢) |
| Higgsfield · Wan 3.0 | 4 créditos | 7 créditos | cotización; el precio del crédito depende de tu plan |
| kie.ai · Seedance 2.5 | US$0,56 | US$1,26 | tarifa de su blog; 480p medido (224 créditos por 8 s) |
| Comfy Cloud · Seedance 2.5 | US$0,64 | US$1,51 | medido |
Para animación 3D, donde el realismo importa menos, Wan 3.0 a 480P es lo más barato de esta tabla; para UGC con voz y
cara real, Seedance 2.5. Cotizar siempre con el servicio antes de pedir permiso.

## Comfy Cloud (API, llave `COMFY_API_KEY`)
- Base `https://cloud.comfy.org`. Cabecera `X-API-Key`; para nodos de pago, la misma llave también en
  `extra_data.api_key_comfy_org` del envío. Nodo `ByteDance2ReferenceNodeV2` (Seedance 2.5 Reference to Video),
  `task_type: edit` para transformar.
- Costo: 480p ≈ US$0,16–0,17 por segundo; 720p ≈ US$0,377 por segundo.
- **Un trabajo a la vez:** dos en paralelo → 429 del proveedor y se pierde el trabajo. Un clip de 10–14 s tarda
  4–7 min.
- La salida pierde 0–0,3 s, a veces dentro de una escena (ver `transformar.md`).

- **Wan 3.0** (medido el 22-oct-2026, videos 3D de una marca de gomitas): nodo `Wan3ReferenceToVideoApi` (también `Wan3ImageToVideoApi`
  para primer y último fotograma). Entradas: `model` = `wan3.0-video`, `model.prompt`, `model.resolution` (`480P`),
  `model.ratio`, `model.duration` como TEXTO (`"4"`), `model.audio` (false), `model.prompt_extend`, `seed`, `watermark`
  y las referencias como `model.reference_images.image1`, `image2`… (**sin guion bajo**, a diferencia de Seedance, que
  usa `image_1`; con el nombre equivocado falla con «unexpected keyword argument», sin cobro). 480P cuesta
  28,6 centavos de dólar por 4 s. Imágenes del kit con `GeminiNanoBanana2V2` (≈ 8 centavos cada una). El detalle de un
  trabajo fallido está en `GET /api/job/{id}/status` → `error_message` (`history_v2` da 404 si falló).

## Otro servicio
Si la persona usa otro (Kling, Veo, Runway…): leer su documentación vigente, cotizar con su calculadora, y
aplicar igual las capas de `senales-ia.md`. Anotar lo aprendido en el cuaderno.
