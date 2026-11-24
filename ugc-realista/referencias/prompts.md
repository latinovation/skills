# Prompts que funcionan (modelos de video con referencias: Seedance 2.5 y similares)

Los prompts van en inglés aunque el diálogo sea en español: así se hicieron todos los videos medidos (no se probó
con el prompt en español).
El diálogo va entre comillas y en el idioma del video.

## Estructura del video y de cada plano

Número de planos ≈ duración ÷ 7 s (planos de 4–8 s). Esquema que funciona para UGC: gancho a cámara → producto
→ uso o detalle → cierre con llamado a la acción. Palabras por plano ≈ 3,3 × segundos.

```
<PLANO: quién, dónde, qué hace (UNA acción), qué dice>  +  <BLOQUES FIJOS, pegados después, iguales en todos los planos>
```
El texto del plano y los bloques pueden repetir una regla (p. ej. «sin anillos»): no estorba. En un plano donde el
producto **no aparece**, quitar PRODUCT LOCK y escribir en el plano «no product appears in this shot».

Orden de las imágenes de referencia (importa: los bloques se refieren a ellas por posición):
1. Poses del personaje (las del kit, siempre las mismas).
2. Foto real del producto, recortada y sin texto añadido → **penúltima**.
3. Placa limpia del lugar → **última**.

Audio de referencia: la línea de voz de ESE plano (ver `voz.md`).

## Plano: ejemplo real aprobado

```
The woman from the character reference images sits at the wooden dining table of the last reference image.
The shot is her own handheld front-camera point of view: she holds the phone at arm's length with one hand,
out of frame, so the phone itself is never visible; we only see her and her other hand. With her free hand,
which has no rings, she brings the closed product jar toward the camera with the front label facing the lens and
holds it there, fairly steady, while she keeps talking from behind it. She does not rotate the jar and the label
stays exactly as in the product reference image. She says: "Pero eso no es lo único que miraría.
Quiero saber qué contiene y cómo se usa." Vertical video.
```

## Bloques fijos (se pegan al final de todos los planos; adaptar lo que está entre <>)

**SPEECH:** (con mayores de 70, añadir la edad de la voz: «an elderly voice for her age: slightly hoarse and breathy, a faint tremble, softer volume, lower-pitched than a young woman's» y escribir menos palabras; ver `senales-ia.md`, capa 3) she speaks <Spanish with a soft, natural Colombian accent>, in the voice of the reference audio,
saying exactly the quoted words and nothing else. She starts talking right away and speaks fluidly at a lively,
normal conversational pace, like telling a friend about something on a video call: natural rhythm and
intonation, no long pauses, no slow or careful delivery, no announcer tone.

**PERFORMANCE:** she is relaxed, warm and animated, never stiff, frozen or posed: her head moves naturally while
she talks, her eyebrows and expression change with what she says, she blinks naturally, glances away for a moment
and comes back to the lens, shifts her shoulders slightly and makes small spontaneous gestures with her free hand.

**PHONE LOOK:** raw, unedited vertical smartphone video recorded on the phone's front camera and held in her hand,
the kind of clip a real person posts on Instagram or TikTok: natural handheld movement and small autofocus
breathing, slight wide-angle front-camera look, auto-exposure with the window slightly blown out, mild noise in
the shadows, no color grading, no cinematic lighting, soft overcast daylight from the window, slightly imperfect
framing; natural skin texture with visible pores and no beauty-filter smoothing, understated makeup.

**REAL LIFE** (sin probar; añadido el 30-oct-2026 porque la persona pidió más realismo): se pega después de PHONE LOOK,
y también en el ancla y en la placa. Con «filmed on a smartphone by someone nearby» en lugar de la cámara frontal,
sirve igual para `documental`.
an ordinary person, not a model: natural asymmetry in the face, slight shadows under the eyes, a few flyaway
hairs, uneven skin tone, everyday clothes with small creases. A lived-in home with ordinary everyday clutter
without any printed packaging (no books, no labeled jars, bottles or boxes), not a styled or magazine interior. Phone-camera optics: deep focus with the background mostly sharp, no shallow depth of
field and no bokeh; ordinary mixed indoor light, the face a little darker than the bright window; no color
grading, no golden hour, no rim light. The framing is a little off-center and drifts slightly with the hand.

**REALISM:** the product keeps exactly the same size, shape, colours, label and parts in every frame, and it does
not appear, vanish, open or change state unless described; never morph one object into another; she moves
naturally at a normal speed, with natural anatomy: five fingers per hand and a real grip.

**IDENTITY LOCK:** she is exactly the woman of the character reference images, <edad aparente, piel, ojos, cejas,
cara, pelo y peinado exactos, «never tied up» o lo que aplique>. Her only jewelry is <small gold hoop earrings>:
she wears NO rings, no bracelets, no watch <, no necklace> and no other jewelry, and her hands are bare with short
natural unpainted nails. Her outfit never changes: <prenda exacta>.

**PRODUCT LOCK:** the <product> is exactly the <marca> <product> of the product reference image (the
second-to-last image): <descripción física exacta: material, color, tapa, forma de la etiqueta, palabra visible>.
It fits comfortably in one hand (<tamaño real>); <agarre real según peso, tamaño y edad: «she holds it by the neck, its base resting on her lap»>, <the top of the cap is completely plain and smooth with no
embossed text>, the cap stays closed for the whole shot, and the label is never redrawn, rewritten or changed;
the word <marca> and all the label text always read the right way round, never mirrored or reversed.

**SCENE LOCK:** the room is exactly the <lugar> of the last reference image, with the same <objetos de la placa>;
no other people; no phone, camera or other device visible anywhere in the picture; she never touches her chest,
neck or face; no on-screen text, captions, subtitles, stickers, logos or readable text anywhere except the
<marca> label on the <product>.

## Qué NO escribir (cada uno produjo un defecto medido)
| Frase | Defecto que produjo |
|---|---|
| «waits before speaking», «small pauses», «calmly», «moves slowly» | Actriz lenta y quieta: «se ve muy robot» |
| «selfie mode» + acción con la otra mano | Aparece el iPhone en cuadro |
| «phone propped on the table» | El modelo dibuja el celular en primer plano |
| Pedir la etiqueta sin foto real del producto | Etiqueta ilegible o inventada |
| Nombrar personajes con derechos o pedir parecido a famosos | El filtro del servicio bloquea la salida (y no se debe hacer) |
| «resting its base on her open palm», «holds it up toward the camera» con un objeto grande o pesado | Pose de anuncio: una señora de 76 años con una botella de 500 ml parada sobre la palma estirada (11-nov-2026). Escribir el agarre real («she holds the bottle by its neck with one hand, its base resting on her thigh»); los anillos se evitan con IDENTITY LOCK |
| Escribir las palabras por sílabas («au-di-to-rí-a») para la pronunciación | Empeora: agrega sílabas basura |
| Prometer conteos o estados constantes en una toma larga («every sphere is completely full from the first frame to the last», «exactly one ball per machine») | Wan no los conserva: 6 balotas en vez de 5 y esferas que se vacían (sorteo, 5-nov-2026). La acción exacta va en clips de un evento desde una imagen fija (`estilos/presentadora-tv.md`) |
| «shot on a cinema camera», «documentary still» (ancla y Wan de `documental`, 25-oct) | Look de banco de imágenes: fondo desenfocado, color cálido de película, contraluz y hora dorada (visto en T4 y V2 el 30-oct) |

## Placa del lugar
Imagen generada aparte (modelo de imagen del servicio, 2k), del lugar vacío, sin texto, carteles, logos ni
personas, con la luz que tendrá el video. Si el lugar es real (una tienda, un teatro), usar fotos oficiales del
sitio como referencia de la placa y no usar fotos de terceros en publicidad sin permiso.
