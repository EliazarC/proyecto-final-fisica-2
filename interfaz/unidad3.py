"""Interfaz de la Unidad 3: simulador de circuitos y visualizador de la Ley de Ohm."""
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from matplotlib.colors import hsv_to_rgb

from nucleo.circuitos import f, fI, fP, fR, resolver, PRESETS


# ======================= INTERFAZ =======================
class Unidad3(ttk.Frame):
    """Unidad 3: Corriente eléctrica y Ley de Ohm (interfaz original, ahora como pestaña)."""

    def __init__(self, parent):
        super().__init__(parent)
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        self.t1 = ttk.Frame(nb)
        self.t2 = ttk.Frame(nb)
        nb.add(self.t1, text="Simulador de circuitos")
        nb.add(self.t2, text="Visualizador de Ley de Ohm")
        self.etapas = []
        self.build_circuitos()
        self.build_ohm()
        self.cargar("Ejercicio 2 (28 V)")
        self.calc_ohm()

    # ---------------- Módulo 1 ----------------
    def build_circuitos(self):
        izq = ttk.Frame(self.t1, padding=8)
        izq.pack(side="left", fill="y")
        der = ttk.Frame(self.t1, padding=8)
        der.pack(side="right", fill="both", expand=True)

        ttk.Label(izq, text="Fuente V (voltios)").pack(anchor="w")
        self.eV = ttk.Entry(izq, width=14)
        self.eV.pack(anchor="w")
        ttk.Label(izq, text="Resistencia interna (Ω)").pack(anchor="w", pady=(6, 0))
        self.eRi = ttk.Entry(izq, width=14)
        self.eRi.pack(anchor="w")

        ttk.Label(izq, text="Ejemplos:").pack(anchor="w", pady=(10, 0))
        for nombre in PRESETS:
            ttk.Button(izq, text=nombre,
                       command=lambda n=nombre: self.cargar(n)).pack(fill="x", pady=1)

        ttk.Label(izq, text="Etapas (en serie, de izq. a der.):").pack(anchor="w", pady=(10, 0))
        self.lb = tk.Listbox(izq, height=7, width=30)
        self.lb.pack()
        ttk.Label(izq, text="Valores en Ω separados por coma\n(usa punto decimal: 1.6, 2.4)").pack(anchor="w", pady=(6, 0))
        self.eVal = ttk.Entry(izq, width=28)
        self.eVal.pack()
        ttk.Button(izq, text="+ Serie (cada valor = 1 resistor)", command=lambda: self.agregar("s")).pack(fill="x", pady=1)
        ttk.Button(izq, text="+ Bloque en paralelo (2 o más)", command=lambda: self.agregar("p")).pack(fill="x", pady=1)
        ttk.Button(izq, text="Eliminar etapa seleccionada", command=self.eliminar).pack(fill="x", pady=1)
        ttk.Button(izq, text="CALCULAR", command=self.calcular).pack(fill="x", pady=(10, 0))

        self.fig = Figure(figsize=(7, 3.2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=der)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.resumen = ttk.Label(der, font=("Segoe UI", 11, "bold"))
        self.resumen.pack(anchor="w", pady=4)
        cols = ("Resistor", "R", "V", "I", "P")
        self.tv = ttk.Treeview(der, columns=cols, show="headings", height=6)
        for c in cols:
            self.tv.heading(c, text=c)
            self.tv.column(c, width=100, anchor="center")
        self.tv.pack(fill="x")
        self.txt = tk.Text(der, height=9, font=("Consolas", 9))
        self.txt.pack(fill="both", expand=True, pady=(6, 0))

    def cargar(self, nombre):
        V, ri, et = PRESETS[nombre]
        self.eV.delete(0, "end"); self.eV.insert(0, str(V))
        self.eRi.delete(0, "end"); self.eRi.insert(0, str(ri))
        self.etapas = [(t, list(rs)) for t, rs in et]
        self.refrescar_lista()
        self.calcular()

    def refrescar_lista(self):
        self.lb.delete(0, "end")
        for k, (t, rs) in enumerate(self.etapas, 1):
            tipo = "Serie" if t == "s" else "Paralelo"
            self.lb.insert("end", f"{k}. {tipo}: " + ", ".join(f(r) for r in rs) + " Ω")

    def agregar(self, tipo):
        try:
            vals = [float(x) for x in self.eVal.get().replace(";", ",").split(",") if x.strip()]
            if not vals or any(v <= 0 for v in vals):
                raise ValueError
            if tipo == "p" and len(vals) < 2:
                messagebox.showwarning("Paralelo", "Un bloque en paralelo necesita 2 o más valores.")
                return
        except ValueError:
            messagebox.showerror("Error", "Ingresa números positivos separados por coma.")
            return
        if tipo == "s":
            self.etapas += [("s", [v]) for v in vals]
        else:
            self.etapas.append(("p", vals))
        self.refrescar_lista()
        self.calcular()

    def eliminar(self):
        sel = self.lb.curselection()
        if sel and len(self.etapas) > 1:
            self.etapas.pop(sel[0])
            self.refrescar_lista()
            self.calcular()

    def calcular(self):
        try:
            V = float(self.eV.get().replace(",", "."))
            ri = float(self.eRi.get().replace(",", ".") or 0)
            if V < 0 or ri < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "V e interna deben ser números ≥ 0.")
            return
        s = resolver(V, ri, self.etapas)
        self.resumen.config(text=f"Req = {fR(s['Req'])}   |   I total = {fI(s['It'])}   |   "
                                 f"V = {f(V)} V   |   P total = {fP(s['Pt'])}")
        for i in self.tv.get_children():
            self.tv.delete(i)
        for r in s["filas"]:
            self.tv.insert("", "end", values=(f"R{r['n']}", fR(r["R"]), f"{f(r['V'])} V", fI(r["I"]), fP(r["P"])))
        if ri > 0:
            self.tv.insert("", "end", values=("r interna", fR(ri), f"{f(s['It'] * ri)} V", fI(s["It"]), fP(s["Pint"])))
        self.procedimiento(s)
        self.dibujar(s)

    def procedimiento(self, s):
        L = []
        for k, (t, rs) in enumerate(self.etapas):
            if t == "p":
                L.append(f"Etapa {k+1} (paralelo): 1/Req = " + " + ".join(f"1/{f(r)}" for r in rs)
                         + f" = 1/{f(s['eq'][k])}  ->  Req = {fR(s['eq'][k])}")
            else:
                L.append(f"Etapa {k+1} (serie): R = {fR(rs[0])}")
        L.append("Req total = " + " + ".join(f(e) for e in s["eq"])
                 + (f" + {f(s['r_int'])} (interna)" if s["r_int"] > 0 else "") + f" = {fR(s['Req'])}")
        L.append(f"I total = V/Req = {f(s['V'])}/{f(s['Req'])} = {fI(s['It'])}")
        L.append("Cada resistor: V = I·Req_etapa ; I = V/R ; P = V·I = V²/R")
        suma = sum(r["P"] for r in s["filas"]) + s["Pint"]
        ok = abs(suma - s["Pt"]) <= 1e-9 * max(1, s["Pt"])
        L.append(f"Verificación: suma de P = {fP(suma)}  vs  V·I = {fP(s['Pt'])}  -> "
                 + ("OK, se conserva la energía" if ok else "REVISAR"))
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", "\n".join(L))

    def dibujar(self, s):
        ax = self.ax
        ax.clear()
        ax.axis("off")
        W = 110
        for t, rs in self.etapas:
            W += 110 if t == "s" else 145 + (len(rs) - 1) * 110
        W = max(W, 420)
        pmax = max(r["P"] for r in s["filas"]) or 1

        def color(p):  # amarillo (poca potencia) -> rojo (mucha)
            q = p / pmax
            return hsv_to_rgb(((55 * (1 - q)) / 360, 0.3 + 0.55 * q, 1))

        def wire(x1, y1, x2, y2, lw=1.8):
            ax.plot([x1, x2], [y1, y2], color="black", lw=lw, zorder=1)

        wire(50, 50, W - 10, 50); wire(50, 220, W - 10, 220); wire(W - 10, 50, W - 10, 220)
        wire(50, 50, 50, 105); wire(50, 155, 50, 220)
        wire(30, 105, 70, 105); wire(40, 118, 60, 118, 5)
        ax.text(78, 105, "+", fontsize=10, va="center")
        ax.text(5, 145, f"{f(s['V'])} V", fontsize=9)
        if s["r_int"] > 0:
            ax.text(5, 165, f"r={fR(s['r_int'])}", fontsize=8, color="gray")

        x, i = 110, 0
        for t, rs in self.etapas:
            if t == "s":
                r = s["filas"][i]; i += 1
                cx = x + 55
                ax.add_patch(Rectangle((cx - 36, 37), 72, 26, fc=color(r["P"]), ec="tab:blue", lw=2, zorder=3))
                ax.text(cx, 24, f"R{r['n']} = {fR(r['R'])}", ha="center", fontsize=8)
                ax.text(cx, 78, f"{fI(r['I'])} · {fP(r['P'])}", ha="center", fontsize=7, color="gray")
                x += 110
            else:
                bx = x
                for j in range(len(rs)):
                    fila = s["filas"][i]; i += 1
                    bx = x + 45 + j * 110
                    wire(bx, 50, bx, 107); wire(bx, 163, bx, 220)
                    ax.add_patch(Rectangle((bx - 13, 107), 26, 56, fc=color(fila["P"]), ec="tab:blue", lw=2, zorder=3))
                    ax.text(bx + 18, 122, f"R{fila['n']} = {fR(fila['R'])}", fontsize=7)
                    ax.text(bx + 18, 138, fI(fila["I"]), fontsize=7, color="gray")
                    ax.text(bx + 18, 154, fP(fila["P"]), fontsize=7, color="gray")
                x = bx + 100
        ax.set_xlim(0, W); ax.set_ylim(250, 0); ax.set_aspect("equal")
        ax.set_title("Color térmico: amarillo = poca potencia, rojo = la mayor", fontsize=8)
        self.fig.tight_layout()
        self.canvas.draw()

    # ---------------- Módulo 2 ----------------
    def build_ohm(self):
        izq = ttk.Frame(self.t2, padding=8)
        izq.pack(side="left", fill="y")
        der = ttk.Frame(self.t2, padding=8)
        der.pack(side="right", fill="both", expand=True)

        ttk.Label(izq, text="Incógnita").pack(anchor="w")
        self.modo = ttk.Combobox(izq, state="readonly", width=24,
                                 values=["Hallar I (dados V y R)", "Hallar V (dados I y R)", "Hallar R (dados V e I)"])
        self.modo.current(0)
        self.modo.pack(anchor="w")
        self.modo.bind("<<ComboboxSelected>>", lambda e: self.calc_ohm())
        self.o = {}
        for clave, txt, ini in (("V", "Voltaje V (V)", "28"), ("I", "Corriente I (A)", ""), ("R", "Resistencia R (Ω)", "0.8")):
            ttk.Label(izq, text=txt).pack(anchor="w", pady=(8, 0))
            e = ttk.Entry(izq, width=16)
            e.insert(0, ini)
            e.pack(anchor="w")
            e.bind("<KeyRelease>", lambda ev: self.calc_ohm())
            self.o[clave] = e
        self.ohm_res = ttk.Label(izq, font=("Segoe UI", 10, "bold"), justify="left")
        self.ohm_res.pack(anchor="w", pady=14)
        ttk.Label(izq, text="V = I·R   I = V/R   R = V/I\nP = V·I = I²R = V²/R", justify="left").pack(anchor="w")

        self.fig2 = Figure(figsize=(6, 4), dpi=100)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=der)
        self.canvas2.get_tk_widget().pack(fill="both", expand=True)

    def calc_ohm(self):
        m = self.modo.current()  # 0: I, 1: V, 2: R
        clave = "IVR"[m]
        for k, e in self.o.items():
            e.config(state="disabled" if k == clave else "normal")

        def leer(k):
            try:
                return float(self.o[k].get().replace(",", "."))
            except ValueError:
                return float("nan")

        V, I, R = leer("V"), leer("I"), leer("R")
        if m == 0:
            I = V / R if R > 0 else float("nan")
        elif m == 1:
            V = I * R
        else:
            R = V / I if I > 0 else float("nan")
        val = {"V": V, "I": I, "R": R}[clave]
        e = self.o[clave]
        e.config(state="normal"); e.delete(0, "end")
        if val == val:
            e.insert(0, f"{val:.6g}")
        e.config(state="disabled")

        self.ohm_res.config(text=f"V = {f(V)} V\nI = {fI(I) if I == I else '—'}\n"
                                 f"R = {fR(R) if R == R else '—'}\nP = {fP(V * I) if V * I == V * I else '—'}")
        ax = self.ax2
        ax.clear()
        if not (R == R and R > 0 and V == V and I == I):
            self.canvas2.draw()
            return
        Vm = max(abs(V) * 1.5, 1)
        k, u = (1000, "mA") if Vm / R < 1 else (1, "A")
        ax.plot([0, Vm], [0, Vm / R * k], lw=2.5, label=f"R = {fR(R)}")
        ax.plot([V, V, 0], [0, I * k, I * k], "--", color="crimson", lw=1)
        ax.plot([V], [I * k], "o", color="crimson", ms=9)
        ax.annotate(f"({f(V)} V, {fI(I)})", (V, I * k), textcoords="offset points", xytext=(-90, 12))
        ax.set_xlabel("Voltaje V (V)")
        ax.set_ylabel(f"Corriente I ({u})")
        ax.set_title("Ley de Ohm: I vs V (pendiente = 1/R)")
        ax.grid(alpha=0.3)
        ax.legend()
        self.fig2.tight_layout()
        self.canvas2.draw()
