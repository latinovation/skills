# Modo historia: referencia

Plantilla genérica salida de dos videos reales de resultados de un asistente de chat (primer fin de semana y dos semanas,
nov-2026). Cada proyecto guarda su `REVIEW.md` de decisiones.

## historia.json

| Campo | Qué es |
|---|---|
| `nombre`, `idioma`, `hyperframes` | Nombre del asistente o la marca, idioma del HTML y versión fijada de la CLI |
| `texto_prohibido` | Cadenas que la marca prohíbe; `construir.py` se detiene si aparecen. Ej.: `["—", "Marca Mal Escrita"]` (la forma incorrecta del nombre de la marca) |
| `marca.fondo`, `oscuro`, `primario`, `suave`, `resalte`, `tinta` | Fondo, cabecera del chat y negritas, burbuja del cliente y botones, etiquetas, palabra resaltada, texto del asistente |
| `marca.fuentes` | `[{familia, archivo, peso}]` en `assets/fonts/`; `peso` admite rango variable `"200 800"` |
| `marca.familia_texto`, `familia_titulos` | Ej.: Barlow + Barlow Condensed (títulos en mayúsculas condensadas) |
| `marca.fondo_imagen` | Captura real del sitio donde vive el asistente (`assets/…png`); `null` = fondo liso |
| `marca.logo` | SVG/PNG real (el del kit de marca, nunca texto de reemplazo); `null` = nombre en texto |
| `asistente` | `nombre`, `saludo`, `placeholder`, `enviar`, `escribiendo`, `enlace`: textos reales de la interfaz del chat |
| `intro` | `ceja` (sitio · periodo), `titulo`, `sub`, `nota` («conversaciones reales, resumidas; contacto oculto»), `boton_h`/`boton_v` = dónde está el botón del chat en la captura (el cursor hace clic ahí), `titulo_px` opcional |
| `capitulos[]` | `id`, `ceja` (día · hora con zona · ciudad), `nombre` (de pila), `pregunta` (el primer mensaje, con comillas tipográficas), `pregunta_sub` (p. ej. «Sent with a photo»), `pasos` `[[etiqueta, texto, palabra_resaltada o null]]`, `resultado` `[etiqueta, texto]`, `mensajes` `[[rol, texto, extra]]` |
| `resumen` | `ceja`, `filas` `[[nombre, lugar · detalle, resultado]]`, `cierre` (con `**resalte**`): cifras copiadas de la consulta |
| `fin.lema` | Línea bajo el logo |

Mensajes: rol `u` (cliente), `a` (asistente, admite `**negrita**` como el widget real), `photo` (marcador, nunca la
imagen), `card` (tarjeta con enlace). `extra`: `{"step": i}` muestra el paso i del riel cuando llega ese mensaje,
`{"step2": j}` un segundo paso 0,9 s después, `{"result": true}` en el mensaje que cierra el caso (exactamente uno).

## Datos: consultas, crudos y cifras

- **Ejecutor de solo lectura:** un script pequeño (no viene en la skill) que corre la consulta y la guarda.
  - El de referencia usa la Management API de Supabase con `read_only: true`, acepta una sola sentencia `select`/`with`, escribe a archivo y no trunca.
  - Para otro cliente se copia y se cambian sus variables de entorno, con el token de la cuenta del cliente: el MCP de Supabase no ve los proyectos de los clientes.
- **Consultas:**
  - van en `sql/`, con fecha inicial y final explícitas en la zona del cliente;
  - `casos` y `mensajes` escriben a `private/`;
  - `excluidos` y `resumen` escriben a `sql/*.result.json`, que guardan solo agregados.
- **Transcripciones para elegir casos:** `transcripts.py` del mismo proyecto. Se adapta al esquema y escribe en `private/`.
- **`private/prohibidos.txt` (lo escribe un script, nunca a mano):**
  - por cada caso: los apellidos (el nombre sin su primera palabra), el correo completo y su parte local, y el teléfono (sus dígitos, los últimos 7 y los últimos 4);
  - en los mensajes del cliente: los ZIP o códigos postales y las palabras de direcciones o comunidades;
  - no metas las ciudades públicas que el video sí muestra.
- **Cifras:**
  - todo número de `intro.sub` y `resumen.cierre` debe estar en `sql/*.result.json`. Compruébalo con un script antes de construir;
  - una cifra que no está ahí no va en el video.

## Fondo, botón del chat y canal

- **`fondo_imagen`:** captura real del sitio donde vive el asistente, con Playwright.
  - Una a 1920×1080 para `h`. Para `v` sirve la misma: se recorta con `object-position: 100% 50%`.
  - Si el chat no está a la derecha, pasa una captura a 1080×1920.
- **`boton_h` / `boton_v`:** el centro del botón del chat, en píxeles del cuadro final (1920×1080 o 1080×1920), medido en esa captura.
  - Allí hace clic el cursor de la intro y desde allí se inunda el color.
  - Sin captura: `fondo_imagen: null`, y el botón por defecto queda en la esquina inferior derecha.
- **Si el canal no es un widget web** (WhatsApp, Instagram): el panel de la plantilla imita un chat web y mostraría algo falso.
  - Adapta el CSS de `.panel` y `.header` al canal real, o avísale al usuario antes de construir.

## Ritmo (construir.py)

- Pregunta gigante: 0,6 s + 0,3 s por palabra (tope 4,4 s), luego «cae» al chat.
- Cliente: 0,6 + 0,08 s/palabra (0,95–1,8 s). Asistente: indicador «escribiendo» 0,6 s + 0,8 + 0,055 s/palabra (1,35–2,9 s).
- Paso del riel: 0,3 s después de su mensaje; resultado: barrido 0,5 s después y 3,8 s quieto.
- Escenas cuadradas a cuadro entero (30 fps) para que las uniones de los tramos caigan en cuadro exacto.
- Sonidos: tic por mensaje del cliente, pop por resultado y por fila del resumen, whoosh al entrar cada escena; cada uno
  alineado por su pico (no por su inicio).

## Lo que aprendieron los primeros videos (aplicarlo sin que lo pidan)

- Mismo caso guía primero si el usuario lo pidió («pidió algo que no era y el asistente le mostró lo que sí»).
- Rayas largas del asistente → dos puntos o coma (si la marca lo pide); recortes con «…»; direcciones de tiendas también con «…».
- En 9:16 un resumen de muchas filas pide 2 líneas por fila; con 3 se encima el cierre: mirar el cuadro.
- El último paso del riel no puede llegar con el mensaje del resultado (en 9:16 el riel se oculta y ese paso dura 0,1 s):
  ponlo un mensaje antes.
- Título del periodo en pasado si el periodo ya pasó («last two weeks», no «next»).
- Sin música: no hay catálogo con licencia local; los sonidos se miden, no se oyen → decirlo en el LEEME.
