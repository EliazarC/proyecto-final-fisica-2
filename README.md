# Simulador de Física 2 – Electricidad y Magnetismo

Programa único con las unidades 1 a 4 (pestañas).

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
        magnetismo.py       U4: campos magnéticos y fuerza de Lorentz
    interfaz/            Tkinter + Matplotlib
        unidad1.py  unidad2.py  unidad3.py  unidad4.py  graficos_campo.py
    tests/test_fisica.py Validación numérica de las unidades 1 a 3
    tests/test_magnetismo.py Validación numérica de la Unidad 4

## Unidad 4 — Fuerza y campo magnético
- El imán de barra abre por defecto. Usa **Girar imán** para invertir los polos y las flechas.
- El alambre recto representa un conductor ideal infinito en el eje z. Cambia la corriente y su sentido y usa **Dibujar**.
- En **Fuerza de Lorentz** puedes cargar campos cruzados u órbita circular y modificar los parámetros en unidades SI.
- Ejecuta `python -m unittest tests.test_magnetismo` para comprobar los cálculos de la Unidad 4.

## Crear el .exe (Windows)
    pip install pyinstaller
    pyinstaller simulador_fisica2.spec
