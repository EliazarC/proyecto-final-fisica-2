# Simulador de Física 2 – Electricidad y Magnetismo

Programa único con las unidades 1, 2 y 3 (pestañas).

## Ejecutar
    pip install -r requirements.txt
    python main.py

## Pruebas
    python -m tests.test_fisica

## Estructura
    main.py              Ventana principal (una pestaña por unidad, carga perezosa)
    nucleo/              Física pura, sin interfaz (testeable)
        campo.py            U1: campo y potencial de cargas puntuales
        trayectoria.py      U1: partícula cargada (SciPy solve_ivp)
        capacitores.py      U2: capacitancia, dieléctricos, energía
        circuitos.py        U3: serie / paralelo / mixto, Ley de Ohm
    interfaz/            Tkinter + Matplotlib
        unidad1.py  unidad2.py  unidad3.py  graficos_campo.py
    tests/test_fisica.py Validación numérica de las tres unidades

## Agregar la Unidad 4
Crear interfaz/unidad4.py con una clase `ttk.Frame` y añadirla a la lista UNIDADES de main.py.

## Crear el .exe (Windows)
    pip install pyinstaller
    pyinstaller simulador_fisica2.spec
