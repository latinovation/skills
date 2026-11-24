# Transformar un video existente

La persona entrega un video y pide cambiar **la persona**, **el fondo** o **el producto** (se pueden combinar).
Se conservan guion, planos, gestos y ritmo del original. El método probado es la **edición de video con
referencias** (Seedance 2.5 en modo edición: el video de origen + las imágenes de lo nuevo). Regenerar el video
desde cero pierde los gestos, el encuadre y el ritmo del original: solo si la edición no sirve. (En kie a 720p
regenerar cuesta 63 créditos/s y editar 38 × (segundos subidos + generados) ≈ 76 por segundo de salida: no es
más barato editar, es más fiel.)

## Antes de gastar
1. **Analizar el original** (gratis): `ffprobe` (duración, resolución, fps, códec), cortes de escena, y la
   transcripción con tiempos (Whisper). Armar la lista de escenas: inicio, fin, quién aparece, qué se cambia.
2. **Avisar lo que NO cambia la edición:** el audio original y los subtítulos quemados se quedan. Si dicen la
   marca o el nombre viejo, el video no sirve tal cual (pasó: el resultado decía la marca anterior en audio y
   subtítulos). Decirlo antes y acordar qué hacer.
3. **La voz** (si cambia la persona), preguntar cuál de estas:
   - **Dejar el audio original:** los labios siguen cuadrando porque la edición conserva la boca del original.
     Si la voz es de una persona real, hace falta su autorización.
   - **Cambiar la voz conservando los tiempos** (cambiador de voz «voice-change»): los labios siguen cuadrando.
     En Higgsfield la ayuda de `voices` lo menciona pero no aparece en `model list --audio` (sin verificar).
   - **Voz nueva desde el guion** (TTS o grabación): los labios ya no cuadran; obliga a regenerar las escenas
     desde cero con la voz nueva como referencia, y se pierden los gestos del original.
4. **Lo que dice y muestra el original:**
   - Si la persona original se presenta con una credencial («soy doctora», «como nutricionista»), la cara nueva
     no puede heredarla salvo que sea cierta: esas frases se cortan o se reescriben.
   - La ropa: por defecto la edición conserva la del original; si debe ser la del kit, decirlo en el prompt y
     verificarlo en la prueba.
   - La foto real del producto solo hace falta si se cambia el producto o si la etiqueta se degrada.
5. **Escena de prueba:** cotizarla, transformar UNA escena representativa, mostrarla y esperar el visto bueno.
6. **Cotizar el resto** con la cifra real de la prueba y esperar el sí (ver `proveedores.md`).

## Partir en escenas
- Límite de la edición: 30 s por trabajo. Partir los planos continuos más largos en un corte natural.
- Las escenas cortas (1–3 s) del mismo tipo se pueden agrupar en un trabajo de ≤ 14,5 s (funcionó: la misma cara
  en 6 trabajos).
- Las escenas sin la persona (rótulos, archivo, producto solo) se dejan originales si solo cambia la persona.
- Un plano continuo partido en dos: cortar en una pausa natural del habla y revisar la cara a los dos lados del
  corte (`revisar_toma.py` en cada parte); si se nota el salto, tapar el corte con un plano de producto o rótulo.
- Normalizar la fuente a 720p H.264 antes de subir si viene en otro códec (AV1, 4K).

## Generar
- **Un trabajo a la vez.** En paralelo: error 429 (se pierde el trabajo) o 402 por saldo reservado.
- Mismas imágenes de referencia en todas las escenas (las poses del kit) para que la persona sea la misma.
- Prompt de edición: decir qué se reemplaza y qué se conserva. Ejemplo:
  `Replace only the woman in @Video1 with the woman of @Image1–@Image6. Keep exactly the framing, camera motion,
  gestures, lip movements, lighting, background and every object. No new text, logos or captions.`
  Para el fondo: `Keep the person, her movements, lips and the product exactly as in @Video1; replace only the
  background with the place of the last reference image.` (Cambio de fondo: sin medir todavía en el equipo;
  por eso la escena de prueba es obligatoria.)

## Después de cada escena
- **La salida pierde 0–0,3 s**, a veces dentro de la escena. Separar el resultado por los cortes REALES de la
  salida (pico de diferencia entre fotogramas en una ventana de −0,7/+0,3 s alrededor del corte esperado), no por
  las posiciones de entrada; rellenar la cola con el último fotograma para mantener la sincronía con el audio.
- La salida puede llegar **sin audio** (pasó en kie a 480p): volver a poner la pista original o la nueva.
- Cambio de producto a 480p: la etiqueta no se lee → 720p o pegar la etiqueta real.
- Revisar cada escena con `revisar_toma.py toma` (cara contra el kit) + hoja + recortes de manos.

## Filtros del servicio
El filtro juzga el **parecido del resultado**: si se parece a un personaje con derechos, falla (sin cobro en kie).
Traducir ese error a un mensaje claro para la persona; no intentar esquivarlo.
