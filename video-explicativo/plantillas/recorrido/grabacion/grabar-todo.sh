#!/bin/bash
# Graba todas las tomas, una por proceso, con tope de tiempo y un reintento. Registro en salida/todo.log.
#   bash grabar-todo.sh            → todas las tomas de proyecto.json
#   bash grabar-todo.sh lote mapa  → solo esas
cd "$(dirname "$0")" || exit 1
mkdir -p salida
TOPE=${TOPE:-600}
TOMAS=${*:-$(node grabar.mjs --listar)}
for t in $TOMAS; do
  for intento in 1 2; do
    echo "== $t (intento $intento) $(date +%H:%M:%S)" | tee -a salida/todo.log
    if timeout "$TOPE" node grabar.mjs --toma "$t" >> salida/todo.log 2>&1; then break; fi
    echo "   ✖ $t salió con error o le faltan escenas (ver salida/$t/grabar.log)" | tee -a salida/todo.log
  done
done
echo "== FIN $(date +%H:%M:%S)" | tee -a salida/todo.log
