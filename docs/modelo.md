# Modelo HMM y diseño experimental

Este documento fija el diseño previo a la implementación. Los valores son hipotéticos; no se han estimado de un servidor real. La configuración ejecutable se conserva en [config/escenarios.json](../config/escenarios.json).

## 1. Notación y supuestos
Se usará el orden de estados **normal = 0, saturado = 1** y de observaciones **rápida = 0, lenta = 1**. Cada instante representa una respuesta; no equivale a segundos ni a una tasa real de peticiones.

- Z_t: estado oculto en el instante t.
- O_t: respuesta observada en ese instante.
- π_i = P(Z_1 = i): distribución del primer estado.
- A_ij = P(Z_(t+1) = j | Z_t = i): fila de origen y columna de destino.
- B_ik = P(O_t = k | Z_t = i): fila del estado y columna de la respuesta.

π y cada fila de A y B deben tener entradas entre cero y uno y sumar uno. Las matrices se mantienen constantes dentro de cada escenario. El siguiente estado depende del actual; la observación depende del estado de su instante y es condicionalmente independiente de las demás observaciones dados los estados.

La probabilidad conjunta de una trayectoria es:

`P(z_1:T, o_1:T) = π[z_1] B[z_1,o_1] ∏(t=2..T) A[z_(t-1),z_t] B[z_t,o_t]`.

Primero se genera Z_1 con π y se emite O_1 con B. Después se alternan transición y emisión hasta completar T instantes. No se hace una transición adicional antes de la primera observación.

## 2. Escenario base
Se toman del caso docente *Investiga con IA. Decide con criterio* los siguientes parámetros ilustrativos:

`π = [0.80, 0.20]`

| A: origen → destino | Normal | Saturado |
|---|---:|---:|
| Normal | 0.90 | 0.10 |
| Saturado | 0.30 | 0.70 |

| B: estado → observación | Rápida | Lenta |
|---|---:|---:|
| Normal | 0.85 | 0.15 |
| Saturado | 0.20 | 0.80 |

Por ejemplo, un servidor normal tiene probabilidad 0.10 de pasar a saturado y probabilidad 0.15 de producir una respuesta lenta. El estado saturado también puede producir una respuesta rápida, con probabilidad 0.20. Esta superposición hace incierta la inferencia.

## 3. Variantes controladas

### Saturación persistente
Se conserva π y B. Se sustituye únicamente la fila saturado de A por `[0.10, 0.90]`. La salida de saturación resulta menos probable.

Como consecuencia matemática del diseño, la duración media de una racha saturada pasa de `1/(1−0.70) ≈ 3.33` a `1/(1−0.90) = 10` instantes. La probabilidad estacionaria de saturación pasa de `0.10/(0.10+0.30) = 0.25` a `0.10/(0.10+0.10) = 0.50`. Estas son propiedades teóricas, no resultados experimentales; la distribución inicial sigue siendo π y no es la estacionaria.

El cambio combina mayor persistencia y mayor presencia de saturación. No se atribuirán las diferencias de exactitud exclusivamente a una de ellas. Se reportarán también métricas por estado y proporción real de saturación.

### Observaciones ambiguas
Se conserva π y A. Se sustituye B por `[[0.60, 0.40], [0.40, 0.60]]`. Ambos estados pueden producir ambas respuestas con probabilidades más parecidas. Esto reduce la separación de las emisiones por construcción; su efecto sobre la recuperación se medirá mediante los experimentos.

## 4. Decodificación y comparación
Viterbi reconstruirá la secuencia conjunta de estados más probable dadas todas las respuestas y los parámetros del escenario. Se implementará con logaritmos para evitar el subdesbordamiento de productos largos:

```text
δ_1(j) = log π_j + log B[j,o_1]
δ_t(j) = log B[j,o_t] + max_i(δ_(t−1)(i) + log A[i,j])
```

Se guardará el predecesor que maximiza cada paso y se reconstruirá la trayectoria hacia atrás. Los empates se resolverán eligiendo el menor índice. Una probabilidad cero se representará por menos infinito; una observación imposible bajo todo el modelo deberá producir un error explícito.

Se comparará con una regla sin memoria: `estado = argmax_i B[i,o_t]`, con empate a favor del menor índice. En los tres escenarios actuales esto equivale a rápida → normal y lenta → saturado. Es un clasificador por máxima emisión, sin prior; no se lo presentará como posterior Bayesiano ni como el mejor competidor posible.

Ambos métodos reciben exactamente la misma secuencia observada en cada réplica. Los estados verdaderos se usan únicamente para evaluar. No hay entrenamiento ni ajuste a las etiquetas de prueba. Viterbi usa información futura de la secuencia y no representa un detector en tiempo real; además, maximizar la probabilidad conjunta no garantiza maximizar la exactitud por instante.

## 5. Protocolo fijado antes de experimentar
Se usarán **200 réplicas de 1000 instantes por escenario**, con semilla maestra **20261108**. Estas cantidades son una decisión de escala del ejercicio, no una garantía de precisión estadística. Se conservará el transitorio inicial de π, sin descarte de calentamiento, porque el objetivo incluye reconstruir secuencias desde esa condición inicial.

Se generarán 600 flujos pseudoaleatorios hijos mediante `numpy.random.SeedSequence(20261108).spawn(600)`: primero las 200 réplicas del escenario base, después saturación persistente y finalmente observaciones ambiguas. Cada réplica usará su propio `default_rng` y se registrarán la entropía y `spawn_key`. No se reiniciará la misma semilla en cada réplica. La secuencia ilustrativa tendrá un generador separado con semilla 42; no se mezclará con el resumen experimental.

Las comparaciones Viterbi/regla simple estarán emparejadas dentro de una réplica. Los escenarios tendrán flujos distintos; no se asumirán comparaciones emparejadas entre escenarios.

### Métricas por réplica
Considerando saturado como clase positiva:

- Exactitud: `(TP + TN) / T`.
- Sensibilidad de saturación: `TP / (TP + FN)`.
- Especificidad de normal: `TN / (TN + FP)`.
- Exactitud balanceada: media de sensibilidad y especificidad.
- Proporción real de saturación: cantidad de estados saturados / T.
- Diferencia emparejada de exactitud: exactitud de Viterbi menos exactitud de la regla simple.

Si una clase no aparece en una réplica, la métrica que dependa de ella será no definida, se guardará como valor ausente y se informará el número de réplicas válidas. No se reemplazará por cero.

### Resumen estadístico
Para cada escenario, método y métrica se reportarán cantidad válida, media, desviación estándar muestral (divisor n−1), mínimo, máximo e IC del 95 % de la media:

`media ± t_(0.975,n−1) × s/√n`.

La unidad estadística será la réplica, no cada instante correlacionado. El intervalo t es aproximado para estas métricas acotadas y no se recortarán sus extremos para ocultar esa limitación. Con menos de dos valores válidos se omitirá el intervalo. También se resumirá la diferencia emparejada entre métodos; si su intervalo incluye cero no se afirmará una mejora concluyente.

## 6. Evidencias y validaciones previstas
Se guardarán las métricas por réplica y su resumen en CSV, configuración utilizada y versiones de Python y dependencias. Se producirán al menos una tabla de comparación y dos figuras: trayectoria real/inferida del ejemplo con observaciones, y comparación de desempeño por escenario con intervalos.

Antes de experimentar se comprobarán: dimensiones y sumas de probabilidades; alineación de estados y observaciones; Viterbi contra enumeración exhaustiva en secuencias pequeñas; casos de emisiones deterministas; métricas con ejemplos calculables a mano; repetibilidad con idéntica configuración y diversidad de los flujos hijos.

**Estado:** diseño implementado y ejecutado. Las evidencias están en `resultados/` y su interpretación en [resultados.md](resultados.md). Los valores teóricos anteriores se distinguen de las estimaciones simuladas.