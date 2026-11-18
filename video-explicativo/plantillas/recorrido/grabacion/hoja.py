"""Hoja de una toma para revisarla ANTES de montar: 3 cuadros por escena (20 %, 55 %, 90 %), una fila por escena.

    python3 hoja.py <toma> [salida.png]

Imprime la duración de cada escena contra su voz. Una escena mucho más larga que su voz = una acción que esperó un timeout.
"""
import json
import subprocess
import sys
from pathlib import Path

# Sin -font explícita, ImageMagick de Homebrew falla con «unable to read font»
FUENTE = "/System/Library/Fonts/Helvetica.ttc"
toma = sys.argv[1]
d = Path("salida") / toma
out = sys.argv[2] if len(sys.argv) > 2 else str(d / f"hoja-{toma}.png")
frames = json.loads((d / "frames.json").read_text())
escenas = json.loads((d / "escenas.json").read_text())["escenas"]
sel = []
for s in escenas:
    for fr in (0.2, 0.55, 0.9):
        t = s["t0"] + fr * (s["t1"] - s["t0"])
        n = max((x for x in frames if x["t"] <= t), key=lambda x: x["t"], default=frames[0])["n"]
        sel.append(str(d / "frames" / f"f{n:06d}.jpg"))
    dur = s["t1"] - s["t0"]
    aviso = "  ⚠ larga: ¿una acción esperó un timeout o las acciones no caben en la voz?" if dur > s["voz"] + 2.5 else ""   # lo normal: voz + 1,45 s
    print(f"{s['id']}: {dur:.1f} s (voz {s['voz']:.1f} s, focos {len(s.get('focos', []))}){aviso}")
subprocess.run(["magick", "montage", *sel, "-font", FUENTE, "-resize", "480x270", "-tile", "3x", "-geometry", "+3+3", "-background", "#888", out],
               check=True)
print(out)
