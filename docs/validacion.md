# Validación de la implementación
Fecha: 8 de noviembre de 2026. Entorno utilizado: Windows, Python 3.14.3, NumPy 2.4.3. No se requirieron instalaciones durante esta comprobación.

## Ejecución realizada
Desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
python simulacion.py --escenario base
python simulacion.py --escenario saturacion_persistente
python simulacion.py --escenario observaciones_ambiguas
```

**Resultado:** nueve pruebas correctas y tres ejemplos ejecutados sin errores. La instalación en un entorno nuevo no se ha probado; se utilizó NumPy ya disponible con la versión fijada en `requirements.txt`.

## Qué comprueban las pruebas
1. Viterbi recupera una trayectoria con probabilidad conjunta máxima frente a enumeración exhaustiva: 16 secuencias observadas por cada uno de los tres modelos, evaluando los 16 caminos de estados de longitud cuatro para cada caso.
2. Emisiones deterministas permiten recuperar la trayectoria y verificar que la primera observación corresponde al primer estado, sin transición previa.
3. Las probabilidades cero se admiten y una secuencia imposible produce un error explícito.
4. Los empates eligen el menor índice en Viterbi y en la regla sin memoria.
5. La matriz de confusión y las métricas coinciden con un ejemplo calculable a mano.
6. Una clase ausente produce métricas no definidas, sin reemplazarlas por cero.
7. La misma semilla reproduce estados y observaciones; hay 600 claves hijas distintas y dos flujos de ejemplo producen secuencias distintas. Esto comprueba la gestión de semillas, no demuestra independencia estadística universal.
8. Se rechazan probabilidades inválidas, dimensiones incompatibles, observaciones fuera de rango y longitudes incorrectas.
9. La comparación sin memoria aplica rápida → normal y lenta → saturado en los tres escenarios actuales.

## Alcance de los ejemplos
Cada ejemplo utiliza T=1000 y semilla 42. Esa semilla está reservada a la ilustración, separada del protocolo de réplicas experimentales. Reutilizarla en los ejemplos no implica que los futuros escenarios experimentales deban compartir flujos.

En el ejemplo ambiguo, Viterbi clasificó todos los instantes como normales. Esto permite observar una limitación relevante: una exactitud global relativamente elevada puede coexistir con sensibilidad de saturación nula. Es una observación de una sola secuencia, no una conclusión general sobre el desempeño.

## Validación del experimento completo

Se incorporó `tests/test_experimentos.py`. La suite completa tiene **12 pruebas correctas**: las nueve iniciales y tres adicionales que comprueban el intervalo t con un caso calculable a mano, el manejo de valores ausentes y muestras insuficientes, y la integración de réplicas, semillas y diferencias emparejadas.

Se ejecutó `python experimentos.py` con SciPy 1.17.1 y Matplotlib 3.10.8, además del entorno indicado arriba: 600 secuencias de 1000 instantes, evaluadas con dos métodos, para 1200 filas de métricas. Las dos figuras se inspeccionaron visualmente.

La tabla, CSV y análisis están enlazados desde el README. No se ha entrenado el modelo ni validado su uso con datos de un servidor real.

Se repitieron las 600 simulaciones con la misma configuración y se compararon byte a byte los CSV de métricas, resumen y diferencias: los tres coincidieron. También se comprobaron 600 claves hijas distintas, suma 1000 en cada matriz de confusión y 200 valores válidos en cada uno de los 30 resúmenes. Esta comprobación de reproducción corresponde al entorno y versiones registrados.