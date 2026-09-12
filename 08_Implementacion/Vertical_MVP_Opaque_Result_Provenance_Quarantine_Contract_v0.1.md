# EIOS — Vertical MVP Opaque Result Provenance Quarantine Contract v0.1

**Estado:** 🔒 CERRADO EN RAMA — AUDITORÍA 2 SUPERADA — MATERIALIZADO — INTEGRACIÓN PENDIENTE DE CI

## 1. Propósito

Eliminar de las fronteras públicas del Vertical MVP la posibilidad de incorporar resultados analíticos opacos de QTG y Decision Twin como si pertenecieran al `PurchaseOperation` / `DecisionContext` de la ejecución actual cuando esos resultados no transportan evidencia suficiente para demostrarlo.

Esta unidad corrige una frontera de composición. No modifica la semántica de QTG, Decision Twin, O1, C0, CRC, Price, TCO, Scenario Coordination, NI ni Ladder.

## 2. Hallazgo objetivo

En el baseline `main @ 4810d80f5490dcb9407fe34d552d82d223e02297`:

- `run_mvp_execution(...)` aceptaba `quality_result: QualityTrustResult` y `decision_twin_result: DecisionTwinComparison` ya producidos;
- ambos se convertían mediante `_snapshot_invoker(...)` en capacidades de la ejecución actual;
- `_snapshot_invoker(...)` ignoraba los `PurchaseOperation` y `DecisionContext` recibidos por el boundary;
- `QualityTrustResult` no conserva identidad decisional, escenario, versiones, snapshot ni fingerprint de entrada;
- `DecisionTwinComparison` tampoco conserva identidad decisional/contextual suficiente y sus `trace_refs` son referencias opacas no resolubles por esta frontera;
- además, Decision Twin puede comparar alternativas pertenecientes a escenarios distintos, por lo que forzar un único `scenario_id` del `DecisionContext` sobre sus alternativas sería semánticamente incorrecto.

Consecuencia: el servicio podía re-etiquetar un resultado QTG/Decision Twin desprendido de su procedencia como si perteneciera al contexto de ejecución actual.

## 3. Fronteras que se preservan

1. No se añaden campos de identidad a `QualityTrustResult`.
2. No se añaden campos de identidad a `DecisionTwinComparison`.
3. No se exige que las alternativas de Decision Twin compartan el `context.scenario_id`.
4. No se interpreta `trace_refs` como prueba contextual si esta frontera no puede resolverlas.
5. No se crea ningún nuevo estado de negocio, ranking, recomendación o decisión.
6. No se cambia la semántica de `NOT_EVALUABLE`, `FAILED`, `PARTIALLY_COMPLETED` ni del boundary E2E.
7. No se reabre U1.1 ni se conecta el frontend visual estático al runtime.

## 4. Diseño autorizado

### 4.1 Servicio core

`run_mvp_execution(...)` deja de aceptar resultados crudos:

- `quality_result`
- `decision_twin_result`

En su lugar acepta invocadores explícitos compatibles con `CapabilityInvoker`:

- `quality_invoker: CapabilityInvoker | None`
- `decision_twin_invoker: CapabilityInvoker | None`

Si están presentes, se incorporan directamente al catálogo de ejecución:

- `QTG` → `quality_invoker`
- `DECISION_TWIN` → `decision_twin_invoker`

El servicio no snapshoteará ni adaptará internamente resultados QTG/Decision Twin preproducidos.

### 4.2 Fachada pública

`run_vertical_mvp_support(...)` aplica la misma frontera:

- elimina `quality_result` y `decision_twin_result`;
- acepta `quality_invoker` y `decision_twin_invoker`;
- los reenvía sin transformar a `run_mvp_execution(...)`.

La fachada tampoco vuelve a crear un snapshot invoker de esos resultados.

### 4.3 Alcance de la garantía

Un invocador explícito **no constituye por sí solo una certificación de procedencia**.

Esta unidad garantiza algo más estrecho y verificable: las capas de composición Vertical MVP dejan de fabricar procedencia aparente mediante re-etiquetado de resultados opacos. La construcción de invocadores QTG/Decision Twin realmente provenance-safe, a partir de material verificable, corresponde a unidades específicas posteriores.

## 5. Compatibilidad y migración

El cambio de firma es intencionadamente fail-closed. Mantener los parámetros crudos como alias silenciosos conservaría exactamente la contradicción que esta unidad elimina.

Los consumidores físicos identificados en el repositorio son:

- `eios/core/mvp_execution.py`;
- `eios/mvp.py`;
- tests de ambas fronteras.

La unidad actualiza conjuntamente estos consumidores. No se crea una ruta legacy que permita re-etiquetar QTG/Decision Twin.

## 6. Orden y ejecución

Se conserva `MVP_CAPABILITY_ORDER` sin cambios:

`QTG → PRICE → TCO → C0 → DECISION_TWIN → SCENARIO_COORDINATION → NEGOTIATION_INTELLIGENCE → NEGOTIATION_LADDER`.

La ejecución continúa delegándose en `execute_plan(...)`. Errores técnicos de los invocadores siguen siendo gestionados por la semántica técnica ya autorizada del boundary; no se convierten en rechazo de negocio.

## 7. Pruebas materializadas

La implementación demuestra en tests dedicados:

1. QTG por invocador conserva su posición canónica.
2. Decision Twin por invocador conserva su posición canónica.
3. Ambos invocadores reciben el `PurchaseOperation` y `DecisionContext` de la ejecución actual.
4. La fachada `run_vertical_mvp_support(...)` reenvía los invocadores sin snapshotear resultados opacos.
5. La ausencia de esos invocadores sigue siendo válida si existe al menos otra capacidad.
6. Una ejecución sin ninguna capacidad sigue fallando cerrada.
7. No existe en las firmas públicas migradas `quality_result` ni `decision_twin_result`.
8. No se alteran los modelos QTG/Decision Twin.
9. No se introducen campos de decisión, recomendación o ranking.
10. La suite completa Python + SQL queda como gate obligatorio de CI.

## 8. Auditoría 2

**Resultado: SUPERADA — SIN BLOQUEADORES DE DISEÑO O MATERIALIZACIÓN.**

Comparación contra `main @ 4810d80f5490dcb9407fe34d552d82d223e02297` antes del cierre documental:

- rama exclusivamente por delante del baseline;
- 5 artefactos físicos afectados: este contrato, dos fronteras productivas y dos archivos de tests;
- ningún modelo QTG o Decision Twin modificado;
- ningún adaptador de capacidad modificado;
- ningún cambio de autoridad decisional o semántica de negocio;
- `MVP_CAPABILITY_ORDER` intacto;
- las firmas públicas ya no contienen `quality_result` ni `decision_twin_result`;
- los invocadores QTG/Decision Twin reciben el contexto real del boundary;
- la semántica multi-escenario de Decision Twin permanece intacta;
- no se presenta el invocador como certificado de procedencia: únicamente se elimina la re-etiquetación opaca realizada por estas capas.

El rebuild o validación provenance-safe de QTG y Decision Twin queda fuera de esta unidad y requerirá contrato específico antes de añadir productores de invocadores.

## 9. Cierre e integración

El diseño, Auditoría 1, depuración, Auditoría 2 y materialización quedan cerrados en la rama.

**Este estado no autoriza a declarar la unidad integrada en `main`.** La integración solo quedará cerrada cuando se cumplan todos los gates siguientes:

- CI Python + SQL del head exacto del PR en verde;
- reconciliación de `main` inmediatamente antes del merge;
- merge del head exacto que superó CI;
- reconciliación postintegración;
- CI post-merge sobre el SHA exacto de `main` en verde.
