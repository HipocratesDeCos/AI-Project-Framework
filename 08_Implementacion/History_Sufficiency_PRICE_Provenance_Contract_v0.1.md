# EIOS — History Sufficiency PRICE Provenance Contract v0.1

## Estado

DISEÑADO. Pendiente de AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI.

## 1. Unidad

**HIS-PRICE-PROV-01**

Baseline de diseño: `main @ 64ffacefc26f2199a9caa81ad58aa227c9dc4125`.

## 2. Propósito

Cerrar la frontera de procedencia entre Price Intelligence C1 y la regla `R-HIS-002 — Histórico insuficiente` sin modificar la metodología PRICE, la semántica empresarial de `R-HIS-002` ni el contrato de `P-PRE-006`.

La regla debe evaluar el número de operaciones comparables producido por una ejecución PRICE reconstruible desde sus inputs autorizados. No puede aceptar un `PriceIntelligenceResult` desprendido suministrado por el llamador.

## 3. Contradicción objetiva

La frontera pública Vertical cerrada por `Price_Provenance_Invoker_Contract_v0.1` y PR #115 establece que un `PriceIntelligenceResult` ya producido no es una frontera reusable autorizada. PRICE debe reconstruirse desde `PriceIntelligenceInput + PriceIntelligenceAssessmentContext` tras validar la identidad completa de `PurchaseOperation` y `DecisionContext`.

Sin embargo, el bridge vigente de `R-HIS-002` acepta simultáneamente:

- `PriceIntelligenceInput`;
- un `PriceIntelligenceResult` ya producido;
- una evidencia cuyo `demonstration_ref` se calcula a partir de ese mismo resultado recibido.

Además, `HistorySufficiencyRuleInputs` transporta ese `PriceIntelligenceResult` desprendido y `run_vertical_mvp_support` evalúa Rules antes e independientemente del `price_invoker` de O1. Por tanto, Rules puede evaluar `R-HIS-002` con un resultado PRICE que no haya sido producido por la frontera provenance-safe.

## 4. Autoridad reutilizada

Esta unidad no crea nueva autoridad PRICE. Reutiliza exclusivamente la política ya cerrada en:

- `08_Implementacion/Price_Provenance_Invoker_Contract_v0.1.md`;
- PR #115;
- `eios/core/price_integration.py`;
- `eios/pricing/engine.py`;
- `eios/pricing/models.py`.

La relación `P-PRE-006 → R-HIS-002` y la condición de la regla permanecen bajo sus autoridades actuales.

## 5. Entrada autorizada del bridge

El bridge de `R-HIS-002` consumirá:

- `PurchaseOperation`;
- `DecisionContext`;
- `Rule` autorizada;
- `PriceIntelligenceInput`;
- `PriceIntelligenceAssessmentContext`;
- evidencia PRICE;
- `company_id`;
- `ResolvedConfiguration(P-PRE-006)` cuando exista;
- evidencia de configuración de `P-PRE-006` cuando exista.

No aceptará `PriceIntelligenceResult` como argumento externo.

`HistorySufficiencyRuleInputs` deberá aplicar la misma frontera: transportará los inputs PRICE necesarios para reconstruir el resultado, no un resultado PRICE desprendido.

## 6. Reconstrucción PRICE

Tras validar la identidad del bridge, se ejecutará el motor C1 cerrado:

`run_price_intelligence(pricing_input, pricing_assessment_context)`

sobre snapshots/copies de los inputs recibidos para evitar depender de mutaciones posteriores durante la evaluación.

El `PriceIntelligenceResult` obtenido será local a la evaluación de `R-HIS-002` y no formará parte de la API de entrada del bridge.

## 7. Identidad exigida

Antes de consumir el resultado reconstruido deberán mantenerse o reforzarse las comprobaciones siguientes:

- `PurchaseOperation.decision_id == DecisionContext.decision_id`;
- `PurchaseOperation.scenario_id == DecisionContext.scenario_id`;
- `Rule.rule_id == R-HIS-002`;
- `Rule.version == DecisionContext.rules_version`;
- `Rule.requires_evidence == True`;
- `pricing_input.decision_context == DecisionContext` completo;
- `pricing_input.purchase_operation == PurchaseOperation` completo.

La igualdad completa ya expresada por el bridge vigente se conserva como requisito mínimo.

## 8. Evidencia PRICE

La evidencia PRICE continuará exigiendo:

- `source_type = PriceIntelligenceResultEvidence`;
- `captured_at == PurchaseOperation.operation_date`;
- evidencia `DEMONSTRATED` vinculada mediante `demonstration_ref` al resultado PRICE reconstruido localmente.

La evidencia no podrá validar un resultado elegido por el llamador, porque dicho resultado deja de ser una entrada autorizada.

Si la evidencia PRICE no es válida, `R-HIS-002` seguirá produciendo `Assessment(status=NOT_EVALUABLE, outcome=None)` conforme al comportamiento vigente.

## 9. P-PRE-006

La unidad preserva íntegramente la frontera existente de `P-PRE-006`:

- `parameter_id == P-PRE-006`;
- `parameters_version` coincidente;
- `company_id` coincidente;
- vigencia para la fecha de la operación;
- unidad canónica `operaciones`;
- valor entero, finito y positivo;
- evidencia de configuración vinculada a `configuration_ref`.

No se valida el valor inicial `2 operaciones` como política empresarial definitiva.

## 10. Semántica de R-HIS-002 preservada

La condición ejecutable sigue siendo exactamente:

`pricing_result.counts.n_comparable < P-PRE-006`

No se modifica:

- el identificador de regla;
- efecto/severidad;
- significado de histórico insuficiente;
- comparabilidad PRICE;
- representatividad;
- suficiencia;
- selección;
- agregación;
- temporalidad;
- metodología de Price Intelligence;
- autoridad de CRC.

## 11. Relación con price_invoker público

Esta unidad no modifica `build_provenanced_price_invoker(...)` ni el contrato público O1/Vertical de PRICE.

El bridge de Rules no reutiliza el `CapabilityExecution` de O1 como fuente de datos analíticos, porque ese envelope no transporta `PriceIntelligenceResult`. En su lugar aplica la misma política de procedencia: reconstruir PRICE desde los inputs C1 completos y autorizados.

No se afirma identidad entre dos ejecuciones construidas desde inputs distintos. La garantía de esta unidad es que `R-HIS-002` deja de aceptar un resultado PRICE desprendido y que el resultado consumido por la regla se deriva de los inputs que el propio bridge valida contra la compra y contexto actuales.

## 12. Fail closed

La evaluación debe fallar antes de consumir `n_comparable` si:

- `pricing_input` pertenece a otra compra o `DecisionContext`;
- `PriceIntelligenceAssessmentContext` no puede ejecutar válidamente el C1 cerrado con ese input;
- la evidencia PRICE `DEMONSTRATED` no referencia el resultado reconstruido;
- la configuración/evidencia de `P-PRE-006` incumple su contrato vigente.

No se añade fallback a un resultado PRICE suministrado externamente.

## 13. Delta físico previsto

Alcance máximo previsto:

- `eios/rules/pricing.py`;
- `eios/rules/orchestrator.py`;
- tests directamente afectados por `evaluate_r_his_002`, `HistorySufficiencyRuleInputs` y/o `run_vertical_mvp_support`;
- artefactos metodológicos de esta unidad.

Fuera de alcance:

- `eios/pricing/*` salvo importación/uso;
- `eios/core/price_integration.py`;
- modelos PRICE;
- RDM;
- Catálogo de Parámetros;
- Matriz de Reglas;
- CRC;
- QTG;
- TCO;
- Decision Twin;
- Scenario Engine.

## 14. Criterios de aceptación previstos

1. Ninguna API de Rules para `R-HIS-002` acepta `PriceIntelligenceResult` desprendido.
2. El resultado PRICE consumido se reconstruye mediante `run_price_intelligence` desde `PriceIntelligenceInput + PriceIntelligenceAssessmentContext`.
3. Se rechaza una compra/contexto incompatible con `pricing_input`.
4. Se rechaza evidencia PRICE que no corresponda al resultado reconstruido.
5. Se conserva la validación provenance-safe existente de `P-PRE-006`.
6. Casos positivo y negativo de `n_comparable < P-PRE-006` conservan su semántica.
7. Regresión completa y CI permanecen verdes.

## 15. Prohibiciones

Esta unidad no puede:

- aceptar de nuevo `pricing_result=` como compatibilidad;
- sintetizar un `PriceIntelligenceAssessmentContext` por defecto;
- inferir temporalidad, representatividad o suficiencia;
- convertir errores de procedencia en resultado empresarial favorable/desfavorable;
- crear nuevas reglas, parámetros, scores, pesos o heurísticas.
