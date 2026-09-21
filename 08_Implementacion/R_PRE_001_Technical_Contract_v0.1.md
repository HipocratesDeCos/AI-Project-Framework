# EIOS — R-PRE-001 Technical Contract v0.1

**Autoridad:** `PRE001 Comparable Recent Price Authority v0.1`  
**Estado:** CERRADO PARA MATERIALIZACIÓN

## 1. Carrier

Se define `ComparablePriceReference` como modelo frozen/extra-forbid.

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
reference_operation_ref
reference_date
reference_price
comparability_state
source_ref
authority_ref
methodology_ref
trace_refs
```

Estados:

```text
COMPARABLE
NOT_COMPARABLE
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Invariantes:

- COMPARABLE → reference_price obligatorio, Decimal finito y > 0.
- estados restantes → reference_price puede estar presente solo si el productor lo conoce, pero Rules no lo usa.
- currency normalizada a mayúsculas.
- trace_refs sin duplicados.

## 2. Purchase binding

`comparable_price_purchase_ref(PurchaseOperation)` será SHA-256 canónico del `model_dump(mode="json")` completo.

## 3. Evidence binding

```text
source_type = ComparablePriceReferenceEvidence
captured_at = evaluation_date
```

Si DEMONSTRATED:

```text
demonstration_ref = comparable_price_reference_ref(carrier)
```

## 4. Identity

Antes de evaluar:

- purchase/context decision/scenario coinciden;
- rule_id = R-PRE-001;
- rule.version = context.rules_version;
- rule.requires_evidence = true;
- carrier decision/scenario/snapshot/article/date coinciden;
- carrier.purchase_operation_ref coincide con PurchaseOperation exacta;
- carrier.currency = purchase.currency.

## 5. P-PRE-001

Validaciones:

- parameter_id exacto;
- parameters_version;
- company_id;
- effective_at.date == evaluation_date;
- configuración vigente;
- unit == `meses`;
- valor entero positivo;
- Evidence ligada a configuration_ref.

## 6. Cutoff

Se implementa resta de meses calendario sin dependencia de Price Intelligence:

```text
target_month = evaluation_date - N calendar months
target_day = min(original_day, last_day(target_month))
```

Reciente:

```text
cutoff_date <= reference_date <= evaluation_date
```

reference_date > evaluation_date → error estructural.

## 7. P-PRE-004

Validaciones:

- parameter_id exacto;
- parameters_version;
- company_id;
- effective_at.date == evaluation_date;
- configuración vigente;
- unit == `%`;
- Decimal finito >= 0;
- Evidence ligada a configuration_ref.

## 8. Evaluación

Si comparability_state != COMPARABLE:

```text
NOT_EVALUABLE
```

Si Evidence no válida:

```text
NOT_EVALUABLE
```

Si referencia comparable pero no reciente:

```text
EVALUABLE / FALSE
```

Si es reciente:

```text
uplift_pct =
((purchase.unit_price - reference_price) / reference_price) * 100

triggered =
uplift_pct >= threshold
```

## 9. Assessment

TRUE/FALSE con Evidence IDs, en orden:

1. reference evidence;
2. P-PRE-001 evidence;
3. P-PRE-004 evidence.

## 10. Catálogo

```text
R-PRE-001 → R2 / ALTA
```

## 11. Orquestador

Bundle:

`ComparableRecentPriceRuleInputs`

con:

- reference;
- reference_evidence;
- recency_resolution;
- recency_evidence;
- alert_resolution;
- alert_evidence.

Bundle ausente → omitted.

## 12. No-alcance

No se modifica:

- Price Intelligence C1;
- R-PRE-002;
- R-PRE-003;
- CRC;
- SQL;
- selección upstream de referencias.

**Contrato técnico: CERRADO PARA MATERIALIZACIÓN.**
