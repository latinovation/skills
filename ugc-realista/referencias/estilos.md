# Estilos de video

Cada estilo es una receta probada en entregas reales: cómo se ve, cómo se produce, cuánto costó, cómo se monta y en
qué falla. Su ficha está en `estilos/<id>.md`. **Antes de cotizar, se elige el estilo y se lee su ficha completa.**
Donde la ficha difiera del proceso de `SKILL.md` (planos de 4–8 s, 2 tomas por plano, kit de personaje, audio de
celular), manda la ficha: el proceso de `SKILL.md` es el del estilo UGC.

Hay una tira de 5 cuadros de cada estilo en `~/ugc-realista/estilos/<id>.jpg`, solo en la computadora de quien mantiene la skill,
porque las de UGC y 3D personaje muestran el producto de un cliente.

| id | Estilo | Qué es | Sirve para | Costo medido | Método |
|---|---|---|---|---|---|
| `ugc` | UGC realista | Una persona habla a la cámara de su celular, en su casa | Confianza en un producto; reseñas, «te cuento» | Wan 3.0 720P: 176 cr por toma de 11 s (2 tomas por plano) | Planos de 4–8 s con personaje calibrado (proceso de `SKILL.md`) |
| `documental` | Real documental | Personas inventadas en su vida diaria; voz en off; luz natural | Explicar un beneficio con una historia cotidiana | 240 cr por 30 s (480P) + 8 cr por personaje | 1 toma de Wan de 30 s con 5 escenas y narración propia |
| `3d-cristal` | 3D médico de cristal | Cuerpo translúcido con esqueleto, órganos que brillan, fondo azul noche | Mecanismos del cuerpo y cifras de estudios | 240 cr por 30 s (480P) + 8 cr de imagen de estilo por serie | 1 toma de Wan de 30 s con 5 escenas y narración propia |
| `3d-personaje` | 3D animado de personaje | Personajes de película animada que viven una historia, a menudo sobre una canción | Historias emocionales, jingles, marcas cercanas | Wan 3.0 480P: US$0,0715/s en Comfy; 4 cr por 4 s en Higgsfield | Planos mudos de 4 s con el kit 3D del personaje, cortados al compás |
| `collage` | Collage editorial | Recortes de fotos con trama de puntos sobre un solo color, neón y tramos 3D en la misma paleta; una palabra por subtítulo | Ganchos para redes, mito contra verdad, datos | 528 cr por 30 s (3D a 720P) o 288 cr (480P) | 1 toma de Wan (voz y 3D) + 6 imágenes de collage + montaje con efectos |
| `presentadora-tv` | Presentadora de TV (piloto) | Una presentadora inventada conduce una transmisión en vivo desde un set de TV con cámara fija; la mecánica del set (máquinas de balotas) tiene que verse real | Sorteos, resultados y anuncios en vivo | ≈ 1.048 cr por 30 s a 720P (toma 480 + 6 clips de 80 + 11 imágenes de 8) | 1 toma de Wan de 30 s con voz propia + un clip de 5 s por evento físico (`first_frame_url`) cortado en el montaje; números solo en montaje |
| `ilustracion-animada` | Ilustración animada | Ilustración plana de cartel serigrafiado animada por capas, con una metáfora visual, voz en off, subtítulos arriba y datos con fuente | Explicar un concepto de salud o ciencia, mito contra realidad, «qué es X» | US$1,09 por 75 s (`gemini-api`: imágenes NB2.1, TTS y Lyria) | Imágenes fijas + piezas recortadas animadas en HyperFrames, ancladas a cada palabra de la voz |

## Cómo elegir
- **Una persona tiene que dar la cara por el producto:** `ugc`.
- **Hay que explicar qué pasa dentro del cuerpo:** `3d-cristal`.
- **El beneficio se entiende mejor en una escena de la vida diaria:** `documental`.
- **Es una historia con emoción o una canción:** `3d-personaje`.
- **El gancho es una pregunta o un dato que tiene que parar el scroll:** `collage`.
- **Hay que explicar un concepto con datos que se puedan defender, barato y con control total de lo que se ve:** `ilustracion-animada`.
- **Alguien conduce una transmisión desde un set (sorteo, resultados, anuncio en vivo):** `presentadora-tv` (piloto).
- Si la persona trae un video de referencia, se analiza (`ffprobe`, cortes, transcripción y hoja de cuadros) y se
  dice a qué estilo se parece. Si no se parece a ninguno, se propone un piloto y, cuando se aprueba, se escribe su
  ficha (ver «Agregar un estilo»).

## Reglas comunes a todos los estilos
- **Un solo estilo por video.** Cada ficha dice qué cabe dentro. Por ejemplo, el collage incluye tramos 3D en su
  misma paleta, pero ningún estilo admite planos de otro sin un pedido expreso.
- **El estilo y la marca son cosas separadas.** El estilo dice cómo se hace el video. La marca dice:
  - colores, logo y tipografía;
  - el cierre;
  - la voz;
  - qué afirmaciones están aprobadas.

  La marca vive en `~/ugc-realista/marcas/<marca>.md` (plantilla abajo). Cualquier estilo se combina con cualquier
  marca.
- **Todo texto en pantalla va en el montaje** (HyperFrames, Remotion o similar): subtítulos, cifras, siglas,
  neón, logo y fuente. El modelo de imagen o de video recibe siempre «no text, no letters, no numbers…».
- **Gasto:** cotización aprobada antes de generar, en cualquier estilo. Al cotizar, la resolución va explícita.
- **Medicamentos con fórmula:** el contenido es educativo. Lleva un llamado a consultar, nunca a comprar, y no
  usa imágenes que avergüencen el cuerpo. En Colombia, el Decreto 677 de 1995 (art. 79) prohíbe anunciarlos al
  público; Meta solo permite anuncios de esos medicamentos hacia EE. UU., Canadá y Nueva Zelanda.
- **Acciones físicas que deben verse exactas** (una balota que cae, un objeto que cambia de estado, un conteo): Wan no
  cuenta ni conserva cantidades en una toma larga (6 balotas en vez de 5; esferas que se vacían, 5-nov-2026). La toma
  larga pone la voz y los planos de la persona; cada evento se genera en un clip de 5 s desde una imagen fija del mismo
  set (`first_frame_url`, 80 cr a 720P, 6/6 a la primera) y se corta en el montaje para que ocurra 0,3 s antes de la
  palabra (`estilos/presentadora-tv.md`).
- **El render final se mira como espectador** antes de entregar, en cualquier estilo: los rótulos no tapan la acción y
  cada cosa dicha se ve en ese segundo (paso 9 de `SKILL.md`).
- **Comparaciones** («baja más que el placebo», «una columna sube y otra no»): se dibujan en el montaje. Wan no
  respetó la diferencia entre dos columnas en 2 de 2 intentos.
- **Voz generada por Wan:**
  - se transcribe y se compara con el guion palabra por palabra (`scripts/montaje/comparar.py`);
  - la cola después de la última palabra se mide aparte, porque Wan puede añadir algo;
  - Claude no oye, así que la persona juzga la voz.

## Plantilla de marca (`~/ugc-realista/marcas/<marca>.md`)
```
# Marca: <nombre>
- Logo: <ruta a los PNG> (versión vertical y horizontal; cuál va en el cierre)
- Colores: principal <hex>, acento <hex>, fondo para collage <hex>, tinta sobre fondo claro <hex>
- Tipografía: <familia y peso> (subtítulos y tarjetas)
- Cierre: <qué lleva: logo, llamado a la acción, «Contenido educativo», fuente>
- Voz: <género, acento, tono>; palabras con grafía fonética (por ejemplo «ge-ele-pe uno»)
- Personajes inventados de la marca: <rutas a las imágenes ancla y su prompt>
- Afirmaciones aprobadas: <dónde están y quién las aprueba>
- Reglas: <lo que la marca no permite>
```

## Agregar un estilo
Cuando un video en un formato nuevo se entrega y la persona lo aprueba, se escribe `estilos/<id>.md` con la misma
estructura que las demás fichas: qué es, firma, estructura de 30 s, producción con costos medidos, prompt base,
montaje, revisión, fallas conocidas y entregas de referencia. Después se agrega su renglón a la tabla de arriba.
Solo entra lo medido o lo que la persona aprobó; lo que no se probó se marca «sin probar».
