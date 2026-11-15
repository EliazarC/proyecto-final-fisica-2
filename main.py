"""Simulador interactivo de Física 2 – Electricidad y Magnetismo.
Ejecutar:  python main.py

Para agregar una unidad nueva (p. ej. la Unidad 4): crea interfaz/unidad4.py con una
clase ttk.Frame y añádela a la lista UNIDADES de abajo."""
import tkinter as tk
from tkinter import ttk

from interfaz.unidad1 import Unidad1
from interfaz.unidad2 import Unidad2
from interfaz.unidad3 import Unidad3

UNIDADES = [
    ("Unidad 1 · Campo eléctrico y potencial", Unidad1),
    ("Unidad 2 · Capacitores y dieléctricos", Unidad2),
    ("Unidad 3 · Corriente y Ley de Ohm", Unidad3),
]


class Principal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Física 2 – Campos eléctricos, capacitores y circuitos")
        self.geometry("1250x800")
        self.minsize(1000, 650)
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)
        self._marcos = []            # (marco contenedor, clase, instancia o None)
        for titulo, clase in UNIDADES:
            marco = ttk.Frame(self.nb)
            self.nb.add(marco, text=titulo)
            self._marcos.append([marco, clase, None])
        self.nb.bind("<<NotebookTabChanged>>", self._crear_pestana)
        self._crear_pestana()        # construye la primera unidad al abrir

    def _crear_pestana(self, _evento=None):
        """Construye cada unidad solo la primera vez que se abre (arranque rápido)."""
        i = self.nb.index(self.nb.select())
        marco, clase, inst = self._marcos[i]
        if inst is None:
            self._marcos[i][2] = clase(marco)
            self._marcos[i][2].pack(fill="both", expand=True)


if __name__ == "__main__":
    try:                              # nitidez en pantallas HiDPI de Windows
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    Principal().mainloop()
