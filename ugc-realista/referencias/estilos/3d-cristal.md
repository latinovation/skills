# Estilo «3D médico de cristal» (`3d-cristal`)

Muestra: `~/ugc-realista/estilos/3d-cristal.jpg`. Estado: en uso; se entregó en dos series de explicativos de salud.

## Qué es
Animación médica 3D estilizada, no fotorrealista:
- un cuerpo humano translúcido como de vidrio, tipo radiografía, con el esqueleto blanco apenas visible;
- órganos como volúmenes que brillan;
- moléculas de luz, fondo azul noche con neblina.

Lo acompañan una voz en off documental y tarjetas con cifras. Sirve para explicar mecanismos (receptores, cerebro,
estómago, tejido graso) y resultados de estudios.

- **Dentro del estilo cabe:** el cuerpo de cristal, macros de células y moléculas, y gráficos de cristal (columnas,
  línea de tiempo, figuras pequeñas) en la misma paleta.
- **No cabe:** personas reales ni manos reales (ver la regla 3D de `SKILL.md`).

## Firma (en números)
- **Paleta:** fondo azul noche; brillos verde azulado y ámbar (coral como tercer color). Las tarjetas usan los
  colores de la marca.
- **Ritmo:** 5 escenas en 30 s, una cada 5–7 s, con cortes limpios que hace Wan. La cámara se mueve lento dentro
  de cada escena.
- **Título:** los primeros ≤2,6 s, una píldora con el tema en mayúsculas (30 px, letra 800) y un título blanco de
  88 px en y = 250.
- **Subtítulos:** grupos de hasta 5 palabras.
  - El grupo se corta en la puntuación o en pausas de ≥0,15 s.
  - Montserrat 800 a 60 px, en una caja oscura (`rgba(6,12,28,.62)`, radio 22) en y = 1130.
  - Las siglas, las cifras y las palabras clave van en el color de acento.
- **Tarjetas de cifra:** caja oscura con la cifra a 150 px en el color de acento, el texto a 44 px y la
  comparación a 36 px. También hay variante de etiquetas de color («GLP-1», «GIP»).
- **Cierre:** 2,8 s con el logo en caja blanca, «Contenido educativo» y la fuente. Como la toma termina en 30 s, se
  congela el último cuadro 2,6 s para que quepa.

## Estructura de 30 s (≤75 palabras)
| s | Escena que funcionó |
|---|---|
| 0–5 | El cuerpo de cristal de pie; dos tipos de moléculas viajan por los vasos del torso |
| 5–11 | La cámara sube a la cabeza; el cerebro se ilumina en los dos colores |
| 11–18 | La cámara baja al estómago, que se ve lleno y en calma |
| 18–24 | Macro de células de grasa ámbar que se encogen soltando chispas |
| 24–30 | El cuerpo camina hacia la cámara |

**Variante de cifras:** una línea de tiempo de cristal, unas 100 figuritas de cristal de las que se encienden
algo más de la mitad, y una molécula que gira al cierre. Las comparaciones entre grupos se dibujan en el montaje
(ver «Fallas»).

## Producción
- **Imagen de estilo:** una por serie, con Nano Banana 2 (8 cr). Se pasa a Wan como `reference_image_urls`
  («Image1 defines the exact visual style…»). No se combina con `first_frame_url`.
- **Video:** una toma de Wan 3.0 de 30 s, 480P, 9:16, con `audio` activado. Cuesta 240 cr en kie y tardó 266–283 s.
  - La narración salió exacta en 4 de 4 tomas (texto ≤75 palabras, termina hacia 29,4 s).
  - 480P alcanza para el 3D (regla de `SKILL.md`).
- **Total por video:** 240 cr, más 8 cr de la imagen de estilo, una sola vez por serie.

## Prompt base
Imagen de estilo:
```
A translucent glass-like human body in x-ray style, the white skeleton faintly visible inside, organs rendered as soft
glowing volumes. Full-body figure standing in the center, three-quarter view, arms relaxed. Stylized 3D medical
animation still, not photorealistic. Deep midnight-blue background with subtle volumetric haze and soft rim light.
Glass-like translucent materials, soft inner glow. Color palette: teal, warm amber and coral red glows over navy.
Clean, elegant, high-end pharmaceutical explainer look, cinematic lighting, shallow depth of field. Vertical 9:16
composition with calm empty space in the upper third. No text, no letters, no numbers, no labels, no logos, no watermark.
```
Wan (plantilla: `prompts/wan/t1.txt` y `t3.txt` del proyecto de tirzepatida):
1. «Image1 defines the exact visual style: stylized 3D medical animation, not photorealistic, a translucent glass-like
   human body…».
2. «Keep this style in every scene. Vertical 9:16.».
3. `Scene 1 (0-5 s): …` hasta `Scene 5 (24-30 s): …`, cada escena con UNA acción visual.
4. «Audio: a single voiceover narrator, a warm and clear Latin American Spanish <female|male> voice, documentary
   tone, natural conversational pace; nobody on screen speaks. The narrator says exactly these words, word for word,
   nothing added and nothing removed: "<texto>" Under the voice: soft ambient electronic pads and subtle glassy
   whooshes on each transition, no music with vocals.».
5. «No text, no letters, no numbers, no labels, no logos, no subtitles, no watermark anywhere in the video.».

Las siglas se escriben como suenan («ge-ele-pe uno», «ge-i-pe») y Wan las dice como siglas.

## Montaje
`scripts/montaje/montar_explicativo.py` es el ejemplo de la serie de tirzepatida. Se copia a `<proyecto>/scripts/` y
se edita lo siguiente:
- `VIDEOS`: el título, y cada tarjeta con su frase de aparición (`ancla`) y de salida (`fin_ancla`);
- `ETIQUETA`, `FUENTE`, los colores y el logo de la marca;
- `corte_voz` e `ignorar_desde` si hace falta.

Antes se transcribe la toma con Whisper y se comprueba con `scripts/montaje/comparar.py <v>`. En 3D las tarjetas van
arriba (`tarjeta_abajo=False`).

## Revisión propia del estilo
- `comparar.py` contra el guion. Las cifras se normalizan: Whisper escribe «21 %» donde el guion dice «veintiuno
  por ciento».
- **Cola:** las palabras que Whisper pone después de la última del guion («Gracias por ver el video», «Adiós») se
  transcriben aparte y se mide su volumen con `volumedetect`. A −91 dB no suenan; si suenan más fuerte que la
  música sola, se corta la voz (`corte_voz`).
- **Hoja de cuadros:** que no haya manos ni piel fotorrealistas y que no aparezca ningún texto.

## Fallas conocidas
| Falla | Qué hacer |
|---|---|
| «Dos columnas: una baja mucho y la otra casi nada»: la de placebo también se hundió, en 2 de 2 intentos | La comparación va en una tarjeta o en barras dibujadas en el montaje; Wan solo hace el ambiente |
| «Triumph uno» sonó «Triunfuno» y Whisper escribe «tirsepatida» | Fusionar en los subtítulos (`palabras()` del script) y que la persona lo oiga |
| Whisper inventa frases sobre la cola o la música | Transcribir la cola aparte y medir el volumen antes de tocar el audio |
| La música puede tapar la voz | Lo juzga la persona al oírlo; en el prompt, «soft ambient pads… no music with vocals» |

## Entregas de referencia
Los videos y proyectos de referencia de este estilo están en la computadora de quien mantiene la skill; no vienen en esta copia pública.
