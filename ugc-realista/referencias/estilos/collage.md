# Estilo «Collage editorial» (`collage`)

Muestra: `~/ugc-realista/estilos/collage.jpg`. Estado: piloto; falta aprobar la voz.

## Qué es
Recortes de fotos en blanco y negro con trama de puntos y bordes de papel rasgado, sobre un solo color de fondo de
principio a fin. Lleva flechas y garabatos de tiza, neón y tramos 3D en la misma paleta. El subtítulo va de a una
palabra y el corte es rápido.

Viene de un anuncio de Instagram de una crema que vende directamente. El formato sirve; el guion de venta no. En
salud no lleva calaveras, cruces ni marcas sobre la piel, y no pide comprar.

- **Dentro del estilo cabe:** collage, objetos 3D tipo macro (moléculas, receptores, órganos de cristal) en los
  colores de la marca, y gráficos dibujados en el montaje.
- **No cabe:** planos de video real ni personajes 3D animados.

## Firma (en números)
- **Fondo:** un solo color oscuro de la marca (`fondo para collage`). El acento de la marca va en el neón y en las
  palabras destacadas.
- **Ritmo:** un plano cada 2–3,5 s. En 30 s salen unos 10 planos.
  - Algunos cortes llevan un destello blanco de 0,16 s al 70 %.
  - La imagen entra con un zoom de 1,07 a 1,00 en 0,3 s y después avanza lento de 1,00 a 1,04 hasta el corte.
- **Subtítulo:**
  - una palabra a la vez, en mayúsculas, Montserrat 800 a 74 px, centrado en y = 1390 de 1920, con sombra;
  - las siglas, las cifras y las palabras clave van en el color de acento;
  - sobre fondo claro (papel, una superficie del mismo color que el acento) lleva caja oscura con el color de
    tinta de la marca: sin ella, el contraste medido fue 1,2:1.
- **Efectos, todos dibujados en el montaje:**
  - signos «?» que se trazan solos;
  - el retrato cortado en 6 tiras desplazadas ±46 px;
  - ondas de neón;
  - etiquetas de neón con el color del objeto 3D que tienen debajo;
  - una píldora con el nombre del estudio;
  - barras de papel que crecen cuando la voz dice la cifra.

## Estructura de 30 s (piloto C1)
| s | Función | Qué se ve |
|---|---|---|
| 0–4 | Gancho en forma de pregunta | Retrato en collage de un personaje inventado; «?» y después tiras con ondas de señal |
| 4–6 | Cómo funciona el cuerpo | Grabado antiguo (cerebro y estómago) con flechas de tiza |
| 6–14 | Mecanismo | Tramos 3D de Wan (moléculas que se acoplan, cerebro de cristal) con etiquetas de neón |
| 14–16 | Consecuencia | Objeto en collage (un plato con los cubiertos juntos) |
| 16–26 | Dato | Multitud en collage con la píldora del estudio, y papel en blanco con barras que crecen |
| 26–29 | Cierre responsable | Manos de médico con fonendoscopio |
| 29–32 | Marca | Logo y llamado a consultar |

## Producción
- **Voz y 3D:** una toma de Wan 3.0 de 30 s con `audio` activado y 5 escenas 3D, sin imagen de referencia.
  - En kie a 720P cuesta 480 cr y tardó 786 s; a 480P cuesta 240 cr (no probado en este estilo).
  - Se eligió 720P para que el 3D no se viera borroso al lado del collage nítido.
- **Collage:** unas 6 imágenes de Nano Banana 2 a 1K y 9:16 (salen de 768×1376). Cuestan 8 cr cada una y tardan
  17–50 s.
  - El retrato lleva como `image_input` el ancla del personaje.
  - Una variación del mismo retrato (las tiras) se hace en el montaje, no con otra imagen.
- **Total del piloto:** 536 cr (480 de Wan y 56 de 7 imágenes, porque una se repitió).

## Prompt base
**Wan:** la plantilla es `prompts/wan/c1.txt` del piloto. Se pide así:
- Primero el bloque de estilo:
  > Stylized 3D medical macro animation, not photorealistic: glossy translucent glass forms, deep dark-teal
  > background with volumetric haze, glowing rose-pink and soft gold light accents, fine golden dust particles,
  > shallow depth of field, premium pharmaceutical explainer look.

  Se cambian los colores por los de la marca.
- Luego 5 escenas con su segundo, cada una en el momento en que la narración la nombra. Wan respetó los 5 cortes
  dentro de 0,05 s.
- Después el bloque de audio del método explicativo: «a single voiceover narrator… says exactly these words…», con
  máximo 75 palabras y las siglas escritas como suenan.
- Al final, «No text, no letters, no numbers…».

**Imágenes:** todas empiezan con el mismo bloque y terminan con el mismo cierre negativo.
```
Editorial mixed-media collage, vertical 9:16. Flat deep <color> background (<hex>) with subtle paper grain and a
faint darker vignette. Black-and-white halftone photo cutouts with slightly torn white paper edges and soft drop
shadows; hand-drawn white chalk lines. High contrast, graphic, magazine cut-out aesthetic. Keep the band between 68%
and 82% of the height free of important detail (captions go there). <SUJETO> Absolutely no text, no letters, no
numbers, no symbols, no question marks, no labels, no logos, no watermark anywhere.
```
Sujetos que funcionaron:
- retrato de hombros arriba del ancla («the woman from Image1»);
- grabado antiguo de un cerebro y un estómago «without any labels»;
- un plato visto desde arriba;
- unas 40 figuras pequeñas de adultos diversos, vestidos y vistos de lejos;
- una hoja de papel en blanco con cinta;
- manos de médico con un fonendoscopio, con «No papers, no documents, no notepad, no prescription, no pens».

## Montaje
`scripts/montaje/montar_collage.py` es el ejemplo del piloto. Se copia a `<proyecto>/scripts/` y se edita lo
siguiente:
- `VIDEOS`: cada `Plano` con su frase de inicio, tipo (`img`, `tiras` o `wan`), imagen o segundo de la toma, lo que
  va encima, si lleva destello y si lleva caja;
- `CORTE_VOZ`: el fin de la última palabra;
- los colores, el logo y la fuente de la marca.

Después:
1. Transcribir la toma con Whisper: `revision/<v>_t1/<v>_t1.json`.
2. `python montar_collage.py <v>`.
3. `npx hyperframes check`.
4. Capturas a mitad de cada plano.
5. `npx hyperframes render -q delivery`.

## Revisión propia del estilo
- **Imágenes:** cada una a tamaño completo, buscando cualquier carácter. Un recetario salió con «Rx» y renglones
  ilegibles pese al «no text»: se repitió sin papeles.
- **Subtítulos:** que cada palabra se lea sobre su fondo. Pasa la comprobación de contraste de HyperFrames y además
  se miran capturas de los tramos de Wan, que la comprobación no siempre muestrea.
- **Neón:** que cada etiqueta tenga el color del objeto 3D que está debajo.
- **Barras:** que cada rótulo aparezca con su barra, nunca antes.
- **Cola de la voz:** medirla (ver «Fallas»).

## Fallas conocidas
| Falla | Qué hacer |
|---|---|
| Wan añadió algo después de la última palabra: cola a −17,5 dB en la banda de voz, frente a −37 dB de una pausa con solo música | Cortar la voz en el fin de la última palabra (`CORTE_VOZ`) con un desvanecido de 0,2 s |
| `kie_tarea.py crear` va sin audio si no se pasa `--audio` | Simular primero sin `--si` y leer `"audio": true` en el cuerpo |
| Nano Banana dibuja letras en papeles, recetas y pantallas | No pedir papeles; si hace falta una hoja, que sea en blanco y para dibujar encima |
| Las etiquetas de neón quedaron con los colores al revés respecto a las moléculas | Ver la hoja de cuadros de la toma antes de fijar los colores |
| El rótulo de una barra aparecía antes que la barra | Meter el rótulo dentro del bloque que aparece con la cifra |

## Entregas de referencia
Los videos y proyectos de referencia de este estilo están en la computadora de quien mantiene la skill; no vienen en esta copia pública.
