"""Recorta las piezas sobre verde (#00FF00) a PNG con transparencia: clave por «verdor», quita el reflejo verde del borde
y ajusta el lienzo al objeto con un margen. Informa los píxeles verdes que queden visibles.

Uso: uv run --with pillow --with numpy python scripts/recortar_piezas.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "img/piezas/crudo"
SALIDA = RAIZ / "img/piezas"
VERDOR_OPACO = 18     # verdor (g - max(r, b)) por debajo de esto: píxel del objeto
VERDOR_TRANSP = 70    # por encima: fondo
MARGEN_PX = 12
ALFA_MINIMO = 8


def recortar(ruta: Path) -> tuple[Path, int]:
    rgb = np.asarray(Image.open(ruta).convert("RGB")).astype(np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    verdor = g - np.maximum(r, b)
    alfa = 1.0 - np.clip((verdor - VERDOR_OPACO) / (VERDOR_TRANSP - VERDOR_OPACO), 0.0, 1.0)
    g_limpio = np.where(verdor > 0, np.maximum(r, b), g)  # quita el reflejo verde
    salida = np.dstack([r, g_limpio, b, alfa * 255.0]).clip(0, 255).astype(np.uint8)
    ys, xs = np.nonzero(salida[..., 3] > ALFA_MINIMO)
    y0, y1 = max(ys.min() - MARGEN_PX, 0), min(ys.max() + MARGEN_PX, salida.shape[0])
    x0, x1 = max(xs.min() - MARGEN_PX, 0), min(xs.max() + MARGEN_PX, salida.shape[1])
    recorte = salida[y0:y1, x0:x1]
    a = recorte[..., 3] > 128
    restos = int(np.sum(a & (recorte[..., 1] > 200) & (recorte[..., 0] < 80) & (recorte[..., 2] < 80)))
    destino = SALIDA / f"{ruta.stem}.png"
    Image.fromarray(recorte, "RGBA").save(destino)
    return destino, restos


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    for ruta in sorted(ENTRADA.glob("*.jpg")):
        destino, restos = recortar(ruta)
        w, h = Image.open(destino).size
        print(f"{destino.name:26s} {w}x{h}  píxeles verdes visibles: {restos}")


if __name__ == "__main__":
    main()
