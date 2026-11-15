"""Interfaz de la Unidad 1: campo eléctrico, potencial y trayectorias.
Unidades de la interfaz: cargas en µC, distancias en m, masa en g."""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from nucleo.campo import Carga, MAX_CARGAS, K, campo_electrico, potencial, energia_potencial_sistema
from nucleo.trayectoria import simular
from interfaz import graficos_campo as vis

UC = 1e-6


class Unidad1(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.cargas = [Carga(+5 * UC, -1, 0, 0), Carga(-5 * UC, 1, 0, 0)]
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True)
        self.t1, self.t2, self.t3 = ttk.Frame(nb), ttk.Frame(nb), ttk.Frame(nb)
        nb.add(self.t1, text="Visualizador de cargas")
        nb.add(self.t2, text="Calculadora de potencial")
        nb.add(self.t3, text="Simulador de trayectoria")
        self._tab_visualizador(); self._tab_potencial(); self._tab_trayectoria()
        self._refrescar_tabla(); self.dibujar()

    # ---------- utilidades ----------
    def _entrada(self, parent, etiqueta, valor, fila):
        ttk.Label(parent, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=2)
        v = tk.StringVar(value=str(valor))
        ttk.Entry(parent, textvariable=v, width=10).grid(row=fila, column=1, pady=2)
        return v

    def _canvas(self, parent, fig):
        c = FigureCanvasTkAgg(fig, master=parent)
        NavigationToolbar2Tk(c, parent, pack_toolbar=False).pack(side="bottom", fill="x")
        c.get_tk_widget().pack(side="right", fill="both", expand=True)
        return c

    # ---------- Pestaña: visualizador ----------
    def _tab_visualizador(self):
        p = ttk.Frame(self.t1, padding=8); p.pack(side="left", fill="y")
        self.tabla = ttk.Treeview(p, columns=("q", "x", "y", "z"), show="headings", height=10)
        for c, h in zip(("q", "x", "y", "z"), ("q [µC]", "x [m]", "y [m]", "z [m]")):
            self.tabla.heading(c, text=h); self.tabla.column(c, width=65, anchor="center")
        self.tabla.pack()
        f = ttk.Frame(p); f.pack(pady=8)
        self.vq = self._entrada(f, "q [µC]", 3, 0); self.vx = self._entrada(f, "x [m]", 0, 1)
        self.vy = self._entrada(f, "y [m]", 1, 2);  self.vz = self._entrada(f, "z [m]", 0, 3)
        ttk.Button(p, text="Agregar carga", command=self.agregar).pack(fill="x")
        ttk.Button(p, text="Eliminar seleccionada", command=self.eliminar).pack(fill="x", pady=2)
        ttk.Separator(p).pack(fill="x", pady=8)
        g = ttk.Frame(p); g.pack()
        self.lim = self._entrada(g, "Límite ± [m]", 3, 0)
        self.modo = tk.StringVar(value="2D")
        ttk.Radiobutton(p, text="Vista 2D", variable=self.modo, value="2D", command=self.dibujar).pack(anchor="w")
        ttk.Radiobutton(p, text="Vista 3D", variable=self.modo, value="3D", command=self.dibujar).pack(anchor="w")
        ttk.Button(p, text="Dibujar", command=self.dibujar).pack(fill="x", pady=6)
        self.lbl_U = ttk.Label(p, text=""); self.lbl_U.pack()
        self.fig1 = Figure(figsize=(6, 6)); self.canvas1 = self._canvas(self.t1, self.fig1)

    def _refrescar_tabla(self):
        self.tabla.delete(*self.tabla.get_children())
        for c in self.cargas:
            self.tabla.insert("", "end", values=(f"{c.q/UC:g}", c.x, c.y, c.z))
        self.lbl_U.config(text=f"U del sistema = {energia_potencial_sistema(self.cargas):.4g} J")

    def agregar(self):
        if len(self.cargas) >= MAX_CARGAS:
            return messagebox.showwarning("Límite", f"Máximo {MAX_CARGAS} cargas.")
        try:
            q = float(self.vq.get()) * UC
            if q == 0: raise ValueError
            self.cargas.append(Carga(q, float(self.vx.get()), float(self.vy.get()), float(self.vz.get())))
        except ValueError:
            return messagebox.showerror("Error", "Valores inválidos (q no puede ser 0).")
        self._refrescar_tabla(); self.dibujar()

    def eliminar(self):
        sel = self.tabla.selection()
        if sel:
            del self.cargas[self.tabla.index(sel[0])]
            self._refrescar_tabla(); self.dibujar()

    def dibujar(self):
        self.fig1.clear()
        if not self.cargas:
            self.canvas1.draw(); return
        try: lim = float(self.lim.get())
        except ValueError: return
        if self.modo.get() == "2D":
            vis.dibujar_2d(self.fig1.add_subplot(111), self.cargas, lim)
        else:
            vis.dibujar_3d(self.fig1.add_subplot(111, projection="3d"), self.cargas, lim)
        self.canvas1.draw()

    # ---------- Pestaña: calculadora de potencial ----------
    def _tab_potencial(self):
        p = ttk.Frame(self.t2, padding=15); p.pack(side="left", fill="y")
        ttk.Label(p, text="Punto de evaluación", font=("", 11, "bold")).grid(columnspan=2)
        self.px = self._entrada(p, "x [m]", 0, 1); self.py = self._entrada(p, "y [m]", 0.5, 2)
        self.pz = self._entrada(p, "z [m]", 0, 3)
        ttk.Button(p, text="Calcular", command=self.calcular_potencial).grid(row=4, columnspan=2, pady=8)
        self.res_pot = tk.Text(p, width=38, height=14, state="disabled"); self.res_pot.grid(row=5, columnspan=2)
        self.fig2 = Figure(figsize=(6, 5)); self.canvas2 = self._canvas(self.t2, self.fig2)

    def calcular_potencial(self):
        if not self.cargas:
            return messagebox.showwarning("Sin cargas", "Agrega al menos una carga en el visualizador.")
        try: x, y, z = float(self.px.get()), float(self.py.get()), float(self.pz.get())
        except ValueError: return messagebox.showerror("Error", "Coordenadas inválidas.")
        V = float(potencial(self.cargas, x, y, z))
        Ex, Ey, Ez = (float(a) for a in campo_electrico(self.cargas, x, y, z))
        txt = (f"V = {V:.6g} V\n\nEx = {Ex:.4g} N/C\nEy = {Ey:.4g} N/C\nEz = {Ez:.4g} N/C\n"
               f"|E| = {np.sqrt(Ex**2+Ey**2+Ez**2):.4g} N/C\n\nDesglose por carga:\n")
        for i, c in enumerate(self.cargas, 1):
            r = np.linalg.norm(c.pos - np.array([x, y, z]))
            txt += f"  q{i}: r = {r:.3g} m, V = {K*c.q/max(r,1e-3):.4g} V\n"
        self.res_pot.config(state="normal"); self.res_pot.delete("1.0", "end")
        self.res_pot.insert("end", txt); self.res_pot.config(state="disabled")
        xs = np.linspace(-3, 3, 600)
        Vs = potencial(self.cargas, xs, y, z)
        self.fig2.clear(); ax = self.fig2.add_subplot(111)
        lim = np.percentile(np.abs(Vs), 95) * 1.5 or 1
        ax.plot(xs, np.clip(Vs, -lim, lim)); ax.plot(x, V, "ro")
        ax.set_xlabel("x [m]"); ax.set_ylabel("V [V]"); ax.grid(alpha=.3)
        ax.set_title(f"Perfil de potencial (y={y:g}, z={z:g})")
        self.canvas2.draw()

    # ---------- Pestaña: trayectoria ----------
    def _tab_trayectoria(self):
        p = ttk.Frame(self.t3, padding=10); p.pack(side="left", fill="y")
        ttk.Label(p, text="Partícula de prueba", font=("", 11, "bold")).grid(columnspan=2)
        self.tq = self._entrada(p, "q [µC]", 1, 1); self.tm = self._entrada(p, "masa [g]", 1, 2)
        self.tx = self._entrada(p, "x0 [m]", -2, 3); self.ty = self._entrada(p, "y0 [m]", 1.5, 4)
        self.tvx = self._entrada(p, "vx0 [m/s]", 3, 5); self.tvy = self._entrada(p, "vy0 [m/s]", -1, 6)
        self.tT = self._entrada(p, "t máx [s]", 5, 7)
        ttk.Label(p, text="Campo uniforme extra", font=("", 10, "bold")).grid(row=8, columnspan=2, pady=(10, 0))
        self.tEx = self._entrada(p, "Ex [N/C]", 0, 9); self.tEy = self._entrada(p, "Ey [N/C]", 0, 10)
        ttk.Button(p, text="Lanzar partícula", command=self.lanzar).grid(row=11, columnspan=2, pady=10)
        self.lbl_tr = ttk.Label(p, text="", wraplength=220, justify="left"); self.lbl_tr.grid(row=12, columnspan=2)
        self.fig3 = Figure(figsize=(6, 6)); self.canvas3 = self._canvas(self.t3, self.fig3)

    def lanzar(self):
        if not self.cargas:
            return messagebox.showwarning("Sin cargas", "Agrega al menos una carga en el visualizador.")
        try:
            q, m = float(self.tq.get()) * UC, float(self.tm.get()) * 1e-3
            r0 = [float(self.tx.get()), float(self.ty.get()), 0.0]
            v0 = [float(self.tvx.get()), float(self.tvy.get()), 0.0]
            T = float(self.tT.get()); Eu = (float(self.tEx.get()), float(self.tEy.get()), 0.0)
            if m <= 0 or T <= 0: raise ValueError
        except ValueError:
            return messagebox.showerror("Error", "Parámetros inválidos.")
        res = simular(self.cargas, q, m, r0, v0, T, E_uniforme=Eu, lim=6.0)
        self.fig3.clear(); ax = self.fig3.add_subplot(111)
        vis.dibujar_2d(ax, self.cargas, 5.0, n=200, lineas=False)
        sc = ax.scatter(res.r[0], res.r[1], c=res.t, s=4, cmap="plasma", zorder=4)
        ax.plot(*r0[:2], "g^", ms=10, zorder=6)
        self.fig3.colorbar(sc, ax=ax, label="t [s]", shrink=0.8)
        ax.set_title("Trayectoria de la partícula")
        self.canvas3.draw()
        dE = abs(res.energia[-1] - res.energia[0]) / (abs(res.energia[0]) + 1e-30)
        self.lbl_tr.config(text=f"{res.motivo}\nt final = {res.t[-1]:.3g} s\n"
                                f"v final = {np.linalg.norm(res.v[:, -1]):.3g} m/s\n"
                                f"Error rel. de energía = {dE:.2e}")
