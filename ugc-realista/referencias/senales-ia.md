# Señales de IA por capa

Un video «parece IA» por señales concretas. Cada capa tiene cómo **prevenir** (prompt y referencias), cómo
**detectar** (medir o mirar) y cómo **corregir**. Medido en los videos del equipo (oct-2026): de 15 tomas
generadas salieron 6 utilizables, así que se presupuestan 2 tomas por plano y se elige.

## 1. Imagen
| Señal de IA | Prevenir | Detectar | Corregir |
|---|---|---|---|
| Luz de estudio, color «de cine», piel suavizada, simetría, encuadre perfecto, cámara que flota | Bloque PHONE LOOK (ver `prompts.md`): celular en mano, exposición automática, ventana algo quemada, ruido en sombras, sin gradación, poros visibles | Hoja de fotogramas | Repetir la toma; no «arreglar» con filtros |
| Look de banco de imágenes o de anuncio: fondo desenfocado, hora dorada, contraluz, persona de modelo, casa de revista (en documental y en UGC de Wan) | Ancla y prompt sin «cinema camera»; bloque REAL LIFE de `prompts.md` (sin probar) | Hoja de fotogramas: ¿el fondo está nítido como en un celular? ¿hay desorden de uso diario? | Rehacer el ancla con REAL LIFE y repetir |
| Lugar genérico o con defectos (carteles, luces rojas, texto) | Placa limpia del lugar como **última** imagen de referencia, generada aparte sin texto ni carteles | Hoja de fotogramas | Rehacer la placa y repetir |
| Gente del fondo con cara definida | «background people are tiny, distant and unidentifiable» o «no other people» | Hoja | Repetir |

## 2. Actuación
| Señal de IA | Prevenir | Detectar | Corregir |
|---|---|---|---|
| Habla lenta, con pausas, tiesa, quieta, «robot» | Bloques SPEECH y PERFORMANCE: empieza a hablar de inmediato, ritmo de conversación vivo, cabeza y cejas que se mueven, gestos espontáneos. **Nunca** escribir «despacio», «pausa», «calmly», «waits before speaking», «moves slowly» | `revisar_toma.py`: falla por debajo de 2,2 palabras/s y avisa entre 2,2 y 2,6 o por encima de 3,8 (la toma «robot» medida iba a 1,72; la aprobada a 2,64) | Acelerar la voz de referencia y repetir; al montar, recortar cada plano a su voz |
| Gestos no pedidos (mano al pecho, tocarse el pelo o la cara) | Una sola acción por plano en el guion; SCENE LOCK: «she never touches her chest, neck or face». No reforzarlo con más reglas de quietud: la v2 con un bloque de «acción única» salió tiesa | Hoja | Repetir |
| Boca que no coincide con el sonido (lipsync) | Nada probado. En una prueba corta `wan3_0` salió bien y `wan3_0_prime` mal (ver `proveedores.md`) | **Solo la persona**, mirando con sonido. `revisar_toma.py` no lo mide: su «diálogo» compara audio contra guion | Otra toma u otro modelo: Wan 3.0 con voz propia o Seedance 2.5 con voz de referencia (ambos salieron bien en la prueba). La pasada `kie_tarea.py lipsync` sobre un video ya hecho salió mal: no usarla por defecto |
| Al terminar de hablar la cámara se va a otro lado (techo del teatro, de 5,5 a 8 s en una toma de una avatar) | Nada probado; pedir encuadre fijo hasta el final es una hipótesis | Últimos 2 s de la hoja | Recortar la toma donde termina la voz |
| Pose de anuncio o físicamente ilógica: objeto pesado parado sobre la palma abierta, producto en alto hacia la cámara, brazo estirado sosteniendo peso, una postura que esa persona no haría a su edad (botella de 500 ml en la palma estirada de una señora de 76 años, 11-nov-2026) | Escribir el agarre real según peso, tamaño y edad («she holds the bottle by its neck, its base resting on her thigh»); lo pesado va apoyado (piernas, mesa); nunca «resting on her open palm» con algo que no se lleva así | Ancla y hoja con la pregunta «¿así lo haría esta persona en la vida real?»; no se mide, se mira antes de pagar la toma | Rehacer el ancla y la toma con el agarre real |
| Mirada fija sin parpadeo | «blinks naturally, glances away for a moment and comes back to the lens» | Hoja | Repetir |

## 3. Audio
| Señal de IA | Prevenir | Detectar | Corregir |
|---|---|---|---|
| Palabras mal pronunciadas (el modelo de video genera la voz desde el texto y en español falla: «auditoría»→«auditía») | Con Seedance: voz de referencia ya grabada o generada con TTS y aprobada por oído. Con Wan 3.0: su voz propia, verificando el texto con la transcripción (puede añadir palabras). Jerga técnica → que la persona grabe el guion | `revisar_toma.py`: diálogo ≥ 0,93 contra el guion; con duda, un segundo modelo de Whisper | Otra toma; reescribir la palabra (ver `voz.md`) |
| Voz más joven que el personaje: tono de mujer joven en una abuela, habla rápida de adulto joven (11-nov-2026: abuela de 76 a 219 Hz y 3,1 palabras/s; abuelo de 79 a 3,6 palabras/s, más rápido que la meta de una persona de 38) | Guion a ≈ 2,7 palabras/s con mayores de 70 (menos palabras, sin pedir lentitud); en SPEECH, rasgos de la edad: «an elderly voice: slightly hoarse and breathy, a faint tremble, softer volume», y en mujeres «lower-pitched than a young woman's» | `scripts/medir_voces.py` por hablante: tono mediano y palabras/s. Heurística sin norma exacta: una mujer de más de 70 por encima de ~200 Hz suena joven. Las fuentes coinciden en la dirección: con la edad el tono baja en mujeres y sube en hombres, y las sílabas duran 20–25 % más. Jitter y shimmer en habla corrida no son comparables con normas de vocal sostenida | Otra toma con menos palabras y SPEECH por edad, o Seedance con una voz de referencia de persona mayor que la persona aprobó oyendo |
| Voz de locutor, tono plano | Elegir la voz oyendo 3–4 muestras; «she is not a presenter, no announcer tone» | **La persona escucha.** Claude no oye: nunca afirmar que «suena natural» | Otra voz |
| Audio limpio «de estudio», siempre al mismo tono | Nada en el prompt probado | La persona escucha | Filtro de celular `scripts/fx_celular.sh` (ver `voz.md`) |
| Silencio digital, música sintetizada «de PowerPoint» | Ambiente de cuarto; música con licencia o ninguna | La persona escucha | Quitar la música |

## 4. Producto y texto
| Señal de IA | Prevenir | Detectar | Corregir |
|---|---|---|---|
| Etiqueta redibujada, letras inventadas o borrosas | PRODUCT LOCK con la descripción exacta + foto real del producto como **penúltima** referencia; el producto no gira ni se acerca mucho a cámara | Leer TODO texto visible en fotogramas a tamaño completo (también sobre el producto). Texto ilegible o inventado = defecto grave | Encuadrar el producto más lejos y repetir; o pegar la etiqueta real con seguimiento (trabajo avanzado: medir que no «nade») |
| Etiqueta en espejo | «the label always reads the right way round, never mirrored» | Hoja | Repetir |
| Producto que se abre, cambia de tamaño, aparece o desaparece | REALISM: mismo tamaño, forma, colores y partes en cada cuadro; tapa cerrada; no se abre ni se come salvo que el guion lo exija | Hoja | Repetir |
| Relieve o letras en la tapa | «the top of the cap is completely plain and smooth» | Recorte de la tapa | Repetir |
| Anillos, pulseras o reloj no pedidos (aparecen sobre todo cuando la mano rodea el producto) | Reglas fijas del personaje: «NO rings, no bracelets, no watch»; la palma hacia arriba reduce anillos solo con objetos chicos que de verdad se llevan así (frasco de gomitas); con uno pesado es pose de anuncio (capa 2) | **Recortes de manos a tamaño completo** en cada toma (no se mide solo) | Usar la otra toma o repetir |
| Joya permitida que aparece cortada o ausente al inicio y completa después (collar fino de una avatar con Wan 3.0 y Prime, 22-oct-2026) | Escribir «visible desde el primer fotograma» en el prompt **no lo arregló** (3 tomas). Lo más seguro: un canon sin esa joya | Fotograma 0 y primeros 0,5 s a tamaño completo (no se mide) | Recortar el inicio al montar, o `start_image` con el personaje entero y la joya visible (sin probar) |
| Producto que sale de cuadro por una indicación de actuación (pedir «levanta el frasco hacia la cámara»: con Wan 3.0 el frasco desapareció del encuadre desde los 5 s de 11) | Mantener el frasco quieto en la mano, a la altura del pecho y con la etiqueta hacia la cámara; dirigir los gestos solo de la cara y la cabeza | Hoja de fotogramas del recorte de la zona baja del encuadre (donde está el frasco), no solo de la cara | Repetir la toma sin esa indicación |
| Celular dibujado en cuadro | Describir «handheld front-camera point of view… the phone itself is never visible». No escribir «selfie mode» ni «phone propped on the table» si la otra mano hace algo | Hoja | Repetir |

## 5. Coherencia
| Señal de IA | Prevenir | Detectar | Corregir |
|---|---|---|---|
| La cara cambia entre planos | Mismas poses del kit en todos los planos + IDENTITY LOCK | `revisar_toma.py`: cara media ≥ 0,50 contra el kit | Repetir el plano |
| Ropa, peinado o lugar distintos entre planos | Ropa y peinado fijos en IDENTITY LOCK; misma placa en todos los planos | Hoja del video armado | Repetir el plano |
| Mezcla de estilos en un mismo video (una mano o un plano realista dentro de un video 3D) | Un solo estilo por video salvo pedido expreso; en 3D, referencia 3D en todo plano con manos, piel o pelo y «not photorealistic» | Hoja de fotogramas a ≥200 px y 2 por segundo, y el video a velocidad real | Rehacer el plano con la referencia 3D |
| Video que termina antes (la edición de Seedance pierde 0–0,3 s) | — | `ffprobe` de cada salida | Rellenar la cola con el último fotograma; no estirar (desfasa la voz) |
| Cortes con salto de color o luz | Misma placa y misma hora del día en todos los planos | Hoja del montaje | Repetir el plano |
| Movimiento «mágico»: un objeto aparece de la nada, atraviesa un vidrio, se reemplaza por otro o se mueve sin causa (balotas del sorteo, 5-nov-2026: «aparecen de la nada… antinaturales y mágicos»; «una cae y otra misteriosamente la reemplaza») | Placa con el camino físico del objeto (salida → copa) y un bloque PHYSICS en el prompt («the only way a ball leaves… never appears out of thin air… the cup starts empty and ends with exactly one ball»); la acción exacta en un clip de 5 s por evento desde una imagen fija (`estilos/presentadora-tv.md`) | Tira a 5–10 cuadros/s del tramo de acción, no la hoja de 2 | Clip por evento y corte en el montaje; con la voz en la toma, el audio no se toca |
| Las cantidades cambian durante la toma: 6 balotas en vez de 5, esferas que se vacían, un plato que vuelve a llenarse | No prometer conteos ni estados constantes en una toma larga (Wan no los conserva); un evento por clip | Comparar el primer y el último cuadro de cada escena en la hoja | Clips por evento, o documentar el defecto en el LEEME |
| Lo dicho no coincide con lo que se ve en ese segundo (el número cantado ~1 s antes de que cayera su balota, v3) | La acción antes de la palabra, con clips por evento | Tiempos de palabra (Whisper) cruzados con la tira de cuadros | Cortar al clip con la acción 0,3 s antes de la palabra (`data-media-start`) |
| Rótulos del montaje que tapan la acción (panel sobre las copas, ventana sobre las esferas, 5-nov) | Diseñar panel y ventanas fuera de la zona de acción y comprobarlos en un snapshot | Mirar el RENDER final a 2 cuadros/s como espectador | Mover el panel (0 cr) y volver a renderizar |
