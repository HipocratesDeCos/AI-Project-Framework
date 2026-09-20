# EIOS — R-FIN-002 Technical Contract v0.1

**Estado:** CERRADO PARA MATERIALIZACIÓN  
**Autoridad:** `FIN002_Post_Operation_Working_Capital_Authority_v0.1.md`

## 1. Objetivo

Materializar una frontera Rules provenance-safe para `R-FIN-002` sin modificar Finance Basic.

## 2. Carrier factual

Se define un carrier inmutable:

`PostOperationWorkingCapitalPosition`

Campos mínimos:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
evaluation_date
currency
purchase_operation_ref
current_assets_after_operation
current_liabilities_after_operation
post_operation_snapshot_ref
source_ref
authority_ref
trace_refs
```

Restricciones:

- strings no vacíos;
- moneda ISO-like de 3 caracteres normalizada a mayúsculas;
- importes Decimal finitos;
- trace_refs sin duplicados;
- carrier frozen / extra forbid.

## 3. Purchase binding

Se define:

`purchase_operation_ref(PurchaseOperation) -> str`

como SHA-256 determinista del `model_dump(mode="json")` canónico de la operación completa.

El carrier debe portar exactamente esa referencia.

No se acepta binding solo por `article_id`, `supplier_id` o `scenario_id`.

## 4. Evidence binding

La evidencia de posición usa:

```text
source_type = PostOperationWorkingCapitalEvidence
captured_at = evaluation_date
demonstration_ref =
post_operation_working_capital_position_ref(position)
```

La referencia es SHA-256 determinista del carrier completo.

Si Evidence es `DEMONSTRATED` pero su `demonstration_ref` no coincide, se trata como error estructural.

Si Evidence no valida, la Rule queda `NOT_EVALUABLE`.

## 5. P-FIN-003

El evaluator consume:

- `ResolvedConfiguration | None`;
- `Evidence | None`.

Validaciones estructurales:

- `parameter_id == P-FIN-003`;
- `parameters_version == DecisionContext.parameters_version`;
- `company_id == position.company_scope`;
- `effective_at.date() == position.evaluation_date`;
- configuración vigente en `effective_at`;
- `unit == position.currency` o alias explícito `€` únicamente cuando currency sea `EUR`;
- Evidence source type canónico;
- Evidence captured_at coincidente;
- Evidence DEMONSTRATED ligada a `configuration_ref`.

Valor no finito/no numérico o Evidence no válida → `NOT_EVALUABLE`.

No se impone signo positivo al threshold: la autoridad solo exige Decimal finito.

## 6. Identity checks

Antes de evaluar se exige:

```text
purchase.decision_id == context.decision_id
purchase.scenario_id == context.scenario_id
rule.rule_id == R-FIN-002
rule.version == context.rules_version
rule.requires_evidence == true

position.decision_id == context.decision_id
position.scenario_id == context.scenario_id
position.data_snapshot_id == context.data_snapshot_id
position.article_id == purchase.article_id
position.evaluation_date == purchase.operation_date
position.purchase_operation_ref == purchase_operation_ref(purchase)
```

La empresa se liga a `P-FIN-003` mediante `company_id`.

## 7. Cálculo

Solo con carrier + Evidence + parámetro válidos:

```text
working_capital_after_operation =
current_assets_after_operation
-
current_liabilities_after_operation
```

```text
triggered =
working_capital_after_operation
<
threshold
```

No hay redondeo ni tolerancia implícita.

## 8. Assessment

TRUE:

```text
status = EVALUABLE
outcome = TRUE
evidence_ids = [position_evidence, parameter_evidence]
```

FALSE:

```text
status = EVALUABLE
outcome = FALSE
evidence_ids = [position_evidence, parameter_evidence]
```

Fail closed:

```text
status = NOT_EVALUABLE
outcome = null
```

Nunca se construye una recomendación de compra dentro del evaluator.

## 9. Catálogo

Se materializa:

```text
R-FIN-002 → R0 / CRÍTICA
```

sin mecanismo de downgrade o excepción.

## 10. Orquestador

Nuevo bundle:

`FinanceWorkingCapitalRuleInputs`

con:

- `position`;
- `position_evidence`;
- `minimum_resolution`;
- `parameter_evidence`.

Si el bundle falta, `R-FIN-002` aparece como omitted.

## 11. No-alcance físico

No se modifica:

- Finance Basic;
- Finance provenance;
- CRC;
- MED;
- SQL;
- asientos;
- FX;
- P-FIN-001/002/004/005/006;
- R-FIN-001/003.

## 12. Tests mínimos

- TRUE por debajo;
- FALSE en igualdad;
- FALSE por encima;
- números negativos válidos;
- mismatch de purchase ref;
- mismatch decision/scenario/snapshot/article/date;
- Evidence GAP;
- Evidence ref forjada;
- P-FIN-003 ausente;
- parameter Evidence ausente;
- wrong parameter id/version/company/date/unit;
- configuración no vigente;
- threshold no numérico/no finito;
- metadata exacta R0/CRÍTICA;
- orquestador ejecuta/omite correctamente;
- ausencia de dependencia de Finance Basic.

**Contrato técnico: CERRADO PARA MATERIALIZACIÓN.**
