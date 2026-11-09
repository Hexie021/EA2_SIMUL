"""Ejecuta las réplicas del diseño y guarda estadísticas, figuras y trazabilidad."""

import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.stats import t as student

from simulacion import (RAIZ, metricas, regla_sin_memoria, semillas_replicas,
                        simular, validar_modelo, viterbi)

METRICAS = ('exactitud', 'sensibilidad', 'especificidad',
            'exactitud_balanceada', 'proporcion_saturacion')
NOMBRES = {'base': 'Base', 'saturacion_persistente': 'Saturación persistente',
           'observaciones_ambiguas': 'Observaciones ambiguas'}


def resumir(valores, confianza=.95):
    """IC t de la media entre réplicas, omitiendo solo métricas no definidas."""
    if not 0 < confianza < 1:
        raise ValueError('La confianza debe estar entre cero y uno')
    x = np.asarray(valores, dtype=float)
    if x.ndim != 1 or np.any(np.isinf(x)):
        raise ValueError('Se requiere un vector sin valores infinitos')
    x = x[~np.isnan(x)]
    n = len(x)
    salida = dict(n=n, media=None, desviacion=None, minimo=None,
                  maximo=None, ic_inferior=None, ic_superior=None)
    if n:
        salida.update(media=float(x.mean()), minimo=float(x.min()), maximo=float(x.max()))
    if n >= 2:
        s = float(x.std(ddof=1))
        margen = float(student.ppf((1 + confianza) / 2, n - 1) * s / np.sqrt(n))
        salida.update(desviacion=s, ic_inferior=salida['media'] - margen,
                      ic_superior=salida['media'] + margen)
    return salida


def ejecutar(cfg):
    e = cfg['experimento']
    if e['metodo_intervalo'] != 't_student_entre_replicas':
        raise ValueError('Método de intervalo no implementado')
    if not 0 < e['nivel_confianza'] < 1:
        raise ValueError('Nivel de confianza inválido')
    escenarios = cfg['escenarios']
    ids = [s['id'] for s in escenarios]
    if len(ids) != len(set(ids)):
        raise ValueError('Los identificadores deben ser únicos')
    for s in escenarios:
        validar_modelo(s['pi'], s['A'], s['B'])
    hijos = semillas_replicas(e['semilla_maestra'], len(escenarios), e['replicas'])
    filas, resumen, diferencias = [], [], []
    for i, s in enumerate(escenarios):
        inicio = len(filas)
        delta = []
        for r in range(e['replicas']):
            hijo = hijos[i * e['replicas'] + r]
            z, obs = simular(s['pi'], s['A'], s['B'], e['longitud_secuencia'],
                             np.random.default_rng(hijo))
            metodos = [('viterbi', viterbi(obs, s['pi'], s['A'], s['B'])),
                       ('sin_memoria', regla_sin_memoria(obs, s['B']))]
            resultados = {}
            for metodo, pred in metodos:
                m = metricas(z, pred)
                resultados[metodo] = m
                filas.append(dict(escenario=s['id'], replica=r + 1, metodo=metodo,
                                  entropia=hijo.entropy, spawn_key='.'.join(map(str, hijo.spawn_key)),
                                  **m))
            delta.append(resultados['viterbi']['exactitud'] - resultados['sin_memoria']['exactitud'])
        for metodo in ('viterbi', 'sin_memoria'):
            seleccion = [f for f in filas[inicio:] if f['metodo'] == metodo]
            for metrica in METRICAS:
                resumen.append(dict(escenario=s['id'], metodo=metodo, metrica=metrica,
                                    **resumir([f[metrica] for f in seleccion], e['nivel_confianza'])))
        diferencias.append(dict(escenario=s['id'], metrica='delta_exactitud_viterbi_menos_sin_memoria',
                                **resumir(delta, e['nivel_confianza'])))
        print(f"{s['id']}: {e['replicas']} réplicas completas", flush=True)
    return filas, resumen, diferencias


def guardar_csv(ruta, filas):
    with ruta.open('w', encoding='utf-8', newline='') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas[0]))
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({k: '' if isinstance(v, float) and np.isnan(v) else v
                               for k, v in fila.items()})


def figuras(cfg, resumen, salida):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), layout='constrained')
    ids = [s['id'] for s in cfg['escenarios']]
    for ax, metrica, titulo in zip(axes, ['exactitud', 'sensibilidad', 'exactitud_balanceada'],
                                   ['Exactitud', 'Sensibilidad de saturación', 'Exactitud balanceada']):
        for metodo, offset, color, etiqueta in [('viterbi', -.09, '#155e9b', 'Viterbi'),
                                                ('sin_memoria', .09, '#c26818', 'Sin memoria')]:
            datos = [next(r for r in resumen if r['escenario'] == sid and
                          r['metodo'] == metodo and r['metrica'] == metrica) for sid in ids]
            media = np.array([r['media'] for r in datos], dtype=float)
            errores = np.array([[np.nan if r['ic_inferior'] is None else r['media'] - r['ic_inferior'] for r in datos],
                                 [np.nan if r['ic_superior'] is None else r['ic_superior'] - r['media'] for r in datos]])
            ax.errorbar(np.arange(len(ids)) + offset, media, yerr=errores, fmt='o',
                        capsize=4, color=color, label=etiqueta)
        ax.set_xticks(range(len(ids)), [NOMBRES.get(s, s).replace(' ', '\n', 1) for s in ids], fontsize=9)
        ax.set_ylim(-.04, 1.04)
        ax.set_title(titulo, fontsize=11)
        ax.grid(axis='y', alpha=.25)
    axes[0].set_ylabel('Media e intervalo de confianza')
    axes[-1].legend(loc='lower right')
    fig.suptitle(f"Comparación de escenarios · {cfg['experimento']['replicas']} réplicas · IC {cfg['experimento']['nivel_confianza']:.0%}")
    fig.savefig(salida / 'comparacion_escenarios.png', dpi=200)
    plt.close(fig)

    s = cfg['escenarios'][0]
    e = cfg['experimento']
    z, obs = simular(s['pi'], s['A'], s['B'], e['longitud_secuencia'],
                     np.random.default_rng(e['semilla_ejemplo']))
    v = viterbi(obs, s['pi'], s['A'], s['B'])
    simple = regla_sin_memoria(obs, s['B'])
    guardar_csv(salida / 'ejemplo_trayectoria.csv', [dict(instante=i+1, real=int(z[i]),
                observacion=int(obs[i]), viterbi=int(v[i]), sin_memoria=int(simple[i])) for i in range(len(z))])
    n = min(100, len(z))
    x = np.arange(1, n+1)
    fig, axes = plt.subplots(4, 1, figsize=(11, 6.4), sharex=True, layout='constrained')
    for ax, datos, titulo, color in zip(axes, [obs, z, v, simple],
                    ['Respuesta observada', 'Estado real', 'Viterbi', 'Sin memoria'],
                    ['#555555', '#278153', '#155e9b', '#c26818']):
        ax.step(x, datos[:n], where='mid', color=color)
        ax.set_yticks([0, 1], ['Rápida', 'Lenta'] if titulo == 'Respuesta observada' else ['Normal', 'Saturado'])
        ax.set_ylim(-.2, 1.2)
        ax.set_ylabel(titulo, fontsize=9)
        ax.grid(alpha=.2)
    axes[-1].set_xlabel('Instante (una respuesta)')
    fig.suptitle(f"Ejemplo {NOMBRES.get(s['id'], s['id'])} · primeros {n} de {len(z)} instantes · semilla {e['semilla_ejemplo']}")
    fig.savefig(salida / 'trayectoria_ejemplo.png', dpi=200)
    plt.close(fig)


def tabla(resumen, diferencias, salida):
    lineas = ['# Resumen experimental', '',
              'Valores calculados automáticamente. Las métricas se muestran en porcentaje; IC de la media entre réplicas.', '',
              '| Escenario | Método | Exactitud (IC 95 %) | Sensibilidad de saturación | Exactitud balanceada |',
              '|---|---|---:|---:|---:|']
    for sid in dict.fromkeys(r['escenario'] for r in resumen):
        for metodo in ('viterbi', 'sin_memoria'):
            def dato(m):
                return next(r for r in resumen if r['escenario'] == sid and r['metodo'] == metodo and r['metrica'] == m)
            a, se, b = (dato(m) for m in ('exactitud', 'sensibilidad', 'exactitud_balanceada'))
            intervalo = 'no disponible' if a['ic_inferior'] is None else f"{100*a['ic_inferior']:.2f}–{100*a['ic_superior']:.2f}"
            lineas.append(f"| {NOMBRES.get(sid, sid)} | {metodo} | {100*a['media']:.2f} ({intervalo}) | {100*se['media']:.2f} | {100*b['media']:.2f} |")
    lineas += ['', '## Diferencia emparejada de exactitud', '',
               'Viterbi menos regla sin memoria, en puntos porcentuales.', '',
               '| Escenario | Media | IC 95 % |', '|---|---:|---:|']
    for r in diferencias:
        intervalo = 'no disponible' if r['ic_inferior'] is None else f"{100*r['ic_inferior']:.2f}–{100*r['ic_superior']:.2f}"
        lineas.append(f"| {NOMBRES.get(r['escenario'], r['escenario'])} | {100*r['media']:.2f} | {intervalo} |")
    lineas += ['', 'Las estadísticas completas (n, media, desviación muestral, mínimo, máximo e intervalos) están en `resumen.csv`. Las filas con métricas no definidas se excluyen solo de esa métrica; n informa la cantidad válida.', '']
    (salida / 'resumen.md').write_text('\n'.join(lineas), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=RAIZ / 'config/escenarios.json')
    parser.add_argument('--salida', type=Path, default=RAIZ / 'resultados')
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text(encoding='utf-8-sig'))
    if cfg['experimento']['nivel_confianza'] != .95:
        parser.error('La tabla está definida para IC del 95 %')
    filas, resumen, diferencias = ejecutar(cfg)
    args.salida.mkdir(parents=True, exist_ok=True)
    guardar_csv(args.salida / 'metricas_replicas.csv', filas)
    guardar_csv(args.salida / 'resumen.csv', resumen)
    guardar_csv(args.salida / 'diferencias_pareadas.csv', diferencias)
    figuras(cfg, resumen, args.salida)
    tabla(resumen, diferencias, args.salida)
    (args.salida / 'configuracion.json').write_text(json.dumps(cfg, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    archivos = ['simulacion.py', 'experimentos.py', 'requirements.txt', 'config/escenarios.json']
    registro = dict(python=platform.python_version(), plataforma=platform.platform(),
                    numpy=np.__version__, scipy=scipy.__version__, matplotlib=matplotlib.__version__,
                    generador='PCG64', orden_flujos='escenario, réplica',
                    sha256={p: hashlib.sha256((RAIZ / p).read_bytes()).hexdigest() for p in archivos})
    (args.salida / 'entorno.json').write_text(json.dumps(registro, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(f'Resultados guardados en {args.salida}', flush=True)


if __name__ == '__main__':
    main()
