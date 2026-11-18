"""Comprueba que el video no lleve datos personales: busca en historia.json, el HTML generado (film/, film-v/),
REVIEW.md, LEEME.md y revision*/informe.md.

    python3 pii_guard.py

Busca (1) cada línea de private/prohibidos.txt (apellidos, correos, teléfonos, ZIP, palabras de direcciones: se escriben
desde los crudos con un script, nunca a mano en el chat) y (2) cualquier correo o teléfono con forma de correo o teléfono.
Imprime solo CUÁNTOS hay y en qué archivo, nunca el dato (para no copiar PII a la consola). Sale con 1 si encuentra algo.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CORREO = re.compile(r"[\w.+-]+@[\w-]+\s*[.,]\s*[a-z]{2,}", re.IGNORECASE)
TELEFONO = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{8,}\d)(?!\d)")


def prohibidos() -> list[str]:
    p = RAIZ / "private" / "prohibidos.txt"
    if not p.exists():
        print("⚠ falta private/prohibidos.txt: solo se buscan correos y teléfonos por forma")
        return []
    return [l.strip() for l in p.read_text().splitlines() if l.strip() and not l.startswith("#")]


def patron(t: str) -> str:
    pat = re.escape(t)
    if t.isdigit():
        return rf"(?<!\d){pat}(?!\d)"
    return rf"\b{pat}\b" if re.fullmatch(r"\w+", t) else pat


def main() -> int:
    toks = prohibidos()
    archivos = [RAIZ / "historia.json"] + sorted(RAIZ.glob("film*/**/*.html"))
    archivos += [f for f in [RAIZ / "REVIEW.md", RAIZ / "LEEME.md", *RAIZ.glob("revision*/informe.md")] if f.exists()]
    malos = 0
    for f in archivos:
        texto = html.unescape(f.read_text())
        n = sum(1 for t in toks if re.search(patron(t), texto, flags=re.IGNORECASE))
        visible = re.sub(r"<(style|script)\b.*?</\1>", " ", texto, flags=re.S)        # CSS y JS: números que no son teléfonos
        visible = re.sub(r"<[^>]+>", " ", visible)
        n += len(CORREO.findall(visible)) + len(TELEFONO.findall(visible))
        if n:
            malos += n
            print(f"PII: {n} hallazgo(s) en {f.relative_to(RAIZ)}")
    print(f"prohibidos revisados: {len(toks)} · archivos: {len(archivos)} · hallazgos: {malos}")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
