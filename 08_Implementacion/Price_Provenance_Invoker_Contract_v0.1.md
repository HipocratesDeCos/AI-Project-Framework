# EIOS — Price Provenance Invoker Contract v0.1

## Estado

DISEÑADO → AUDITADO → DEPURADO → AUDITORÍA 2 SUPERADA → MATERIALIZADO. Pendiente de CI e integración.

## 1. Propósito

Cerrar la frontera de reutilización de Price Intelligence en el Vertical MVP sin aceptar un `PriceIntelligenceResult` desprendido cuya identidad parcial pueda ser re-etiquetada dentro de otra compra o contexto.

Esta unidad no modifica la metodología cerrada de Price Intelligence ni el modelo físico de `PriceIntelligenceResult`.

## 2. Contradicción objetiva

`PriceIntelligenceInput` conserva `DecisionContext`, `PurchaseOperation`, referencias, validaciones de evidencia, base de normalización, evidencia de base económica y `methodology_version`.

`PriceIntelligenceResult` conserva `decision_id`, `scenario_id`, `data_snapshot_id` y `methodology_version`, pero no permite demostrar por sí solo qué `PurchaseOperation` ni qué conjunto completo de entrada produjo el resultado.

La frontera Vertical previa solo contrastaba una parte de la identidad del resultado. Por tanto, dos operaciones distintas con igual `decision_id`, `scenario_id` y `data_snapshot_id` podían reutilizar el mismo resultado sin prueba de procedencia.

## 3. Entrada autorizada de reutilización

La frontera provenance-safe congela conjuntamente:

- `PriceIntelligenceInput`;
- `PriceIntelligenceAssessmentContext`.

No se acepta como frontera reusable:

- `PriceIntelligenceResult` ya producido;
- un resultado con IDs coincidentes sin su input de origen;
- una reconstrucción parcial de referencias, evidencia, bases o contexto metodológico.

## 4. Validación en cada ejecución

El invocador público tiene forma:

`(PurchaseOperation, DecisionContext) -> CapabilityExecution`.

Antes de ejecutar PRICE exige igualdad exacta entre el contexto actual y `payload.decision_context` en:

- `decision_id`;
- `scenario_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`.

También exige igualdad exacta entre el `PurchaseOperation` actual y `payload.purchase_operation`, incluyendo todos sus campos físicos.

No se permite sustituir solo `decision_id`/`scenario_id`, ni aceptar una compra con artículo, proveedor, cantidad, precio, moneda o fecha distintos.

## 5. Ejecución

Tras validar identidad completa, el invocador ejecuta el motor cerrado:

`run_price_intelligence(payload, assessment_context)`

sobre copias profundas congeladas y adapta el resultado mediante `adapt_price(...)`.

El invocador no altera referencias, evidencia, normalización, temporalidad, representatividad, suficiencia, agregación ni metodología.

La garantía de esta frontera es de procedencia de ejecución respecto del input PRICE congelado: no pretende certificar externamente la veracidad de cada fuente; esa autoridad permanece en los contratos especializados aguas arriba.

## 6. Snapshot e inmutabilidad

La construcción del invocador copia profundamente `PriceIntelligenceInput` y `PriceIntelligenceAssessmentContext`.

Mutaciones posteriores del llamador no pueden modificar la ejecución futura.

## 7. Migración Vertical

`run_mvp_execution` y `run_vertical_mvp_support` dejan de aceptar `price_result` y pasan a aceptar `price_invoker`.

No existe fallback compatible que envuelva un `PriceIntelligenceResult` desprendido.

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

## 10. Auditoría 2

Resultado: **SUPERADA — SIN BLOQUEADORES**.

Comprobado contra:

- `Price_Intelligence_Implementation_Contract.md` v1.3;
- `eios/pricing/models.py`;
- `eios/pricing/engine.py`;
- `eios/core/capability_adapters.py`;
- `eios/core/mvp_execution.py`;
- `eios/mvp.py`;
- tests específicos de frontera PRICE.

Hallazgos de cierre:

- el motor PRICE y sus modelos cerrados no se modifican;
- la nueva frontera valida los cinco campos de `DecisionContext`;
- la compra se valida campo a campo, no solo por IDs;
- la ejecución se reconstruye desde inputs congelados;
- `price_result` desaparece de las dos APIs Vertical públicas;
- no se introduce fallback de resultado desprendido;
- no cambia la semántica `PR_NOT_JUSTIFIABLE` ni la autoridad empresarial;
- no se crean scores, pesos, ranking ni heurísticas.

## 11. Criterio de cierre

Implementación y Auditoría 2 quedan cerradas en rama. La unidad no se considera integrada hasta completar:

1. CI de PR satisfactoria sobre el head exacto;
2. merge de ese mismo head;
3. CI post-merge satisfactoria.
