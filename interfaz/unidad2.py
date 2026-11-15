"""Interfaz de la Unidad 2: capacitores, dieléctricos y energía almacenada."""
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from nucleo import capacitores as cap

W, H = 540, 370


class Unidad2(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True)
        self.t1, self.t2 = ttk.Frame(nb), ttk.Frame(nb)
        nb.add(self.t1, text="Simulador de capacitores")
        nb.add(self.t2, text="Calculadora de energía")
        self._tab_simulador(); self._tab_energia()
        self.actualizar()

    # ================= Pestaña 1 =================
    def _tab_simulador(self):
        p = ttk.Frame(self.t1, padding=10); p.pack(side="left", fill="y")
        ttk.Label(p, text="Parámetros", font=("", 11, "bold")).pack(anchor="w")

        self.A = tk.DoubleVar(value=100.0)    # cm²
        self.d = tk.DoubleVar(value=1.0)      # mm
        self.val = tk.DoubleVar(value=12.0)   # V  o  nC
        self.modo = tk.StringVar(value="V")
        self.diel = tk.StringVar(value="Vacío")

        self.lbl_A = self._slider(p, "Área A", self.A, 10, 1000)
        self.lbl_d = self._slider(p, "Separación d", self.d, 0.1, 10)
        ttk.Label(p, text="Dieléctrico").pack(anchor="w", pady=(10, 0))
        cb = ttk.Combobox(p, textvariable=self.diel, values=list(cap.DIELECTRICOS), state="readonly")
        cb.pack(fill="x"); cb.bind("<<ComboboxSelected>>", lambda e: self.actualizar())

        ttk.Label(p, text="Condición", font=("", 10, "bold")).pack(anchor="w", pady=(12, 0))
        ttk.Radiobutton(p, text="Fuente conectada (V constante)", variable=self.modo,
                        value="V", command=self._cambio_modo).pack(anchor="w")
        ttk.Radiobutton(p, text="Aislado (Q constante)", variable=self.modo,
                        value="Q", command=self._cambio_modo).pack(anchor="w")
        self.lbl_val = ttk.Label(p); self.lbl_val.pack(anchor="w", pady=(6, 0))
        self.sc_val = ttk.Scale(p, from_=1, to=200, variable=self.val, command=lambda e: self.actualizar())
        self.sc_val.pack(fill="x")

        ttk.Separator(p).pack(fill="x", pady=10)
        ttk.Label(p, text="Resultados", font=("", 11, "bold")).pack(anchor="w")
        self.res = tk.Text(p, width=34, height=11, state="disabled", font=("Consolas", 10))
        self.res.pack()
        self.aviso = ttk.Label(p, text="", foreground="red", wraplength=250); self.aviso.pack(pady=4)

        der = ttk.Frame(self.t1); der.pack(side="right", fill="both", expand=True)
        self.cv = tk.Canvas(der, width=W, height=H, bg="white", highlightthickness=1)
        self.cv.pack(pady=6)
        self.fig = Figure(figsize=(7.5, 2.7)); self.fig.subplots_adjust(wspace=0.45, bottom=0.34, top=0.9, left=0.07, right=0.98)
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=der)
        self.canvas_fig.get_tk_widget().pack(fill="both", expand=True)

    def _slider(self, parent, texto, var, lo, hi):
        lbl = ttk.Label(parent); lbl.pack(anchor="w", pady=(8, 0))
        ttk.Scale(parent, from_=lo, to=hi, variable=var, command=lambda e: self.actualizar()).pack(fill="x")
        return lbl

    def _cambio_modo(self):
        if self.modo.get() == "V": self.sc_val.config(from_=1, to=200); self.val.set(12)
        else:                      self.sc_val.config(from_=0.1, to=100); self.val.set(1)
        self.actualizar()

    def _estado(self):
        A, d = self.A.get() * 1e-4, self.d.get() * 1e-3
        kappa, rig = cap.DIELECTRICOS[self.diel.get()]
        v = self.val.get() * (1 if self.modo.get() == "V" else 1e-9)
        return A, d, kappa, rig, cap.estado(A, d, kappa, self.modo.get(), v, rig)

    def actualizar(self):
        A, d, kappa, rig, s = self._estado()
        self.lbl_A.config(text=f"Área A = {self.A.get():.0f} cm²")
        self.lbl_d.config(text=f"Separación d = {self.d.get():.2f} mm")
        if self.modo.get() == "V": self.lbl_val.config(text=f"Voltaje V = {self.val.get():.1f} V")
        else:                      self.lbl_val.config(text=f"Carga Q = {self.val.get():.2f} nC")
        txt = (f"κ        = {kappa:g}\n"
               f"C        = {cap.fmt(s['C'], 'F')}\n"
               f"Q        = {cap.fmt(s['Q'], 'C')}\n"
               f"V        = {cap.fmt(s['V'], 'V')}\n"
               f"E        = {cap.fmt(s['E'], 'V/m')}\n"
               f"U        = {cap.fmt(s['U'], 'J')}\n"
               f"u        = {cap.fmt(s['u'], 'J/m³')}\n"
               f"σ (libre)= {cap.fmt(s['sigma'], 'C/m²')}")
        self.res.config(state="normal"); self.res.delete("1.0", "end")
        self.res.insert("end", txt); self.res.config(state="disabled")
        self.aviso.config(text="⚠ ¡Ruptura dieléctrica! E supera la rigidez del material." if s["ruptura"] else "")
        self._dibujar(A, d, kappa, s)
        self._graficas(A, d, kappa)

    # ---------- esquema del capacitor ----------
    def _dibujar(self, A, d, kappa, s):
        c = self.cv; c.delete("all")
        a_cm2, d_mm = A * 1e4, d * 1e3
        w = 120 + 280 * np.sqrt((a_cm2 - 10) / 990)
        g = 30 + (d_mm - 0.1) / 9.9 * 150
        cx, cy = 200, H / 2
        y1, y2 = cy - g / 2, cy + g / 2
        x0, x1 = cx - w / 2, cx + w / 2
        # dieléctrico (más oscuro = κ mayor)
        t = np.log10(kappa) / np.log10(1200)
        col = "#%02x%02x%02x" % (int(235 - 150 * t), int(245 - 130 * t), 255)
        c.create_rectangle(x0, y1, x1, y2, fill=col, outline="")
        c.create_text(x1 + 8, cy, anchor="w", text=f"κ = {kappa:g}", fill="#234", font=("", 10, "bold"))
        # placas
        c.create_rectangle(x0, y1 - 10, x1, y1, fill="#555", outline="black")
        c.create_rectangle(x0, y2, x1, y2 + 10, fill="#555", outline="black")
        # cargas
        n = int(np.clip(3 + 2 * np.log10(max(abs(s["Q"]), 1e-12) / 1e-10), 3, 12))
        for i in range(n):
            x = x0 + (i + 0.5) * w / n
            c.create_text(x, y1 + 8, text="+", fill="red", font=("", 12, "bold"))
            c.create_text(x, y2 - 8, text="−", fill="blue", font=("", 12, "bold"))
        # líneas de campo
        ancho = float(np.clip(1 + np.log10(abs(s["E"]) + 1) / 1.5, 1, 4))
        colE = "red" if s["ruptura"] else "#228B22"
        for i in range(7):
            x = x0 + (i + 0.5) * w / 7
            c.create_line(x, y1 + 18, x, y2 - 18, arrow="last", fill=colE, width=ancho)
        # cotas
        c.create_line(x0 - 20, y1, x0 - 20, y2, arrow="both")
        c.create_text(x0 - 25, cy, anchor="e", text=f"d = {d_mm:.2f} mm")
        c.create_text(cx, y2 + 28, text=f"A = {a_cm2:.0f} cm²")
        # fuente o aislado
        if self.modo.get() == "V":
            bx = 470
            for pts in ((cx, y1 - 10, cx, 35, bx, 35, bx, 150), (cx, y2 + 10, cx, H - 35, bx, H - 35, bx, 205)):
                c.create_line(*pts, width=2)
            c.create_line(bx - 18, 160, bx + 18, 160, width=3)
            c.create_line(bx - 9, 175, bx + 9, 175, width=5)
            c.create_text(bx + 24, 168, anchor="w", text=f"{s['V']:.1f} V")
            c.create_text(W - 70, 10, text="V constante", fill="gray")
        else:
            c.create_text(W - 70, 10, text="Aislado: Q constante", fill="gray")

    # ---------- curvas C vs d, A, κ ----------
    def _graficas(self, A, d, kappa):
        self.fig.clear()
        ax1, ax2, ax3 = (self.fig.add_subplot(1, 3, i) for i in (1, 2, 3))
        self.fig.subplots_adjust(wspace=0.45, bottom=0.34, top=0.9, left=0.07, right=0.98)
        ds = np.linspace(0.1, 10, 200) * 1e-3
        ax1.plot(ds * 1e3, [cap.capacitancia(A, x, kappa) * 1e12 for x in ds])
        ax1.plot(d * 1e3, cap.capacitancia(A, d, kappa) * 1e12, "ro")
        ax1.set_xlabel("d [mm]"); ax1.set_ylabel("C [pF]"); ax1.set_title("C vs d  (∝ 1/d)", fontsize=9)
        As = np.linspace(10, 1000, 200) * 1e-4
        ax2.plot(As * 1e4, [cap.capacitancia(x, d, kappa) * 1e12 for x in As])
        ax2.plot(A * 1e4, cap.capacitancia(A, d, kappa) * 1e12, "ro")
        ax2.set_xlabel("A [cm²]"); ax2.set_title("C vs A  (∝ A)", fontsize=9)
        nombres = list(cap.DIELECTRICOS)
        ks = [cap.DIELECTRICOS[n][0] for n in nombres]
        Cs = [cap.capacitancia(A, d, k) * 1e12 for k in ks]
        colores = ["tab:red" if n == self.diel.get() else "tab:gray" for n in nombres]
        ax3.bar(range(len(nombres)), Cs, color=colores); ax3.set_yscale("log")
        ax3.set_xticks(range(len(nombres))); ax3.set_xticklabels([n.split(" ")[0] for n in nombres], rotation=60, fontsize=7)
        ax3.set_title("C según dieléctrico [pF]", fontsize=9)
        for ax in (ax1, ax2, ax3): ax.grid(alpha=.3); ax.tick_params(labelsize=8)
        self.canvas_fig.draw_idle()

    # ================= Pestaña 2 =================
    def _tab_energia(self):
        p = ttk.Frame(self.t2, padding=15); p.pack(side="left", fill="y")
        ttk.Label(p, text="Calculadora de energía almacenada", font=("", 11, "bold")).grid(columnspan=3, sticky="w")
        ttk.Label(p, text="U = ½CV² = Q²/2C = ½QV").grid(columnspan=3, sticky="w", pady=(0, 8))
        self.par = tk.StringVar(value="CV")
        for i, (v, t) in enumerate((("CV", "Conozco C y V"), ("QC", "Conozco Q y C"), ("QV", "Conozco Q y V"))):
            ttk.Radiobutton(p, text=t, variable=self.par, value=v, command=self._etiquetas).grid(row=1 + i, columnspan=3, sticky="w")
        self.l1 = ttk.Label(p); self.l1.grid(row=4, column=0, sticky="w", pady=4)
        self.l2 = ttk.Label(p); self.l2.grid(row=5, column=0, sticky="w", pady=4)
        self.e1, self.e2 = tk.StringVar(value="100"), tk.StringVar(value="12")
        ttk.Entry(p, textvariable=self.e1, width=10).grid(row=4, column=1)
        ttk.Entry(p, textvariable=self.e2, width=10).grid(row=5, column=1)
        self.u1, self.u2 = tk.StringVar(), tk.StringVar()
        self.cb1 = ttk.Combobox(p, textvariable=self.u1, width=5, state="readonly"); self.cb1.grid(row=4, column=2)
        self.cb2 = ttk.Combobox(p, textvariable=self.u2, width=5, state="readonly"); self.cb2.grid(row=5, column=2)
        ttk.Button(p, text="Calcular", command=self.calcular).grid(row=6, columnspan=3, pady=10)
        self.res2 = tk.Text(p, width=36, height=7, state="disabled", font=("Consolas", 10)); self.res2.grid(row=7, columnspan=3)
        self.fig2 = Figure(figsize=(6, 4.5)); self.cv2 = FigureCanvasTkAgg(self.fig2, master=self.t2)
        self.cv2.get_tk_widget().pack(side="right", fill="both", expand=True)
        self._etiquetas()

    _UNI = {"C": {"pF": 1e-12, "nF": 1e-9, "µF": 1e-6, "mF": 1e-3, "F": 1.0},
            "V": {"V": 1.0, "kV": 1e3},
            "Q": {"nC": 1e-9, "µC": 1e-6, "mC": 1e-3, "C": 1.0}}

    def _etiquetas(self):
        a, b = {"CV": ("C", "V"), "QC": ("Q", "C"), "QV": ("Q", "V")}[self.par.get()]
        self.m1, self.m2 = a, b
        self.l1.config(text=f"{a} ="); self.l2.config(text=f"{b} =")
        self.cb1.config(values=list(self._UNI[a])); self.cb2.config(values=list(self._UNI[b]))
        self.u1.set(list(self._UNI[a])[0 if a != "C" else 2]); self.u2.set(list(self._UNI[b])[0])

    def calcular(self):
        try:
            a = float(self.e1.get()) * self._UNI[self.m1][self.u1.get()]
            b = float(self.e2.get()) * self._UNI[self.m2][self.u2.get()]
            r = cap.energia_desde(self.par.get(), a, b)
        except (ValueError, ZeroDivisionError) as ex:
            return messagebox.showerror("Error", f"Datos inválidos. {ex}")
        txt = (f"C = {cap.fmt(r['C'], 'F')}\nV = {cap.fmt(r['V'], 'V')}\nQ = {cap.fmt(r['Q'], 'C')}\n"
               f"\nU = {cap.fmt(r['U'], 'J')}\n    ({r['U']:.4e} J)")
        self.res2.config(state="normal"); self.res2.delete("1.0", "end")
        self.res2.insert("end", txt); self.res2.config(state="disabled")
        self.fig2.clear(); ax = self.fig2.add_subplot(111)
        Vs = np.linspace(0, 2 * abs(r["V"]) or 1, 200)
        ax.plot(Vs, 0.5 * r["C"] * Vs**2, label="U = ½CV²")
        ax.plot(r["V"], r["U"], "ro", label="Tu capacitor")
        ax.set_xlabel("V [V]"); ax.set_ylabel("U [J]"); ax.grid(alpha=.3); ax.legend()
        ax.set_title("Energía vs voltaje (C fija)")
        self.cv2.draw()
