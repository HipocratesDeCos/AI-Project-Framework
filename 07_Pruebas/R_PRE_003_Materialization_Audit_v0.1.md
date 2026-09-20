# EIOS — R-PRE-003 Materialization Audit v0.1

**Baseline:** `main @ 9948eba7b412a0d0f4c2e9f0db41af06d5459c37`  
**Estado:** MATERIALIZADO — PENDIENTE CI

## 1. Superficie física

Se materializan:

- `eios/pricing/recommended_ceiling.py`;
- exports pricing;
- bridge `evaluate_r_pre_003`;
- metadata R3/INFORMATIVA;
- `RecommendedPriceRuleInputs`;
- integración en `run_domain_rules`;
- tests dedicados;
- reconciliación de tests históricos.

Price Intelligence engine/models no se modifican.

## 2. Audit de implementación

### I1 — PR ≠ PMR

`RecommendedPriceCeiling` es un tipo separado de `PriceIntelligenceResult`.

El evaluator no consume `PriceIntelligenceResult` ni ejecuta `run_price_intelligence`.

**PASS.**

### I2 — PMR no se calcula en Rules

El carrier debe llegar ya producido y evidenciado.

**PASS.**

### I3 — Purchase binding

El carrier porta SHA-256 canónico de la `PurchaseOperation` completa.

**PASS.**

### I4 — Evidence binding

Evidence DEMONSTRATED debe apuntar al hash exacto del carrier.

**PASS.**

### I5 — moneda

Carrier y PurchaseOperation deben usar la misma moneda exacta.

No existe FX.

**PASS.**

### I6 — condición

```text
triggered = purchase.unit_price <= ceiling_price
```

Igualdad → TRUE.

**PASS.**

### I7 — fail closed

Carrier no AVAILABLE o Evidence no VALID → NOT_EVALUABLE.

**PASS.**

### I8 — parámetros

No se consumen P-PRE-*.

**PASS.**

### I9 — metadata

`R-PRE-003 → R3 / INFORMATIVA`.

**PASS.**

### I10 — no-alcance

No se modifica:

- Price Intelligence C1;
- R-PRE-001;
- R-PRE-002;
- CRC;
- SQL;
- parametrización PRE.

**PASS.**

## 3. Tests

Se cubren:

- menor/igual/mayor que PMR;
- PMR = 0;
- estados no disponibles;
- Evidence GAP;
- reference forjada;
- identity mismatch;
- purchase binding;
- moneda incompatible;
- metadata;
- orquestador;
- omisión;
- invariantes del carrier;
- guard estática contra dependencia de Price Intelligence en el evaluator.

## 4. Dictamen

**AUDIT 2 FÍSICO: SUPERADA — 0 bloqueadores observados antes de CI.**

Cierre condicionado a CI exact-head, suite completa, SQL SUCCESS y merge protegido por SHA.
