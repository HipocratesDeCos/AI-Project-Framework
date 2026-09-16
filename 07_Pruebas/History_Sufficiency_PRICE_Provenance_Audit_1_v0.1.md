# EIOS — History Sufficiency PRICE Provenance · Audit 1 v0.1

## Estado

**AUDIT 1: SUPERADA — 0 BLOQUEADORES**

Unidad: `HIS-PRICE-PROV-01`

Baseline auditado: `main @ 64ffacefc26f2199a9caa81ad58aa227c9dc4125`

Diseño auditado: `08_Implementacion/History_Sufficiency_PRICE_Provenance_Contract_v0.1.md`

## 1. Objetivo de auditoría

Comprobar que cerrar la frontera PRICE consumida por `R-HIS-002`:

- está autorizado por una política ya cerrada;
- no redefine metodología PRICE;
- no altera la semántica de `R-HIS-002`;
- no crea una segunda autoridad de ejecución;
- puede materializarse sin mantener una ruta heredada que acepte `PriceIntelligenceResult` desprendido.

## 2. Hallazgo raíz confirmado

La ruta vigente de Rules acepta un `PriceIntelligenceResult` suministrado por el llamador:

`HistorySufficiencyRuleInputs.pricing_result`
→ `run_domain_rules(...)`
→ `evaluate_r_his_002(..., pricing_result, ...)`.

La evidencia PRICE se valida contra una referencia derivada de ese mismo resultado recibido. Por tanto, el par `resultado + evidencia` no demuestra que PRICE haya sido ejecutado desde los inputs autorizados de la compra/contexto actuales.

Esto contradice la política cerrada por `Price_Provenance_Invoker_Contract_v0.1` y PR #115, que eliminó el resultado PRICE desprendido como frontera reusable y exige reconstrucción desde `PriceIntelligenceInput + PriceIntelligenceAssessmentContext`.

**Dictamen:** contradicción física reproducible y suficiente para autorizar una reparación provenance-safe.

## 3. Autoridad

La reparación reutiliza autoridad existente. No se crea política nueva.

Autoridad aplicable:

- `08_Implementacion/Price_Provenance_Invoker_Contract_v0.1.md`;
- PR #115;
- `eios/pricing/engine.py::run_price_intelligence`;
- contratos físicos `PriceIntelligenceInput` y `PriceIntelligenceAssessmentContext`.

La condición de `R-HIS-002` y la relación con `P-PRE-006` permanecen sin cambios.

## 4. Compatibilidad con PRICE C1

`run_price_intelligence(...)` es el productor físico cerrado del `PriceIntelligenceResult`.

Reejecutarlo dentro del bridge de Rules desde snapshots de los inputs C1:

- no recalcula mediante una fórmula alternativa;
- no redefine selección, suficiencia, representatividad, temporalidad ni agregación;
- no crea un resultado PRICE manual;
- utiliza el mismo motor C1 autorizado.

**Dictamen:** compatible.

## 5. Relación con el invoker público de PRICE

El invoker público O1 devuelve `CapabilityExecution`, no el detalle `PriceIntelligenceResult` requerido por `R-HIS-002`.

Por ello el bridge no puede consumir el resultado analítico desde O1 sin ampliar contratos cerrados innecesariamente.

Aplicar internamente la misma política —validar identidad y reconstruir C1 desde inputs autorizados— no contradice el invoker público. Ambos protegen fronteras diferentes y reutilizan el mismo productor C1.

**Dictamen:** no existe duplicación de autoridad.

## 6. Mapa de consumidores

Producción:

1. `eios/rules/pricing.py` — bridge directo de `R-HIS-002`.
2. `eios/rules/orchestrator.py` — `HistorySufficiencyRuleInputs` y llamada al bridge.
3. `eios/mvp.py` — reenvía el bundle a `run_domain_rules`; no lee ni transforma PRICE.

Tests directos:

- `tests/test_r_his_002_vertical.py` construye actualmente resultados PRICE manuales y deberá migrar a inputs/contexto C1 reales.

`tests/test_vertical_mvp_support.py` no construye `HistorySufficiencyRuleInputs`; verifica la fachada genérica y no requiere compatibilidad con `pricing_result`.

No se ha identificado otro consumidor físico que justifique conservar la API heredada.

## 7. P-PRE-006

La validación vigente de `P-PRE-006` ya es provenance-safe y debe preservarse exactamente:

- identidad del parámetro;
- versión;
- empresa;
- vigencia;
- unidad;
- valor entero positivo;
- evidencia de configuración.

**Dictamen:** no requiere rediseño.

## 8. Semántica empresarial

La reparación no modifica la condición:

`n_comparable < P-PRE-006`

Solo cambia la procedencia de `n_comparable`: debe provenir de PRICE reconstruido localmente y no de un resultado aportado por el llamador.

**Dictamen:** semántica preservada.

## 9. Riesgos identificados para depuración

No bloqueantes, pero obligatorios antes de materializar:

1. El `PriceIntelligenceAssessmentContext` también debe copiarse en profundidad junto con `PriceIntelligenceInput` antes de ejecutar C1.
2. Las excepciones contractuales de C1 no deben transformarse silenciosamente en TRUE/FALSE ni en un fallback.
3. La evidencia PRICE inválida debe conservar el comportamiento actual `NOT_EVALUABLE`, después de haber reconstruido el resultado autorizado.
4. Debe eliminarse completamente `pricing_result` de la API de Rules; no se admite alias ni compatibilidad transitoria.
5. Los tests deben dejar de fabricar `PriceIntelligenceResult` como input válido de la regla.
6. Debe existir una prueba negativa que demuestre que una evidencia ligada a un resultado distinto del reconstruido queda `NOT_EVALUABLE`.

## 10. Resultado

| Control | Resultado |
|---|---|
| Autoridad previa suficiente | PASS |
| Contradicción física demostrada | PASS |
| Metodología PRICE preservada | PASS |
| Semántica R-HIS-002 preservada | PASS |
| P-PRE-006 preservado | PASS |
| Consumidores acotados | PASS |
| Necesidad de fallback | NO |
| Bloqueadores | **0** |

**AUDIT 1 SUPERADA.**

La unidad puede pasar a **DEPURAR**.
