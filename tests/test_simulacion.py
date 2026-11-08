"""Comprobaciones contra soluciones exactas y ejemplos calculables a mano."""

import itertools
import json
import unittest

import numpy as np

from simulacion import (RAIZ, metricas, regla_sin_memoria, semillas_replicas,
                        simular, validar_modelo, viterbi)


class ModeloTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = json.loads((RAIZ / 'config/escenarios.json').read_text(encoding='utf-8-sig'))
        cls.s = cls.cfg['escenarios'][0]

    def test_viterbi_contra_enumeracion_exhaustiva(self):
        # Todos los caminos de estados y observaciones de longitud 4, tres modelos.
        for s in self.cfg['escenarios']:
            pi, A, B = validar_modelo(s['pi'], s['A'], s['B'])
            for observaciones in itertools.product(range(2), repeat=4):
                def prob(camino):
                    p = pi[camino[0]] * B[camino[0], observaciones[0]]
                    for t in range(1, 4):
                        p *= A[camino[t-1], camino[t]] * B[camino[t], observaciones[t]]
                    return p
                maxima = max(prob(c) for c in itertools.product(range(2), repeat=4))
                obtenido = viterbi(observaciones, pi, A, B)
                self.assertAlmostEqual(prob(obtenido), maxima, places=14)

    def test_emision_determinista_y_alineacion_inicial(self):
        pi, A, B = [0, 1], [[0, 1], [1, 0]], np.eye(2)
        z, o = simular(pi, A, B, 5, np.random.default_rng(7))
        np.testing.assert_array_equal(z, [1, 0, 1, 0, 1])
        np.testing.assert_array_equal(o, z)
        np.testing.assert_array_equal(viterbi(o, pi, A, B), z)

    def test_probabilidades_cero_e_imposibilidad(self):
        with self.assertRaises(ValueError):
            viterbi([0, 1], [1, 0], np.eye(2), np.eye(2))
        np.testing.assert_array_equal(viterbi([0], [1, 0], np.eye(2), np.eye(2)), [0])

    def test_empates(self):
        np.testing.assert_array_equal(viterbi([0, 1, 0], [.5, .5],
                                     np.full((2, 2), .5), np.full((2, 2), .5)), [0, 0, 0])
        np.testing.assert_array_equal(regla_sin_memoria([0, 1], np.full((2, 2), .5)), [0, 0])

    def test_metricas_manuales(self):
        m = metricas([0, 0, 1, 1], [0, 1, 1, 1])
        self.assertEqual((m['tp'], m['tn'], m['fp'], m['fn']), (2, 1, 1, 0))
        self.assertEqual(m['exactitud'], .75)
        self.assertEqual(m['sensibilidad'], 1)
        self.assertEqual(m['especificidad'], .5)
        self.assertEqual(m['exactitud_balanceada'], .75)
        self.assertEqual(m['proporcion_saturacion'], .5)

    def test_ausencia_de_clase(self):
        m = metricas([0, 0], [0, 0])
        self.assertTrue(np.isnan(m['sensibilidad']))
        self.assertTrue(np.isnan(m['exactitud_balanceada']))
        self.assertEqual(m['exactitud'], 1)

    def test_reproducibilidad_y_flujos_distintos(self):
        a = semillas_replicas(20261108, 3, 200)
        b = semillas_replicas(20261108, 3, 200)
        self.assertEqual(len({x.spawn_key for x in a}), 600)
        for i in (0, 199, 200, 599):
            np.testing.assert_array_equal(a[i].generate_state(4), b[i].generate_state(4))
        pi, A, B = (self.s[k] for k in ('pi', 'A', 'B'))
        z1, o1 = simular(pi, A, B, 100, np.random.default_rng(a[0]))
        z2, o2 = simular(pi, A, B, 100, np.random.default_rng(b[0]))
        np.testing.assert_array_equal(z1, z2)
        np.testing.assert_array_equal(o1, o2)
        z3, o3 = simular(pi, A, B, 100, np.random.default_rng(a[1]))
        self.assertFalse(np.array_equal(z1, z3) and np.array_equal(o1, o3))

    def test_entradas_invalidas(self):
        for pi in ([.4, .4], [-.1, 1.1], [float('nan'), 0]):
            with self.assertRaises(ValueError):
                validar_modelo(pi, np.eye(2), np.eye(2))
        with self.assertRaises(ValueError):
            validar_modelo([1, 0], [[1, 0]], np.eye(2))
        for obs in ([], [2], [-1], [0.5], [[0]]):
            with self.assertRaises(ValueError):
                viterbi(obs, [1, 0], np.eye(2), np.eye(2))
        with self.assertRaises(ValueError):
            simular([1, 0], np.eye(2), np.eye(2), 0, np.random.default_rng(0))
        with self.assertRaises(ValueError):
            metricas([0], [0, 1])

    def test_regla_sin_memoria(self):
        for s in self.cfg['escenarios']:
            np.testing.assert_array_equal(regla_sin_memoria([0, 1, 1, 0], s['B']), [0, 1, 1, 0])


if __name__ == '__main__':
    unittest.main()
