# EIOS — R-PRE-001 Materialization Audit v0.1

**Baseline:** `main @ b58b8b61f87fd66269e8f55ede5242efdf69ef29`  
**Fecha:** 21/09/2026  
**Estado:** MATERIALIZADO — PENDIENTE CI

## 1. Superficie física

Se materializan:

- `eios/pricing/comparable_reference.py`;
- exports pricing;
- bridge `evaluate_r_pre_001`;
- metadata R2/ALTA;
- `ComparableRecentPriceRuleInputs`;
- integración en `run_domain_rules`;
- tests dedicados;
- reconciliación de tests históricos.

Price Intelligence C1 no se modifica.

## 2. Audit de implementación

### I1 — referencia individual

`ComparablePriceReference` es independiente de `PriceIntelligenceResult`.

**PASS.**

### I2 — selección

Rules no selecciona última compra, mínimo, proveedor habitual ni PR.

**PASS.**

### I3 — Purchase binding

El carrier porta SHA-256 canónico de la `PurchaseOperation` completa.

**PASS.**

### I4 — Evidence binding

Evidence DEMONSTRATED debe apuntar al hash exacto del carrier.

**PASS.**

### I5 — P-PRE-001

Se valida ID, versión, empresa, fecha, vigencia, unidad `meses`, entero positivo y Evidence.

No hay default 3.

**PASS.**

### I6 — meses calendario

La resta usa meses calendario con clipping al último día del mes destino.

Cutoff inclusivo.

**PASS.**

### I7 — P-PRE-004

Se valida ID, versión, empresa, fecha, vigencia, unidad `%`, Decimal finito >= 0 y Evidence.

No hay default 5.

**PASS.**

### I8 — fórmula

```text
uplift_pct =
((purchase.unit_price - reference_price) / reference_price) * 100
```

Sin redondeo previo.

```text
triggered = uplift_pct >= P-PRE-004
```

**PASS.**

### I9 — fail closed

Comparabilidad no demostrada / Evidence inválida / parámetro inválido → NOT_EVALUABLE.

Referencia comparable fuera del horizonte → EVALUABLE/FALSE.

**PASS.**

### I10 — no-alcance

No se modifica:

- Price Intelligence;
- R-PRE-002;
- R-PRE-003;
- CRC;
- SQL;
- selección upstream.

**PASS.**

## 3. Tests

Se cubren:

- debajo/igual/encima del threshold;
- threshold 0;
- clipping 31 mayo → 28 febrero;
- frontera temporal inclusiva;
- referencia futura;
- estados de comparabilidad;
- Evidence GAP/ref forjada;
- identity/purchase/currency mismatch;
- semántica inválida de parámetros;
- ausencia de defaults;
- configuración no vigente;
- metadata;
- orquestador;
- invariantes carrier;
- guard contra PriceIntelligenceResult/run_price_intelligence en evaluator.

## 4. Dictamen

**AUDIT 2 FÍSICO: SUPERADA — 0 bloqueadores observados antes de CI.**

Cierre condicionado a CI exact-head, suite completa, SQL SUCCESS y merge protegido por SHA.
