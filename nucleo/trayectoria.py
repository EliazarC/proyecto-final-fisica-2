"""Módulo 3: trayectoria de una partícula cargada en el campo de cargas puntuales."""
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from .campo import campo_electrico, potencial


@dataclass
class Resultado:
    t: np.ndarray
    r: np.ndarray        # (3, N)
    v: np.ndarray        # (3, N)
    motivo: str
    energia: np.ndarray  # energía mecánica total en cada instante [J]


def simular(cargas, q, m, r0, v0, t_max, E_uniforme=(0.0, 0.0, 0.0),
            lim=10.0, r_min=0.05, n_puntos=2000):
    """Integra m·dv/dt = q·E con RK45 adaptativo (SciPy).
    Termina si t = t_max, la partícula sale de la caja (±lim) o choca con una carga (r_min)."""
    Eu = np.asarray(E_uniforme, dtype=float)

    def f(t, s):
        r, v = s[:3], s[3:]
        Ex, Ey, Ez = campo_electrico(cargas, r[0], r[1], r[2])
        a = q / m * (np.array([Ex, Ey, Ez], dtype=float) + Eu)
        return np.concatenate([v, a])

    def choque(t, s):
        return min(np.linalg.norm(s[:3] - c.pos) for c in cargas) - r_min
    def salida(t, s):
        return lim - np.max(np.abs(s[:3]))
    choque.terminal = salida.terminal = True

    s0 = np.concatenate([r0, v0]).astype(float)
    sol = solve_ivp(f, (0, t_max), s0, method="RK45", rtol=1e-9, atol=1e-12,
                    events=(choque, salida), t_eval=None, dense_output=True)
    t = np.linspace(0, sol.t[-1], n_puntos)
    S = sol.sol(t)
    r, v = S[:3], S[3:]
    V = potencial(cargas, r[0], r[1], r[2]) - Eu @ r      # V del campo uniforme: -E·r
    energia = 0.5 * m * np.sum(v**2, axis=0) + q * V
    if sol.t_events[0].size: motivo = "Colisión con una carga"
    elif sol.t_events[1].size: motivo = "Salió de la región"
    else: motivo = "Tiempo máximo alcanzado"
    return Resultado(t, r, v, motivo, energia)
