import copy
import json
import unittest

import numpy as np

from experimentos import ejecutar, resumir
from simulacion import RAIZ


class ExperimentoTests(unittest.TestCase):
    def test_intervalo_con_ejemplo_manual(self):
        r = resumir([1, 2, 3])
        self.assertEqual(r['media'], 2)
        self.assertEqual(r['desviacion'], 1)
        self.assertAlmostEqual(r['ic_superior'], 2 + 4.302652729696142 / np.sqrt(3), places=8)
        self.assertEqual((r['n'], r['minimo'], r['maximo']), (3, 1, 3))

    def test_ausentes_constantes_y_muestra_insuficiente(self):
        self.assertEqual(resumir([np.nan, 1, 1])['ic_inferior'], 1)
        self.assertEqual(resumir([np.nan, 1])['n'], 1)
        self.assertIsNone(resumir([1])['desviacion'])
        self.assertIsNone(resumir([np.nan])['media'])
        with self.assertRaises(ValueError):
            resumir([np.inf])

    def test_integracion_flujos_y_diferencias_pareadas(self):
        cfg = json.loads((RAIZ / 'config/escenarios.json').read_text(encoding='utf-8-sig'))
        cfg = copy.deepcopy(cfg)
        cfg['experimento'].update(replicas=3, longitud_secuencia=20)
        filas, resumen, deltas = ejecutar(cfg)
        repetidas, _, _ = ejecutar(cfg)
        self.assertEqual(len(filas), 18)
        self.assertEqual(len(resumen), 30)
        self.assertEqual(len({r['spawn_key'] for r in filas}), 9)
        np.testing.assert_equal([r['exactitud'] for r in filas], [r['exactitud'] for r in repetidas])
        for s, d in zip(cfg['escenarios'], deltas):
            f = [r for r in filas if r['escenario'] == s['id']]
            esperado = np.mean([f[i]['exactitud'] - f[i+1]['exactitud'] for i in range(0, 6, 2)])
            self.assertAlmostEqual(d['media'], esperado)
            for i in range(0, 6, 2):
                self.assertEqual(f[i]['spawn_key'], f[i+1]['spawn_key'])
                self.assertEqual(sum(f[i][k] for k in ('tp','tn','fp','fn')), 20)


if __name__ == '__main__':
    unittest.main()
