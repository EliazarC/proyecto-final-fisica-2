import unittest

import numpy as np

from nucleo.magnetismo import campo_alambre, campo_iman, simular_lorentz


class MagnetismoTest(unittest.TestCase):
    def test_alambre(self):
        np.testing.assert_allclose(campo_alambre(1., 0., 5.), (0, 1e-6))
        np.testing.assert_allclose(campo_alambre(2., 0., -5.), (0, -0.5e-6))

    def test_iman(self):
        x = np.array([-1.1, 0, 1.1])
        y = np.array([0, 1, 0])
        b = np.asarray(campo_iman(x, y))
        self.assertTrue(np.all(b[0] * [-1, 1, -1] > 0))
        np.testing.assert_allclose(campo_iman(x, y, False), -b)

    def test_orbita_circular(self):
        _, r, v = simular_lorentz(1, 1, (1, 0, 0), (0, 0, 0), (0, 0, 3), 2*np.pi/3)
        np.testing.assert_allclose(np.linalg.norm(v, axis=0), 1, atol=1e-7)
        np.testing.assert_allclose(r[:, -1], 0, atol=1e-7)
        np.testing.assert_allclose(np.hypot(r[0], r[1]+1/3), 1/3, atol=1e-7)

    def test_deriva_en_campos_cruzados(self):
        t, r, _ = simular_lorentz(1, 1, (2.8, 0, 0), (0, 3, 0), (0, 0, 3), 2*np.pi/3)
        np.testing.assert_allclose(r[:, -1], (t[-1], 0, 0), atol=1e-7)

    def test_masa_invalida(self):
        with self.assertRaises(ValueError):
            simular_lorentz(1, 0, (1, 0, 0), (0, 0, 0), (0, 0, 3), 1)
