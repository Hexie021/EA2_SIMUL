# Resumen experimental

Valores calculados automáticamente. Las métricas se muestran en porcentaje; IC de la media entre réplicas.

| Escenario | Método | Exactitud (IC 95 %) | Sensibilidad de saturación | Exactitud balanceada |
|---|---|---:|---:|---:|
| Base | viterbi | 86.95 (86.73–87.17) | 60.51 | 78.24 |
| Base | sin_memoria | 83.76 (83.59–83.92) | 79.94 | 82.50 |
| Saturación persistente | viterbi | 89.16 (88.92–89.41) | 90.36 | 89.07 |
| Saturación persistente | sin_memoria | 82.50 (82.32–82.67) | 79.94 | 82.50 |
| Observaciones ambiguas | viterbi | 75.11 (74.73–75.49) | 0.00 | 50.00 |
| Observaciones ambiguas | sin_memoria | 60.01 (59.78–60.23) | 59.75 | 59.92 |

## Diferencia emparejada de exactitud

Viterbi menos regla sin memoria, en puntos porcentuales.

| Escenario | Media | IC 95 % |
|---|---:|---:|
| Base | 3.19 | 2.99–3.39 |
| Saturación persistente | 6.67 | 6.45–6.88 |
| Observaciones ambiguas | 15.11 | 14.67–15.54 |

Las estadísticas completas (n, media, desviación muestral, mínimo, máximo e intervalos) están en `resumen.csv`. Las filas con métricas no definidas se excluyen solo de esa métrica; n informa la cantidad válida.