"""Mide tono, temblor (jitter), aspereza (shimmer), HNR y velocidad de cada hablante con Praat (parselmouth).

Uso: python medir_voces.py <audio.wav> <whisper.json> <tramos>
<tramos> = "abuela:0-6.2,10.2-11.8;abuelo:6.2-10.0" (segundos). Un nombre que empieza por «abuelo», «hombre» o
«h_» se mide con piso de tono 75 Hz; el resto, 100 Hz. Requiere praat-parselmouth: `uv run --no-project --with praat-parselmouth
--with numpy python -I medir_voces.py ...`. Las palabras de Whisper se asignan a cada
hablante por su tramo para calcular palabras por segundo.
"""
import json
import sys

import numpy as np
import parselmouth
from parselmouth.praat import call


def leer_tramos(texto: str) -> dict[str, list[tuple[float, float]]]:
    salida = {}
    for parte in texto.split(";"):
        nombre, rangos = parte.split(":")
        salida[nombre] = [tuple(float(x) for x in r.split("-")) for r in rangos.split(",")]
    return salida


def medir(sonido: parselmouth.Sound, tramos: list[tuple[float, float]], piso: float, techo: float) -> dict:
    trozos = [sonido.extract_part(a, b, preserve_times=False) for a, b in tramos]
    valores = np.concatenate([t.values for t in trozos], axis=1)
    junto = parselmouth.Sound(valores, sampling_frequency=sonido.sampling_frequency)
    tono = junto.to_pitch(pitch_floor=piso, pitch_ceiling=techo)
    f0 = tono.selected_array["frequency"]
    f0 = f0[f0 > 0]
    puntos = call(junto, "To PointProcess (periodic, cc)", piso, techo)
    jitter = call(puntos, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3) * 100
    shimmer = call([junto, puntos], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6) * 100
    armonia = call(junto.to_harmonicity_cc(), "Get mean", 0, 0)
    return {
        "f0_mediana_hz": round(float(np.median(f0)), 1),
        "f0_p10_p90_hz": [round(float(np.percentile(f0, 10)), 1), round(float(np.percentile(f0, 90)), 1)],
        "jitter_pct": round(jitter, 2),
        "shimmer_pct": round(shimmer, 2),
        "hnr_db": round(armonia, 1),
        "segundos": round(sum(b - a for a, b in tramos), 2),
    }


def main() -> None:
    sonido = parselmouth.Sound(sys.argv[1])
    datos = json.load(open(sys.argv[2], encoding="utf-8"))
    palabras = [w for s in datos["segments"] for w in s.get("words", [])]
    for nombre, tramos in leer_tramos(sys.argv[3]).items():
        piso, techo = (75, 300) if nombre.startswith(("abuelo", "hombre", "h_")) else (100, 500)
        r = medir(sonido, tramos, piso, techo)
        suyas = [w for w in palabras if any(a <= w["start"] < b for a, b in tramos)]
        habla = sum(min(b, max(w["end"] for w in suyas)) - max(a, min(w["start"] for w in suyas)) for a, b in tramos)
        r["palabras"] = len(suyas)
        r["palabras_por_s"] = round(len(suyas) / habla, 2) if habla > 0 else None
        print(nombre, json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
