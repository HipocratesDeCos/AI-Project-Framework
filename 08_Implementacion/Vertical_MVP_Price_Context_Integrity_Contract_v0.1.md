# EIOS — Vertical MVP Price Context Integrity Contract v0.1

**Estado:** CERRADO PARA MATERIALIZACIÓN  
**Baseline:** `main @ c3d6042139e0a50ba835e9bc7cc4b29cbaee7c23`  
**Ámbito:** composición de resultados Price Intelligence preproducidos dentro de `run_mvp_execution`.

## 1. Propósito

Cerrar un hueco de integridad contextual en la composición Vertical MVP sin modificar la autoridad ni la metodología de Price Intelligence.

`PriceIntelligenceResult` es un resultado analítico ya producido. Su incorporación a una ejecución Vertical no autoriza a reinterpretar su identidad ni a asociarlo a un `DecisionContext` distinto.

## 2. Autoridad existente

Este contrato deriva exclusivamente de autoridades ya cerradas:

- `Price_Intelligence_Implementation_Contract.md`: C1 reutiliza las identidades canónicas de `DecisionContext`; su salida conserva `decision_id`, `scenario_id` y `data_snapshot_id`.
- `E2E_Execution_Boundary_Implementation_Contract.md`: la ejecución recibe contexto canónico y debe rechazar identidad inconsistente antes de ejecutar capacidades.
- `eios/core/models.py`: `DecisionContext` define `decision_id`, `scenario_id`, `rules_version`, `parameters_version` y `data_snapshot_id`.

No se crea identidad nueva ni se amplía ningún contrato upstream.

## 3. Regla cerrada

Cuando `run_mvp_execution` recibe `price_result`, antes de crear el snapshot/invocador de PRICE debe verificar igualdad exacta de:

```text
price_result.decision_id      == context.decision_id
price_result.scenario_id      == context.scenario_id
price_result.data_snapshot_id == context.data_snapshot_id
```

Una desigualdad en cualquiera de estos campos es una inconsistencia estructural de identidad y debe producir `ValueError` antes de iniciar el plan.

## 4. Límites

La validación:

- no recalcula Price Intelligence;
- no revalida evidencia;
- no interpreta `pr_status`, suficiencia, representatividad o valor económico;
- no compara `rules_version` ni `parameters_version`, porque `PriceIntelligenceResult` no transporta esos campos;
- no crea `decision_version`, fingerprint ni identidad paralela;
- no convierte el error técnico/estructural en decisión empresarial;
- no modifica `PriceIntelligenceResult`, `DecisionContext` ni `PurchaseOperation`.

## 5. Orden fail-closed

La inconsistencia se detecta durante la construcción del catálogo de ejecución y antes de `execute_plan`. Por tanto, ninguna capacidad puede ejecutarse parcialmente bajo un Price perteneciente a otro contexto.

## 6. Auditoría 1

Hallazgo confirmado: `run_mvp_execution` ya valida `SCENARIO_COORDINATION`, pero Price era snapshoteado y adaptado sin comprobar su identidad contra el `DecisionContext` actual.

No existe contradicción con el contrato Price ni con E2E; la validación materializa una obligación ya declarada.

## 7. Depuración

Se descartan ampliaciones no autorizadas:

- TCO queda fuera de esta unidad porque su contrato Core no fija `data_snapshot_id` en el resultado.
- QTG y Decision Twin quedan fuera porque sus resultados actuales no transportan identidad contextual suficiente para esta comparación.
- NI/Ladder se auditarán en unidades posteriores conforme a sus propias referencias de contexto.

La unidad queda reducida exclusivamente a Price.

## 8. Criterios de aceptación

1. Price con las tres identidades coincidentes se ejecuta sin regresión.
2. `decision_id` distinto se rechaza antes de ejecutar.
3. `scenario_id` distinto se rechaza antes de ejecutar.
4. `data_snapshot_id` distinto se rechaza antes de ejecutar.
5. El mensaje identifica los campos incompatibles.
6. La validación no muta resultado ni contexto.
7. No se añade autoridad decisional ni semántica Price.

## 9. Materialización prevista

```text
eios/core/mvp_execution.py
tests/test_mvp_price_context_integrity.py
```

## 10. Método

**DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI**
