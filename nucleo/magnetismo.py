"""Campos magnéticos idealizados y movimiento en campos uniformes."""
import numpy as np
from scipy.integrate import solve_ivp


def campo_alambre(x, y, corriente):
    """Campo B [T] de un alambre infinito a lo largo del eje z."""
    r2 = x*x + y*y
    factor = 2e-7 * corriente / np.where(r2 > 0, r2, np.nan)
    return -factor*y, factor*x


def campo_iman(x, y, norte_izquierda=True):
    """Modelo de dos polos para visualizar el campo exterior en un plano axial."""
    signo = 1 if norte_izquierda else -1
    dx_n, dx_s = x + 0.9, x - 0.9
    r_n = np.hypot(dx_n, y)
    r_s = np.hypot(dx_s, y)
    a = 1 / np.where(r_n > 0, r_n, np.nan)**3
    b = 1 / np.where(r_s > 0, r_s, np.nan)**3
    return signo*(dx_n*a - dx_s*b), signo*y*(a - b)


def simular_lorentz(q, masa, v0, electrico, magnetico, duracion):
    """Devuelve tiempo, posición y velocidad para una partícula que parte del origen."""
    v0, electrico, magnetico = (np.asarray(v, dtype=float)
                               for v in (v0, electrico, magnetico))
    if any(v.shape != (3,) for v in (v0, electrico, magnetico)):
        raise ValueError("Ingresa tres componentes para cada vector.")
    if not np.isfinite(np.r_[q, masa, duracion, v0, electrico, magnetico]).all():
        raise ValueError("Ingresa valores numéricos finitos.")
    if masa <= 0 or duracion <= 0:
        raise ValueError("La masa y la duración deben ser positivas.")
    razon = q / masa
    vueltas = abs(razon) * np.linalg.norm(magnetico) * duracion / (2*np.pi)
    if not np.isfinite(vueltas) or vueltas > 100:
        raise ValueError("Reduce la duración o el campo B para mostrar hasta 100 giros.")

    def derivada(t, estado):
        v = estado[3:]
        return np.r_[v, razon * (electrico + np.cross(v, magnetico))]

    t = np.linspace(0, duracion, max(501, int(vueltas*40) + 1))
    resultado = solve_ivp(derivada, (0, duracion), np.r_[np.zeros(3), v0],
                          t_eval=t, rtol=1e-8, atol=1e-11,
                          max_step=duracion/max(1, vueltas*12))
    if not resultado.success or not np.isfinite(resultado.y).all():
        raise ValueError("No se pudo simular con estos parámetros.")
    return resultado.t, resultado.y[:3], resultado.y[3:]
