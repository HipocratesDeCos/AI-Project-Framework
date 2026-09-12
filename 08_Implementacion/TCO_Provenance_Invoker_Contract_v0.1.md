# EIOS — TCO Provenance Invoker Contract v0.1

## Estado

DISEÑADO → AUDITADO → DEPURADO. Pendiente de materialización, Auditoría 2 y CI.

## 1. Propósito

Cerrar la frontera de reutilización de TCO en el Vertical MVP sin aceptar un `TCOResult` desprendido cuya identidad parcial pueda reutilizarse contra una propuesta de compra distinta.

La unidad no modifica el contrato económico de TCO Core, `TCOResult`, `TCOInput` ni `calculate_tco`.

## 2. Contradicción objetiva

`TCOInput` conserva:

- `purchase_operation` completa;
- `attributable_costs` completos.

`calculate_tco` usa directamente `quantity × unit_price` y agrega los costes atribuibles aplicables y determinables.

`TCOResult` conserva `decision_id` y `scenario_id`, pero no permite demostrar por sí solo qué `PurchaseOperation` ni qué conjunto de costes atribuibles produjo el resultado.

La frontera Vertical previa solo contrastaba `decision_id + scenario_id`; por tanto podía reutilizar un TCO calculado para otra cantidad, precio, artículo, proveedor, moneda, fecha o conjunto de costes mientras esos dos IDs coincidieran.

## 3. Entrada autorizada de reutilización

La frontera segura congela un `TCOInput` completo.

No se acepta como frontera reutilizable:

- `TCOResult` ya producido;
- un resultado con IDs coincidentes sin su `TCOInput` de origen;
- una reconstrucción parcial de costes atribuibles.

## 4. Validación por ejecución

El invocador público tiene forma:

`(PurchaseOperation, DecisionContext) -> CapabilityExecution`.

Antes de calcular debe exigir:

1. igualdad exacta, campo por campo, entre la `PurchaseOperation` actual y `payload.purchase_operation`;
2. `DecisionContext.decision_id == PurchaseOperation.decision_id`;
3. `DecisionContext.scenario_id == PurchaseOperation.scenario_id`.

TCO Core v0.1 no contiene `rules_version`, `parameters_version` ni `data_snapshot_id` en su input físico; esta unidad no inventa esos campos ni modifica el modelo TCO para añadirlos.

## 5. Ejecución

Tras superar las validaciones, el invocador ejecuta:

`calculate_tco(payload)`

sobre una copia profunda congelada y adapta el resultado mediante `adapt_tco(...)`.

No se modifica la semántica de ausencia, moneda, aplicabilidad, determinabilidad ni GAP-TCO-01/GAP-TCO-02.

## 6. Snapshot

La construcción del invocador copia profundamente `TCOInput`.

Mutaciones posteriores del llamador no pueden afectar ejecuciones futuras.

## 7. Migración Vertical

`run_mvp_execution` y `run_vertical_mvp_support` dejan de aceptar `tco_result` y pasan a aceptar `tco_invoker`.

No existe fallback que envuelva un `TCOResult` desprendido.

La posición canónica de TCO en O1 permanece intacta.

## 8. Semántica preservada

Esta unidad no:

- modifica `TCOResult` ni `TCOInput`;
- añade costes o reglas;
- convierte ausencia en cero;
- inventa FX;
- convierte TCO incompleto en completo;
- convierte TCO en decisión empresarial;
- modifica `adapt_tco`.

## 9. Fail closed

Debe fallar antes del cálculo si:

- `payload` no es `TCOInput`;
- cualquier campo de la compra actual difiere de la compra congelada;
- la identidad decision/scenario entre compra y contexto no coincide.

## 10. Criterio de cierre

La unidad solo se considera integrada cuando:

1. implementación y tests respetan este contrato;
2. Auditoría 2 no detecta rutas de `tco_result` desprendido en las dos fronteras Vertical públicas;
3. CI de PR es satisfactoria sobre el head exacto;
4. se integra ese mismo head;
5. CI post-merge es satisfactoria.
