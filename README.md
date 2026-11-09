# EA2 · Simulación de un servidor con un modelo oculto de Markov

**Curso:** Simulación · IU Digital de Antioquia  
**Autor:** Esteban Jaramillo Garro

En esta actividad estudiaré un servidor que puede encontrarse en dos estados internos: normal o saturado. Las señales observables serán respuestas rápidas o lentas. El propósito es evaluar cómo un modelo oculto de Markov (HMM) permite reconstruir los estados a partir de esas respuestas.

Trabajaré con datos simulados y parámetros hipotéticos. Una respuesta lenta no demuestra por sí sola que un servidor real esté saturado; este proyecto es un ejercicio académico para estudiar esa incertidumbre.

La implementación genera estados y respuestas, reconstruye los estados con Viterbi y compara sus métricas con una regla sin memoria. Incluye tres escenarios: base, saturación persistente y observaciones ambiguas.

El [planteamiento](docs/planteamiento.md) describe los objetivos y el alcance. El [modelo](docs/modelo.md) define las matrices y el protocolo de evaluación. Las referencias se registran en [fuentes](docs/fuentes.md).

## Organización
```text
EA2_/
├── .gitattributes
├── .gitignore
├── README.md
├── requirements.txt
├── simulacion.py
├── experimentos.py
├── tests/
│   ├── test_simulacion.py
│   └── test_experimentos.py
├── config/
│   └── escenarios.json
├── resultados/
│   └── CSV, resumen, configuración, entorno y dos figuras
└── docs/
    ├── planteamiento.md
    ├── modelo.md
    ├── fuentes.md
    ├── validacion.md
    └── resultados.md
```

## Cómo ejecutar
Abre una terminal en la carpeta del repositorio. Se comprobó con Python 3.14.3, NumPy 2.4.3, SciPy 1.17.1 y Matplotlib 3.10.8. Para instalar las dependencias en un entorno propio:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Ejecuta las pruebas y un ejemplo:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe simulacion.py --escenario base
```

También puedes seleccionar `saturacion_persistente` u `observaciones_ambiguas`. Si tu entorno ya tiene las dependencias, puedes usar `python` directamente. El ejemplo lee la configuración, usa su semilla ilustrativa y muestra las métricas de ambos métodos. No genera archivos ni representa el experimento completo.

Las comprobaciones y sus límites se describen en [docs/validacion.md](docs/validacion.md).

## Experimento y resultados

Para ejecutar las 200 réplicas de 1000 respuestas de cada uno de los tres escenarios:

```powershell
.\.venv\Scripts\python.exe experimentos.py
```

El programa guarda o reemplaza sus archivos en `resultados/`: métricas por réplica, estadísticas e intervalos del 95 %, diferencias entre métodos, dos figuras, configuración y versiones del entorno. Para conservar otra ejecución utiliza `--salida otra_carpeta`.

Consulta la [tabla de resultados](resultados/resumen.md) y su [análisis](docs/resultados.md). Las figuras muestran la [comparación de escenarios](resultados/comparacion_escenarios.png) y una [trayectoria ilustrativa](resultados/trayectoria_ejemplo.png).

## Material de partida
El caso y los parámetros base se adaptan del laboratorio docente **Investiga con IA. Decide con criterio**, incluido en el material complementario de EA2 del curso de Simulación.