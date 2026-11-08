"""Simulación y decodificación de un HMM discreto con parámetros conocidos."""

import argparse
import json
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent


def validar_modelo(pi, A, B):
    """Devuelve matrices válidas; A usa filas de origen y B filas de estado."""
    pi, A, B = (np.asarray(x, dtype=float) for x in (pi, A, B))
    if pi.ndim != 1 or not pi.size:
        raise ValueError('pi debe ser un vector no vacío')
    n = pi.size
    if A.shape != (n, n) or B.ndim != 2 or B.shape[0] != n or B.shape[1] == 0:
        raise ValueError('Dimensiones incompatibles de pi, A y B')
    for nombre, matriz in [('pi', pi), ('A', A), ('B', B)]:
        if not np.all(np.isfinite(matriz)) or np.any(matriz < 0) or np.any(matriz > 1):
            raise ValueError(f'{nombre}: probabilidades inválidas')
        if not np.allclose(matriz.sum(axis=-1), 1, rtol=0, atol=1e-12):
            raise ValueError(f'{nombre}: las probabilidades deben sumar uno')
    return pi, A, B


def _secuencia(valores, limite):
    valores = np.asarray(valores)
    if valores.ndim != 1 or valores.size == 0 or valores.dtype.kind not in 'iu':
        raise ValueError('Se requiere una secuencia no vacía de índices enteros')
    if np.any(valores < 0) or np.any(valores >= limite):
        raise ValueError('Índice fuera del alfabeto permitido')
    return valores


def simular(pi, A, B, longitud, rng):
    """Emite después de elegir cada estado; rng pertenece a una sola réplica."""
    pi, A, B = validar_modelo(pi, A, B)
    if isinstance(longitud, bool) or not isinstance(longitud, (int, np.integer)) or longitud < 1:
        raise ValueError('La longitud debe ser un entero positivo')
    estados = np.empty(longitud, dtype=int)
    observaciones = np.empty(longitud, dtype=int)
    estados[0] = rng.choice(len(pi), p=pi)
    observaciones[0] = rng.choice(B.shape[1], p=B[estados[0]])
    for t in range(1, longitud):
        estados[t] = rng.choice(len(pi), p=A[estados[t - 1]])
        observaciones[t] = rng.choice(B.shape[1], p=B[estados[t]])
    return estados, observaciones


def viterbi(observaciones, pi, A, B):
    """Devuelve trayectoria MAP conjunta; los empates eligen el menor índice."""
    pi, A, B = validar_modelo(pi, A, B)
    obs = _secuencia(observaciones, B.shape[1])
    with np.errstate(divide='ignore'):
        log_pi, log_A, log_B = (np.log(x) for x in (pi, A, B))
    anterior = log_pi + log_B[:, obs[0]]
    predecesores = np.zeros((len(obs), len(pi)), dtype=int)
    for t in range(1, len(obs)):
        candidatos = anterior[:, None] + log_A
        predecesores[t] = np.argmax(candidatos, axis=0)
        anterior = candidatos[predecesores[t], np.arange(len(pi))] + log_B[:, obs[t]]
    if not np.any(np.isfinite(anterior)):
        raise ValueError('La secuencia observada es imposible bajo este modelo')
    trayectoria = np.empty(len(obs), dtype=int)
    trayectoria[-1] = np.argmax(anterior)
    for t in range(len(obs) - 1, 0, -1):
        trayectoria[t - 1] = predecesores[t, trayectoria[t]]
    return trayectoria


def regla_sin_memoria(observaciones, B):
    """Máxima emisión, sin prior ni uso de observaciones vecinas."""
    B = np.asarray(B, dtype=float)
    if B.ndim != 2 or min(B.shape) == 0:
        raise ValueError('B debe ser una matriz no vacía')
    validar_modelo(np.full(B.shape[0], 1 / B.shape[0]), np.eye(B.shape[0]), B)
    obs = _secuencia(observaciones, B.shape[1])
    if np.any(B[:, obs].max(axis=0) == 0):
        raise ValueError('Observación imposible en B')
    return np.argmax(B[:, obs], axis=0)


def metricas(reales, inferidos):
    """Métricas binarias: saturado=1. Ausencia de clase produce NaN."""
    reales = _secuencia(reales, 2)
    inferidos = _secuencia(inferidos, 2)
    if reales.shape != inferidos.shape:
        raise ValueError('Las secuencias deben tener igual longitud')
    tp = int(np.sum((reales == 1) & (inferidos == 1)))
    tn = int(np.sum((reales == 0) & (inferidos == 0)))
    fp = int(np.sum((reales == 0) & (inferidos == 1)))
    fn = int(np.sum((reales == 1) & (inferidos == 0)))
    sensibilidad = tp / (tp + fn) if tp + fn else float('nan')
    especificidad = tn / (tn + fp) if tn + fp else float('nan')
    return {
        'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
        'exactitud': (tp + tn) / len(reales),
        'sensibilidad': sensibilidad,
        'especificidad': especificidad,
        'exactitud_balanceada': (sensibilidad + especificidad) / 2,
        'proporcion_saturacion': float(np.mean(reales == 1)),
    }


def semillas_replicas(semilla_maestra, numero_escenarios, replicas):
    """Orden: escenario primero y después réplica; no reutiliza semillas hijas."""
    for valor in (numero_escenarios, replicas):
        if isinstance(valor, bool) or not isinstance(valor, int) or valor < 1:
            raise ValueError('Escenarios y réplicas deben ser enteros positivos')
    return np.random.SeedSequence(semilla_maestra).spawn(numero_escenarios * replicas)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=RAIZ / 'config' / 'escenarios.json')
    parser.add_argument('--escenario', default='base')
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text(encoding='utf-8-sig'))
    opciones = {s['id']: s for s in cfg['escenarios']}
    if args.escenario not in opciones:
        parser.error('Escenario desconocido. Opciones: ' + ', '.join(opciones))
    s = opciones[args.escenario]
    e = cfg['experimento']
    reales, obs = simular(s['pi'], s['A'], s['B'], e['longitud_secuencia'],
                          np.random.default_rng(e['semilla_ejemplo']))
    print(f"Ejemplo: {s['id']}, T={len(obs)}, semilla={e['semilla_ejemplo']}")
    print('Primeras 30 observaciones:', obs[:30].tolist())
    print('Primeros 30 estados reales:', reales[:30].tolist())
    for nombre, pred in [('Viterbi', viterbi(obs, s['pi'], s['A'], s['B'])),
                         ('Sin memoria', regla_sin_memoria(obs, s['B']))]:
        print(nombre, metricas(reales, pred))
    print('Ejemplo ilustrativo; no sustituye las 200 réplicas por escenario.')


if __name__ == '__main__':
    main()