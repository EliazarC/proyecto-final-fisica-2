"""Pruebas de validación del núcleo físico (Unidades 1, 2 y 3).
Ejecutar desde la raíz del proyecto:  python -m tests.test_fisica"""
import numpy as np
from nucleo import campo, capacitores as cap, circuitos as circ
from nucleo.trayectoria import simular


def casi(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(abs(b), 1e-30)


def unidad1():
    K, UC = campo.K, 1e-6
    # V de una carga puntual a 1 m  (k·q/r)
    assert casi(campo.potencial([campo.Carga(UC)], 1, 0, 0), K * UC, 1e-5)
    # Campo en el centro de un dipolo: 2kq/r²
    dip = [campo.Carga(5 * UC, -1), campo.Carga(-5 * UC, 1)]
    assert casi(campo.campo_electrico(dip, 0, 0, 0)[0], 2 * K * 5 * UC, 1e-5)
    # Simetría: V = 0 en el plano medio del dipolo
    assert abs(campo.potencial(dip, 0, 3, 0)) < 1e-3
    # Conservación de la energía en la trayectoria
    r = simular(dip, 1e-6, 1e-3, [-2, 1.5, 0], [3, -1, 0], 5, lim=6)
    assert abs(r.energia[-1] - r.energia[0]) / abs(r.energia[0]) < 1e-7
    # Límite de 10 cargas
    try:
        campo.campo_electrico([campo.Carga(UC)] * 11, 0, 0, 0); assert False
    except ValueError:
        pass


def unidad2():
    C0 = cap.capacitancia(0.01, 1e-3)
    assert casi(C0, 8.8541878128e-11, 1e-9)                       # ε0·A/d
    assert casi(cap.capacitancia(0.01, 2e-3), C0 / 2)             # C ∝ 1/d
    assert casi(cap.capacitancia(0.02, 1e-3), 2 * C0)             # C ∝ A
    assert casi(cap.capacitancia(0.01, 1e-3, 5.4), 5.4 * C0)      # C ∝ κ
    r = cap.energia_desde("CV", 100e-12, 12.0)
    assert casi(r["U"], 0.5 * 100e-12 * 144)
    assert casi(cap.energia_desde("QC", r["Q"], r["C"])["U"], r["U"])
    assert casi(cap.energia_desde("QV", r["Q"], r["V"])["U"], r["U"])
    a, b = cap.estado(0.01, 1e-3, 1, "V", 12), cap.estado(0.01, 1e-3, 4, "V", 12)
    assert casi(b["Q"], 4 * a["Q"]) and casi(b["U"], 4 * a["U"])  # V constante
    a, b = cap.estado(0.01, 1e-3, 1, "Q", 1e-9), cap.estado(0.01, 1e-3, 4, "Q", 1e-9)
    assert casi(b["V"], a["V"] / 4) and casi(b["U"], a["U"] / 4)  # Q constante
    assert casi(cap.asociacion([2, 2], "serie"), 1.0) and casi(cap.asociacion([2, 2], "paralelo"), 4.0)
    assert cap.estado(0.01, 1e-6, 1.0006, "V", 12, 3e6)["ruptura"]


def unidad3():
    # Paralelo de 1.6, 2.4 y 4.8 Ω → 0.8 Ω ; con 28 V: I = 35 A, P = 980 W
    s = circ.resolver(28, 0, [("p", [1.6, 2.4, 4.8])])
    assert casi(s["Req"], 0.8) and casi(s["It"], 35) and casi(s["Pt"], 980)
    # Mixto: 100 + (200 ∥ 300) = 220 Ω ; I = 12/220
    s = circ.resolver(12, 0, [("s", [100]), ("p", [200, 300])])
    assert casi(s["Req"], 220) and casi(s["It"], 12 / 220)
    # Conservación de la energía: ΣP de los resistores = V·I
    assert casi(sum(f["P"] for f in s["filas"]) + s["Pint"], s["Pt"])
    # Resistencia interna incluida
    s = circ.resolver(12, 2, [("s", [10])])
    assert casi(s["It"], 1.0) and casi(s["Pint"], 2.0)


if __name__ == "__main__":
    for u in (unidad1, unidad2, unidad3):
        u(); print(f"{u.__name__}: OK ✔")
    print("Todas las pruebas pasaron.")
