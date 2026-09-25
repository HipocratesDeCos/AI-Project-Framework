# EIOS — Reference Analytical Result Retention: auditoría v0.1

**Base:** `main @ 6e3c6dc9fce16923d67045d9a8573f0906ef9886`.
**Pregunta:** ¿puede el caso sintético mostrar resultados analíticos de negocio
sin inventarlos, repetir motores ni modificar O1?

## DISEÑAR

Separar tres niveles que el producto no debe confundir:

1. Resultado tipado del productor (importe, evaluación, comparación o contenido).
2. `CapabilityExecution` (estado técnico, disponibilidad y trazas para O1).
3. `ReferenceSimulationExecution` (terminal sintético con QTG, procedencia,
   compra/contexto, secuencia y `ExecutionOutcome`).

El objetivo futuro es una observación de lectura de los resultados del nivel
1, vinculada causalmente a la misma ejecución que produjo el nivel 2.

## AUDITAR — puntos de reducción

| Capacidad | Productor público y resultado | Reducción en el invocador existente |
| --- | --- | --- |
| PRICE | `run_price_intelligence` → `PriceIntelligenceResult` (PR, moneda, suficiencia, limitaciones, referencias) | `build_provenanced_price_invoker` → `adapt_price` |
| TCO | `calculate_tco` → `TCOResult` (valor, componentes, incompletitud) | `build_provenanced_tco_invoker` → `adapt_tco`; no conserva trazas en `CapabilityExecution` |
| SUPPLIER_RISK_VALUE | `produce_supplier_risk_value` → `SupplierRiskValueResult` (dimensiones, evidencias, trazas) | `build_provenanced_supplier_risk_value_invoker` → estado y trazas |
| C0 | `run_provenanced_assessments_vertical` → `RuleSetVerticalResult` (assessments, traces, CRC, support) | `build_provenanced_rules_engine_c0_invoker` → `c0_capability` |
| DECISION_TWIN | `build_provenanced_decision_twin_comparison` → `DecisionTwinComparison` (observaciones y diferencias, sin preferencia) | `build_provenanced_decision_twin_invoker` → `adapt_twin` |
| SCENARIO_COORDINATION | `complete_provenanced_o4_o2_o3_orchestration` y `build_o2_support_from_orchestration` → `O2SupportPackage` | `build_provenanced_scenario_coordination_invoker` → `adapt_scenario_coordination` |
| NEGOTIATION_INTELLIGENCE | `produce_negotiation_intelligence` → `NegotiationIntelligenceResult` | `build_c0_bound_ni_ladder_invokers` → `adapt_ni` |
| NEGOTIATION_LADDER | `produce_negotiation_ladder` → `NegotiationLadderResult` | el mismo builder → `adapt_nl` |

QTG es distinto: su resultado funcional sí se conserva en el terminal mediante
el consumo sintético. `CapabilityExecution.result_available=true` no contiene
el resultado del productor; es un indicador de disponibilidad.

## DEPURAR — alternativas descartadas

- **Interpretar las trazas como resultados:** una referencia identifica un
  rastro; no permite recuperar importe, estado de riesgo o comparación.
- **Ejecutar cada productor otra vez para construir la página:** sería otra
  ejecución, sin garantía de ser exactamente la que pasó por O1; en NI/Ladder
  ya hay reproducción interna de NI y no debe añadirse una tercera.
- **Añadir campos arbitrarios a `ExecutionOutcome`:** modifica el contrato
  cerrado y confunde estado técnico con producto analítico.
- **Presentar selección o recomendación desde Twin:** su contrato es
  descriptivo y carece deliberadamente de preferencia o selección.

## AUDITAR 2 — frontera de diseño propuesta

Un futuro contrato **aditivo y exclusivamente de referencia** podría capturar
una copia inmutable del resultado tipado en el punto donde el invocador lo
produce, antes de la reducción al estado técnico. Para cada observación deberá
definir al menos:

- identidad de decisión, escenario, compra/contexto y versión de política;
- tipo y versión del resultado, huella canónica y vínculo con la capacidad
  ejecutada de esa misma corrida;
- huellas de fuente o referencias de evidencia que el productor realmente
  ofrece, sin fabricar trazas faltantes (en particular TCO);
- estado parcial/no evaluable y limitaciones tal como los emitió el productor;
- cierre sintético (`SYNTHETIC_TEST_ONLY`, `FORBIDDEN`, sin efecto ni autoridad).

Primero deberá probarse una única capacidad, preferiblemente PRICE, por tener
resultado tipado con valor, moneda, identidad y trazas. La prueba de concepto
debe demostrar una sola producción, correspondencia exacta entre observación
y `CapabilityExecution`, y rechazo de identidades ajenas. La ampliación al
resto dependerá de sus contratos particulares. Este documento **no aprueba**
una implementación ni declara disponible un informe de negocio E2E.

## CERRAR

La frontera existente es suficiente para ejecutar y auditar estados, pero no
para un informe analítico sustantivo de todas las capacidades. No hay una
contradicción objetiva que exija alterar O1: el siguiente paso consiste en
diseñar un contrato nuevo de observación de referencia antes de materializar.

## MATERIALIZAR / CI

Esta unidad es una auditoría de código y contratos sin cambios runtime. La CI
del PR confirma ausencia de regresiones; una futura implementación necesitará
pruebas de captura causal, procedencia y autoridad propias.
