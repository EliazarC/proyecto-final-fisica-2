"""Núcleo físico: campo eléctrico y potencial de cargas puntuales (SI)."""
from dataclasses import dataclass
import numpy as np

K = 8.9875517923e9      # constante de Coulomb  [N·m²/C²]
EPS = 1e-3              # suavizado para evitar singularidades [m]
MAX_CARGAS = 10


@dataclass
class Carga:
    q: float            # carga en coulombs
    x: float = 0.0      # posición en metros
    y: float = 0.0
    z: float = 0.0

    @property
    def pos(self):
        return np.array([self.x, self.y, self.z], dtype=float)


def validar(cargas):
    if len(cargas) > MAX_CARGAS:
        raise ValueError(f"Máximo {MAX_CARGAS} cargas puntuales.")


def campo_electrico(cargas, X, Y, Z=0.0):
    """E = k q (r - r_i)/|r - r_i|³ por superposición. Devuelve (Ex, Ey, Ez) en N/C.
    X, Y, Z pueden ser escalares o arreglos de NumPy (se difunden)."""
    validar(cargas)
    X, Y, Z = np.broadcast_arrays(*(np.asarray(a, dtype=float) for a in (X, Y, Z)))
    Ex, Ey, Ez = np.zeros_like(X), np.zeros_like(X), np.zeros_like(X)
    for c in cargas:
        dx, dy, dz = X - c.x, Y - c.y, Z - c.z
        r3 = (dx**2 + dy**2 + dz**2 + EPS**2) ** 1.5
        f = K * c.q / r3
        Ex += f * dx; Ey += f * dy; Ez += f * dz
    return Ex, Ey, Ez


def potencial(cargas, X, Y, Z=0.0):
    """V = Σ k q_i / r_i  (referencia V(∞)=0). Devuelve voltios."""
    validar(cargas)
    X, Y, Z = np.broadcast_arrays(*(np.asarray(a, dtype=float) for a in (X, Y, Z)))
    V = np.zeros_like(X)
    for c in cargas:
        r = np.sqrt((X - c.x)**2 + (Y - c.y)**2 + (Z - c.z)**2 + EPS**2)
        V += K * c.q / r
    return V


def energia_potencial_sistema(cargas):
    """U = Σ_{i<j} k q_i q_j / r_ij  [J]."""
    U = 0.0
    for i in range(len(cargas)):
        for j in range(i + 1, len(cargas)):
            r = np.linalg.norm(cargas[i].pos - cargas[j].pos)
            U += K * cargas[i].q * cargas[j].q / max(r, EPS)
    return U
