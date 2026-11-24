---
name: ugc-realista
description: Usar al crear o transformar videos con IA (Seedance, Wan, Higgsfield, kie, Comfy) en uno de sus estilos: UGC o de producto que debe verse real, explicativo documental, 3D médico de cristal, 3D animado de personaje, collage editorial, ilustración animada (explicativos con metáfora y datos) o presentadora de TV en un set (sorteos, resultados en vivo); desde prompt, producto, buyer persona, avatar, canción o un video existente.
---

# UGC realista

## Principio
Un video parece IA por señales concretas en cinco capas: imagen, actuación, audio, producto/texto y coherencia
(`referencias/senales-ia.md`). Cada una se **previene** en el prompt y las referencias, se **detecta** midiendo y
mirando, y se **corrige** antes de entregar. **No se gasta un crédito sin una cotización que la persona aprobó.**

## Entradas
| Llega | Qué hace la skill |
|---|---|
| Solo un prompt | Crea personaje, lugar y voz. Un producto de marca real nunca se inventa: sin foto real, no hay producto de marca en cuadro |
| Prompt + producto | La foto real del producto es la referencia fija; crea un personaje del nicho del producto |
| Prompt + producto + buyer persona | El personaje sale de la buyer persona |
| Kit o imágenes de un avatar o persona digital | Revisa y calibra el kit; no lo recrea |
| Video existente + cambiar persona, fondo o producto | Edición por escenas: `referencias/transformar.md` |

## Primera vez en esta computadora
1. Carpeta de trabajo: `~/ugc-realista/` con `cuaderno-ugc.md` (plantilla en `referencias/cuaderno.md`),
   `personajes/` y `proyectos/`.
2. Entorno para el control de calidad (una vez; ≈ 1,9 GB con el modelo de Whisper):
   - Mac/Linux: `python3 -m venv ~/ugc-realista/.venv && ~/ugc-realista/.venv/bin/pip install opencv-python-headless numpy faster-whisper`
   - Windows (terminal de Claude Code): `python -m venv ~/ugc-realista/.venv && ~/ugc-realista/.venv/Scripts/pip install opencv-python-headless numpy faster-whisper`;
     el Python es `~/ugc-realista/.venv/Scripts/python`.
   - Requiere `ffmpeg` y `ffprobe` en el PATH (Mac: `brew install ffmpeg`; Windows: `winget install ffmpeg`).
3. El servicio de la persona: `referencias/proveedores.md`. Las llaves las guarda ella en `~/ugc-realista/.env`;
   nunca se piden, se pegan, se leen ni se imprimen: se cargan al entorno del comando (ver `proveedores.md`).
   **Si la persona empieza con kie.ai (lo habitual en las primeras pruebas):** seguir «Empezar con kie.ai» de `proveedores.md`; el cliente `scripts/kie_tarea.py` no guarda llaves, cotiza antes de enviar y solo envía con `--si`.

## Proceso (en orden)
0. **Cuaderno:**
   - Leer y curar `~/ugc-realista/cuaderno-ugc.md` y aplicarlo sin anunciarlo (`referencias/cuaderno.md`).
   - Durante todo el proceso, **escribir en el cuaderno en el momento** en que se rechaza una toma por algo
     nuevo, la persona corrige algo, una receta funciona o el costo se desvía.
1. **Entender y preguntar:**
   - Primero mirar lo que trajo, que es gratis: las fotos, el producto y, si hay video, `ffprobe`, cortes y
     transcripción.
   - Después, en UN solo mensaje, preguntar solo lo que bloquea gastar:
     - qué servicio usa y el precio de su plan;
     - qué afirmaciones están aprobadas (obligatorio en salud, suplementos y cosméticos) y si hay testimonios
       aprobados por escrito;
     - si aparece la cara o la voz de una persona real, si hay autorización.
   - Duración, formato, idioma, acento, lugar y plataforma: si no los dijo, proponer un valor en una línea y
     seguir.
2. **Estilo, guion y plan** (`referencias/estilos.md`, `referencias/prompts.md`):
   - Primero el estilo: elegirlo con `referencias/estilos.md` (UGC, documental, 3D de cristal, 3D de
     personaje, collage, ilustración animada o presentadora de TV) y leer su ficha completa en `referencias/estilos/`. Donde la ficha difiera de estos pasos
     (que son los del estilo UGC: planos de 4–8 s, 2 tomas por plano, kit, audio de celular), manda la ficha. Si hay
     marca, leer su archivo (`~/ugc-realista/marcas/<marca>.md` o el que suba la persona).
   - Planos de 4–8 s, UNA acción por plano, palabras por plano ≈ 3,3 × segundos (mayores de 70: ≈ 2,7).
   - **Acción física lógica:** cada plano describe cómo lo haría esa persona real (edad, contextura, fuerza) con ese
     objeto (peso, tamaño): cómo lo agarra, dónde lo apoya, cómo se sienta, se levanta o gesticula. Nunca una pose de
     anuncio ni una que contradiga la física o la edad (ver «Pose lógica» en la lista visual).
   - Proyecto en `~/ugc-realista/proyectos/<AAAA-MM-DD>-<nombre>/` (`refs/ voz/ prompts/ tomas/ revision/
     final/ gasto.tsv LEEME.md`). `gasto.tsv` lleva una fila por trabajo pagado: fecha, servicio, id del
     trabajo, concepto, créditos, US$, etapa cotizada.
3. **Cotización de preparación** (si hay algo que generar):
   - Qué entra: el kit (crearlo o completar ángulos), la placa del lugar, las muestras de voz y las líneas de
     voz de cada plano (hasta 4 intentos por línea).
   - Cómo: créditos y dólares, más el saldo actual. Si la persona no sabe el precio de su plan, solo créditos, y
     decirlo.
   - Esperar un **sí** explícito: ese sí es el tope de esta etapa.
4. **Personaje, placa y voz:**
   - Personaje con `referencias/personaje.md`: crear o traer, hasta un kit calibrado.
   - Voz con `referencias/voz.md`: la persona elige oyendo.
   - Antes de mostrar el kit o la imagen inicial, mirarlos con la pregunta «¿así lo haría esta persona en la vida
     real?» (agarre, postura, peso, edad). Si no, se rehace antes de cotizar el video.
   - Mostrar el kit y esperar el visto bueno.
5. **Cotización del video:**
   - 2 tomas por plano. Al transformar, primero solo la escena de prueba y después el resto con la cifra real.
   - Esperar un **sí** explícito: ese sí es el tope.
   - Si el gasto se va a pasar del tope, parar y pedir un nuevo sí con la cifra adicional.
6. **Generar:**
   - Bloques fijos de `referencias/prompts.md`.
   - Voz de referencia a ~3,3 palabras/s.
   - Un trabajo a la vez y 2 tomas por plano.
   - Cada gasto se anota en `gasto.tsv`.
7. **Revisar cada toma:**
   - **Medir**, desde la carpeta del proyecto:
     `~/ugc-realista/.venv/bin/python <carpeta de esta skill>/scripts/revisar_toma.py toma tomas/<toma>.mp4 --poses <kit>/poses --texto "<línea exacta>" --criticas "<marca>,<producto>" --salida revision`
     - Una vez por kit, antes: `revisar_toma.py calibrar <kit>/poses`.
     - Deja `revision/<toma>.json` y `revision/<toma>_hoja.jpg` (un cuadro cada 0,5 s).
     - Resultado: **FALLA** se descarta; **INCOMPLETO** algo quedó sin medir y no se entrega como verificado;
       **REVISAR** alguna palabra no coincide con el guion, se confirma con otro modelo o la persona lo escucha;
       **PASA** todo medido dentro de umbral.
   - **Mirar:** la hoja y, donde aparezcan manos o producto, el cuadro a tamaño completo
     (`ffmpeg -ss <t> -i toma.mp4 -frames:v 1 cuadro_<t>.png`), con la **lista visual** de abajo.
   - **Lipsync:** el «diálogo» del script compara el audio con el guion; **no mide si la boca coincide con el
     sonido**. Nunca declarar bueno el lipsync: la persona mira la boca con el sonido puesto. Si la boca no sigue la voz, el arreglo no es una pasada de sincronía (salió mal): es cambiar de enfoque (Wan con voz propia o Seedance con voz de referencia; ver `senales-ia.md`). (Prueba de Wan,
     22-oct-2026: el control dio PASA en todas y la persona vio el lipsync fallido en las de `wan3_0_prime`.)
   - Se elige la toma que pasa las dos revisiones.
   - Si ninguna pasa: una toma más dentro del tope. Si tampoco, decirlo con el defecto concreto.
8. **Montar:**
   - Cortar cada plano a su voz y unir.
   - Rellenar con el último fotograma la cola que falte.
   - **Audio de celular:** procesar el audio del montaje final para que suene grabado con un celular
     (`referencias/voz.md`, `scripts/fx_celular.sh`); entregar también la versión sin procesar.
   - Los rótulos van aparte, nunca generados por el modelo.
   - Los rótulos nunca tapan la acción que el guion promete (copas, producto, caras): se diseñan fuera de esa zona y se
     comprueban en el render, no solo en el `check` (5-nov-2026).
   - Transcribir el audio del MP4 final y comprobar la duración con `ffprobe`.
9. **Entregar** en `final/`, con un `LEEME.md` que diga:
   - qué se hizo y el gasto real frente a lo cotizado;
   - **qué se midió y qué solo se miró**;
   - **el veredicto de coherencia**: antes de entregar, mirar el RENDER final completo como espectador (hoja a 2
     cuadros/s, y 5–10 cuadros/s donde hay acción) y escribir si se ve la acción que promete el guion, si cada cosa
     dicha se ve en pantalla en ese segundo y si algún rótulo tapa algo que importa; las métricas (texto, cara,
     `check`) no miden coherencia (5-nov-2026: un render con todo en verde tapaba la mecánica que se pedía);
   - qué debe escuchar y mirar la persona antes de publicar (voz, acento, audio de celular y lipsync);
   - que al publicar se marca como contenido hecho con IA si la plataforma lo pide.
10. **Curar el cuaderno** otra vez; marcar `[proponer]` lo que ya sirvió en 2 o más proyectos.

## Lista visual (cada toma, mirando la hoja y los cuadros a tamaño completo)
- **Manos:** sin anillos, pulseras ni reloj en ningún cuadro; cinco dedos; agarre real.
- **Pose lógica:** cada agarre y postura es el que haría una persona real de esa edad y contextura con ese objeto
  (peso, tamaño, fuerza, equilibrio). Nada de poses de anuncio: un objeto pesado parado sobre la palma abierta, el
  producto en alto hacia la cámara o el brazo estirado sosteniendo peso. Pregunta, en el ancla y en la toma: «¿así lo
  haría esta persona en la vida real?» (11-nov-2026: botella de 500 ml en la palma estirada de una señora de 76 años).
- **Producto:**
  - igual a la foto (forma, tamaño, colores), con la tapa cerrada;
  - la etiqueta no está en espejo y **todo texto visible se lee y existe en el producto real**;
  - la tapa es lisa.
- **Sin celular en cuadro**; sin gente con cara en el fondo; sin carteles, logos ni texto inventado.
- **Actuación:** hace solo la acción pedida; parpadea, mueve la cabeza, gesticula; no está tiesa.
- **Continuidad:** misma ropa, peinado y lugar que los otros planos.
- **Inicio y final:** el fotograma 0 y los primeros 0,5 s a tamaño completo (encuadre cortado, joyas permitidas
  ausentes o incompletas) y los últimos 2 s (la cámara sigue encuadrando a la persona, no se va al techo).

## No se negocia
- **Gastos:**
  - nada de créditos sin la cotización de su etapa aprobada;
  - si se va a pasar del tope, parar y pedir un nuevo sí;
  - una toma que dio error 503 o quedó «in_progress» se recupera antes de pagar otra;
  - una cuenta compartida mezcla gastos de otras sesiones: anotar en `gasto.tsv` por id de trabajo
    (`higgsfield account transactions --size 20`), no por diferencia de saldo;
  - una llave de API compartida con otras apps puede dejar sin saldo a mitad de una etapa (kie 402 «Credits
    insufficient», 5-nov-2026): `saldo` antes de cada etapa, scripts que reanudan sin repetir lo que ya existe, y
    avisar si falta saldo sin tarea propia.
- **Resolución explícita:**
  - nunca dejar la resolución al valor por defecto del servicio: en kie, Wan 3.0 usa 1080P si no se envía, 4 veces el
    costo de 480P;
  - en animación 3D, con Wan 3.0, 480P alcanza.
- **Voz:**
  - con Seedance, el modelo no inventa bien la voz desde el texto en español (cambia palabras): siempre va una voz de
    referencia elegida por la persona;
  - con Wan 3.0 NO usar una voz de referencia ajena (solo mueve la boca hacia ese audio y la sincronía falló en la
    prueba): dejar que Wan genere su propia voz, que salió bien (22-oct-2026), y **comprobar con la transcripción que
    el texto sea exacto, repitiendo la toma si añade o quita palabras**;
  - la marca se escribe con grafía fonética en la voz (una marca escrita en inglés va escrita como se pronuncia en español) y se comprueba con la transcripción;
  - Claude no oye: nunca afirma que la voz «suena bien».
  - **la voz tiene la edad del personaje:** con mayores de 70, el guion va a ≈ 2,7 palabras/s (menos palabras, nunca
    pedir lentitud) y la voz se describe por rasgos de la edad (algo ronca y aireada, con un leve temblor, menos
    volumen; en mujeres, tono más grave que el de una joven). Medir tono y velocidad por hablante con
    `scripts/medir_voces.py` (11-nov-2026: una abuela de 76 salió con tono de mujer joven, 219 Hz, y el abuelo a
    3,6 palabras/s, más rápido que la meta de una persona de 38); la persona confirma oyendo.
- **Prompts y producto:**
  - nunca escribir «iPhone», «selfie mode» con la otra mano ocupada, ni «phone propped»;
  - siempre «the phone itself is never visible»;
  - el producto no se abre, no gira, no se come y no cambia, salvo que el guion lo exija y se avise del riesgo;
  - nunca pedir pausas, lentitud ni calma.
- **Guion:**
  - solo afirmaciones aprobadas;
  - testimonios de experiencia del personaje («llevo dos semanas y…», resultados en el tiempo) solo si el cliente
    los aprobó **por escrito con el texto exacto**: guardar la aprobación en `refs/` (quién, fecha, frases) y
    citarla en el `LEEME.md` de la entrega;
  - sin esa aprobación, el personaje habla de impresiones del momento y de lo que se ve («mira esta textura»,
    «me encanta que sean gomitas»), sin prometer resultados;
  - nunca credenciales que el personaje no tiene («como doctora…»).
- **Un solo estilo por video:**
  - un video es todo real o todo 3D/animado, nunca una mezcla; cada ficha de `referencias/estilos/` dice qué cabe
    dentro (el collage, por ejemplo, incluye tramos 3D en su misma paleta);
  - solo se mezclan estilos (por ejemplo, un plano real dentro de un video 3D) si la persona lo pide
    **expresamente**: si no lo dijo, no se mezcla ni se propone;
  - en 3D, todo plano con manos, piel o pelo lleva la referencia 3D del personaje y «stylized 3D animated, not
    photorealistic»; sin referencia el modelo lo dibuja fotorrealista (una mano real en un video 3D, 22-oct-2026).
- **Medir, no opinar:** el parecido de la cara se mide con el script; lo que no se mide se mira a tamaño
  completo.
- **Personas reales y origen:**
  - nada de caras ni voces de figuras públicas, ni personajes con derechos;
  - cara o voz real solo con autorización, también la de la persona del video original si se conserva;
  - «que no parezca IA» es calidad, no ocultar el origen.
- **APIs:** antes de escribir código contra una API, leer su documentación vigente.

## Señales de alarma
| Pensamiento | Realidad |
|---|---|
| «Es solo una toma de prueba, la mando ya» | La prueba también cuesta: va en una cotización aprobada |
| «La voz del modelo de video bastará» | Con Seedance cambia palabras en español: voz de referencia. Con Wan 3.0 la voz propia salió bien, pero se verifica el texto con la transcripción |
| «Que hable con calma para que se vea natural» | Calma = robot. Ritmo de conversación |
| «Que gire el frasco para mostrarlo mejor» | Girar y acercar es donde el modelo redibuja la etiqueta |
| «Que lo muestre sobre la palma abierta para que no salgan anillos» | Es pose de anuncio: nadie sostiene así una botella. El agarre lo deciden el objeto y la persona; los anillos se evitan con IDENTITY LOCK y se revisan en las manos |
| «Un testimonio con tiempo de uso convence más» | Solo con aprobación escrita del cliente, con el texto exacto, guardada en el proyecto |
| «Se ve igual, no hace falta medir la cara» | El ojo se ha equivocado; el script decide |
| «Una toma por plano alcanza» | 6 de 15 tomas salieron utilizables. Presupuestar 2 |
| «Lanzo los planos en paralelo para ahorrar tiempo» | Error 429/402 y trabajos perdidos. Uno a la vez |
| «El script dio PASA, ya sirve» | PASA no mide lipsync, joyas, manos ni el inicio y el final: se miran |
| «El `check` pasó y el texto da 61/61: ya está listo» | Las métricas no miden coherencia: el render final se mira como espectador antes de entregar |
| «Wan lo hará en una toma: cinco balotas, una por máquina» | Wan no cuenta ni conserva cantidades en una toma larga: un clip de 5 s por evento desde una imagen fija (`first_frame_url`) y cortes en el montaje |
