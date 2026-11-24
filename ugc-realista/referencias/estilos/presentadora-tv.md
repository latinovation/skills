# Estilo «Presentadora de TV» (`presentadora-tv`) — piloto

Muestra: `~/ugc-realista/estilos/presentadora-tv.jpg`. Estado: piloto (un sorteo de balotas con una presentadora inventada, en su quinta versión). El método se aprobó
paso a paso viendo cada versión; falta aprobar la voz, el acento y el lipsync. Lo que no se probó va marcado «sin probar».

## Qué es
Una presentadora inventada conduce una transmisión en vivo desde un set de televisión (sorteo de balotas, resultados,
noticias) y habla a cámara con voz propia, mientras en el mismo set ocurre una mecánica física (máquinas de balotas).
Lo que importa es que la mecánica se vea REAL: la balota sale por donde debe, cae donde debe y se ve en el segundo
en que ella la canta. Se rechazaron versiones con balotas sin números que aparecían de la nada, movimientos antinaturales, una balota
que caía en el vaso y otra que la reemplazaba, o balotas que se revolvían poco.

- **Dentro del estilo cabe:** presentadora, set de TV con cámara fija de estudio, máquinas y objetos del set, panel
  de resultados y ventanas de «cámara» en el montaje.
- **No cabe:** números o letras legibles generados por el modelo dentro de la toma, marcas reales (Baloto es marca
  registrada), look de celular (es cámara de estudio).

## Firma (en números)
- **Imagen:** «Live television broadcast of a lottery draw, as seen on a TV channel's live stream: static studio
  cameras at eye level… even soft studio key light with a cooler blue backlight from the set, deep focus with the
  whole set sharp, slight broadcast video sharpness, no cinematic shallow depth of field, no film color grade, no
  handheld shake». Vertical 9:16 (16:9 sin probar).
- **Presentadora:** una, inventada, sin joyas, vestido liso; voz propia de Wan con ritmo de presentadora en vivo.
  Texto exacto 61/61 en 2 de 2 tomas de 30 s.
- **Mecánica:** una máquina por balota, en fila sobre un mesón; cada balota sale por la boca inferior de SU máquina a
  SU copa. La toma larga pone la voz y los planos de ella; la acción exacta de cada balota viene de un clip de 5 s por
  máquina (ver Producción).
- **Sincronía:** la balota toca la copa 0,3 s ANTES de la palabra; el círculo del panel aparece con la palabra.
- **Números legibles solo en montaje:** panel de círculos arriba, bajo el título (300–440 px en 1080×1920), y ventana
  «cámara de balota» de 200×356 a la derecha (852, 460) con un inserto fijo por balota.
- **Los rótulos nunca tapan copas, salidas ni esferas.** El primer montaje los tapaba y la mecánica no se veía.

## Estructura de 30 s (61 palabras)
| s | Escena | Qué se ve |
|---|---|---|
| 0–6 | Saludo | Plano medio de ella junto a la fila de máquinas; presenta el sorteo |
| 6–10 | Mezcla | Primer plano de dos máquinas mezclando con aire (clips) |
| 10–19 | Cinco balotas | Por cada número: corte al clip de su máquina (mezcla → sale → cae → copa), vuelta a ella cantando, círculo y ventana |
| 19–24 | Dorada | Igual con la sexta máquina, de balotas doradas |
| 24–30 | Cierre | Plano de ella a cámara; la fila completa en la ventana |

## Producción (medido el 5-nov-2026 en kie.ai, 1 cr = US$0,005)
| Paso | Qué | Costo |
|---|---|---|
| Ancla de la presentadora | Nano Banana 2, 1K 9:16 (`scripts/kie_lote.py imagen`); si el modelo le pone texto al objeto del set, se recorta sin él (0 cr) | 8 cr |
| Placa del set | NB2: seis máquinas en fila con el camino físico descrito (salida en la base → copa), copas vacías, sin texto | 8 cr |
| Insertos de balota | NB2, uno por número («printed with the black number 23 facing the camera, printed once, crisp»): 7/7 dígitos exactos a la primera; más la fila final | 8 cr c/u |
| Fijas de máquina | NB2 con la placa como `--ref` (blanca y dorada): primer cuadro de los clips. Sin `--ref` no coincidían con el set (2/2) | 8 cr c/u |
| Toma larga | Wan 3.0, 30 s, 720P, 9:16, con audio; `reference_image_urls`: Image1 = presentadora recortada sin la máquina, Image2 = placa; 9–15 min | 480 cr (480P: 240) |
| Clips por máquina | Wan 3.0, 5 s, 720P, `first_frame_url` (`kie_tarea.py crear --primer-cuadro`), UN evento por clip: 6/6 bien a la primera (mezcla visible 0,6–2,0 s, aterrizaje 3,55–3,65 s, esfera llena, copa vacía → una balota) | 80 cr c/u |
- Un video nuevo con el método final: ancla + placa + 7 insertos + 2 fijas + toma + 6 clips ≈ **1.048 cr a 720P**.
- El piloto costó 1.312 cr porque incluye una v1 (una sola máquina, 256 cr) descartada.
- Nano Banana 2 dio «generate task timeout» en 2 de 8 imágenes, sin cobro: relanzar el script (salta lo existente).

## Prompt base
Las plantillas completas están en el proyecto de referencia (no vienen en esta copia).
- **Ancla** (`img/presentadora.txt`): presentadora «around 32, medium-full shot from the knees up» en el set, «a real
  person, not a model: natural asymmetry… visible pores», «No jewelry at all», la mirada a cámara «mouth slightly open
  as if starting to speak», el bloque de imagen de la firma y «No text, no letters, no numbers, no logos…».
- **Placa** (`img/estudio_v3.txt`): el set vacío con la mecánica descrita como camino físico: «each one is a clear
  sphere on a short dark base, completely full of glossy white lottery balls printed with small black two-digit
  numbers, with a round outlet at the bottom of the sphere that drops one ball into a small clear acrylic cup fixed to
  the front of its base; all six cups are empty».
- **Toma larga** (`wan/toma3.txt`), en este orden:
  1. «Image1 is MARIANA, the presenter: keep exactly her face, her long straight dark brown hair worn loose and her
     plain deep-blue fitted dress in every scene. Image2 is the studio: …; every scene happens here.»
  2. `LOOK:` el bloque de imagen de la firma + «She wears no jewelry at all…».
  3. `MACHINE PHYSICS:` «There are exactly six machines and they never change number, size or position… A ball never
     appears out of thin air and never passes through the acrylic: the only way a ball leaves a sphere is through the
     round outlet at the bottom, and it drops straight down into the small clear cup of that same machine… each cup
     starts empty and ends holding exactly one ball… nothing floats, slides upward or teleports.» (Con esto cada balota
     salió por su boca a su copa; lo que NO cumplió fue «every sphere is completely full from the very first frame to
     the last»: las esferas se vaciaron.)
  4. `Scene 1 (0-6 s): …` hasta `Scene 5 (24-30 s): …`, cada una con «She says: "…"».
  5. `ACTING:` «acts like a real live TV host: lively, warm and natural… starts each line right away… bright
     professional broadcast delivery, no long pauses».
  6. `AUDIO:` «Colombian Spanish spoken by MARIANA on screen… lips in sync… exactly the quoted words… no narrator, no
     music; only her voice, the sound of the balls and the quiet studio room tone».
  7. `NOTEXT:` «No on-screen text… the only numbers in the picture are the small printed numbers on the balls, never
     close enough to read».
- **Clip de máquina** (`wan/clip_maquina.txt`, 5 s desde la fija): «The video starts exactly from the first frame: a
  single transparent lottery drum machine in close-up… the small clear cup at the front of the base empty. Seconds 0
  to 2.5: the machine mixes vigorously like an air-mix lottery machine: a strong air blower inside tosses the balls up
  so they fly, tumble and bounce chaotically… Seconds 2.5 to 3.5: the blower stops, the balls settle, the round outlet
  at the bottom opens and exactly one ball is released: it drops straight down through the outlet, lands in the clear
  cup, bounces lightly and settles with its printed number turned away from the camera. Seconds 3.5 to 5: the ball
  rests still in the cup and the sphere stays full and still. Physics: that is the only ball that leaves the sphere;
  no ball appears out of thin air…; the cup starts empty and ends with exactly one ball… Static broadcast camera at
  eye level, locked off… Audio: only the rattle of the balls and the hum of the blower, no speech, no music.» Para la
  dorada, «golden-yellow balls» y la fija dorada.

## Montaje (HyperFrames 1080×1920; un script del proyecto de referencia, no incluido)
- Tiempos de palabra de la toma con `mlx_whisper` (`--word-timestamps True`); la voz de la toma queda continua.
- Por cada número, un corte al clip de su máquina con `data-media-start` = aterrizaje − pre, donde pre = 1,10 s si el
  número tiene aire y 0,55 s si va seguido del anterior (post 0,30 / 0,20 s); el aterrizaje cae en t(palabra) − 0,30 s.
  Los cortes de números seguidos se pegan uno con otro (sin volver a ella por 0,1 s).
- El aterrizaje se mide en cada clip con una tira a 10 cuadros/s (crop de la copa): 3,55–3,65 s en los seis.
- La escena de esferas quietas se reemplaza por dos clips mezclando (0–1,6 s de cada uno).
- El audio de cada clip (balotas, soplador) entra con su corte: `<audio>` aparte a 0,45 de volumen, fundidos 0,08/0,12.
- Panel arriba (círculo por número en t(palabra) − 0,05); ventana «cámara de balota» entre cortes solo si dura ≥ 1 s;
  fila completa en la ventana de 24 a 30 s.
- `npx hyperframes check --json` limpio → `render --quality delivery` → revisión como espectador (abajo).

## Revisión propia del estilo
- **Cada clip** (0 cr): hoja a 5 cuadros/s (mezcla visible, una sola balota, esfera llena), tira a 10 cuadros/s del
  aterrizaje y la copa a 4,6 s (una balota).
- **Render final, como espectador:** hoja a 2 cuadros/s completa; tira a 5 cuadros/s del sorteo (cada balota cae
  ANTES de su número y el círculo entra con la palabra); tira a 10 cuadros/s de cada empalme toma↔clip comprobando
  que la caída real de la toma quede DENTRO del corte (si no, se ve una doble caída); nada tapa copas, salidas ni
  esferas.
- **Texto** del MP4 final contra el guion (61/61), ignorando lo que Whisper alucina después del fin del audio.
- **Cara** contra el kit: 0,62–0,76 (en el plano abierto la cara queda pequeña y no se mide).
- **La persona:** voz, acento y lipsync.

## Fallas conocidas
| Falla | Qué hacer |
|---|---|
| Balotas lisas que «aparecen de la nada» y un tubo al lado de la esfera (v1: la placa no tenía camino físico) | Placa con el camino físico (salida en la base → copa) y balotas numeradas, nunca legibles en la toma; los números legibles van en insertos y panel |
| Wan no cuenta ni conserva cantidades en 30 s: 6 balotas en vez de 5 (v1); esferas que se vacían durante el sorteo (v3) aunque el prompt diga «completely full from the first frame to the last» | No prometer conteos; la acción exacta en clips de 5 s por evento; lo que quede en el plano abierto se documenta en el LEEME |
| «Una balota cae en el vaso y otra misteriosamente la reemplaza» (v3, copa 2 a 12,9 y 13,9 s) | Clip por máquina con «the cup starts empty and ends with exactly one ball»; en el render, comprobar que la caída de la toma queda dentro del corte |
| Ella canta el número ~1 s ANTES de que caiga la balota (v3) | Cortes al clip con la balota tocando la copa 0,3 s antes de la palabra |
| Sin mezclado visible en la toma larga («se revuelven poco, poco creíble») | Escena de mezcla con dos clips; cada corte largo empieza 1,1 s antes del aterrizaje y muestra la mezcla |
| La balota en reposo del clip muestra dígitos del modelo | Volver a ella 0,2–0,3 s después del aterrizaje |
| El panel tapaba las copas y la ventana tapaba tres esferas (defecto de montaje, 5-nov) | Panel arriba, ventana pequeña a la derecha; comprobar en el render, no solo en `check` |
| Nano Banana 2 puso números en las balotas del ancla pese a «plain… nothing readable» | Recortar el ancla sin la máquina (0 cr) y usar el recorte como Image1 |
| Las fijas de máquina no coincidían con el set (2/2 sin referencia) | Generarlas con la placa como `--ref` (2/2 iguales) |
| El inserto de la fila final muestra vasos distintos al set | Generarlo con la placa como `--ref` (sin probar) |
| kie 402 «Credits insufficient» a mitad de la etapa (llave compartida con otra app) | `saldo` antes de cada etapa; los `etapa*.sh` reanudan sin repetir lo que ya existe; avisar a la persona |

## Marca y legalidad
- Sin marca real; nombre provisional solo en montaje y la presentadora no lo dice (la toma sirve para cualquier marca).
- Un sorteo real es un juego de suerte y azar regulado (en Colombia, Coljuegos): si se publica la demostración, se
  marca como contenido hecho con IA y sorteo ficticio.

## Entregas de referencia
Los videos y proyectos de referencia de este estilo están en la computadora de quien mantiene la skill; no vienen en esta copia pública.
