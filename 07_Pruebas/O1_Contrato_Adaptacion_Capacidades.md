# O1 — Contrato de Adaptación de Capacidades

## Estado

**DISEÑADO — pendiente de materialización técnica**

## Propósito

Definir la traducción operacional, sin alterar autoridad, de resultados ya ejecutados por capacidades existentes a `CapabilityExecution` de O1.

## Principio

El adaptador **no ejecuta capacidades, no recalcula resultados y no interpreta resultados de negocio**. Únicamente normaliza estado, disponibilidad, trazas y elementos no resueltos para el envelope O1.

## Mapeo normativo mínimo

| Capacidad | Resultado de origen | Estado O1 |
|---|---|---|
| C0 | `Assessment` + `Trace` | `COMPLETED` si todas las evaluaciones son `EVALUABLE`; `NOT_EVALUABLE` si el conjunto no es evaluable |
| PRICE | `PriceIntelligenceResult` | `COMPLETED` para `PR_AVAILABLE`/`PR_LIMITED`; `NOT_EVALUABLE` para `PR_NOT_JUSTIFIABLE` |
| TCO | `TCOResult` | `COMPLETED` si `complete`; `PARTIALLY_COMPLETED` si quedan componentes no resueltos |
| QTG | `QualityTrustResult` | `COMPLETED`; `NO_APTO` y advertencias son resultado de calidad, no fallo de ejecución |

## Reglas

1. `FALSE` de C0 nunca se transforma en `FAILED`.
2. `NOT_EVALUABLE` nunca se transforma en `FALSE` ni en `FAILED`.
3. `PR_NOT_JUSTIFIABLE` nunca se transforma en `FAILED`.
4. TCO incompleto conserva sus `unresolved_components`.
5. QTG `NO_APTO` conserva su semántica de calidad y no se clasifica como fallo técnico.
6. Las trazas se propagan sin modificación cuando el resultado de origen dispone de trazas O1 compatibles.
7. QTG no dispone de `Trace` propio en `QualityTrustResult`: sus `evidence_refs` son referencias de evidencia del control y **no se relabelizan como `trace_references` O1**.
8. Los adaptadores no crean `decision_id`, `scenario_id`, versiones ni snapshots: los toma el `O1ExecutionContext`.
9. Ningún adaptador produce una decisión, recomendación, ranking, aprobación o rechazo empresarial.

## Perímetro

Este contrato cubre exclusivamente la adaptación de resultados existentes hacia O1. La ejecución secuencial/paralela de capacidades queda fuera de este contrato y requiere un alcance posterior explícito.

## Criterio de cierre

El contrato se considera materializable cuando cada adaptación definida tenga una función determinista y pruebas de conservación semántica, especialmente para `NOT_EVALUABLE`, resultados negativos de negocio, resultados parciales y `NO_APTO`.
