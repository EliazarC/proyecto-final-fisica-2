"""Unidad 4: líneas de campo magnético y trayectorias de Lorentz."""
import tkinter as tk
from tkinter import ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from nucleo.magnetismo import campo_alambre, campo_iman, simular_lorentz


class Unidad4(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        pestañas = ttk.Notebook(self)
        pestañas.pack(fill="both", expand=True)
        campo, lorentz = ttk.Frame(pestañas), ttk.Frame(pestañas)
        pestañas.add(campo, text="Campo magnético")
        pestañas.add(lorentz, text="Fuerza de Lorentz")
        self._crear_campo(campo)
        self._crear_lorentz(lorentz)

    def _paneles(self, parent):
        controles = ttk.Frame(parent, padding=12)
        controles.pack(side="left", fill="y")
        grafica = ttk.Frame(parent)
        grafica.pack(side="left", fill="both", expand=True)
        figura = Figure(figsize=(6, 5), layout="constrained")
        canvas = FigureCanvasTkAgg(figura, master=grafica)
        NavigationToolbar2Tk(canvas, grafica, pack_toolbar=False).pack(
            side="bottom", fill="x")
        canvas.get_tk_widget().pack(fill="both", expand=True)
        return controles, figura, canvas

    def _crear_campo(self, parent):
        panel, self.fig_campo, self.canvas_campo = self._paneles(parent)
        self.fuente = tk.StringVar(value="imán")
        self.vista = tk.StringVar(value="2D")
        self.norte_izquierda = True
        ttk.Label(panel, text="Fuente del campo").pack(anchor="w")
        for valor, etiqueta in (("imán", "Imán de barra"), ("alambre", "Alambre recto")):
            ttk.Radiobutton(panel, text=etiqueta, value=valor, variable=self.fuente,
                            command=self._cambiar_fuente).pack(anchor="w")
        self.config_fuente = ttk.Frame(panel)
        self.config_fuente.pack(fill="x", pady=10)
        self.config_iman = ttk.Frame(self.config_fuente)
        ttk.Button(self.config_iman, text="Girar imán", command=self._girar).pack(fill="x")
        self.config_alambre = ttk.Frame(self.config_fuente)
        ttk.Label(self.config_alambre, text="Corriente [A]").pack(anchor="w")
        self.corriente = tk.StringVar(value="5")
        ttk.Entry(self.config_alambre, textvariable=self.corriente, width=12).pack(anchor="w")
        self.sentido = tk.IntVar(value=1)
        for signo, etiqueta in ((1, "Sale del plano (+z)"), (-1, "Entra al plano (−z)")):
            ttk.Radiobutton(self.config_alambre, text=etiqueta, value=signo,
                            variable=self.sentido, command=self._dibujar_campo).pack(anchor="w")
        for vista in ("2D", "3D"):
            ttk.Radiobutton(panel, text=f"Vista {vista}", value=vista, variable=self.vista,
                            command=self._dibujar_campo).pack(anchor="w")
        ttk.Button(panel, text="Dibujar", command=self._dibujar_campo).pack(fill="x", pady=8)
        self.info_campo = ttk.Label(panel, wraplength=190)
        self.info_campo.pack(anchor="w")
        self._cambiar_fuente()

    def _cambiar_fuente(self):
        self.config_iman.pack_forget()
        self.config_alambre.pack_forget()
        marco = self.config_iman if self.fuente.get() == "imán" else self.config_alambre
        marco.pack(fill="x")
        self._dibujar_campo()

    def _girar(self):
        self.norte_izquierda = not self.norte_izquierda
        self._dibujar_campo()

    def _dibujar_campo(self):
        iman = self.fuente.get() == "imán"
        corriente = 0
        if not iman:
            try:
                corriente = float(self.corriente.get().replace(",", "."))
                if not np.isfinite(corriente) or corriente < 0:
                    raise ValueError
            except ValueError:
                self.info_campo.config(text="Ingresa una corriente finita y mayor o igual a cero.")
                return
            corriente *= self.sentido.get()

        coords = np.linspace(-3, 3, 101)
        x, y = np.meshgrid(coords, coords)
        if iman:
            bx, by = campo_iman(x, y, self.norte_izquierda)
            mascara = (abs(x) <= 0.96) & (abs(y) <= 0.21)
            titulo = "Campo magnético de un imán de barra"
            nota = "Modelo idealizado\nFuera del imán, el campo va de N a S."
        else:
            bx, by = campo_alambre(x, y, corriente)
            mascara = np.hypot(x, y) < 0.17
            titulo = "Campo magnético de un alambre recto"
            nota = f"|B| a 1 m = {2e-7*abs(corriente):.3g} T"
            if corriente == 0:
                nota = "Corriente nula. B = 0."

        bx, by = (np.ma.masked_where(mascara, componente) for componente in (bx, by))
        polos = (("N", "#d73037"), ("S", "#265db1"))
        if not self.norte_izquierda:
            polos = polos[::-1]

        self.fig_campo.clear()
        if self.vista.get() == "2D":
            ax = self.fig_campo.add_subplot()
            ax.streamplot(coords, coords, bx, by, density=1.25, color="#2762a7",
                          linewidth=0.9, arrowsize=1.1)
            if iman:
                for inicio, (polo, color) in zip((-0.95, 0), polos):
                    ax.add_patch(Rectangle((inicio, -0.21), 0.95, 0.42, color=color, zorder=5))
                    ax.text(inicio + 0.475, 0, polo, color="white", weight="bold",
                            ha="center", va="center", zorder=6)
            else:
                ax.add_patch(Circle((0, 0), 0.15, color="#25334a", zorder=5))
                marca = {0: "–", 1: "•", -1: "×"}[int(np.sign(corriente))]
                ax.text(0, 0, marca, ha="center", va="center", color="white", zorder=6)
            ax.set(aspect="equal", xlim=(-3, 3), ylim=(-3, 3))
        else:
            ax = self.fig_campo.add_subplot(projection="3d")
            if iman:
                self._iman_3d(ax, coords, bx, by, polos)
            else:
                self._alambre_3d(ax, corriente)
            ax.set(xlim=(-3, 3), ylim=(-3, 3), zlim=(-3, 3), zlabel="z [m]")
            ax.set_box_aspect((1, 1, 1))

        ax.set(title=titulo, xlabel="x [m]", ylabel="y [m]")
        self.info_campo.config(text=nota)
        self.canvas_campo.draw_idle()

    def _iman_3d(self, ax, coords, bx, by, polos):
        # El modelo es simétrico alrededor de x. Rotar cortes axiales conserva el campo.
        corte = Figure().add_subplot()
        flujos = corte.streamplot(coords, coords, bx, by, density=0.85)
        trazos = [trazo for trazo in flujos.lines.get_segments() if len(trazo) > 1]
        for angulo in (0, np.pi/3, 2*np.pi/3):
            segmentos = []
            for trazo in trazos:
                giro = np.column_stack((trazo[:, 0], trazo[:, 1]*np.cos(angulo),
                                        trazo[:, 1]*np.sin(angulo)))
                segmentos.extend(np.stack((giro[:-1], giro[1:]), axis=1))
            ax.add_collection3d(Line3DCollection(segmentos, colors="#2762a7",
                                                  linewidths=0.65, alpha=0.65))
            radios = np.array([0.65, 1.4, 2.2])
            for lado in (-1, 1):
                r = lado*radios
                vx, _ = campo_iman(np.zeros_like(r), r, self.norte_izquierda)
                ax.quiver(np.zeros_like(r), r*np.cos(angulo), r*np.sin(angulo),
                          np.sign(vx), 0, 0, length=0.27, color="#163e76")
        for inicio, (polo, color) in zip((-0.95, 0), polos):
            ax.bar3d(inicio, -0.21, -0.21, 0.95, 0.42, 0.42, color=color)
            ax.text(inicio + 0.475, 0, 0.28, polo, color=color, weight="bold")

    def _alambre_3d(self, ax, corriente):
        ax.plot([0, 0], [0, 0], [-3, 3], color="#25334a", linewidth=3)
        if corriente == 0:
            return
        theta = np.linspace(0, 2*np.pi, 180)
        signo = np.sign(corriente)
        ax.quiver(0, 0, 0, 0, 0, signo, length=1.2, color="#25334a")
        for altura in (-1.8, 0, 1.8):
            for radio in (0.6, 1.3, 2.1):
                ax.plot(radio*np.cos(theta), radio*np.sin(theta), altura,
                        color="#2762a7", linewidth=0.8)
                ax.quiver(radio, 0, altura, 0, signo, 0, length=0.35, color="#163e76")

    def _crear_lorentz(self, parent):
        panel, self.fig_lorentz, self.canvas_lorentz = self._paneles(parent)
        ttk.Label(panel, text="F = q(E + v × B)").pack(anchor="w", pady=(0, 8))
        self.parametros = {}
        for clave, etiqueta in (("q", "Carga [C]"), ("m", "Masa [kg]"),
                                 ("t", "Duración [s]")):
            fila = ttk.Frame(panel)
            fila.pack(fill="x", pady=2)
            ttk.Label(fila, text=etiqueta, width=14).pack(side="left")
            valor = self.parametros[clave] = tk.StringVar()
            ttk.Entry(fila, textvariable=valor, width=12).pack(side="left")

        for clave, etiqueta in (("v", "Velocidad inicial [m/s]"),
                                 ("E", "Campo eléctrico [V/m]"),
                                 ("B", "Campo magnético [T]")):
            marco = ttk.LabelFrame(panel, text=etiqueta, padding=4)
            marco.pack(fill="x", pady=4)
            valores = self.parametros[clave] = [tk.StringVar() for _ in range(3)]
            for columna, (eje, valor) in enumerate(zip("xyz", valores)):
                ttk.Label(marco, text=eje).grid(row=0, column=columna)
                ttk.Entry(marco, textvariable=valor, width=8).grid(row=1, column=columna)
        for etiqueta, cruzados in (("Ejemplo: campos cruzados", True),
                                    ("Ejemplo: órbita circular", False)):
            ttk.Button(panel, text=etiqueta,
                       command=lambda c=cruzados: self._ejemplo(c)).pack(fill="x", pady=2)
        ttk.Button(panel, text="Simular trayectoria", command=self._simular).pack(fill="x", pady=6)
        self.info_lorentz = ttk.Label(panel, wraplength=220)
        self.info_lorentz.pack(anchor="w")
        self._ejemplo(True)

    def _ejemplo(self, cruzados):
        # Partícula de ejemplo con q/m = 1 C/kg, para trabajar a escala de segundos.
        for clave, valor in zip(("q", "m", "t"), (1e-6, 1e-6, 8 if cruzados else 2*np.pi/3)):
            self.parametros[clave].set(f"{valor:.9g}")
        for clave, vector in (("v", (2.8, 0, 0) if cruzados else (1, 0, 0)),
                              ("E", (0, 3, 0) if cruzados else (0, 0, 0)),
                              ("B", (0, 0, 3))):
            for campo, valor in zip(self.parametros[clave], vector):
                campo.set(str(valor))
        self._simular()

    def _simular(self):
        try:
            leer = lambda var: float(var.get().replace(",", "."))
            q, m, t = (leer(self.parametros[k]) for k in ("q", "m", "t"))
            v, e, b = ([leer(var) for var in self.parametros[k]] for k in ("v", "E", "B"))
        except ValueError:
            self.info_lorentz.config(text="Ingresa un número en cada casilla.")
            return
        try:
            tiempo, r, velocidad = simular_lorentz(q, m, v, e, b, t)
        except (ValueError, OverflowError) as error:
            self.info_lorentz.config(text=str(error))
            return
        self.fig_lorentz.clear()
        ax = self.fig_lorentz.add_subplot(projection="3d")
        ax.plot(*r, color="#2762a7", linewidth=2)
        ax.scatter(*r[:, 0], color="#208249", label="Inicio")
        ax.scatter(*r[:, -1], color="#d73037", label="Fin")
        ax.legend(loc="upper right")
        ax.set(title="Trayectoria de la partícula", xlabel="x [m]", ylabel="y [m]", zlabel="z [m]")
        centro = (r.max(axis=1) + r.min(axis=1)) / 2
        semiancho = max(float(np.ptp(r, axis=1).max()) * 0.55, 1e-12)
        ax.set(xlim=centro[0] + np.array([-semiancho, semiancho]),
               ylim=centro[1] + np.array([-semiancho, semiancho]),
               zlim=centro[2] + np.array([-semiancho, semiancho]))
        ax.set_box_aspect((1, 1, 1))
        self.info_lorentz.config(text=f"Tiempo: {tiempo[-1]:.3g} s\n"
                                      f"Rapidez final: {np.linalg.norm(velocidad[:, -1]):.3g} m/s")
        self.canvas_lorentz.draw_idle()
