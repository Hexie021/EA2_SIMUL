# EA2 · Simulación de un servidor con un modelo oculto de Markov

**Curso:** Simulación · IU Digital de Antioquia  
**Autor:** Esteban Jaramillo Garro

En esta actividad estudiaré un servidor que puede encontrarse en dos estados internos: normal o saturado. Las señales observables serán respuestas rápidas o lentas. El propósito es evaluar cómo un modelo oculto de Markov (HMM) permite reconstruir los estados a partir de esas respuestas.

Trabajaré con datos simulados y parámetros hipotéticos. Una respuesta lenta no demuestra por sí sola que un servidor real esté saturado; este proyecto es un ejercicio académico para estudiar esa incertidumbre.

## Estado del proyecto

Primer avance: planteamiento del problema y organización del repositorio. Todavía no hay código de simulación ni resultados experimentales.

## Preguntas del estudio

1. ¿Cómo representar la condición del servidor y sus respuestas mediante un HMM?
2. ¿Cómo cambia la recuperación de los estados al modificar las transiciones o la capacidad informativa de las observaciones?
3. ¿Qué tan reproducibles y variables son los resultados entre repeticiones con semillas registradas?

El detalle está en [docs/planteamiento.md](docs/planteamiento.md).

## Organización actual

```text
EA2_/
├── .gitattributes
├── .gitignore
├── README.md
└── docs/
    └── planteamiento.md
```

## Ruta de trabajo

1. Definir el problema, objetivos y alcance.
2. Documentar el modelo, las fuentes verificadas y tres escenarios comparables.
3. Implementar la simulación y la inferencia con Viterbi; comprobar su funcionamiento.
4. Ejecutar experimentos, guardar evidencias y analizar resultados.
5. Completar la documentación, el artículo y el video de la actividad.

Las instrucciones de ejecución y las dependencias se añadirán cuando exista una implementación comprobada.

## Evidencias y entregables

El repositorio reunirá código, parámetros, dependencias, documentación técnica y evidencias de resultados. El artículo y el video se prepararán por separado. No se incluirán copias completas del material docente ni archivos temporales.

Cada avance corresponderá a un cambio real y revisado. Los commits y push los realizará el autor.

## Material de partida

El caso se adapta del laboratorio docente **Investiga con IA. Decide con criterio**, disponible en el material complementario de EA2. La consigna de referencia es **S25 - Módulo 2. Actividad didáctica 2**. Las fuentes académicas se documentarán después de verificar su contenido y pertinencia; este avance no presenta una revisión bibliográfica ya terminada.