# EIOS — R-PRE-003 Technical Contract v0.1

**Autoridad:** `PRE003 Recommended Price Ceiling Authority v0.1`  
**Estado:** CERRADO PARA MATERIALIZACIÓN

## 1. Carrier

Se define `RecommendedPriceCeiling` como modelo frozen/extra-forbid.

Campos:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
evaluation_date
currency
purchase_operation_ref
state
ceiling_price
source_ref
authority_ref
methodology_ref
trace_refs
```

Estados:

```text
AVAILABLE
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Invariantes:

- AVAILABLE → ceiling_price obligatorio, Decimal finito, >= 0.
- estados no disponibles → ceiling_price = null.
- currency se normaliza a mayúsculas.
- trace_refs sin duplicados.

## 2. Purchase binding

`recommended_price_purchase_ref(PurchaseOperation)` será SHA-256 canónico del `model_dump(mode="json")` completo de la operación.

## 3. Evidence binding

Evidence:

```text
source_type = RecommendedPriceCeilingEvidence
captured_at = evaluation_date
```

Si DEMONSTRATED:

```text
demonstration_ref = recommended_price_ceiling_ref(carrier)
```

## 4. Identity

Antes de evaluar:

- purchase/context decision/scenario coinciden;
- rule_id = R-PRE-003;
- rule.version = context.rules_version;
- rule.requires_evidence = true;
- carrier decision/scenario/snapshot/article/date coinciden;
- carrier.purchase_operation_ref coincide con PurchaseOperation exacta;
- carrier.currency = purchase.currency.

## 5. Evaluación

Carrier AVAILABLE + Evidence VALID:

```text
triggered = purchase.unit_price <= ceiling_price
```

Estados no disponibles → NOT_EVALUABLE.

Evidence no válida → NOT_EVALUABLE.

## 6. Assessment

TRUE/FALSE solo con PMR demostrada.

```text
evidence_ids = [recommended_price_ceiling_evidence]
```

## 7. Catálogo

```text
R-PRE-003 → R3 / INFORMATIVA
```

## 8. Orquestador

Bundle:

`RecommendedPriceRuleInputs`

con:

- ceiling;
- ceiling_evidence.

Bundle ausente → R-PRE-003 omitted.

## 9. Arquitectura

El carrier se materializa en un módulo separado del Price Intelligence C1.

No se importa ni consume `PriceIntelligenceResult` en el evaluator R-PRE-003.

## 10. No-alcance

No se modifica:

- Price Intelligence engine/models;
- R-PRE-001;
- R-PRE-002;
- P-PRE-*;
- CRC;
- SQL.

**Contrato técnico: CERRADO PARA MATERIALIZACIÓN.**
