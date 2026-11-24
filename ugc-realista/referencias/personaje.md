# Personaje: crear o traer, y el kit

Las dos maneras terminan en el mismo **kit de personaje**. Desde ahí, el proceso no distingue si el personaje
se creó o se trajo.

## Contenido del kit (`personajes/<nombre>/`)
| Archivo | Qué es |
|---|---|
| `poses/` | 8–12 imágenes de la MISMA cara: frente, 3/4 izquierda, 3/4 derecha, primer plano, sonrisa, hablando, risa, mano con la palma abierta, plano medio, cuerpo entero. Fondo neutro, misma ropa |
| `poses/calibracion.json` | Lo escribe `revisar_toma.py calibrar` |
| `ficha.md` | Canon: edad aparente, piel, ojos, cejas, pelo y peinado, joyas permitidas, manos, ropa, mercado al que habla, voz. Lo que NO puede cambiar entre planos |
| `locks.txt` | El bloque IDENTITY LOCK ya escrito para este personaje (ver `prompts.md`) |
| `voz.txt` | Servicio, nombre o id de la voz elegida y quién la aprobó oyendo |
| `origen.md` | Creado (con qué modelo y prompt) o traído (de quién) y la autorización si es una persona real |

## Crear (entradas: solo prompt · prompt + producto · prompt + producto + buyer persona)
Generar poses gasta créditos: va en la cotización de preparación, aprobada antes de empezar.
1. **Quién es.** Si hay buyer persona, el personaje sale de ahí. Si no, se deduce del producto y del mercado:
   edad, región y estilo de quien compra ese producto en ese país. El personaje tiene que ser del nicho («no una
   irlandesa para Boyacá»). Se le dice a la persona en una línea quién se propone y por qué.
2. **Pose maestra.** Una imagen de frente con el modelo de imagen del servicio de la persona. Piel con textura,
   sin maquillaje de estudio, ropa sencilla y sin logos, **sin anillos, pulseras ni reloj** (las joyas de manos
   aparecen luego en video sin que nadie las pida). Cada joya permitida es un defecto posible: el collar fino de
   una avatar salió cortado o ausente al inicio de varias tomas; si no hace falta, no darle collar. Va como foto de
   celular, no como retrato profesional: el bloque REAL LIFE de `prompts.md` (sin probar, 30-oct-2026). El ancla fija
   el look del video: con un ancla «de cine», Wan dio planos de cine en `documental` (25-oct).
3. **Resto de poses** usando la maestra como referencia, una por ángulo o gesto.
4. **Calibrar:** `revisar_toma.py calibrar personajes/<nombre>/poses`. Si marca poses atípicas, quitarlas o
   rehacerlas. Un perfil completo puede quedarse como referencia de generación, fuera de la carpeta que se mide.
5. **Mostrar el kit a la persona** (una hoja con las poses) y esperar su visto bueno antes de gastar en video.
6. **Voz** (ver `voz.md`): la persona elige oyendo.

## Traer (entrada: kit e imágenes de un avatar o persona digital)
1. Revisar que alcance: al menos 3 imágenes con la cara visible, nítidas, ángulos variados, misma ropa si se
   quiere continuidad.
2. Calibrar. Si las poses no son consistentes (media entre poses < 0,60 o atípicas), decirlo con las cifras
   antes de seguir: con un kit inconsistente la cara va a variar en el video.
3. Si faltan ángulos, generarlos con las imágenes traídas como referencia y medir que la cara no cambie
   (`revisar_toma.py comparar`).
4. Escribir `ficha.md` y `locks.txt` desde las imágenes; preguntar solo lo que no se ve (edad, voz, mercado).

## Personas reales
- Si la cara es de una persona real (alguien del equipo, un cliente, un creador contratado), pedir que se
  confirme que hay **autorización para usar su cara y su voz en publicidad** antes de gastar un crédito, y anotarlo
  en `origen.md`.
- Nunca caras ni voces de figuras públicas, ni personajes con derechos.

## Cifras de referencia (medidas con `revisar_toma.py`, oct-2026)
- Poses de un mismo personaje entre sí: 0,72 y 0,83 de media en los dos kits medidos (en uno, la pose de perfil
  completo salió atípica, 0,49, y se quitó de la carpeta de medición).
- Tomas de video de la misma persona contra su kit: 0,565–0,776. Otra persona: 0,337–0,411. Umbral: 0,50.
- El parecido se **mide**, no se opina: la impresión visual de «no se parece» se ha equivocado.
