# EIOS — R-PRE-002 Technical Contract v0.1

**Autoridad:** `PRE002 Critical Price Authority v0.1`  
**Estado:** CERRADO PARA MATERIALIZACIÓN

## 1. Carrier

Se define `CriticalPriceBaseline` como modelo frozen/extra-forbid.

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
baseline_price
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

- AVAILABLE → baseline_price obligatorio, Decimal finito y > 0.
- otros estados → baseline_price = null.
- currency normalizada a mayúsculas.
- trace_refs sin duplicados.

## 2. Purchase binding

`critical_price_purchase_ref(PurchaseOperation)` será SHA-256 canónico del `model_dump(mode="json")` completo.

## 3. Evidence

```text
source_type = CriticalPriceBaselineEvidence
captured_at = evaluation_date
```

Si DEMONSTRATED:

```text
demonstration_ref = critical_price_baseline_ref(carrier)
```

## 4. Identity

Antes de evaluar:

- purchase/context decision/scenario coinciden;
- rule_id = R-PRE-002;
- rule.version = context.rules_version;
- rule.requires_evidence = true;
- carrier decision/scenario/snapshot/article/date coinciden;
- carrier.purchase_operation_ref coincide con PurchaseOperation exacta;
- carrier.currency = purchase.currency.

## 5. P-PRE-005

Validaciones:

- parameter_id exacto;
- parameters_version;
- company_id;
- effective_at.date == evaluation_date;
- configuración vigente;
- unit == `%`;
- Decimal finito >= 0;
- Evidence ligada a configuration_ref.

## 6. Evaluación

Si baseline.state != AVAILABLE:

```text
NOT_EVALUABLE
```

Si Evidence no válida:

```text
NOT_EVALUABLE
```

Con baseline y parámetro válidos:

```text
critical_price_limit =
baseline_price * (1 + threshold_pct / 100)

triggered =
purchase.unit_price > critical_price_limit
```

No hay redondeo previo.

## 7. Assessment

TRUE/FALSE solo con baseline y P-PRE-005 demostrados.

Evidence IDs, en orden:

1. CriticalPriceBaselineEvidence;
2. P-PRE-005 ParameterConfigurationEvidence.

## 8. Catálogo

```text
R-PRE-002 → R1 / ALTA
```

Sin R0.

## 9. Orquestador

Bundle:

`CriticalPriceRuleInputs`

con:

- baseline;
- baseline_evidence;
- critical_resolution;
- critical_evidence.

Bundle ausente → R-PRE-002 omitted.

## 10. No-alcance

No se modifica:

- Price Intelligence;
- R-PRE-001;
- R-PRE-003;
- CRC;
- SQL;
- selección upstream del baseline.

**Contrato técnico: CERRADO PARA MATERIALIZACIÓN.**
