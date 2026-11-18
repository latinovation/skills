# Modo recorrido: referencia

## Archivos del proyecto

| Archivo | Se edita | Qué es |
|---|---|---|
| `proyecto.json` | sí | Nombre, URL local, idioma, voz, grabación, marca, capítulos (toma + escenas), intro, cierre, `pantalla` |
| `guion.json` | sí | `lineas: [{id, texto}]`: una por escena, más la intro y el cierre |
| `grabacion/tomas.mjs` | sí | `preparar()` (sesión, cookies) y una función por toma |
| `voz.py` | no | Kokoro → Whisper → `voz/<id>.wav`, `voz/<id>.palabras.json`, `voz/informe.json` |
| `grabacion/grabar.mjs` | no | Motor: Chrome por Playwright, captura CDP en JPEG, cursor y pulso de clic dibujados en la página |
| `grabacion/grabar-todo.sh`, `hoja.py` | no | Graba todas las tomas, una por proceso, y arma la hoja de control de cada toma |
| `video/montar.py` | no | Composición HyperFrames, `linea-de-tiempo.json` y `package.json` con la versión fijada |
| `video/realzar.py` | no | Realce opcional, después de `montar.py`: intro y cierre con motion, fondo de marca en las tarjetas, efectos y música bajo la voz |
| `video/assets/musica/fondo.*` | se pone | Música del realce (opcional). Licencia: `trampas.md` → Música |
| `render_tramos.sh`, `revisar.py` | no | Render por tramos y revisión del MP4 final |

## proyecto.json

- `url_base`: la app local, por ejemplo `http://127.0.0.1:3000`. Si la llave de un mapa solo vale en `localhost:3000`, usa esa URL.
- `idioma`: `es` o `en`. Lo usan Whisper, el `lang` del HTML y el paso de cifras a palabras (solo en español).
- `hyperframes`: versión fijada de la CLI, la que se probó.
  - Para subirla: cámbiala, corre `python3 montar.py` y `check`. Si `check` falla, vuelve a la anterior.
- `voz`:
  - `id`: `ef_dora` para español latino (también `em_alex`); para inglés, `af_heart`.
  - `fonemas`: `es-419` (con `es` sale el ceceo de España) o `en-us`.
  - `velocidades`: tomas por orden de prueba.
  - `similitud_minima`: 0,9.
- `grabacion`:
  - `ancho`/`alto`: 1600×900. El marco final es de 1728×972.
  - `entrada_s` (0,45) y `salida_s` (1,0): aire antes y después de la voz.
  - `angle`: `metal` (GPU, sirve para mapas deck.gl y WebGL) o `swiftshader` (maquetas 3D que con `metal` no dibujan).
  - `locale`, `zona` y `espera_ms`: el timeout de cada acción.
- `marca`:
  - `fondo`, `acento` (anillos, pulso del clic, capítulo) y `acento2` (degradado de las barras).
  - `fuente` + `archivo_fuente`: un woff2 en `video/assets/fonts/`. La plantilla trae Manrope.
  - `logo`: ruta dentro de `video/`, por ejemplo `assets/marca/logo.png`, horizontal. Con `null` se usa el nombre en texto.
- `capitulos`: `[{id, titulo, toma, escenas: [ids]}]`. Varios capítulos pueden salir de una misma toma.
- `intro` / `cierre`: `{voz: id o null, titulo, sub, extra_s}`.
- `pantalla`: pares `[voz, pantalla]`, por ejemplo `["veinte coma ocho por ciento", "20,8 %"]`. Así la voz dice la cifra en palabras y el subtítulo la muestra en dígitos.
  - Se reemplazan solo palabras completas, sin distinguir mayúsculas.
  - Pon primero los pares más largos («doce pedidos» antes que «doce»). Una cifra larga no debe llevar comas dentro: el subtítulo se parte en las comas.
- `realce` (solo lo lee `realzar.py`; todo es opcional):
  - `intro.logo`: logo blanco y horizontal, ruta dentro de `video/`. Sin él se usa `marca.logo`, y sin ese el nombre en texto.
  - `intro.bajada`: imagen bajo el logo (el descriptor de la marca). Sin ella va `intro.sub` en texto.
  - `intro.pilares`: `[["palabra que dice la voz", "texto del chip"], …]`, de 2 a 5. Cada chip entra cuando la voz de la intro dice esa palabra (por prefijo, sin tildes). Si la voz no la dice, `realzar.py` para y muestra lo que sí dice.
  - `intro.palabra_titulo`: palabra de la voz con la que entra `intro.titulo`. Con `null`, entra 0,6 s después del último pilar.
  - `cierre.logo`: el logo completo (con descriptor), blanco. El lema es `cierre.titulo` y la cápsula de abajo, `cierre.sub`.
  - `motivo`: `"hexagonos"` (campo de hexágonos en los tonos del acento) o `"ninguno"`. La cuadrícula animada va siempre.
  - `efectos`: `true` agrega un whoosh en cada tarjeta de capítulo, otro al cierre y un golpe suave en cada logo. Salen de la skill `media-use` (`~/.agents/skills/media-use/audio/assets/sfx`).
  - La música no se configura: si existe `video/assets/musica/fondo.*`, va a 0,42 y baja a 0,3 mientras habla la voz (sube a 0,85 en los huecos de más de 1,6 s).

## API de tomas.mjs

Cada toma recibe `h` (desestructúralo):

| Función | Para qué |
|---|---|
| `escena(id, async () => {…}, {minimo})` | Una línea del guion. La escena dura `entrada + voz + salida` (o `minimo` s si es más) |
| `aPalabra("x", n)` | Espera hasta que la voz dice «x» (la n-ésima vez). Usa `voz/<id>.palabras.json`; sin tildes ni mayúsculas, por prefijo |
| `a(f)` | Espera hasta la fracción `f` (0–1) de la voz de la escena (cuando la acción no corresponde a una palabra) |
| `intento(nombre, fn)` | Acción que puede fallar sin tumbar la escena; queda anotada en `grabar.log` |
| `señalar(loc)` / `clic(loc)` / `clicEn(x, y)` | Mueve el cursor con suavidad; el clic deja un pulso visible |
| `escribir(loc, texto, ms)` | Clic, borra y teclea letra por letra |
| `desplazar(px, ms)` / `aTexto(contenedor, texto, arriba)` | Desplaza la rueda / lleva un texto al borde de su panel |
| `foco(loc, {seg, zoom, anillo})` | Marca para el montaje: acercamiento suave y anillo que se dibuja. `zoom` se limita a lo que cabe |
| `ir(ruta)` / `listo()` | Navega y espera red quieta + fuentes |
| `page`, `ctx`, `BASE`, `dormir`, `log`, `caja`, `moverA` | Lo de Playwright, por si hace falta |

Patrones:
- `clic()` tarda ~1 s (mover + pulsar) y `escribir()` 50 ms por letra: arráncalos una o dos palabras ANTES de la que nombra la acción, para que el clic caiga sobre ella. Si la acción nombrada es la última palabra de la frase, la escena se estira: termina la frase con algo más.
- Para mostrar un login sin escribir la clave: `ctx.clearCookies()`, `ir("/entrar")`, una escena que solo señala los campos, y luego `ctx.addCookies([...])`.
- 3D o mapas: haz una pasada completa fuera de escena (precalentar), vuelve a la ruta y graba.
- El menú de un `<select>` nativo no sale en la captura. Usa `selectOption()` y que la voz diga la opción.
- Un elemento que puede no existir va en `intento()` con `señalar`. Fuera de `intento()`, un selector malo se come el timeout y alarga la escena.

## Montaje (lo que hace montar.py)

- Arma un MP4 de 30 fps por toma, con tiempos reales, y sostiene el último cuadro: una página quieta no emite cuadros.
- Cada escena es un `<video>` con `data-media-start`. Las cargas entre escenas quedan fuera.
- Cuadro de 1920×1080:
  - la grabación va enmarcada arriba (1728×972);
  - los subtítulos van en la franja de abajo (nunca sobre la app);
  - el chip del capítulo va arriba a la derecha durante 4,5 s.
- Subtítulos:
  - salen de los tiempos por palabra de la voz;
  - se cortan por frase y, si la frase es larga, en la coma central;
  - un trozo que no alcanza a leerse se une al siguiente.
- Focos:
  - la cámara entra en 0,7 s y sale en 0,6 s;
  - si el siguiente foco llega antes de 1,5 s, se encadena;
  - el zoom se limita a lo que cabe y a 1,4×: la grabación de 1600 px ya va a 1,08×, y más zoom ablanda el texto. Si sale por debajo de 1,08×, solo se dibuja el anillo;
  - si hay que leer letra chica, graba a 1920×1080 (`ancho`/`alto`) en vez de subir el zoom.
- Tarjeta de capítulo de 2,6 s, con el índice y el capítulo actual resaltado.
- Intro y cierre, con su voz.
- Con `realzar.py` (después de cada `montar.py`):
  - la intro y el cierre cambian por piezas de motion: cuadrícula que se desplaza, hexágonos que entran del centro hacia afuera, logo que se revela con brillo y anillo, y pilares sincronizados con la voz;
  - las tarjetas de capítulo toman el mismo fondo de cuadrícula;
  - se puede correr varias veces: quita sus pistas de sonido antes de volver a ponerlas.
