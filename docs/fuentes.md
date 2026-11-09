# Registro inicial de fuentes
Consulta: **8 de noviembre de 2026**. Este registro distingue material docente, documentación técnica y artículos candidatos. No constituye todavía el estado del arte ni satisface las diez referencias recientes exigidas por la consigna.

## Material docente
- **S25 - Módulo 2. Actividad didáctica 2**: consigna de EA2, en la carpeta externa `MATERIAL COMPLEMENTARIO EA2`.
- **Investiga con IA. Decide con criterio**: origen del caso servidor y de π, A y B del escenario base. La variante persistente, la variante ambigua y el protocolo de réplicas son decisiones de este proyecto. El material no aporta un dataset real ni una estimación empírica de las matrices.

## Referencia técnica consultada
- **Dynamax, módulo de inferencia HMM**, documentación y código oficiales: <https://probml.github.io/dynamax/_modules/dynamax/hidden_markov_model/inference.html>. Se consultó para distinguir filtrado, suavizado y representación de probabilidades logarítmicas. No se incorporó su código al proyecto ni se decidió instalar Dynamax. Es documentación técnica, sin año editorial verificado aquí; no se contabiliza como artículo reciente.

## Documentación de la implementación

- NumPy, **Parallel random number generation**, sección `SeedSequence` spawning: <https://numpy.org/doc/stable/reference/random/parallel.html>. Consultada el 8 de noviembre de 2026 para la generación reproducible de flujos hijos. La independencia de esos flujos es una propiedad probabilística del procedimiento, no una garantía deducida de que dos secuencias concretas difieran. La página estable puede describir una versión posterior; la ejecución local se verificó con NumPy 2.4.3. No cuenta como artículo reciente.
- SciPy, **scipy.stats.t**: <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.t.html>. Consultada para el cuantil t de los intervalos e incorporada mediante SciPy 1.17.1. No cuenta como artículo reciente.
- Matplotlib, **Axes.errorbar**: <https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.errorbar.html>. Documentación oficial consultada para representar medias e intervalos. Las figuras se verificaron con Matplotlib 3.10.8. No cuenta como artículo reciente.

## Artículos candidatos: metadatos y resúmenes verificados
Se abrieron las páginas editoriales originales y se revisaron sus metadatos y resúmenes. **No se ha realizado una lectura completa de los artículos**. Sus resultados no justifican los valores numéricos de nuestro servidor.

| Referencia y enlace original | Pertinencia preliminar | Límite y siguiente revisión |
|---|---|---|
| L. Rimella y N. Whiteley, “Exploiting locality in high-dimensional Factorial hidden Markov models,” *JMLR*, vol. 23, núm. 4, pp. 1–34, 2022. <https://www.jmlr.org/papers/v23/19-267.html> | Inferencia aproximada en HMM factoriales de alta dimensión. | Modelo mucho más complejo que el nuestro; candidato para límites o trabajo futuro, no evidencia directa sobre servidores. Revisar texto completo antes de seleccionar. |
| G. Mahajan, S. Kakade, A. Krishnamurthy y C. Zhang, “Learning Hidden Markov Models Using Conditional Samples,” *PMLR*, vol. 195, pp. 2014–2066, 2023. <https://proceedings.mlr.press/v195/mahajan23a.html> | Aprendizaje de HMM mediante acceso a muestras condicionales. | Nuestra tarea usa parámetros conocidos; podría contextualizar la diferencia con aprendizaje. Revisar texto completo y decidir si merece incluirse. |
| B. Perets, M. Kozdoba y S. Mannor, “Learning Hidden Markov Models When the Locations of Missing Observations are Unknown,” *PMLR*, vol. 202, pp. 27642–27667, 2023. <https://proceedings.mlr.press/v202/perets23a.html> | Tratamiento de observaciones faltantes con posiciones desconocidas. | El experimento actual no contiene faltantes; posible ampliación, sin afirmar que ese método se implementó. Revisar texto completo. |

## Protocolo para completar la bibliografía
Buscar artículos sobre inferencia de estados, incertidumbre de emisiones, monitoreo de sistemas y detección de anomalías mediante HMM. Priorizar fuentes originales accesibles y pertinencia sobre cantidad. Registrar consulta, fecha, autores, año, publicación, enlace o DOI verificado, sección leída, aporte y decisión de inclusión.

Consultas iniciales utilizadas: `hidden Markov models 2022 2023`, `hidden Markov models missing observations`, `Dynamax hidden Markov inference`. La búsqueda inicial recuperó sobre todo trabajos metodológicos; falta reforzar aplicaciones a sistemas informáticos.

Para evitar dudas con publicaciones de principios de 2021, se priorizarán trabajos de **2022–2026** al completar las diez referencias recientes. Los clásicos se identificarán por separado y no sustituirán ese mínimo. No se asignarán números IEEE definitivos hasta decidir el orden de aparición en el artículo.

**Pendientes:** completar la búsqueda, leer las fuentes seleccionadas, descartar candidatos poco pertinentes, incorporar fundamentos clásicos verificados y construir una síntesis crítica vinculada a las decisiones del estudio.