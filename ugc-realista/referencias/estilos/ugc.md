# Estilo «UGC realista» (`ugc`)

Muestra: `~/ugc-realista/estilos/ugc.jpg`. Estado: en uso; se aprobaron 2 pilotos de un producto de consumo. En un ensayo con Wan en kie (22-oct) salieron bien
la versión de Seedance con voz de referencia y la de Wan con voz propia.

## Qué es
Una persona (inventada o con autorización) le habla a la cámara frontal de su celular, en su casa, como en una
reseña o un «te cuento». Tiene que verse grabado por alguien real, no hecho con IA. Es el estilo original de esta
skill: **su proceso completo es el de `SKILL.md`**, y esta ficha solo resume la firma, los costos y las fallas.

- **Dentro del estilo cabe:** la persona, su casa y el producto real tal como es en la foto.
- **No cabe:** 3D, collage ni voz en off de un narrador.

## Firma (en números)
- **Cámara:** «handheld front-camera point of view… the phone itself is never visible». Cámara en mano con sus
  imperfecciones; luz natural de casa; piel real.
- **Habla:** fluida, a ~3–3,5 palabras por segundo, sin silencios internos largos.
  - Arranca a hablar de inmediato, con actuación viva (cabeza, cejas, gestos) y nunca tiesa.
  - «Calma», «pausas» o «despacio» la vuelven un robot.
- **Producto:** quieto, cerrado y con la etiqueta igual a la foto. Lo que no se lea bien se pega desde la foto real
  (con un script de proyecto, no incluido).
- **Rótulos:** cortos, en etiquetas blancas redondeadas («¿Otra compra guardada?», «Conoce <marca>»), hechos en el
  montaje.
- **Audio:** pasa por `scripts/fx_celular.sh` para que suene grabado con celular. Se entrega también la versión sin
  procesar.
- **Ritmo:** planos de 4–8 s, UNA acción por plano.
- **Más realismo** (sin probar; añadido el 30-oct-2026 porque la persona pidió más realismo):
  - el bloque REAL LIFE de `prompts.md` en el ancla, en la placa y en cada plano;
  - el producto sale solo en los planos que lo necesitan, no junto a la cara toda la toma;
  - un guion hablado, no de anuncio: frases cortas y una o dos muletillas reales («o sea», «bueno», «mira»), escritas
    en el texto para que la transcripción las compruebe.
  - La prueba del 30-oct salió bien (ancla REAL LIFE como primer cuadro de Wan 3.0, 720P).
- **El papel decide qué puede decir** (una ama de casa recitando porcentajes y datos de autoridad no convence):
  - una persona común cuenta una duda, una rutina o lo que siente; nunca recita cifras ni estudios;
  - las cifras van en tarjetas con su fuente, o las dice una autoridad real que lo autorizó (por ejemplo, la médica de
    la marca grabándose ella misma);
  - nunca se inventa un médico, una nutricionista o una enfermera para dar datos de salud: es una autoridad falsa.

## Producción
- **Personaje:** kit calibrado con `referencias/personaje.md`, con poses y parecido medido.
- **Voz y lipsync** (ver `SKILL.md` y `referencias/voz.md`):
  - **Wan 3.0 con voz propia** es lo predeterminado. Se verifica el texto transcribiendo y se repite la toma si
    añade o quita palabras.
  - **Seedance 2.5 con voz de referencia** elegida por la persona, cuando el guion tiene que ser exacto.
  - Nunca una voz ajena dentro de Wan: la sincronía falló con `wan3_0_prime`.
- **Costos medidos:**
  - Wan 3.0 en kie a 720P: 176 cr por toma de 11 s (16 cr/s).
  - Seedance 2.5 en kie a 480P: 308 cr por 11 s.
  - Un UGC en Higgsfield con Seedance: unos 777 créditos de Higgsfield por 30,8 s (no se conoce el precio en
    dólares del plan).
  - Se presupuestan 2 tomas por plano: con Seedance salieron utilizables 6 de 15.

## Prompt base
Los bloques fijos y un plano aprobado de ejemplo están en `referencias/prompts.md`. El lugar se fija con una «placa»
(`prompts.md`) y el personaje con su kit.

## Montaje
Cada plano se corta a su voz y se rellena la cola con el último cuadro. Después van los rótulos aparte, el audio de
celular y la transcripción del MP4 final, como dicen los pasos 8 y 9 de `SKILL.md`. Ese video se montó en Remotion.

## Revisión propia del estilo
La de `SKILL.md`: `revisar_toma.py` (cara, diálogo y texto) y la lista visual (manos, producto, sin celular, inicio
y final). La persona juzga el lipsync con el sonido puesto, porque el script no lo mide.

## Fallas conocidas
| Falla | Qué hacer |
|---|---|
| Aparece un iPhone si el prompt dice «selfie mode» o «phone propped» | «the phone itself is never visible» |
| Etiqueta en espejo, frasco destapado, relieve con letras en la tapa | Revisar cuadro a cuadro; tapa lisa; pegar la etiqueta real |
| Anillos cuando la mano rodea el frasco (5 tomas) | IDENTITY LOCK sin joyas y revisar las manos. La palma hacia arriba solo con un objeto chico que se lleva así; con algo pesado es pose de anuncio (fila siguiente) |
| Pose de anuncio: botella de 500 ml parada sobre la palma estirada de una señora de 76 años | El agarre que haría esa persona: del cuello con la base apoyada en las piernas, o la botella en la mesa a su lado. Preguntar «¿así lo haría en la vida real?» al mirar el ancla, antes de pagar la toma |
| «Levanta el frasco hacia la cámara» lo sacó de cuadro | El producto no se mueve |
| La marca suena mal (un nombre en inglés leído como se escribe) | Grafía fonética en la voz y comprobar con la transcripción |
| La pasada de lipsync (`volcengine`) quedó «malita» | No usarla como arreglo; cambiar de enfoque |
| Look de anuncio (Wan, 22-oct, visto el 30-oct): la cara queda en el mismo punto del cuadro toda la toma, la luz de la cara es pareja aunque la ventana está detrás, la casa parece de revista y el frasco va junto a la cara los 11 s | «Más realismo» de la firma (sin probar) |

## Entregas de referencia
Los videos y proyectos de referencia de este estilo están en la computadora de quien mantiene la skill; no vienen en esta copia pública.
