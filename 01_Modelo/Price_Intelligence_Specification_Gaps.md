# EIOS — Price Intelligence — Specification Gaps

## Estado

Gaps metodológicos pendientes tras el cierre de la semántica económica de PR. Los puntos de esta lista no deben resolverse por inferencia desde parámetros, reglas o implementación.

## Cerrado

- Unidad económica de PR: **B — precio de transacción comparable normalizado**.
- PR no equivale a TCO, PO, PMR ni PPV.
- "Reciente" para `R-PRE-001`: `P-PRE-001` (3 meses, valor inicial).
- Representatividad: enfoque criterial y explicable; no se introduce `representativeness_score` en el MVP.
- Representatividad y suficiencia son conceptos independientes.
- Ponderación: capacidad opcional; no se introducen pesos no autorizados.
- Outlier no equivale automáticamente a error ni implica exclusión.
- Contradicción no equivale automáticamente a outlier y no se resuelve mediante heurística implícita.

## Pendiente de metodología

1. Criterios concretos de representatividad.
2. Reglas concretas de normalización: unidad, cantidad, moneda, descuentos, rappels, transporte, impuestos y demás condiciones económicas.
3. Suficiencia operativa y tratamiento de una única referencia (`N=1`).
4. Selección concreta cuando existen múltiples referencias.
5. Tratamiento de contradicciones.
6. Tratamiento de outliers.
7. Ponderación concreta, si se determina necesaria para algún caso.
8. Método de agregación final de PR.

## Invariante

Ninguno de los puntos pendientes puede cerrarse mediante una inferencia implícita desde datos disponibles, parámetros existentes o comportamiento de la implementación. Cada decisión metodológica debe quedar respaldada por autoridad documental explícita y ser trazable hasta su contrato técnico.
