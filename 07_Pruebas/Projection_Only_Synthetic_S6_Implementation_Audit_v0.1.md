# EIOS — PROJECTION_ONLY Synthetic S6 Implementation Audit v0.1

**Estado:** CERRADO TÉCNICAMENTE — CI PENDIENTE

**Baseline:** `main @ d74d2f78019bfda138a9d027fcfaf6e7b995a9ce`

**Unidad:** S6 — inventario/completitud de flujos, mandato especializado y revisión personal.

## DISEÑAR

Extender exclusivamente la frontera privada sintética desde S1–S5 a S6. Los componentes `flow_inventory`, `flow_mandate` y `flow_review` se decodifican con schemas estrictos y alimentan únicamente:

1. `FinanceFlowCompletenessRecord`;
2. `FlowInventoryMandateVerification`;
3. `FlowInventoryPersonalReview`.

No se agregan flujos a `FinanceBasicInput`, no se deduplican obligaciones, no se interpreta documentación y no se ejecuta Finance/Quality/QTG.

## AUDITAR

**A1 — inventario presentado vs completitud empresarial.** Una lista de candidatos o una valoración para cada flujo capturado no demuestra por sí sola completitud. S6 conserva `coverage_declaration`, `pending_flow_ids`, `unmatched_candidate_refs` y limitaciones sin traducirlos a éxito.

**A2 — candidatos no capturados.** El adaptador permite que el dominio preserve candidatos sin `captured_flow_id`; nunca crea un `CashFlow` ni modifica la preparación.

**A3 — horizonte incierto.** Vencimiento `NOT_ESTABLISHED` o `CONFLICTING` no puede declararse `AFTER_HORIZON`. La regla permanece en `FIN-FLOW-COMP-01`; el adaptador no la replica.

**A4 — criterio de valoración.** `CapturedFlowAssessment` conserva la referencia/versión presentada y la factoría exige que exista en la preparación. El contrato actual no establece una función única del manifiesto que deba gobernar toda valoración de flujo, por lo que el adaptador no inventa un mapeo adicional.

**A5 — duplicación económica.** `economic_identity_ref` y `duplication_assessment` son declaraciones presentadas. No se fusionan registros, no se escoge un flujo y no se convierte `DECLARED_UNIQUE` en certeza empresarial.

**A6 — mandato especializado.** El mandato de inventario usa su cadena propia y no reutiliza el mandato de tesorería. Su outcome global se deriva exclusivamente por `build_flow_inventory_mandate_verification()`.

**A7 — revisión individual de cuotas.** `PURCHASE_PAYMENT_COHERENCE` debe contener exactamente todas las cuotas del calendario S3 mediante `FlowInstallmentReviewFinding`; faltantes, duplicados o referencias ajenas son rechazados por la factoría cerrada.

**A8 — outcome agregado de cuotas.** El adaptador no suministra un resumen libre distinto de los findings. La factoría exige coherencia determinista entre outcomes individuales y outcome de `PURCHASE_PAYMENT_COHERENCE`.

**A9 — autoridad sintética.** `case_kind` y `mandate_kind` quedan restringidos a `SYNTHETIC`. Reviewer/verifier/channel siguen siendo referencias Mock Data presentadas, no autenticación operacional.

**A10 — parcialidad pública.** `_SyntheticStage6` es interno e inmutable; `__all__` permanece vacío.

## DEPURAR

Queda fuera de S6:

- búsqueda ERP/bancaria de flujos;
- inferencia de candidatos omitidos;
- creación o mutación de `CashFlow`;
- heurística de identidad/deduplicación económica;
- normalización FX;
- interpretación de criterios o documentos;
- reutilización del mandato de tesorería;
- omisión de cuotas no revisadas;
- producción de `QualityCheck`, `QualityResult` o resultado QTG;
- admisión `PRESENTED_OPERATIONAL`.

Los documentos internos de inventario y mandato usan base64 estándar canónico y SHA-256 recomputado, además del hash externo del archivo del dataset.

## AUDITAR 2

El delta queda limitado al adaptador privado, sus pruebas y este registro. No modifica `finance_flow_completeness.py`, `flow_inventory_mandate.py`, `flow_inventory_review.py` ni otras fronteras cerradas.

Las pruebas incorporadas cubren:

- cadena S6 completa y exacta;
- documento de inventario base64 no canónico;
- digest documental incorrecto en mandato;
- criterio ajeno a la preparación;
- inventario incompleto preservado sin fabricar éxito;
- exclusión de horizonte incompatible con vencimiento no establecido;
- obligación de revisar todas las cuotas;
- rechazo de cuota ajena;
- mandato inconcluso con findings preservados sin autoridad;
- rechazo de promoción operacional en los tres componentes;
- rechazo de reviewer separado del mandato;
- ausencia de ejecución Finance/Quality/QTG.

No se declara resultado de suite hasta CI exact-head.

## CERRAR → MATERIALIZAR → CI

S6 queda cerrada técnicamente dentro de este alcance. La integración requiere CI exact-head satisfactoria, reconciliación de `main`, merge protegido y comprobación posterior de equivalencia del árbol/CI disponible.

Después de S6, S7 podrá construir el `ProjectionMaterialEnvelope` desde las cadenas exactas S4–S6 y materializar el bundle público atómico. Esa etapa seguirá sin ejecutar QTG.
