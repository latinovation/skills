"""Compara la voz transcrita (Whisper con tiempos por palabra) contra el guion de PLAN.md y escribe voz/palabras.json.

palabras.json = {"tramos": [{"id","inicio","fin","texto"}], "palabras": [{"texto","inicio","fin","tramo"}], "duracion"}.
Las palabras del guion se alinean con las de Whisper por difflib; el tiempo de cada palabra del guion sale de su par.

Uso: python3 -I scripts/tiempos_voz.py voz/transcripciones/voz_charon_v1.json voz/voz_charon_v1.wav
"""
from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PAUSA_LARGA_S = 0.6


def normalizar(p: str) -> str:
    p = unicodedata.normalize("NFD", p.lower())
    return "".join(c for c in p if unicodedata.category(c) != "Mn" and (c.isalnum() or c == "ñ"))


def tramos_del_guion() -> list[tuple[str, list[str]]]:
    plan = (RAIZ / "PLAN.md").read_text(encoding="utf-8")
    bloque = plan.split("<!-- GUION:INICIO -->")[1].split("<!-- GUION:FIN -->")[0]
    salida = []
    for linea in bloque.strip().splitlines():
        m = re.match(r"^(T\d+)\.\s*(.+)$", linea.strip())
        if m:
            salida.append((m.group(1), m.group(2).split()))
    return salida


def duracion(wav: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def main() -> int:
    whisper = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    wav = Path(sys.argv[2])
    oidas = [w for s in whisper["segments"] for w in s.get("words", [])]
    guion = [(tid, p) for tid, pals in tramos_del_guion() for p in pals]
    a = [normalizar(p) for _, p in guion]
    b = [normalizar(w["word"]) for w in oidas]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    diferencias, par = [], {}
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            par.update({i1 + k: j1 + k for k in range(i2 - i1)})
        else:
            diferencias.append((op, " ".join(p for _, p in guion[i1:i2]), " ".join(w["word"].strip() for w in oidas[j1:j2])))
            for k in range(i2 - i1):
                if j1 + min(k, max(j2 - j1 - 1, 0)) < len(oidas) and j2 > j1:
                    par[i1 + k] = j1 + min(k, j2 - j1 - 1)
    palabras = []
    for i, (tid, texto) in enumerate(guion):
        j = par.get(i)
        if j is None:
            print(f"Sin tiempo para «{texto}» ({tid})", file=sys.stderr)
            return 1
        palabras.append({"texto": texto, "inicio": round(oidas[j]["start"], 3), "fin": round(oidas[j]["end"], 3), "tramo": tid})
    tramos = []
    for tid, pals in tramos_del_guion():
        ws = [w for w in palabras if w["tramo"] == tid]
        tramos.append({"id": tid, "inicio": ws[0]["inicio"], "fin": ws[-1]["fin"], "texto": " ".join(pals)})
    total = duracion(wav)
    (RAIZ / "voz/palabras.json").write_text(json.dumps({"tramos": tramos, "palabras": palabras, "duracion": total},
                                                       ensure_ascii=False, indent=1), encoding="utf-8")
    hablado = palabras[-1]["fin"] - palabras[0]["inicio"]
    print(f"palabras: {len(palabras)} · voz {hablado:.1f}s · {len(palabras) / hablado:.2f} pal/s · archivo {total:.2f}s · "
          f"cola tras la última palabra {total - palabras[-1]['fin']:.2f}s")
    print("diferencias con el guion:", diferencias or "ninguna")
    pausas = [(round(palabras[i]["inicio"] - palabras[i - 1]["fin"], 2), palabras[i - 1]["texto"])
              for i in range(1, len(palabras)) if palabras[i]["inicio"] - palabras[i - 1]["fin"] > PAUSA_LARGA_S]
    print("pausas largas:", pausas or "ninguna")
    for t in tramos:
        print(f"  {t['id']}: {t['inicio']:6.2f} → {t['fin']:6.2f}  ({t['fin'] - t['inicio']:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
