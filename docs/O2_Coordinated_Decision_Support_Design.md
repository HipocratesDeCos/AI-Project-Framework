# EIOS — O2 Coordinated Decision Support / Scenario Orchestration

**Estado:** DISEÑAR — cerrado para auditoría
**Base:** `038c03c9a641ea870bd9dc400220722338140efe`
**Naturaleza:** evolución funcional sobre O1; no constituye una nueva fase.

## 1. Propósito

O2 extiende el sobre de orquestación O1 para coordinar escenarios de una misma operación de compra sin crear un motor autónomo de decisión.

O2 organiza, identifica y mantiene separados los resultados por escenario y permite consolidar información comparable para soporte a la decisión humana.

## 2. Alcance

O2 recibe una operación y uno o más escenarios explícitamente identificados. Para cada escenario reutiliza capacidades existentes dentro de su perímetro contractual: C0, PRICE, TCO, QTG, Decision Versioning, Decision Twin y capacidades de negociación cuando sean aplicables.

O2 no recalcula ni sustituye dichas capacidades.

## 3. Invariantes

- O2-01 Identity: un `decision_id` identifica la decisión y cada escenario mantiene un `scenario_id` estable.
- O2-02 Isolation: resultados, evidencias, estados y trazas permanecen asociados a su escenario.
- O2-03 Versioning: reglas, parámetros y snapshot quedan fijados por ejecución/escenario.
- O2-04 No authority: O2 no aprueba, rechaza, recomienda ni selecciona una alternativa.
- O2-05 No mutation: la operación de compra de entrada no se modifica silenciosamente.
- O2-06 Traceability: cada resultado material conserva referencias a su contexto de ejecución.
- O2-07 Determinism: identidad y referencias reproducibles para entradas y versiones materiales equivalentes.
- O2-08 Explicit degradation: escenario no ejecutable, no evaluable o fallido conserva su estado explícito.
- O2-09 Comparison boundary: la comparación entre escenarios describe diferencias; no produce ranking ni preferencia empresarial.
- O2-10 Human boundary: el paquete final es soporte estructurado; la decisión permanece humana.

## 4. Estados de escenario

`READY → RUNNING → COMPLETED`

Salidas controladas: `BLOCKED`, `PARTIALLY_COMPLETED`, `NOT_EVALUABLE`, `FAILED`.

Reglas obligatorias:

`NOT_EXECUTED ≠ FALSE`

`NOT_EVALUABLE ≠ FALSE`

`FAILED ≠ NEGATIVE BUSINESS RESULT`

## 5. Modelo conceptual

```text
O2 Input
  ├── PurchaseOperation
  ├── DecisionContext
  ├── Scenario[]
  └── execution/version context
          │
          ▼
   O1 orchestration envelope
          │
          ├── Scenario A → existing capabilities → results/traces
          ├── Scenario B → existing capabilities → results/traces
          └── Scenario N → existing capabilities → results/traces
          │
          ▼
   Scenario comparison information
          │
          ▼
   Structured Decision Support Package
          │
          ▼
      HUMAN DECISION
```

## 6. Comparación

La comparación O2 puede exponer atributos, diferencias, disponibilidad de resultados, unresolved items y trazabilidad por escenario.

Queda expresamente fuera del contrato: score global, ranking, optimización, selección automática, recomendación empresarial o aprobación/rechazo.

## 7. Criterio de cierre

O2 podrá pasar a AUDITAR únicamente si su materialización conserva estos límites, reutiliza O1 y las capacidades existentes, y dispone de pruebas contractuales que demuestren aislamiento de escenarios, versionado, degradación explícita, trazabilidad y ausencia de autoridad decisoria.
