# Planteamiento del problema

## 1. Contexto
En un sistema informático, el tiempo de respuesta ofrece una señal sobre su funcionamiento, pero no identifica de manera inequívoca la condición interna del servidor. Una respuesta lenta puede aparecer en un estado normal y una respuesta rápida puede ocurrir durante un estado de saturación.

Para estudiar esta incertidumbre, se construirá un caso didáctico con dos estados ocultos (normal y saturado) y dos observaciones (rápida y lenta). Los estados y las observaciones serán generados mediante simulación. No se dispone de mediciones de un servidor real.

El caso parte del laboratorio docente *Investiga con IA. Decide con criterio*, incluido en el material complementario de EA2. Sus parámetros son ilustrativos; no constituyen estimaciones empíricas.

## 2. Problema y pregunta central
Se quiere determinar qué tan bien puede reconstruirse la secuencia de condiciones internas del servidor a partir de respuestas observadas cuando existen cambios de estado y señales ambiguas.

**Pregunta central:** ¿cómo afectan las probabilidades de transición y de emisión de un HMM a la recuperación de los estados normal y saturado en secuencias simuladas de respuestas rápidas y lentas?

## 3. Objetivo general
Evaluar la recuperación de estados ocultos de un servidor mediante un HMM con parámetros conocidos, comparando tres escenarios simulados y documentando su reproducibilidad.

## 4. Objetivos específicos
1. Definir los estados, observaciones, distribución inicial y matrices de transición y emisión, con sus supuestos y significado.
2. Generar secuencias de estados y respuestas e implementar su decodificación mediante Viterbi.
3. Comparar un escenario base, uno con mayor persistencia de saturación y otro con observaciones menos informativas.
4. Medir el desempeño entre repeticiones y reportar media, desviación estándar, mínimo, máximo e intervalos de confianza.
5. Conservar parámetros, semillas, versiones e instrucciones para reproducir los experimentos.

## 5. Preguntas orientadoras
| Pregunta | Evidencia prevista |
|---|---|
| P1. ¿Cómo representa el HMM el problema? | Definición de estados, observaciones, π, A y B; explicación de los supuestos. |
| P2. ¿Cómo influyen sus parámetros en la recuperación de estados? | Comparación de tres escenarios controlados, con métricas y figuras. |
| P3. ¿Qué tan reproducibles y sensibles son los resultados? | Repeticiones con semillas registradas, estadísticas e intervalos de confianza; variaciones de parámetros explicitadas. |

## 6. Justificación del modelo
Un HMM permite representar una condición interna no observada directamente y señales que dependen probabilísticamente de esa condición. La evolución temporal se modelará suponiendo que el siguiente estado depende del estado actual y que la observación depende del estado de ese instante.

Estos supuestos simplifican el problema. El modelo no describirá las causas físicas de una saturación ni sustituirá un diagnóstico operativo de un servidor real.

## 7. Alcance y diseño inicial
- **Estados ocultos:** normal y saturado.
- **Observaciones:** respuesta rápida y respuesta lenta, tratadas como categorías generadas directamente. No se fijará un umbral de latencia real sin datos que lo justifiquen.
- **Datos:** secuencias sintéticas; los estados generados se conservarán como referencia para evaluar las inferencias.
- **Inferencia:** Viterbi con parámetros conocidos para reconstruir una secuencia completa. Se trata de decodificación retrospectiva, no de detección en tiempo real.
- **Comparación sencilla propuesta:** clasificar cada respuesta por su probabilidad de emisión, sin usar la dependencia temporal, con la misma regla en todos los escenarios.
- **Métrica principal propuesta:** proporción de estados recuperados correctamente. Se complementará con medidas por estado, como sensibilidad para saturación, para identificar efectos del desequilibrio entre clases.
- **Repeticiones:** se resumirán métricas por réplica; los intervalos se calcularán entre réplicas independientes, sin tratar los instantes correlacionados como observaciones independientes.

### Escenarios previstos
| Escenario | Cambio frente al base | Propósito |
|---|---|---|
| Base | Parámetros didácticos de referencia por documentar. | Establecer una comparación inicial. |
| Mayor persistencia de saturación | Aumentar la probabilidad de permanecer saturado, ajustando su fila en A para conservar suma uno; mantener B y π del caso base. | Estudiar el efecto de las transiciones, incluida la variación de la frecuencia de saturación. |
| Observaciones menos informativas | Acercar las distribuciones de emisión de ambos estados; mantener A y π del caso base. | Estudiar el efecto de la ambigüedad de las respuestas. |

El tamaño de las secuencias, número de réplicas, semillas, matrices definitivas, métricas complementarias y método de intervalo de confianza se fijarán y justificarán en el diseño antes de ejecutar los experimentos. Las diferencias entre escenarios no se presentarán como conclusiones hasta contar con resultados.

## 8. Límites
No se entrenarán parámetros con Baum-Welch en el alcance inicial. Tampoco se implementará un servidor real, una prueba de carga, un modelo de colas ni predicción de fallos. El desempeño obtenido con datos sintéticos y parámetros conocidos no implica igual desempeño con datos reales o parámetros estimados.

## 9. Evidencias previstas y siguientes pasos
Se prepararán código ejecutable, comprobaciones del modelo, configuración de escenarios, resultados por réplica, al menos una tabla y dos figuras. El artículo integrará metodología, resultados, discusión, conclusiones y referencias verificadas. El video mostrará el problema y una demostración coherente con la implementación.

El siguiente avance documentará el modelo y sus parámetros, el diseño experimental y la búsqueda de fuentes académicas. Se verificará que las referencias recientes cumplan el período exigido por la consigna antes de incorporarlas al artículo.

**Estado de este documento!** planteamiento inicial. No contiene resultados experimentales ni afirma que las propuestas de evaluación ya hayan sido implementadas.