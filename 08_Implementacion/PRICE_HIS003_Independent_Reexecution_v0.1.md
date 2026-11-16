# EIOS — Reconstrucción conjunta PRICE / HIS003 sin mezclar autoridades (fase 1E)

**Rama aislada:** `feat/core-price-his003-provenance-reconciliation-20261115`  
**Dependencias:** PR #578 ← #577 ← #576 ← #575  
**Estado:** implementación de integración técnica no operacional; pendiente de CI y auditoría final

## 1. Hallazgo de frontera

- El PRICE de empresa (C1) exige bases económicas declaradas y ejecuta normalización/precio histórico con `PriceIntelligenceInput`.
- `R-HIS-003` evalúa separadamente siete dimensiones comerciales con su propia `HistoricalComparabilityDimensionDetermination` y evidencias `Evidence`. **Su `Assessment` es resultado de una regla R3 y no una decisión de compra.**
- El QTG especializado de `PROJECTION_ONLY` **no** equivale a un `QualityTrustResult` simple. Sus productores/consumidores construyen y validan `ProjectionQualityReceipt` y `ProjectionQualityConsumption` con material, perfiles, modo y huellas. Existe el enlace causal `projection_quality_o1_binding.py` que exige validación exacta de la cadena antes de O1.
- Por tanto, sería incorrecto unir estados por conveniencia (p. ej., `HIS003=COMPARABLE` + `QTG=APTO` = precio autorizado).

## 2. Materialización acotada

`eios/core/price_his003_reconciliation.py` define:

- `HistoricalReferenceSourceBundle`: por `reference_id`, entradas crudas HIS003 (`dimension_determinations`, `dimension_evidences`), **sin campo para resultado precomputado**;
- `reconcile_price_and_his003(...)`: recibe `PriceIntelligenceInput`, assessment context C1, perfil/empresa esperada, compra, `DecisionContext`, regla R-HIS-003 y todos los bundles históricos;
- `PriceHistoryReconciliation`: contiene el resultado PRICE y cada `Assessment` HIS003 obtenido por ejecución independiente de su puente. Incluye huella de la referencia, trazas y evidencias. Marca `qtg_status=NOT_ASSESSED`, `decision_authority=False`.

Antes de ejecutar:
1. Se coteja la compra íntegra y el `DecisionContext` completo del PRICE con la ejecución presentada.
2. Se comprueba identidad de regla R-HIS-003, versión y exigencia de evidencias.
3. Cada referencia PRICE debe tener una única fuente HIS003 con el mismo `source_transaction_id`; no se permiten ausencias ni fuentes externas/duplicadas.
4. HIS003 se reejecuta **antes de PRICE**, mediante `evaluate_r_his_003`, con la referencia **tomada del mismo payload PRICE** y las determinaciones/evidencias suministradas. Una identidad o evidencia histórica incorrecta detiene la ejecución.
5. Las huellas provienen de `historical_comparability_reference_ref`; las evidencias HIS003 verifican su `demonstration_ref`, fecha, tipo y dimensión con el productor existente.
6. Solo si la cadena HIS003 se ha podido reconstruir sin errores de integridad, PRICE se reejecuta mediante `run_price_intelligence_for_company`, con cobertura estricta y empresa esperada. El estado HIS003 `NOT_EVALUABLE` es un resultado independiente, no un error técnico por sí mismo.

## 3. Semántica preservada

- HIS003 `outcome=TRUE` significa que **hay diferencia comercial material**. No se convierte automáticamente en rechazo, diferencia de precios o fallo QTG.
- HIS003 `status=NOT_EVALUABLE` permanece indeterminado, aunque PRICE pueda emitir una referencia técnicamente utilizable.
- Precio disponible no acredita equivalencia comercial completa; equivalencia comercial no acredita conversión económica.
- El resultado de esta función **no** es un informe de viabilidad ni recomendación operacional. No produce `QTG APTO`.

## 4. QTG: frontera expresamente preservada

El módulo se niega a aceptar `QualityTrustResult` y tickets QTG desligados porque esa firma no admite un QTG de proyecto acreditado.

Para el QTG de proyecciones ya existe el flujo:

`ProjectionMaterialEnvelope` + `ProjectionQualityReceipt`
→ `validate_projection_quality_consumption(...)`
→ `build_projection_quality_o1_input_binding(...)`
→ `run_mvp_execution_with_projection_quality_binding(...)`.

**No se ha vinculado todavía el resultado PRICE/HIS003 con ese flujo QTG**, pues requiere reconstruir la identidad de ejecución y el conjunto de fuentes mediante un adaptador específico sin crear autoridad compartida. El QTG sigue representado como `NOT_ASSESSED` dentro del informe de reconciliación PRICE/HIS003, aunque la empresa pudiera tener otro expediente QTG por separado.

## 5. Seguridad pendiente

- La autenticación de `expected_company_id`, fuente de las evidencias de precio y su procedencia exterior depende del anfitrión. No se materializa aislamiento SaaS.
- El módulo no concede autoría, no aprueba compras ni vincula por sí solo un usuario o sesión de ERP.
- No se reemplaza el invocador PRICE vigente en O1: esta función es un **validador/ejecutor independiente** para una posterior unión causal sin duplicar las reglas de HIS003.

## 6. Pruebas mínimas

`tests/test_price_his003_reconciliation.py` cubre:
- mismo escenario, compra, artículo, fuentes y regla → reconstrucción determinista de ambos dominios;
- diferencias materiales e información indeterminada HIS003 sin forzar el precio;
- compra/snapshot/regla/empresa ajenos;
- fuentes históricas omitidas, cambiadas o duplicadas;
- evidencia HIS003 falsificada, con fecha o tipo incorrecto;
- intento de introducir un resultado precomputado en la entrada;
- conservación de los datos de entrada y bloqueo por falta de cobertura PRICE.

**Cierre técnico:** CI completa y validaciones SQL satisfactorias, revisión del diff y PR en borrador sin integración. La coordinación QTG aún queda pendiente y no debe presentarse como realizada.
