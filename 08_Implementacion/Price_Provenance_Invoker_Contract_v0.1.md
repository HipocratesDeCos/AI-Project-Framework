# EIOS — Price Provenance Invoker Contract v0.1

## Estado

DISEÑADO → AUDITADO → DEPURADO. Pendiente de materialización, Auditoría 2 y CI.

## 1. Propósito

Cerrar la frontera de reutilización de Price Intelligence en el Vertical MVP sin aceptar un `PriceIntelligenceResult` desprendido cuya identidad parcial pueda ser re-etiquetada dentro de otra compra o contexto.

Esta unidad no modifica la metodología cerrada de Price Intelligence ni el modelo físico de `PriceIntelligenceResult`.

## 2. Contradicción objetiva

`PriceIntelligenceInput` conserva `DecisionContext`, `PurchaseOperation`, referencias, validaciones de evidencia, base de normalización, evidencia de base económica y `methodology_version`.

`PriceIntelligenceResult` conserva `decision_id`, `scenario_id`, `data_snapshot_id` y `methodology_version`, pero no permite demostrar por sí solo qué `PurchaseOperation` ni qué conjunto completo de entrada produjo el resultado.

La frontera Vertical actual solo contrasta una parte de la identidad del resultado. Por tanto, dos operaciones distintas con igual `decision_id`, `scenario_id` y `data_snapshot_id` podrían reutilizar el mismo resultado sin prueba de procedencia.

## 3. Entrada autorizada de reutilización

La frontera provenance-safe debe congelar conjuntamente:

- `PriceIntelligenceInput`;
- `PriceIntelligenceAssessmentContext`.

No se acepta como frontera reusable:

- `PriceIntelligenceResult` ya producido;
- un resultado con IDs coincidentes sin su input de origen;
- una reconstrucción parcial de referencias, evidencia, bases o contexto metodológico.

## 4. Validación en cada ejecución

El invocador público tendrá forma:

`(PurchaseOperation, DecisionContext) -> CapabilityExecution`.

Antes de ejecutar PRICE debe exigir igualdad exacta entre el contexto actual y `payload.decision_context` en:

- `decision_id`;
- `scenario_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`.

También debe exigir igualdad exacta entre el `PurchaseOperation` actual y `payload.purchase_operation`, incluyendo todos sus campos físicos.

No se permite sustituir solo `decision_id`/`scenario_id`, ni aceptar una compra con artículo, proveedor, cantidad, precio, moneda o fecha distintos.

## 5. Ejecución

Tras validar identidad completa, el invocador debe ejecutar el motor cerrado:

`run_price_intelligence(payload, assessment_context)`

sobre copias profundas congeladas y adaptar el resultado mediante `adapt_price(...)`.

El invocador no altera referencias, evidencia, normalización, temporalidad, representatividad, suficiencia, agregación ni metodología.

## 6. Snapshot e inmutabilidad

La construcción del invocador debe copiar profundamente `PriceIntelligenceInput` y `PriceIntelligenceAssessmentContext`.

Mutaciones posteriores del llamador no pueden modificar la ejecución futura.

## 7. Migración Vertical

`run_mvp_execution` y `run_vertical_mvp_support` deben dejar de aceptar `price_result` y pasar a aceptar `price_invoker`.

No habrá fallback compatible que envuelva un `PriceIntelligenceResult` desprendido.

La posición canónica de PRICE en O1 permanece intacta.

## 8. Semántica preservada

Esta unidad no:

- modifica `PriceIntelligenceResult`;
- añade nuevas identidades o fingerprints a C1;
- modifica C0, QTG, TCO o Decision Twin;
- convierte `PR_NOT_JUSTIFIABLE` en rechazo empresarial;
- introduce score, ranking, fallback, pesos o heurísticas;
- cambia `adapt_price` ni la metodología PRICE.

## 9. Fail closed

Debe fallar antes de ejecutar PRICE cuando:

- cualquier campo de `DecisionContext` sea distinto del congelado;
- cualquier campo de `PurchaseOperation` sea distinto del congelado;
- el payload o assessment context no sean los tipos físicos autorizados.

## 10. Criterio de cierre

La unidad solo se considera integrada cuando:

1. implementación y tests respetan este contrato;
2. Auditoría 2 no detecta rutas de resultado PRICE opaco en las dos fronteras públicas;
3. CI de PR es satisfactoria sobre el head exacto;
4. se integra ese mismo head;
5. CI post-merge es satisfactoria.
