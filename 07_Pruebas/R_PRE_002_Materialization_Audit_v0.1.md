# EIOS — R-PRE-002 Materialization Audit v0.1

**Baseline:** `main @ 6a37a95510537b253fea75608c27eebef71b5b22`  
**Fecha:** 21/09/2026  
**Estado:** MATERIALIZADO — PENDIENTE CI

## 1. Superficie física

Se materializan:

- `eios/pricing/critical_baseline.py`;
- exports pricing;
- bridge `evaluate_r_pre_002`;
- metadata R1/ALTA;
- `CriticalPriceRuleInputs`;
- integración en `run_domain_rules`;
- tests dedicados;
- reconciliación de guards históricos de regla no materializada.

Price Intelligence, PRE001 y PRE003 no se modifican semánticamente.

## 2. Audit de implementación

### I1 — baseline independiente

`CriticalPriceBaseline` no reutiliza `ComparablePriceReference`, `RecommendedPriceCeiling` ni `PriceIntelligenceResult`.

**PASS.**

### I2 — Purchase binding

El carrier porta SHA-256 canónico de la `PurchaseOperation` completa.

**PASS.**

### I3 — Evidence binding

Evidence DEMONSTRATED debe apuntar al hash exacto del carrier.

**PASS.**

### I4 — P-PRE-005

Se valida ID, versión, empresa, fecha, vigencia, unidad `%`, Decimal finito >= 0 y Evidence.

No hay default 10%.

**PASS.**

### I5 — fórmula

```text
critical_price_limit =
baseline_price * (1 + P-PRE-005 / 100)
```

Sin redondeo previo.

**PASS.**

### I6 — frontera

```text
purchase.unit_price > critical_price_limit
```

Igualdad → FALSE.

**PASS.**

### I7 — fail closed

Baseline no AVAILABLE / Evidence inválida / parámetro inválido → NOT_EVALUABLE.

**PASS.**

### I8 — metadata

`R-PRE-002 → R1 / ALTA`.

Sin R0 automático.

**PASS.**

### I9 — no-alcance

No se modifica:

- Price Intelligence;
- PRE001;
- PRE003;
- CRC;
- SQL;
- selección upstream de baseline.

**PASS.**

## 3. Tests

La suite dedicada cubre:

- menor/igual/mayor que límite crítico;
- threshold 0;
- estados no disponibles;
- Evidence GAP/ref forjada;
- identity/purchase/currency mismatch;
- parámetro ausente;
- ID/version/company/date;
- vigencia;
- unidad;
- valores no finitos/negativos;
- parameter Evidence;
- ausencia de default 10%;
- metadata R1/ALTA;
- orquestador;
- invariantes frozen;
- guard contra dependencia de carriers PRE001/PRE003/Price Intelligence.

## 4. Tests históricos

Los tests que usaban `R-PRE-002` como sentinel de regla no materializada se trasladan a `R-HIS-001`, que sigue fuera del catálogo ejecutable.

No cambia el propósito de esos tests.

## 5. Dictamen

**AUDIT 2 FÍSICO: SUPERADA — 0 bloqueadores observados antes de CI.**

Cierre condicionado a CI exact-head, suite completa, SQL SUCCESS y merge protegido por SHA.
