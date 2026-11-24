# Estilo «Real documental» (`documental`)

Muestra: `~/ugc-realista/estilos/documental.jpg`. Estado: en uso; se entregó en dos series de explicativos de salud.

## Qué es
Video fotorrealista de personas inventadas en su vida diaria: cocina, comedor, consulta, parque. Nadie habla a
cámara: una voz en off explica y unas tarjetas dan las cifras. Parece rodado con cámara de cine en mano, con luz
natural y colores sin saturar.

A diferencia del UGC, nadie habla a la cámara y no hay lipsync. Por eso un solo personaje y una sola toma alcanzan.

- **Dentro del estilo cabe:** personas, lugares y objetos reales.
- **No cabe:** 3D, collage ni ilustración.

## Firma (en números)
- **Imagen (desde el 30-oct-2026, sin probar):** «raw, unedited vertical smartphone video filmed by someone
  standing nearby, natural handheld movement, small autofocus breathing, auto-exposure, mild noise in the shadows»
  + el bloque REAL LIFE de `prompts.md`. La persona pidió más realismo: la receta del 25-oct («shot on a cinema camera»)
  dio un look de banco de imágenes (fondo desenfocado, color cálido de película, contraluz, parque con
  niebla, laboratorio impecable). Esa receta solo se usa si la persona pide look de cine.
- **Ritmo:** 5 escenas en 30 s, una cada 5–7 s. La última es una salida optimista: caminar al aire libre con la luz
  real del día, sin hora dorada de postal.
- **Personaje:** uno por video, inventado, con la misma ropa en todas las escenas. Manos sin anillos, pulseras ni
  reloj.
- **Subtítulos, título y cierre:** iguales al estilo `3d-cristal` (mismo script).
- **Tarjetas:** se apoyan justo encima del subtítulo (`tarjeta_abajo=True`) para no tapar caras. En un plano donde
  la cara queda a media altura, esa tarjeta sube a la pared con `arriba=True` y tiempos fijos `inicio_t`/`fin_t` en
  el corte de escena.

## Estructura de 30 s (≤75 palabras)
| s | Función | Ejemplo que funcionó |
|---|---|---|
| 0–5 | Gancho visual | Plano cenital de un plato gigante; o una mano sobre el estómago, incómoda |
| 5–11 | El problema en la vida diaria | Termina el plato y vuelve el hambre; o toma agua despacio |
| 11–18 | El cambio | Aparta el plato a medio comer; o respira tranquila junto a la ventana |
| 18–24 | Detalle o consulta | Plano del plato; o una consulta con un médico inventado (no se oyen las voces) |
| 24–30 | Salida | Camina al aire libre, de frente |

## Producción
- **Personaje ancla:** Nano Banana 2 a 1K y 9:16 (8 cr).
  - Se sube a kie y entra a Wan como `reference_image_urls`: «Image1 is the main character: keep exactly
    <his|her> face, hair, build and <ropa> in every scene where <he|she> appears».
  - Con eso se mantuvieron la cara y la ropa en 4–5 escenas.
- **Video:** una toma de Wan 3.0 de 30 s, 480P, 9:16, con `audio` activado. Cuesta 240 cr en kie y tardó unos 270 s.
  La narración salió exacta.
- **Dos personas fijas** (un paciente y una persona real con autorización): las dos anclas van en
  `reference_image_urls`, «Image1 is the patient: keep exactly…» y «Image2 is the doctor: keep exactly…». Las dos se
  conservaron: la persona real midió de 0,60 a 0,65 de 3/4 contra sus fotos (1 de 1). Si la persona real no está
  autorizada a hablar: «she listens attentively with her lips closed», y la voz en off es de otro género. Con dos caras
  en cuadro, el parecido se mide recortando cada cara antes de `revisar_toma.py comparar`.
- **Persona real: el parecido depende de la referencia y del encuadre**:
  - las fotos de estudio retocadas se parecían menos a como la persona se ve hoy (0,63) que sus videos entre sí
    (0,81). Se arma el set de referencia con cuadros de sus videos, sin subtítulos ni letras, y el ancla sale de esos
    cuadros (0,71 frente a 0,61 con las fotos);
  - en un plano abierto, con la cara de ~75 px a 480P y casi de perfil, la toma midió 0,43–0,51 aun con la mejor
    ancla. Con un plano medio por encima del hombro del otro personaje y la cara de tres cuartos hacia la cámara, dio
    0,60–0,68 (1 de 1);
  - **color del pelo:** el modelo exagera los adjetivos. «Dark brown hair» dio el pelo casi negro: 0,25 de la
    luminosidad de la piel, contra 0,43–0,45 en la persona real. Se describe el tono medido («medium-brown hair with
    lighter warm caramel-brown strands… never black») y se compara el pelo como fracción de la luminosidad de la piel
    de la misma imagen, para descontar la luz. Se notó a ojo antes que con el script.
- **Total por video:** 240 cr, más 8 cr por cada personaje nuevo.

## Prompt base
Personaje ancla:
```
Medium shot portrait of a Latin American <woman|man> in <her|his> <edad>, <complexión>, <pelo>, wearing <ropa lisa de
un color>, no jewelry, standing in <lugar>, neutral relaxed expression, looking slightly off camera. Candid
smartphone photo taken by a friend, not a professional portrait: <bloque REAL LIFE de `prompts.md`>. Vertical 9:16
frame. No text, no logos, no labels, no watermark, no visible phone. Hands without rings, bracelets or watches.
```
El ancla fija el look de todo el video: con un ancla de cine, Wan dio planos de cine (25-oct).
Wan (plantilla: `prompts/wan/t2.txt` y `t4.txt` del proyecto de tirzepatida):
1. «Image1 is the main character…».
2. El bloque de imagen de la firma.
3. «Vertical 9:16. Hands without rings, bracelets or watches. The phone itself is never visible.».
4. `Scene 1 (0-5 s): …` hasta `Scene 5 (24-30 s): …`.
5. El bloque de audio del método explicativo (igual que en `3d-cristal`), cerrado con «Under the voice: quiet
   natural room tone and ambient sounds of each place, no music with vocals.».
6. «No text, no letters, no numbers…».

## Montaje
Usa `scripts/montaje/montar_explicativo.py` (ver `3d-cristal`), con `tarjeta_abajo=True`. Con personas, las tarjetas
tapan caras: se miden los cortes de la toma (`ffmpeg -vf "select='gt(scene,0.25)',showinfo"`) y cada tarjeta va
`abajo` (sobre el subtítulo), `bajo` (bajo el subtítulo, sobre el torso, cuando la cara queda al centro) o `arriba`
(en la pared, en consultas), con `inicio_t`/`fin_t` en el corte (serie 3, 30-oct).

Cada tarjeta se revisa contra la cara del plano en toda su ventana de tiempo, no solo al aparecer. En un video, una tarjeta
tapaba la cara a mitad de escena.

## Revisión propia del estilo
- **Caras y ropa:** el mismo personaje en todas sus escenas, mirando la hoja de cuadros.
- **Manos:** sin anillos ni reloj, y con cinco dedos.
- **Fondos:** ningún texto legible ni inventado (neveras, básculas, batas, jeringas, carteles).
- **Tarjetas:** ninguna tapa una cara en ningún momento de su ventana.

## Fallas conocidas
| Falla | Qué hacer |
|---|---|
| «Otro día, el plato a medio comer»: salió entero | Wan no respeta bien cantidades ni estados de un objeto. Contar el cambio con la acción (aparta el plato) y aceptarlo, o cotizar otra toma (240 cr) |
| Distorsión de gran angular en los planos cenitales | Pedir «top-down shot with a normal lens, no wide-angle distortion» (sin probar) |
| Letras ilegibles en la nevera, la báscula, la bata o la jeringa | Pedir «plain fridge door without magnets or papers», una pantalla fuera de foco, una bata sin bordados; si quedan, se dicen como defecto menor |
| Whisper oyó «la pérdida promedia» (posible concordancia de Wan) | Escribir el guion para evitarlo («perdieron en promedio») y que la persona lo oiga |
| Look de banco de imágenes: fondo desenfocado, color cálido, contraluz, niebla y hora dorada (se pidió más realismo) | Receta de celular + REAL LIFE (arriba); lugares comunes con cosas de uso diario; nada de laboratorios impecables con filas de frascos iguales (sin probar) |
| El personaje sale descalzo en la sala, la consulta y la calle (en 2 de 2 tomas: el ancla lo cortaba a media espinilla). La segunda toma pedía zapatos «except in his own bathroom, where he is barefoot» y siguió descalzo: la palabra «barefoot» se contagió | Ancla de cuerpo entero con zapatos visibles y calzado escrito en la línea del personaje, **sin nombrar nunca «barefoot»** (sin probar). Si ya salió: acercar el cuadro desde arriba en esas escenas (`acercar` de `montar_explicativo.py`, 12–15 %) |
| Un objeto se mueve solo: la puerta de un gabinete alto se abre y se cierra sin que nadie la toque (se vio en el video, no en la hoja de 1 cuadro/s) | Revisar el fondo a 4–5 cuadros/s en los planos largos. Arreglo probado: como es voz en off, se reemplaza solo la imagen del tramo con Wan desde el último cuadro limpio como `first_frame_url`, a la misma resolución (5 s a 720P = 80 cr). El empalme no se nota (sin corte detectado) y el audio original queda intacto |
| Un personaje secundario se cuela en otra escena: en una escena, quien pica verduras en la cocina lleva la bata y el estetoscopio de la médica de la escena siguiente, con tres manos y dos cuchillos | Mirar a tamaño completo las escenas de manos y objetos. Arreglo probado: reemplazar solo ese tramo con una toma corta con la imagen del personaje como `reference_image_urls`, una sola persona y una acción sin cuchillo (7 s a 480P = 56 cr); el audio original queda intacto y el empalme no agrega cortes. Prevención que funcionó (1/1): «alone» en cada escena de casa, «The doctor appears only in this scene» y bata lisa sin estetoscopio |
| Al comer, la persona saca la lengua medio segundo | Una acción por plano: «takes a small bite with his fork, chews with his lips closed and rests the fork on the plate» (limpio, 1/1). Mirar la boca a 4 cuadros/s con la cara recortada |
| Una pantalla de consultorio con «a blurred grey ultrasound image» salió nítida y con una ecografía que parece de embarazo, en la consulta de un paciente con hígado graso (1/1) | No pedir imágenes médicas en pantallas: «the monitor on the desk is turned off» o sin monitor (sin probar). Arreglo probado sin créditos: desenfocar la pantalla cuadro por cuadro siguiéndola (con un script de proyecto, no incluido: detector de rectángulo oscuro + cajas medidas a mano donde falla). Se lee como pantalla fuera de foco; una mano que pasa por delante también se desenfoca |
| Un frasco en la mano con «a plain white bottle with no label and no print» salió con etiqueta azul, letras y código de barras (1/1). El gotero de vidrio transparente «with no label and no print» salió limpio (1/1) | Envases de vidrio transparente, o que el envase no salga («rubs the lotion between her palms»; sin probar). Arreglo probado sin créditos: un script de proyecto (no incluido) que sigue la franja de color de la etiqueta y desenfoca la etiqueta entera con borde suave |
| Con «no computer, no monitor and no screen» igual salen un teclado o un portátil de lado, y un papel o una tablilla con renglones que parecen texto (2/2) | Teclado y portátil sin pantalla visible: defecto menor. El papel se desenfoca con un script de proyecto, no incluido (cajas en 2 cuadros clave, interpoladas, con borde suave; un recuadro duro se nota) |
| La voz rellenó con frases sin sentido («Un estudiantos en Plinyansidu…», 3 s, y otra al final) para que la última frase cayera en la consulta, puesta en 23–30 s cuando el resto del texto acababa en 22 s | Poner la escena de cierre donde cae la voz a ~2,5 palabras por segundo, no al final de los 30 s. Arreglo probado sin créditos: silenciar el tramo con `volume=0:enable=…` cortando en bordes a −80 dB de la banda de voz; queda una pausa |
| Un objeto pequeño que la persona manipula se transforma: el gotero de vidrio se volvió un frasco blanco de crema al abrirlo, y la crema del tubo cayó en la mesa en vez del antebrazo; se vio en el video | El envase queda quieto sobre una superficie y la acción se hace con las yemas («the dropper bottle stands still on the windowsill; she pats the serum into her cheek with her fingertips»; sin probar). Mirar las manos a 3–5 cuadros/s |
| Molde repetido en toda la serie: cuarto → caminata → cocina → consulta → caminata con un amigo (se vuelve repetitivo) | Máximo una caminata por serie y nunca ese cierre. Escenas de la vida en casa sin texto impreso: terraza con matas, tender o doblar ropa, arepas, tinto en el balcón, peinar a una nieta |
| Con REAL LIFE el desorden trae letras inventadas: lomos de libros, etiquetas de especias, jabón con código de barras (ancla de una prueba) | Pedir el desorden sin nada impreso: «everyday clutter without any printed packaging: no books, no labeled jars, bottles or boxes» (sin probar); revisar el fondo del ancla a tamaño completo antes de lanzar Wan |

## Entregas de referencia
Los videos y proyectos de referencia de este estilo están en la computadora de quien mantiene la skill; no vienen en esta copia pública.
