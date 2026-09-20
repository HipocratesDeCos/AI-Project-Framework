# EIOS — R-STK-002 Technical Contract v0.1

**Autoridad:** `STK002 Projected Coverage & Justified Need Authority v0.1`  
**Estado:** CERRADO PARA MATERIALIZACIÓN

## 1. Inputs físicos

Se definen dos carriers frozen/extra-forbid:

### ProjectedCoverageAfterPurchase

Campos:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
evaluation_date
purchase_operation_ref
state
coverage_days
source_ref
authority_ref
trace_refs
```

Estados:

```text
FINITE
UNBOUNDED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Reglas:

- FINITE → coverage_days obligatorio, finito, >= 0.
- resto → coverage_days = null.

### JustifiedNeedState

Campos de identidad/provenance equivalentes y:

```text
state = PRESENT | ABSENT | NOT_EVIDENCED | CONFLICTING_DATA | NOT_DETERMINABLE
```

PRESENT/ABSENT son estados determinados.

## 2. Purchase binding

Ambos carriers deben portar una huella SHA-256 determinista de la `PurchaseOperation` completa.

## 3. Evidence

Tipos:

```text
ProjectedCoverageAfterPurchaseEvidence
JustifiedNeedStateEvidence
```

Evidence DEMONSTRATED debe apuntar al hash determinista del carrier exacto.

Reference ajena → error estructural.

Evidence no VALID → NOT_EVALUABLE.

## 4. P-STK-004

Validaciones:

- parameter_id exacto;
- parameters_version coincidente;
- company_id coincidente;
- effective_at.date == evaluation_date;
- configuración vigente;
- unit == "días";
- Decimal finito >= 0;
- ParameterConfigurationEvidence ligada a configuration_ref.

Ausencia/invalidación → NOT_EVALUABLE.

## 5. Identity binding

purchase/context/rule/carriers deben coincidir en:

- decision_id;
- scenario_id;
- data_snapshot_id;
- article_id;
- evaluation_date;
- purchase_operation_ref.

Ambos carriers deben coincidir entre sí en:

- company_scope;
- identidad;
- fecha;
- operación.

## 6. Evaluación

Si cualquiera de ambos carriers está indeterminado → NOT_EVALUABLE.

Con ambos determinados y parámetro válido:

```text
if coverage.state == UNBOUNDED:
    coverage_high = True
else:
    coverage_high = coverage_days > threshold

triggered = coverage_high and need.state == ABSENT
```

## 7. Assessment

TRUE/FALSE solo cuando toda la evidencia requerida es válida.

Evidence IDs, en orden:

1. coverage evidence;
2. justified-need evidence;
3. P-STK-004 evidence.

## 8. Catálogo

```text
R-STK-002 → R2 / ALTA
```

Sin R0.

## 9. Orquestador

Bundle:

`StockCoverageNeedRuleInputs`

con carriers, evidencias y resolución/evidence de P-STK-004.

Bundle ausente → R-STK-002 omitted.

## 10. No-alcance

No se modifica:

- M04 engine;
- M07/R-STK-003;
- M08/R-STK-004;
- P-STK-005;
- P-PYE-*;
- CRC;
- SQL;
- productores upstream.

**Contrato técnico: CERRADO PARA MATERIALIZACIÓN.**
