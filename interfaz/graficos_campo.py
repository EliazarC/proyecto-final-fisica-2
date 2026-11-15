"""Módulo 1: visualizador de cargas puntuales (2D y 3D)."""
import numpy as np
from matplotlib.colors import SymLogNorm
from nucleo.campo import campo_electrico, potencial


def _marcar_cargas_2d(ax, cargas):
    for c in cargas:
        ax.plot(c.x, c.y, "o", ms=12, mec="k",
                color="tab:red" if c.q > 0 else "tab:blue", zorder=5)
        ax.annotate("+" if c.q > 0 else "−", (c.x, c.y), ha="center", va="center",
                    color="white", fontsize=9, fontweight="bold", zorder=6)


def dibujar_2d(ax, cargas, lim=3.0, n=300, lineas=True, equipot=True):
    """Líneas de campo (streamplot) + curvas equipotenciales en el plano z=0."""
    ax.clear()
    xs = np.linspace(-lim, lim, n)
    X, Y = np.meshgrid(xs, xs)
    Ex, Ey, _ = campo_electrico(cargas, X, Y, 0.0)
    E = np.hypot(Ex, Ey)
    if equipot:
        V = potencial(cargas, X, Y, 0.0)
        vmax = np.percentile(np.abs(V), 90) or 1.0
        niveles = np.linspace(-vmax, vmax, 25)
        ax.contourf(X, Y, np.clip(V, -vmax, vmax), levels=niveles, cmap="RdBu_r", alpha=0.35)
        ax.contour(X, Y, np.clip(V, -vmax, vmax), levels=niveles, colors="gray", linewidths=0.6)
    if lineas:
        ax.streamplot(X, Y, Ex, Ey, color=np.log10(E + 1e-12), cmap="viridis",
                      density=1.6, linewidth=1, arrowsize=1)
    _marcar_cargas_2d(ax, cargas)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")
    ax.set_title("Campo eléctrico y equipotenciales (plano z = 0)")


def _semillas_esfera(n):
    """Puntos casi uniformes sobre la esfera unidad (espiral de Fibonacci)."""
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    th = np.pi * (1 + 5**0.5) * i
    return np.c_[np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)]


def _linea_de_campo(cargas, p0, sentido, lim, paso=0.03, max_pasos=1500, r_stop=0.08):
    """Integra dr/ds = ±E/|E| con RK2 (punto medio). Se detiene al salir de la caja
    o al acercarse a una carga."""
    def u(p):
        Ex, Ey, Ez = campo_electrico(cargas, p[0], p[1], p[2])
        v = np.array([Ex, Ey, Ez], dtype=float)
        return sentido * v / (np.linalg.norm(v) + 1e-30)
    pts = [p0]; p = p0.copy()
    for _ in range(max_pasos):
        k1 = u(p); k2 = u(p + 0.5 * paso * k1)
        p = p + paso * k2
        pts.append(p.copy())
        if np.max(np.abs(p)) > lim: break
        if any(np.linalg.norm(p - c.pos) < r_stop for c in cargas): break
    return np.array(pts)


def dibujar_3d(ax, cargas, lim=3.0, lineas_por_carga=14, equipot_z0=True):
    """Líneas de campo 3D desde cada carga + equipotenciales proyectadas en z=0."""
    ax.clear()
    qmax = max(abs(c.q) for c in cargas)
    for c in cargas:
        n = max(6, int(round(lineas_por_carga * abs(c.q) / qmax)))
        sentido = 1.0 if c.q > 0 else -1.0
        for s in _semillas_esfera(n):
            L = _linea_de_campo(cargas, c.pos + 0.1 * s, sentido, lim)
            ax.plot(L[:, 0], L[:, 1], L[:, 2], lw=0.8,
                    color="tab:red" if c.q > 0 else "tab:blue", alpha=0.8)
    if equipot_z0:
        xs = np.linspace(-lim, lim, 120)
        X, Y = np.meshgrid(xs, xs)
        V = potencial(cargas, X, Y, 0.0)
        vmax = np.percentile(np.abs(V), 90) or 1.0
        ax.contour(X, Y, np.clip(V, -vmax, vmax), levels=np.linspace(-vmax, vmax, 15),
                   zdir="z", offset=-lim, cmap="RdBu_r", linewidths=0.8)
    for c in cargas:
        ax.scatter(c.x, c.y, c.z, s=120, edgecolor="k",
                   color="tab:red" if c.q > 0 else "tab:blue")
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_zlabel("z [m]")
    ax.set_title("Líneas de campo 3D (equipotenciales en el piso)")
