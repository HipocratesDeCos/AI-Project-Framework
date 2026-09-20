# EIOS — MGE Rules Technical Contract v0.1

**Baseline:** `main @ 6ad89d0bc70900a14cb7a11c4b8fa7660d0bae6e`  
**Autoridad:** `MGE-RULES-AUTH v0.1`  
**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA — LISTO PARA MATERIALIZACIÓN

## 1. Propósito

Materializar bridges de Rules MGE sin reabrir Profitability Core ni aceptar resultados desprendidos.

Cadena autorizada:

```text
ProvenancedProfitabilityExecution
+
Resolved MGE parameter set
+
Evidence
        ↓
R-MGE-001 / 002 / 003
        ↓
Assessment TRUE/FALSE/NOT_EVALUABLE
        ↓
runtime/CRC existente
```

## 2. Entrada común

Se define un bundle coherente:

```text
ProfitabilityRuleInputs
├── profitability_execution
├── profitability_evidence
├── minimum_resolution       # P-MGE-001
├── minimum_evidence
├── target_resolution        # P-MGE-002
├── target_evidence
├── tolerance_resolution     # P-MGE-003
└── tolerance_evidence
```

No se acepta `ProfitabilityResult` desprendido.

## 3. Provenance MGE

La primera operación de cada bridge debe ser:

```python
validate_provenanced_profitability_execution(execution)
```

La evidencia de Profitability debe usar:

```text
source_type = ProfitabilityResultEvidence
captured_at = ProfitabilityInput.evaluation_date
demonstration_ref = deterministic profitability_result_ref(...)
```

Si la evidencia no es VALID, la regla es `NOT_EVALUABLE`.

Una evidencia DEMONSTRATED con reference ajena es error estructural de frontera.

## 4. Binding de parámetros

Cada resolución debe validar:

- parameter_id exacto;
- `parameters_version == DecisionContext.parameters_version`;
- `company_id == ProfitabilityInput.company_scope`;
- `effective_at.date() == ProfitabilityInput.evaluation_date`;
- configuración vigente en `effective_at`;
- Evidence `source_type = ParameterConfigurationEvidence`;
- Evidence `captured_at == evaluation_date`;
- si DEMONSTRATED, `demonstration_ref == configuration_ref`;
- valor Decimal finito;
- unidad exacta.

Un mismatch de identidad/provenance es error estructural.

Una resolución/evidencia ausente o no VALID produce `NOT_EVALUABLE`, no default.

## 5. Unidades

```text
P-MGE-001 → "%"
P-MGE-002 → "%"
P-MGE-003 → "puntos porcentuales"
```

No se aceptan aliases silenciosos en v0.1.

## 6. Coherencia del parameter set

Tras resolver los tres valores:

```text
minimum <= target
tolerance >= 0
```

Si no se cumple, todas las reglas MGE evaluadas con ese bundle son `NOT_EVALUABLE`.

Esto es una condición analítica de configuración contradictoria, no una autorización para corregir valores.

No se obliga a `target - tolerance >= minimum`: la fórmula de R-MGE-002 contiene explícitamente ambos límites y usa el máximo lógico mediante los dos `AND`.

## 7. Profitability no determinada

Si:

- `calculation_state != DETERMINED`; o
- `margin_percentage is None`;

las tres reglas devuelven `NOT_EVALUABLE`.

No se usa `margin_amount` como sustituto.

## 8. Condiciones booleanas

### R-MGE-001

```text
triggered = margin_percentage < minimum
```

### R-MGE-002

```text
triggered =
    margin_percentage >= minimum
    AND margin_percentage >= target - tolerance
    AND margin_percentage < target
```

### R-MGE-003

```text
triggered = margin_percentage >= target
```

Las fronteras son exactas:

- `m == minimum` → R-MGE-001 FALSE;
- `m == target - tolerance`, si además `m >= minimum` → R-MGE-002 TRUE;
- `m == target` → R-MGE-002 FALSE y R-MGE-003 TRUE.

## 9. Metadata

Catálogo ejecutable:

```text
R-MGE-001 → R1 / ALTA
R-MGE-002 → R2 / MEDIA
R-MGE-003 → R3 / INFORMATIVA
```

R-MGE-001 no escala a R0 en v0.1.

## 10. Evidence IDs

Cada Assessment incluye, en orden estable y sin inferencias:

1. profitability evidence;
2. P-MGE-001 evidence;
3. P-MGE-002 evidence;
4. P-MGE-003 evidence.

Aunque una condición use solo uno o dos thresholds de forma matemática, el bundle coherente completo es parte de la evaluabilidad autorizada de las tres reglas.

## 11. Orquestador

`run_domain_rules(...)` puede aceptar:

```text
profitability: ProfitabilityRuleInputs | None
```

Si está presente, produce las tres assessments MGE en la misma ejecución.

Si está ausente, las tres quedan en `omitted_rule_ids` conforme al catálogo.

No existe ejecución parcial de una sola regla MGE desde el orquestador v0.1.

## 12. Errores estructurales vs NOT_EVALUABLE

### Error estructural

- identity mismatch;
- wrong rule id/version;
- forged/detached profitability execution;
- evidence source type incompatible;
- DEMONSTRATED evidence vinculada a otro objeto/configuración;
- resolución de parameter_id distinto;
- parameters_version/company/date incompatibles.

### NOT_EVALUABLE

- Profitability Evidence en GAP/INVALID;
- Profitability no DETERMINED;
- resolución/evidence ausente;
- parameter Evidence en GAP/INVALID;
- valor no numérico/no finito;
- unidad incorrecta;
- `minimum > target`;
- `tolerance < 0`.

## 13. Invariantes

1. Result desprendido no cruza Rules.
2. P-MGE defaults no existen.
3. P-MGE-004/005/006 no se consumen.
4. Las tres reglas comparten un mismo policy bundle.
5. R-MGE-001 y R-MGE-003 no pueden solaparse con parameter set válido.
6. R-MGE-002 no se solapa con R-MGE-001 ni R-MGE-003.
7. NULL ≠ 0.
8. NOT_EVALUABLE ≠ FALSE.
9. Rule evaluation ≠ Profitability calculation.
10. R1 no escala a R0.
11. CRC no se modifica.
12. No I/O, SQL, red o clock implícito.

## 14. Tests mínimos

- R-MGE-001 TRUE/FALSE y frontera minimum;
- R-MGE-002 TRUE/FALSE y fronteras lower/target;
- R-MGE-003 TRUE/FALSE y frontera target;
- hueco entre minimum y target-tolerance cuando exista;
- tolerance=0;
- minimum=target;
- minimum>target → todas NOT_EVALUABLE;
- tolerance<0 → todas NOT_EVALUABLE;
- Profitability NOT_DETERMINED → todas NOT_EVALUABLE;
- missing/invalid param/evidence → NOT_EVALUABLE;
- wrong ids/version/company/date/ref → error estructural;
- unit mismatch → NOT_EVALUABLE;
- detached/tampered execution → error;
- catálogo metadata exacta;
- orchestrator produce 3 MGE assessments;
- no ejecución parcial MGE;
- regresión completa.

## 15. Criterio de materialización

Solo materializar tras Audit 2 limpia y CI de esta autoridad/contrato.
