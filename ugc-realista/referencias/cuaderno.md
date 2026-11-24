# Cuaderno personal: automejora tipo napkin

Cada persona tiene un cuaderno vivo con lo que aprende en SUS videos, clientes y servicios. Es un **manual de
reglas curado**, no una bitácora: sirve para que el próximo video salga mejor y más barato. No se comparte
automáticamente.

## Al empezar: leer y curar
Antes de cualquier otra cosa, leer el cuaderno y aplicarlo sin anunciarlo. Cada vez que se lee, curarlo en el
acto:
- ordenar cada categoría por importancia (lo más útil arriba);
- fusionar repetidos y borrar lo viejo o de poco valor;
- cada entrada con fecha y una línea **«Qué hacer:»**;
- máximo 10 entradas por categoría (si sobran, sale la menos útil);
- **«Indicaciones de la persona» no se borra sin preguntarle**; si se quitó algo de otra categoría, decirlo en una
  línea al final del trabajo.

Lo que ya está en el cuaderno no se vuelve a preguntar (p. ej. el precio de su plan). Si no existe, crearlo con la
plantilla de abajo. Se llama `cuaderno-ugc.md` en Claude Code y en la app; si la persona trae uno de la app a
Claude Code (o al revés), se fusionan.

## Durante el trabajo: escribir en el momento
No esperar al final. Se escribe apenas pasa algo de esto:
- una toma se rechaza por un defecto que el cuaderno no prevenía → la regla que lo habría evitado;
- la persona corrige algo o da una preferencia → como indicación suya;
- una receta funcionó mejor de lo esperado (un bloque de prompt, un ajuste de voz) → la receta;
- el costo real se alejó de la cotización, o el servicio falló de una forma nueva → la cifra o el arreglo;
- algo del cliente o producto que no se deduce (pronunciación de la marca, lo que no se puede decir).

No entra: lo que ya dice la skill, notas de un solo uso, relatos sin acción, llaves o datos personales.

## Al terminar
Curar otra vez. Si una entrada sirvió en 2 o más proyectos distintos, marcarla `[proponer]`: es candidata para
la base de la skill y se le pasa a quien la mantiene (no se copia sola).

## Plantilla
```markdown
# Cuaderno UGC — <nombre de la persona>

## Reglas de curación
- Curar en cada lectura. Máximo 10 por categoría. Cada entrada: fecha + «Qué hacer:».

## Generación y revisión (máxima prioridad)
1. **[2026-10-20] El frasco salió en espejo al acercarlo a cámara**
   Qué hacer: «never mirrored» en el PRODUCT LOCK y no acercar el producto a menos de medio brazo.

## Servicios
1. **[2026-10-20] Mi plan de Higgsfield: <N> créditos por US$<X>**
   Qué hacer: convertir las cotizaciones con esa cifra.

## Clientes y productos
1. **[2026-10-20] <Cliente>: la marca se dice «<pronunciación>»**
   Qué hacer: verificar con Whisper que no salga mal dicha; si sale, escribirla como se pronuncia en el guion.

## Indicaciones de la persona
1. **[2026-10-20] Prefiere ver el personaje antes que la cotización**
   Qué hacer: mostrar el kit primero y cotizar después.
```
