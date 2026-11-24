# Estilo «Ilustración animada» (`ilustracion-animada`)

- **Muestra:** `~/ugc-realista/estilos/ilustracion-animada.jpg`.
- **Estado:** en uso desde el 16-nov-2026, en un explicativo de salud.
- **Origen:** un Reel de una marca de cosméticos usado como referencia, rehecho con guion, dibujos y metáforas
  propios.
- Lo que no se probó va marcado «sin probar».

## Qué es
Es un explicativo con **ilustración plana de cartel serigrafiado**, animada por capas como motion graphics, no como
video generado:
- una metáfora visual sostiene la explicación (las hormonas son llaves y las células, cerraduras);
- voz en off con subtítulos arriba y la palabra clave marcada;
- datos con fuente dibujados en el montaje;
- cierre de marca.

Sirve para **explicar un concepto de salud o ciencia con datos que se pueden defender**: mito y realidad, «qué es X»
o «qué dice la evidencia». Es lo más barato y lo más controlable de la skill.

- **Dentro del estilo cabe:**
  - fondos ilustrados a pantalla completa, piezas recortadas que entran, se mueven y rebotan;
  - rótulos de papel, trazos SVG (✕, ✓, garabatos, gráficas), tarjetas de datos;
  - cámara solo con motivo (atravesar una cerradura, acercarse a lo que se nombra).
- **No cabe:**
  - video generado por IA (Wan, Omni) sin pedido expreso;
  - letras dentro de las ilustraciones;
  - médicos inventados (en una marca médica, la médica no aparece en este estilo);
  - fundidos entre mundos.

## Firma (en números)
- **Imagen** (Nano Banana 2.1 vía `gemini-api image`):
  - 9:16;
  - fondos a 2K y piezas a 1K;
  - una imagen de estilo que luego entra como `-i` en todas las demás.
  - Bloque de estilo: «flat 2D vintage screen-printed poster look, fine grain texture, thick clean dark-ink outlines,
    flat shadows, soft light», la paleta de la marca en hex y «people are simple stylized silhouettes with no facial
    features… calm and friendly, never scary… no text, no letters, no numbers…».
- **Piezas:** sobre verde puro `#00FF00` y recortadas con `scripts/ilustracion/recortar_piezas.py`. Quedaron 0 píxeles
  verdes visibles en 14 de 14, y el vidrio queda transparente.
- **Voz:**
  - `gemini-3.8-flash-tts` con el estilo en `speech_metadata`, usando `scripts/ilustracion/tts_estilo.py`;
  - masculina si la marca lo exige;
  - ≈ 3,2 palabras/s con «ritmo ágil… pronuncia cada palabra completa».
- **Texto (todo en el montaje):**
  - subtítulos arriba (top 200 px), Montserrat 800 a 54 px, en caja de papel crema con borde de tinta 5 px y sombra
    plana 6 px; la palabra clave lleva marcador de color detrás;
  - máximo 47 caracteres, que caben en 2 líneas en 860 px;
  - rótulos de 32–48 px pegados a lo que nombran;
  - ningún texto debajo de 1330 px (interfaz de Instagram).
- **Sincronía:** cada pieza entra en la palabra que la nombra, con los tiempos de Whisper por palabra
  (`scripts/ilustracion/tiempos_voz.py` → `voz/palabras.json`).
- **Movimiento:**
  - caída con `back.out(1.6)` en 0,5 s;
  - rótulos de escala 0,85 a 1 con `expo.out` en 0,4 s;
  - trazos SVG con `strokeDashoffset`;
  - transiciones con causa: barrido, atravesar un objeto, iris desde un punto de la escena.
- **Duración:** 60–75 s. La referencia de 2:51 se recortó a 75 s.

## Estructura (75 s, 231 palabras, 9 tramos)
| s | Tramo | Qué se ve |
|---|---|---|
| 0–6 | Gancho | Pregunta en pantalla desde el cuadro 0, con los objetos del tema ya en escena |
| 6–25 | Metáfora | El mecanismo con la metáfora (llave, cerradura; imita, bloquea, enreda) |
| 25–44 | Lo que dice la ciencia | Definición oficial y lo que todavía no se sabe (asociación ≠ causa) |
| 44–64 | Vida diaria | Dónde aparece, qué hacer y una tarjeta con un dato del estudio |
| 64–71 | A quién le importa más | Las etapas sensibles, con su metáfora |
| 71–75 | Cierre | Logo, nombre, «Contenido educativo» y las fuentes |

## Producción (medido el 16-nov-2026, prepago de AI Studio)
| Paso | Qué | Costo |
|---|---|---|
| Fuentes | PubMed por E-utilities (WebFetch está bloqueado); una fuente por frase en `PLAN.md` | 0 |
| Imagen de estilo | NB2.1 a 2K | US$0,05 |
| 3 muestras de voz | TTS a 3 voces, la persona elige | ≈ US$0,02 |
| 7 fondos + 14 piezas | `scripts/ilustracion/generar_imagenes.py` (4 hilos, salta lo que ya existe) | US$0,82 |
| Revisión de letras | `gemini-api analyze` por imagen | ≈ US$0,03 |
| Voz completa | TTS, 2 tomas (la 1.ª se comía «pero» a 3,5 pal/s) | ≈ US$0,06 |
| Música | Lyria 3.5 instrumental, una pista | US$0,08 |
| **Total** | | **US$1,09** |

- **Condiciones de Google** (23-mar-2026): «Google won't claim ownership over that content». No prohíben el uso en
  redes. Lyria lleva SynthID.
- **Sin efectos de sonido:** el catálogo de HeyGen pide sesión (sin probar).

## Montaje (HyperFrames)
- **Generador:** las escenas se escriben con un generador de Python, no a mano. El ejemplo completo está en
  `scripts/montar.py` del proyecto de referencia (no viene en esta copia):
  - `Escena.pieza / rotulo / svg`;
  - `t(tramo, palabra, n)`;
  - subtítulos que se parten solos.
- **Render por tramos** con vigilante de disco (`render_tramos.sh`), o por piezas de 5 s si el disco está justo
  (`render_subtramos.sh`).
- **El audio va aparte:** se mezcla con ffmpeg (voz al 100 %, música al 0,14, salida de 2,5 s), se normaliza a
  −15 LUFS y se lleva a 48 kHz.
- **Las versiones con y sin música** salen del mismo video mudo.

## Revisión propia del estilo
- `npx hyperframes check --json` limpio y `snapshot --review`. Luego, cuadros sueltos en cada momento corregido.
- **Render final:**
  - hoja a 1 cuadro/s;
  - uniones de tramos ±2 cuadros;
  - la tarjeta de datos a tamaño real;
  - loudness y picos;
  - conteo de cuadros.
- **Un revisor independiente sin contexto**, con el diseño, el guion y los cuadros, pidiendo P0, P1 y P2 en una línea
  cada uno. En el piloto encontró 1 P0 y 23 mejoras que la revisión propia no vio.
- **Copia de la referencia:** n-gramas de 4 palabras contra la transcripción de la referencia. Debe dar cero.

## Fallas conocidas
| Falla | Qué hacer |
|---|---|
| `tts` lee en voz alta la indicación de estilo escrita dentro del texto | Estilo en `speech_metadata` con `agent run --body` (`tts_estilo.py`) |
| La voz se come palabras cortas a 3,5 pal/s («pero» → «por») | Pedir «sin apresurarse, pronuncia cada palabra completa» (3,17 pal/s) y comparar con Whisper |
| `gemini-api image` no acepta `-f` ni PNG | Prompt por `--stdin`; JPEG y recorte propio a PNG |
| Rótulos centrados con `margin-left` en un flex centrado se corren la mitad y se tapan | Contenedor con `left: cx` y `translateX(-50%)`, sin animarlo; el rótulo de adentro es el que anima GSAP |
| Anclar a una palabra común («En») toma la primera aparición y la pieza llega antes | Anclar a una palabra única del tramo o pasar `n` |
| Un dato de la tarjeta queda tapado por su barra al escalarla | El valor por encima (z-index) y moverlo con la barra; mirar la tarjeta a tamaño real |
| La escena entrante con fondo opaco deja una franja lisa en el barrido | `#root` de cada escena con fondo transparente |
| Subtítulos de más de 47 caracteres pasan a 3 líneas | Partirlos por la mitad sin dejar al final una palabra funcional |
| Todos los proyectos pospago de AI Studio dan 402 «prepayment credits are depleted» | La persona recarga prepago; no cuesta nada intentar antes |
| El disco interno se llena con la swap durante el render | Tramos de 15 s o piezas de 5 s con vigilante; temporales en el disco externo |
| Escribir sin darse cuenta una frase de la referencia | Chequeo de n-gramas antes de grabar la voz |

## Marca y legalidad
- La marca sale de `~/ugc-realista/marcas/<marca>.md`. En una marca médica, por ejemplo: voz masculina, cierre con su logo, fuentes y
  «Contenido educativo», y el médico de la marca aprueba el texto.
- No se calca la referencia: el formato es libre, pero el guion, las metáforas y los dibujos de otra marca no.
- Si nombra medicamentos con fórmula, rigen las reglas comunes (educativo, llamado a consultar).

## Entregas de referencia
Los videos y proyectos de referencia de este estilo están en la computadora de quien mantiene la skill; no vienen en esta copia pública.
