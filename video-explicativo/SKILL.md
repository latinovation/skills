---
name: video-explicativo
description: Use when the user asks for a video that explains something we built or something that happened with it - a narrated walkthrough of one of our webapps (recorrido, video explicativo, manual en video, demo narrada, «muestra lo que hace la app»), optionally with a motion intro/outro, sound effects and music for a client presentation, or an animated story told from real data, like a chat assistant's weekly leads (conversaciones reales que terminaron en lead, resultados de la semana, casos atendidos por un asistente). Made with HyperFrames and GSAP motion, in 16:9 and/or 9:16.
---

# Video explicativo (HyperFrames + motion)

Dos modos con plantilla probada de punta a punta. **No se reescribe el método en cada proyecto: se copia la plantilla y se
llena.** El contrato de HyperFrames (clips, timelines, `check`) está en la skill `hyperframes`; aquí va solo lo propio.

| Modo | Cuándo | Qué se ve | Sonido |
|---|---|---|---|
| **recorrido** | «Muéstrale a X cómo funciona la app», manual en video, demo de lo que construimos | La app real grabada, enmarcada, con tarjetas de capítulo, acercamientos con anillo y subtítulos | Voz en off (Kokoro, gratis, local) verificada con Whisper |
| **historia** | «Haz un video con lo que pasó»: leads, chats, casos reales de un periodo | Cada caso como chat animado: la pregunta en grande, el hilo, el riel de pasos y la tarjeta del resultado, más un resumen con cifras | Sin voz; tic, pop y whoosh (sonidos de media-use) |

**Principio de los dos:** lo que se dice o se escribe tiene que ser cierto y verse en pantalla en ese segundo. En el
recorrido, la voz va primero y la escena dura lo que dura su voz. En la historia, el texto sale de la base de datos y el
ritmo sale del tiempo de lectura.

## Antes de empezar

Del pedido y la memoria sale casi todo. Pregunta todo junto (en Claude Code, con AskUserQuestion) solo lo que falte de esto:
- **Modo**, y **para quién** es el video. De eso depende si se graba con datos de ejemplo o reales.
- **Idioma**: el del cliente o del público. Para la voz en inglés: `"idioma": "en"`, voz `af_heart` y `"fonemas": "en-us"`.
- **Formatos**: 16:9 o 9:16. El recorrido es solo 16:9.
- **Marca**: colores, fuente y logo real (SVG o PNG horizontal) del cliente o de la app. Si existe una skill de marca del cliente, se usa.
- **Solo en recorrido, el realce** (apertura y cierre con motion, efectos y música): por defecto sí si el video va a un cliente o a una presentación; no en un manual interno. Si lleva música, de dónde sale: si va a redes o pauta, solo con licencia comercial.
- **Solo en historia**:
  - el **periodo exacto**, con fecha inicial y final en la zona horaria del cliente;
  - **qué cuenta como resultado** en los datos (lead enviado, cita confirmada…) y si cuentan los cancelados;
  - el **destino** (interno, el cliente o redes). Si va a redes, usa seudónimos en vez de nombres de pila y confirma el consentimiento del cliente;
  - el **tope de capítulos**: 5 a 8. El resumen cuenta todos los casos.

Antes de fijar fechas, corre `date`. Carpeta: `~/Developer/_<proyecto>-video-<AAAA-MM-DD>/`, nunca dentro de `Documents/`, porque iCloud vacía los archivos.

```bash
S=~/.claude/skills/video-explicativo   # en Codex: S=~/.agents/skills/video-explicativo
```

## Modo recorrido

```bash
P=~/Developer/_<proyecto>-video-<fecha>
bash $S/scripts/nuevo.sh recorrido $P && cd $P   # copia la plantilla e instala playwright; TODO se corre desde $P
```

1. **La app, local y con el estado sembrado.**
   - Córrela en un worktree o una copia, con `next build && next start -H 127.0.0.1 -p <puerto libre>`. Con `dev` salen la insignia y la compilación lenta, y un `build` pisa el `.next` de un `dev` en marcha.
   - Apágala por puerto: `kill $(lsof -iTCP:<puerto> -sTCP:LISTEN -t)`. Nunca con `pkill -f next-server`, que mata las apps de otras sesiones.
   - Antes de grabar, confirma que `.env.local` no apunte a la base de producción.
   - Usa cuentas `@ejemplo.invalid` o la copia local con datos de producción.
   - **Nunca escribas en producción.** Lo que deba «guardarse» se responde con `page.route`. Si es una Server Action de Next, que responde RSC y no se puede fingir, graba contra la copia local con base de ejemplo.
   - Haz la lista de qué estado necesita cada toma, siémbralo y deja escrita la reversión. Un estado vacío filmado como si fuera la función es el error más caro.
   - Recorre las rutas con un script de solo lectura para sacar los selectores reales (rol y etiqueta, no clases frágiles).
2. **`proyecto.json` y `guion.json`.** Campos en `referencias/recorrido.md`.
   - Una línea del guion = una escena: 5 a 9 s, unas 15 a 25 palabras. Kokoro lee a ~2,9 palabras/s.
   - Duración total ≈ intro (voz + 2,6 s) + 2,6 s por capítulo + la suma de (voz + 1,45 s) de cada escena + cierre (voz + 2,8 s).
   - Si una escena tiene más acciones de las que caben en su voz, alarga la frase. Si no, la escena se estira y queda un silencio.
   - Escribe las cifras en palabras y ponlas en `pantalla` para que el subtítulo las muestre en dígitos. Cada cifra que se dice debe verse en esa escena.
   - Máximo 9 capítulos, con intro y cierre.
3. **Voz:** `~/.venvs/kokoro/bin/python voz.py`. El resultado debe ser `RECHAZADAS: ninguna`.
   - Si Whisper oye otra cosa, **reescribe la frase**, no cambies la voz. Las siglas se escriben como se pronuncian.
   - Cambiar una línea vuelve a sintetizar solo esa línea, y hay que volver a grabar su toma.
4. **`grabacion/tomas.mjs`:** es lo único que se programa. La API está en `referencias/recorrido.md`.
   - Se mantienen `escena(id, fn)` + `aPalabra("palabra")`, o `a(f)` con la fracción de la voz. Así la acción cae sobre la palabra que la nombra.
   - Las cargas y los precalentamientos van fuera de las escenas.
   - Usa `foco()` solo sobre lo que hay que leer, máximo 2 por escena. Una cámara que sube y baja todo el tiempo marea.
5. **Grabar:** `bash grabacion/grabar-todo.sh`. Corre un proceso por toma, con tope y reintento.
   - Cada toma debe terminar en `faltan: []` en `salida/todo.log`.
   - Luego `(cd grabacion && python3 hoja.py <toma>)` y **MIRAR la hoja**. Una escena «larga» contra su voz es una acción que esperó un timeout: corrígela y vuelve a grabar esa toma.
6. **Montar:** `(cd video && python3 montar.py)`. Para una toma de humo: `(cd video && SOLO=<cap> python3 montar.py)`.
   - **Realce (opcional):** `(cd video && python3 montar.py && python3 realzar.py)`. Se configura en `proyecto.json` → `realce` (`referencias/recorrido.md`). Va SIEMPRE después de `montar.py`, porque cada `montar.py` lo borra.
     - Cambia la intro y el cierre por piezas de motion: cuadrícula, hexágonos en los tonos del acento, logo con brillo y anillo, y pilares que entran cuando la voz los nombra.
     - Pone el fondo de marca en las tarjetas de capítulo.
     - Agrega un whoosh por capítulo, un golpe en cada logo y la música de `video/assets/musica/fondo.*`, que baja mientras habla la voz.
     - Música: ver `referencias/trampas.md` → Música (licencia y cómo alargarla).
7. **Revisar la composición:** `(cd video && npm run --silent check -- --json)`. Los scripts de `package.json` llevan la versión fijada.
   - Debe dar `"ok": true`.
   - Avisos esperados, que no se corrigen: `nested_media_start_basis_ambiguous` (los tiempos son locales a propósito) y `timeline_track_too_dense`.
   - Después: `(cd video && npm run --silent snapshot -- --at <s,…> --output snaps)` en cada foco y en cada cambio de capítulo, y mirarlos.
8. **Vista previa antes del render final:** `(cd video && npm run dev)`. El usuario puede editar ahí; ofrécele la app de escritorio de HyperFrames.
   - Renderiza cuando el usuario lo apruebe o cuando haya pedido el video sin paradas.
9. **Render:** `bash render_tramos.sh video entrega/<archivo>.mp4 60`.
   - Renderiza por tramos, con vigilante de disco, unión sin deriva y volumen a −16 LUFS.
   - Antes, apaga la vista previa del mismo proyecto (por su puerto). Si corren a la vez, se pisan en `.transcode-cache` y el render falla con `ENOENT`.
   - Si el disco interno tiene menos de 3 GB libres o la swap está casi llena, usa tramos de 15 a 30 s.
10. **Revisar el render final** (ver «Antes de entregar»): `python3 revisar.py entrega/<archivo>.mp4 revision video/linea-de-tiempo.json`.

## Modo historia

```bash
P=~/Developer/_<proyecto>-video-<fecha>
bash $S/scripts/nuevo.sh historia $P && cd $P   # copia la plantilla y los sonidos; TODO se corre desde $P
```

1. **Datos por consulta guardada.** El ejecutor de ejemplo y el detalle están en `referencias/historia.md`.
   - Guarda en `sql/` las consultas de solo lectura: casos, mensajes y cifras del resumen. Cada consulta lleva fecha inicial y final explícitas.
   - Excluye las pruebas: `is_test`, visitantes de prueba y nombres o correos que empiecen por `probe`.
   - Los crudos con datos personales van a `private/` y no salen de ahí; la consulta escribe a archivo, nunca a la consola.
   - Las cifras de la intro y del resumen se copian de `sql/*.result.json`, nunca se escriben a mano.
   - Confirma cada resultado en su fuente (CRM, agenda). Que el asistente diga «agendé» no prueba que haya cita.
2. **`historia.json`.** El esquema está en `referencias/historia.md` y la plantilla trae un ejemplo ficticio.
   - Los textos son los reales. Lo único permitido es recortar con «…», cambiar las rayas largas por coma o dos puntos (si la marca lo pide) y omitir mensajes enteros.
   - Cada edición se anota en `REVIEW.md`.
   - Los mensajes de agentes humanos se quitan o se rotulan; nunca se atribuyen al asistente.
   - El contacto va con •. Apellidos con `••••••` de largo fijo, para que el largo no delate el apellido real.
   - Las fotos van solo como marcador «Foto enviada».
   - No inventes texto.
3. **Datos personales:** escribe un script que genere `private/prohibidos.txt` desde los crudos (nunca a mano en el chat). Cómo hacerlo: `referencias/historia.md`.
   - Corre `python3 pii_guard.py`. Debe dar `hallazgos: 0`.
   - Prueba negativa: la misma lista contra los crudos de `private/` tiene que encontrar casi todo. Si no encuentra nada, la lista está mal.
4. **Construir:** `python3 construir.py h` y `python3 construir.py v`.
   - Luego `(cd film && npm run --silent check -- --json)`, y lo mismo en `film-v`. Debe dar `"ok": true`.
   - Avisos esperados: `line_unread` del indicador «escribiendo», `first_frame_empty` y `outside_safe_zone` en 9:16.
5. **Mirar los cuadros:** `(cd film && npm run --silent snapshot -- --at <s,…> --output snaps)` en la intro, en el resultado de cada capítulo y en el resumen.
   - El resultado de cada capítulo cae en `fin − 2`. Los tiempos de `film/linea-de-tiempo.json` son absolutos.
   - Comprueba que nada se pise y que el último paso del riel se vea más de 1 s.
   - Vista previa: `(cd film && npm run dev)`. Renderiza cuando el usuario apruebe o cuando haya pedido el video sin paradas.
6. **Render de cada formato:**
   - `bash render_tramos.sh film entrega/<archivo>_16x9.mp4`
   - `bash render_tramos.sh film-v entrega/<archivo>_9x16.mp4`
7. **Revisar el render final:** `python3 revisar.py entrega/<archivo>_16x9.mp4 revision-h film/linea-de-tiempo.json`, y lo mismo con el de 9:16.

## Antes de entregar (los dos modos)

`revisar.py` mide la duración, los cuadros negros, el volumen y, si hay voz, si cada voz se oye en su lugar. **Eso no basta.**
Mira las hojas a 2 cuadros/s completas, como espectador, y contesta por escrito las 6 preguntas de `informe.md`.
Está en `revision/` en el recorrido y en `revision-h/` y `revision-v/` en la historia.

La pregunta 5, la pasada de significado, es la que más ha fallado. Consiste en leer cada texto que escribimos nosotros (título,
capítulos, riel, resumen) y preguntar si es cierto para ese periodo y ese cliente.
- Han salido mal: «next two weeks» por un periodo que ya pasó, «solved each one» cuando no se resolvieron todos, y pronombres deducidos del nombre.
- Si el video va al cliente, que haga esa pasada un revisor sin tu contexto, cotejando con la fuente.

Entrega en `~/Downloads/<Proyecto>_Video_<AAAA-MM-DD>/`. Si la carpeta ya existe, lee primero su LEEME. Va el MP4 con un
`LEEME.md` que dice:
- qué es, cuánto dura, de dónde salieron los datos y qué se decidió;
- cada incoherencia que quede, con su segundo;
- en el recorrido: «nadie oyó la voz: se verificó con Whisper»;
- si lleva música: de dónde salió y su licencia;
- en la historia: «el sonido se midió, no se oyó».

Borra `entrega/*.tramos/` cuando el MP4 final esté revisado.

## Reglas que no se negocian

| Regla | Por qué |
|---|---|
| Voz antes que la grabación; la escena espera a su voz | La sincronía sale de la construcción, no de ajustar después sobre el MP4 |
| Nada se escribe en producción para el video | Un pedido o un recibo de prueba queda en la base del cliente |
| La cifra se ve ≥ 1,5 s antes de decirla y es la misma que está en pantalla. Si se dice en las primeras palabras de la escena, reordena la frase | Tres videos seguidos salieron con las cifras sobre el indicador equivocado |
| Mirar el render final completo antes de entregar | Las métricas en verde no ven rótulos que tapan la acción ni estados vacíos |
| Datos personales: crudos solo en `private/`, `pii_guard.py` en 0 | La redacción de la base no tapa direcciones ni correos mal escritos |
| Nunca desenfocar papeles o pantallas para «arreglar»: se acerca el cuadro o se regraba | Se ve como un error y tapa lo que el video quería mostrar |
| Render largo con poco disco: por tramos | La swap tumba el render a mitad y deja la sesión sin espacio |

## Qué NO cubre

- Video generado con IA (personas, UGC, Higgsfield o Seedance): eso va por su propia skill.
- Una pieza de motion pura, sin app ni datos (un promo o un título): ve directo a la skill `hyperframes`.

Trampas conocidas de grabación, voz, render y ffmpeg: `referencias/trampas.md`.
