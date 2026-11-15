"""Núcleo físico – Unidad 2: capacitores de placas paralelas y dieléctricos (SI)."""
import numpy as np

EPS0 = 8.8541878128e-12   # permitividad del vacío [F/m]

# nombre: (constante dieléctrica κ, rigidez dieléctrica [V/m]).  Valores típicos aproximados.
DIELECTRICOS = {
    "Vacío":                       (1.0,     np.inf),
    "Aire":                        (1.0006,  3.0e6),
    "Teflón":                      (2.1,     60e6),
    "Papel":                       (3.7,     16e6),
    "Mica":                        (5.4,     118e6),
    "Vidrio":                      (5.0,     14e6),
    "Porcelana":                   (6.5,     12e6),
    "Cerámica (titanato de bario)": (1200.0, 8e6),
}


def capacitancia(A, d, kappa=1.0):
    """C = κ ε0 A / d   [F].   A en m², d en m."""
    if A <= 0 or d <= 0 or kappa < 1:
        raise ValueError("Se requiere A > 0, d > 0 y κ ≥ 1.")
    return kappa * EPS0 * A / d


def estado(A, d, kappa, modo, valor, rigidez=np.inf):
    """Calcula todas las magnitudes del capacitor.
    modo 'V': fuente conectada, valor = V [V]  (V constante).
    modo 'Q': capacitor aislado, valor = Q [C] (Q constante)."""
    C = capacitancia(A, d, kappa)
    if modo == "V":
        V = valor; Q = C * V
    elif modo == "Q":
        Q = valor; V = Q / C
    else:
        raise ValueError("modo debe ser 'V' o 'Q'.")
    E = V / d                                   # campo dentro del dieléctrico
    return dict(C=C, Q=Q, V=V, E=E,
                U=0.5 * C * V**2,               # energía almacenada [J]
                u=0.5 * kappa * EPS0 * E**2,    # densidad de energía [J/m³]
                sigma=Q / A,                    # densidad de carga libre [C/m²]
                ruptura=abs(E) > rigidez)


# ----- Calculadora de energía: se conocen dos de {C, V, Q} -----
def energia_desde(par, a, b):
    """par: 'CV' (a=C, b=V), 'QC' (a=Q, b=C) o 'QV' (a=Q, b=V). Devuelve dict C,V,Q,U."""
    if par == "CV":   C, V = a, b; Q = C * V
    elif par == "QC": Q, C = a, b; V = Q / C
    elif par == "QV": Q, V = a, b; C = Q / V
    else: raise ValueError("par inválido")
    if C <= 0: raise ValueError("La capacitancia debe ser positiva.")
    return dict(C=C, V=V, Q=Q, U=0.5 * C * V**2)


def asociacion(capacitancias, tipo):
    """Capacitancia equivalente: 'serie' → 1/Σ(1/Ci); 'paralelo' → ΣCi."""
    c = np.asarray(capacitancias, dtype=float)
    return 1.0 / np.sum(1.0 / c) if tipo == "serie" else float(np.sum(c))


# ----- Formato con prefijos SI -----
_PREF = [(1e-12, "p"), (1e-9, "n"), (1e-6, "µ"), (1e-3, "m"), (1, ""), (1e3, "k"), (1e6, "M"), (1e9, "G")]

def fmt(x, unidad):
    if x == 0 or not np.isfinite(x): return f"{x:g} {unidad}"
    for f, p in reversed(_PREF):
        if abs(x) >= f: return f"{x / f:.4g} {p}{unidad}"
    return f"{x / 1e-12:.4g} p{unidad}"
