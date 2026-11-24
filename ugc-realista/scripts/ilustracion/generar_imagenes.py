"""Genera fondos (2K, 9:16) y piezas (1K, 1:1) de escenas.json con gemini-api, con la imagen de estilo como referencia.

Salta lo que ya existe. Anota cada llamada en gastos.csv. Uso:
  python3 -I scripts/generar_imagenes.py [--solo ID ...] [--rehacer]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
COSTO_2K = 0.0504
COSTO_1K = 0.0336
HILOS = 4
TIEMPO_MAXIMO_S = 240


@dataclass(frozen=True)
class Trabajo:
    id: str
    prompt: str
    salida: Path
    aspecto: str
    tamano: str
    costo: float


def armar_trabajos(cfg: dict) -> list[Trabajo]:
    trabajos = []
    for f in cfg["fondos"]:
        prompt = f["prompt"] if f.get("editar") else f"{f['prompt']} {cfg['sufijo_estilo']}"
        trabajos.append(Trabajo(f["id"], prompt, RAIZ / "img/escenas" / f"{f['id']}.jpg", "9:16", "2K", COSTO_2K))
    for p in cfg["piezas"]:
        prompt = f"{p['prompt']} {cfg['sufijo_pieza']} {cfg['sufijo_estilo']}"
        trabajos.append(Trabajo(p["id"], prompt, RAIZ / "img/piezas/crudo" / f"{p['id']}.jpg", "1:1", "1K", COSTO_1K))
    return trabajos


def generar(t: Trabajo, referencia: Path) -> tuple[str, str]:
    t.salida.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["gemini-api", "image", "--stdin", "-i", str(referencia), "--aspect-ratio", t.aspecto,
         "--image-size", t.tamano, "--out", str(t.salida), "--no-interactive", "-o", "json"],
        input=t.prompt, capture_output=True, text=True, timeout=TIEMPO_MAXIMO_S,
    )
    if r.returncode != 0 or not t.salida.exists():
        return t.id, f"ERROR {r.returncode}: {(r.stderr or r.stdout).strip()[:200]}"
    with (RAIZ / "gastos.csv").open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([dt.date.today().isoformat(), f"image {t.id}", f"gemini-nano-banana-2.1 {t.tamano}", t.costo])
    return t.id, "ok"


def main() -> int:
    a = argparse.ArgumentParser()
    a.add_argument("--solo", nargs="*", default=[])
    a.add_argument("--rehacer", action="store_true")
    args = a.parse_args()
    cfg = json.loads((RAIZ / "escenas.json").read_text(encoding="utf-8"))
    referencia = RAIZ / cfg["referencia_estilo"]
    trabajos = [t for t in armar_trabajos(cfg)
                if (not args.solo or t.id in args.solo) and (args.rehacer or not t.salida.exists())]
    print(f"{len(trabajos)} imágenes, costo estimado US${sum(t.costo for t in trabajos):.2f}")
    fallas = 0
    with ThreadPoolExecutor(HILOS) as ex:
        for fut in as_completed([ex.submit(generar, t, referencia) for t in trabajos]):
            ident, estado = fut.result()
            fallas += estado != "ok"
            print(f"  {ident}: {estado}", flush=True)
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
