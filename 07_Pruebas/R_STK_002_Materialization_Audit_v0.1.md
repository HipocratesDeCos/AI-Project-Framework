# EIOS — R-STK-002 Materialization Audit v0.1

**Baseline:** `main @ 4128771f58aa446d61ad28cb1a8ec96c4f3817a0`  
**Estado:** MATERIALIZADO — PENDIENTE CI

## 1. Superficie física

Se materializan:

- `eios/stock/rule_inputs.py`;
- exports STK;
- bridge `evaluate_r_stk_002`;
- metadata R2/ALTA;
- `StockCoverageNeedRuleInputs`;
- integración en `run_domain_rules`;
- tests dedicados;
- reconciliación de tests históricos.

No se modifican M04/M07/M08 engines, R-STK-003, R-STK-004, CRC ni SQL.

## 2. Audit de implementación

### I1 — carriers independientes

`ProjectedCoverageAfterPurchase` y `JustifiedNeedState` no reutilizan `CoverageResult` ni `ExcessResult`.

**PASS.**

### I2 — binding exacto a compra

Ambos carriers portan SHA-256 canónico de la `PurchaseOperation` completa.

**PASS.**

### I3 — Evidence exacta

Cada Evidence DEMONSTRATED debe apuntar al hash exacto de su carrier.

**PASS.**

### I4 — evaluabilidad conservadora

Cualquier estado no determinado en coverage o need produce `NOT_EVALUABLE`, incluso si el otro predicado permitiría cortocircuitar a FALSE.

**PASS.**

### I5 — P-STK-004

Exige:

- ID;
- parameters_version;
- company;
- fecha;
- vigencia;
- unidad `días`;
- Decimal finito >= 0;
- Evidence ligada a configuration_ref.

No existe default 90.

**PASS.**

### I6 — condición exacta

```text
FINITE: coverage_high = coverage_days > threshold
UNBOUNDED: coverage_high = TRUE
triggered = coverage_high AND need == ABSENT
```

Igualdad → FALSE.

**PASS.**

### I7 — separación M07/M08

No se importa `ExcessResult` en los carriers ni se deriva need desde R-STK-004.

**PASS.**

### I8 — metadata

`R-STK-002 → R2 / ALTA`.

No existe R0.

**PASS.**

### I9 — orquestador

Bundle dedicado y omisión explícita cuando falta.

**PASS.**

### I10 — no-alcance

No hay:

- P-STK-005;
- P-PYE-*;
- cálculo de demanda;
- reconstrucción de cobertura;
- fusión con R-STK-003;
- inferencia de ausencia de necesidad;
- cambio CRC.

**PASS.**

## 3. Tests

La suite dedicada cubre:

- TRUE/FALSE y frontera exacta;
- UNBOUNDED;
- PRESENT/ABSENT;
- estados indeterminados;
- Evidence GAP;
- refs forjadas;
- purchase binding;
- identity mismatch;
- carrier mismatch;
- parámetro ausente;
- ID/version/company/date;
- vigencia;
- unidad;
- threshold inválido;
- parameter Evidence;
- metadata;
- ausencia de default;
- orquestador;
- invariantes frozen/trace.

## 4. Dictamen

**AUDIT 2 FÍSICO: SUPERADA — 0 bloqueadores observados antes de CI.**

Cierre condicionado a CI exact-head, suite completa, SQL SUCCESS y merge protegido por SHA.


## 5. CI y cierre

PR #252 validó el HEAD exacto:

```text
458a941cb5421445b40b44037155759a9f6fa19a
```

CI #1023:

```text
1767 passed
8 warnings
SQL validations SUCCESS
```

Merge protegido por SHA:

```text
main @ be13aad7d1dde788ef6e79cf262c1a7e91ed7374
```

## 6. Estado final

**R-STK-002 v0.1: CERRADA / MATERIALIZADA / CI VALIDADA.**
