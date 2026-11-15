"""Núcleo físico – Unidad 3: circuitos resistivos y Ley de Ohm (lógica pura, sin interfaz)."""

# ======================= FÍSICA (lógica pura) =======================
def f(n):
    """Formatea con 3 cifras significativas."""
    if n != n or n in (float("inf"), float("-inf")):
        return "—"
    if n == 0:
        return "0"
    if abs(n) >= 1000:
        return f"{n:.0f}"
    return f"{float(f'{n:.3g}'):g}"


def fI(i):  # corriente con unidad automática
    return f(i) + " A" if abs(i) >= 1 or i == 0 else f(i * 1000) + " mA"


def fP(p):  # potencia con unidad automática
    return f(p) + " W" if abs(p) >= 1 or p == 0 else f(p * 1000) + " mW"


def fR(r):  # resistencia con unidad automática
    return f(r / 1000) + " kΩ" if r >= 1000 else f(r) + " Ω"


def paralelo(valores):
    """1/Req = 1/R1 + 1/R2 + ..."""
    return 1.0 / sum(1.0 / r for r in valores)


def resolver(V, r_int, etapas):
    """
    etapas: lista de ('s', [R]) o ('p', [R1, R2, ...]); las etapas van en serie.
    Devuelve Req, corriente total y V, I, P de cada resistor.
    """
    eq = [rs[0] if t == "s" else paralelo(rs) for t, rs in etapas]
    Req = sum(eq) + r_int
    It = V / Req
    filas, n = [], 0
    for k, (t, rs) in enumerate(etapas):
        Vk = It * eq[k]                      # voltaje de la etapa
        for r in rs:
            n += 1
            I = Vk / r                       # Ley de Ohm
            filas.append(dict(n=n, k=k, R=r, V=Vk, I=I, P=Vk * I))
    return dict(V=V, r_int=r_int, Req=Req, It=It, eq=eq, filas=filas,
                Pint=It ** 2 * r_int, Pt=V * It)


PRESETS = {
    "Serie": (12, 0, [("s", [100]), ("s", [200]), ("s", [300])]),
    "Paralelo": (12, 0, [("p", [100, 200, 300])]),
    "Mixto": (12, 0, [("s", [100]), ("p", [200, 300])]),
    "Ejercicio 2 (28 V)": (28, 0, [("p", [1.6, 2.4, 4.8])]),
}
