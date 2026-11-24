# Estilo «3D animado de personaje» (`3d-personaje`)

Muestra: `~/ugc-realista/estilos/3d-personaje.jpg`. Estado: en uso; se entregó en varios videos musicales (uno, en una segunda versión que corrigió 2 defectos).

## Qué es
Personajes propios con look de película animada: piel suave, ojos grandes y expresivos, formas redondeadas y luz
cálida de cine. Viven una historia en escenas cortas, a menudo sobre una canción. No hay lipsync ni diálogo; la voz
es la canción o un narrador. Estos videos 3D no necesitan el realismo de los otros estilos.

- **Dentro del estilo cabe:** personajes, lugares y objetos 3D estilizados, y el producto en 3D.
- **No cabe:** ninguna parte fotorrealista. Un plano macro sin referencia 3D salió con una mano y pelo reales.

## Firma (en números)
- **Bloque de estilo:** «Stylized 3D animated feature-film look, warm cinematic lighting, rich saturated colors,
  smooth expressive character animation, shallow depth of field». No se nombra a Pixar ni a Disney.
- **Personajes:** un kit 3D por personaje, con un color propio cada uno (Lucía en verde azulado, Caro en coral) y
  la ropa siempre igual.
- **Ritmo:** planos de 4 s cortados al compás. A 120 BPM, la cuadrícula de 4 s cae en el pulso con un margen de
  0,05 s. En los coros se reutilizan planos.
- **Imagen final:** 720×1280. Los planos se generan a 480P y se reescalan.

## Estructura (sobre una canción)
- Un acto por parte de la canción (verso: el problema; coro: el cambio; puente; cierre), con un plano de 4 s por
  frase musical.
- Un video de ejemplo dura 2:31,5 con 29 planos únicos y 7 repetidos. Para redes conviene cortar a 45–60 s con los
  planos que ya existen.

## Producción
- **Kit:** Nano Banana 2 genera la referencia 3D de cada personaje y la placa de cada lugar (por ejemplo, el baño).
  - Cada plano con manos, piel o pelo lleva la referencia del personaje y «stylized 3D… not photorealistic».
  - Si el guion pide un estado distinto (pelo ralo), se hace una referencia con ese estado.
- **Video:** Wan 3.0 de referencia a video, planos mudos de 4 s (`audio` desactivado), uno a la vez.
  - **Comfy Cloud:** US$0,0715/s a 480P (28,6 ¢ por plano). 29 planos sin fallos, unos 95 s cada uno.
  - **Higgsfield, `wan3_0`:** 4 s cuestan 4 cr a 480P, 7 a 720P y 14 a 1080P.
  - **En kie:** la tarifa publicada es 8 cr/s a 480P (sin probar en este estilo).
  - **Otros modelos:** se compararon 5 con el mismo primer cuadro. Ninguno resultó claramente mejor y más barato
    que `wan3_0`.
- **Totales:** un video de 2:31, unos US$8,62 en Comfy; otro, 309,3 créditos de Higgsfield.

## Prompt base
El ejemplo completo está en `shots.json` del proyecto de Comfy. Cada plano se arma así: bloque común + presentación
del personaje + plano + sufijo.
- **Presentación:** «@{L} shows Lucía, the main character; keep her face, dark wavy hair, teal knit cardigan, white
  t-shirt and gold hoop earrings exactly as in the reference.».
- **Plano:** UNA acción con encuadre y movimiento de cámara («Side tracking shot», «Slow push-in»).
- **Sufijo:** «Vertical video, no on-screen text, no dialogue.».

## Montaje
Los planos se cortan sobre la cuadrícula del compás (`armar.py` del proyecto). Para subtítulos hace falta la letra
exacta: la transcripción de Whisper sobre el canto no sirve, porque sus tiempos se desplazan hasta unos 13 s y
después de unos 2 minutos alucina.

## Revisión propia del estilo
- **Hoja de cuadros** a ≥200 px de ancho por cuadro: que nada se vea fotorrealista (manos, pelo, piel).
- **Continuidad:** la ropa y los accesorios de cada personaje iguales en todos los planos.
- **Producto:** cerrado, sin abrirlo.
- **Letra:** las afirmaciones que dice la canción tienen que estar aprobadas como cualquier guion.
- **Procedimiento médico** (una inyección, por ejemplo): revisar el ángulo y el sitio en el cuadro fijo **antes** de
  animarlo, y que el médico de la marca apruebe la técnica que se muestra.

## Procedimiento médico en cuadro (inyección subcutánea)
Probado en un video musical 3D (23-nov-2026). De frente, Nano Banana dibujó la pluma acostada sobre la piel y
pegada al ombligo en 3 de 3 cuadros, y esa técnica es incorrecta. De perfil salió bien en 3 de 3.
- **Encuadre de perfil:** el personaje mira hacia un borde del cuadro y el ángulo recto se ve completo. En el prompt:
  «The pen is horizontal and sticks straight out from her belly at a right angle (90 degrees) to the skin, its tip
  pressed flat against the skin, like a short horizontal stick pointing out of her belly…; it is not lying along the
  skin and not tilted». El sitio es el abdomen, «a hand-width to the side of her navel, above the waistband».
- **Objeto genérico:** una imagen del kit del objeto solo (pluma blanca y turquesa, «no text, no numbers, no dose
  markings, no label, no logo, no brand»). Nada de marcas: la de Ozempic o Mounjaro sería publicidad de marca.
- **Cuadro fijo y después animación:** Nano Banana arma la escena con las referencias del personaje, el lugar y el
  objeto, y Wan la anima con `--start-image`, que no admite referencias. El prompt pide UN movimiento mínimo: «keeps
  the pen pressed… holds it perfectly still… does not move, change shape or change angle». En 3 de 3 planos la pluma
  conservó el ángulo.
- **Corte educativo de la piel:**
  - un bloque 3D tipo pastel en capas (piel, grasa y músculo), con la aguja que termina en la grasa;
  - Wan lo anima con «locked-off static camera» y el medicamento turquesa se reparte solo en la capa de grasa;
  - los rótulos de las capas se ponen en el montaje: se miden sus alturas en el primer cuadro reescalado a 1080×1920
    y se colocan sobre el borde del bloque.
- **Rótulo fijo de toda la secuencia:** «Aplicación subcutánea · bajo la piel · con acompañamiento médico».
- **Qué no se muestra:** cómo cargar la dosis, el número de clics ni la frecuencia, porque son instrucciones de
  tratamiento.

## Fallas conocidas
| Falla | Qué hacer |
|---|---|
| Un plano macro sin referencia 3D salió con mano y pelo reales | Referencia 3D del personaje y «stylized 3D… not photorealistic» en todo plano con manos, piel o pelo |
| Al abrir el frasco, la tapa desaparecía | El producto queda cerrado sobre el mueble |
| El antes y después no se notaba: la referencia tenía el pelo lleno | Hacer una referencia con el estado «antes» |
| Los macros sin personaje salieron como CGI semirrealista | No se objetó; si importa, dar una referencia de estilo |
| Whisper confunde el nombre de la marca con otras palabras | Letra exacta desde la fuente, no desde la transcripción |
| La pluma de inyección dibujada de frente salió acostada sobre la piel y pegada al ombligo (3 de 3) | Plano de perfil, desde un cuadro fijo, más `--start-image` (sección «Procedimiento médico en cuadro») |

## Entregas de referencia
Los videos y proyectos de referencia de este estilo están en la computadora de quien mantiene la skill; no vienen en esta copia pública.
