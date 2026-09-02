# O1 — Contrato de Orquestación Operacional MVP

**Estado:** 🔒 CERRADO — diseño funcional
**Baseline:** `7734abbe59eefc6badd754c2c7774c0ee6662f09`
**Tipo:** incremento funcional; no constituye una nueva fase.

## 1. Propósito

O1 coordina capacidades MVP existentes para una operación de compra y construye un paquete estructurado de soporte a la decisión. O1 no sustituye, modifica ni absorbe la autoridad de C0, PRICE, TCO, QTG, Decision Twin, Decision Versioning, Negotiation Intelligence o Negotiation Ladder.

## 2. Frontera

```text
PurchaseOperation + DecisionContext + entradas autorizadas
                         |
                         v
                  O1 Execution Context
                         |
        +----------------+----------------+
        |        |       |       |        |
       C0      PRICE    TCO     QTG    Twin/NI/NL
        |        |       |       |        |
        +----------------+----------------+
                         |
                         v
              Decision Support Package
                         |
                         v
                    HUMAN DECISION
```

La salida de O1 es soporte estructurado. `COMPLETED` significa ejecución completa del perímetro contractual, no aprobación de compra.

## 3. Contexto común

Toda ejecución O1 conserva:

- `execution_id`
- `decision_id`
- `scenario_id`
- `rules_version`
- `parameters_version`
- `data_snapshot_id`

`execution_id` identifica la ejecución del orquestador. Las trazas internas continúan perteneciendo a cada capacidad.

## 4. Estados

Estados normales:

`READY → RUNNING → COMPLETED`

Estados controlados:

`BLOCKED`, `PARTIALLY_COMPLETED`, `NOT_EVALUABLE`, `FAILED`.

Invariantes:

- `NOT_EXECUTED ≠ FALSE`
- `NOT_EVALUABLE ≠ FALSE`
- `FAILED ≠ resultado empresarial negativo`
- ausencia de resultado no autoriza una conclusión empresarial.

## 5. Invariantes O1

- **O1-01 Identidad:** una ejecución conserva un `decision_id` y `scenario_id` coherentes.
- **O1-02 Versionado:** se preservan las versiones del contexto; O1 no crea un versionado paralelo.
- **O1-03 Evidencia:** insuficiencia de evidencia permanece explícita.
- **O1-04 Autoridad:** O1 no aprueba, rechaza, compra, ejecuta ni selecciona por cuenta propia.
- **O1-05 No mutación:** la operación y los resultados de capacidades no se modifican silenciosamente.
- **O1-06 Trazabilidad:** cada resultado material conserva referencias de traza.
- **O1-07 Determinismo:** la identidad material del contexto es reproducible para las mismas entradas/versiones.
- **O1-08 Degradación explícita:** una capacidad no ejecutable queda registrada como tal.
- **O1-09 Separación semántica:** estado técnico, assessment, recommendation y human decision son conceptos distintos.

## 6. Salida mínima

```text
DecisionSupportPackage
├── execution_context
├── execution_status
├── capability_results
├── evidence_status
├── version_context
├── trace_references
└── unresolved_items
```

El paquete puede contener resultados de C0, PRICE, TCO, QTG, Twin y negociación cuando estén disponibles. No inventa resultados ausentes.

## 7. Regla de cierre

Este contrato queda cerrado para su materialización inicial. Cualquier ampliación que cambie autoridad, identidad, versionado o semántica de decisión deberá tratarse como cambio de alcance versionado y no como corrección silenciosa de O1.
