"""Valida banco-preguntas/*.json: estructura, ids únicos, respuestas en rango y, en las preguntas con
"verify": "output", ejecuta el código y comprueba que la alternativa correcta sea exactamente la salida.

Uso:  python tools/validar_banco.py            (valida todos los bancos)
Sale con código 1 si encuentra errores (sirve para CI).
"""

import glob
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMPOS = ("id", "exam", "section", "difficulty", "type", "prompt", "options", "answer", "explanation")


def salida(codigo: str) -> str:
    r = subprocess.run([sys.executable, "-I", "-X", "utf8", "-c", codigo], capture_output=True, text=True, timeout=10,
                       encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip().splitlines()[-1] if r.stderr else "error")
    return " ".join(r.stdout.split())


def validar(ruta: str) -> list:
    errores = []
    with open(ruta, encoding="utf-8") as fh:
        banco = json.load(fh)
    secciones = {s["id"] for s in banco.get("sections", [])}
    vistos = set()
    for q in banco.get("questions", []):
        qid = q.get("id", "?")
        for campo in CAMPOS:
            if campo not in q:
                errores.append(f"{qid}: falta '{campo}'")
        if qid in vistos:
            errores.append(f"{qid}: id repetido")
        vistos.add(qid)
        if q.get("section") not in secciones:
            errores.append(f"{qid}: sección desconocida {q.get('section')}")
        opciones, respuesta = q.get("options", []), q.get("answer", [])
        if len(opciones) < 2 or len(set(opciones)) != len(opciones):
            errores.append(f"{qid}: opciones insuficientes o repetidas")
        if not respuesta or any(not 0 <= i < len(opciones) for i in respuesta):
            errores.append(f"{qid}: respuesta fuera de rango")
        if q.get("type") == "single" and len(respuesta) != 1:
            errores.append(f"{qid}: 'single' debe tener exactamente una respuesta")
        if q.get("type") == "multiple" and len(respuesta) < 2:
            errores.append(f"{qid}: 'multiple' debe tener al menos dos respuestas")
        if q.get("verify") == "output":
            try:
                real = salida(q["code"])
            except Exception as exc:  # noqa: BLE001
                errores.append(f"{qid}: el código falla al ejecutarse ({exc})")
                continue
            correcta = " ".join(opciones[respuesta[0]].split())
            if real != correcta:
                errores.append(f"{qid}: la salida real es «{real}», pero la opción correcta dice «{correcta}»")
            for i, op in enumerate(opciones):
                if i != respuesta[0] and " ".join(op.split()) == real:
                    errores.append(f"{qid}: la opción {i} también coincide con la salida")
    return errores


def main() -> int:
    total = 0
    errores = []
    for ruta in sorted(glob.glob(os.path.join(RAIZ, "banco-preguntas", "*.json"))):
        if ruta.endswith("schema.json"):
            continue
        with open(ruta, encoding="utf-8") as fh:
            total += len(json.load(fh).get("questions", []))
        errores += [f"{os.path.basename(ruta)} · {e}" for e in validar(ruta)]
    for e in errores:
        print("ERROR", e)
    print(f"{total} preguntas revisadas, {len(errores)} errores")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
