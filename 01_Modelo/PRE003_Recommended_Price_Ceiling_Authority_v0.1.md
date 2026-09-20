# EIOS — PRE003 Recommended Price Ceiling Authority v0.1

**Estado:** AUTORIZADO  
**Fecha:** 20/09/2026  
**Baseline:** `main @ 9948eba7b412a0d0f4c2e9f0db41af06d5459c37`  
**Origen:** `PRE003_Recommended_Price_Ceiling_Authority_Proposal_v0.1.md`

## 1. Autoridad humana explícita

Se autoriza expresamente la semántica propuesta para `R-PRE-003`:

```text
purchase.unit_price <= recommended_price_ceiling
```

## 2. Separación PR / PMR

Se preserva como invariante:

```text
Price Intelligence PR ≠ Recommended Price Ceiling (PMR)
```

`PriceIntelligenceResult.pr_value` no puede reutilizarse como PMR por similitud nominal.

## 3. Carrier factual

R-PRE-003 consumirá un carrier independiente `RecommendedPriceCeiling` producido por una fuente/metodología autorizada.

Estados:

```text
AVAILABLE
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

AVAILABLE exige precio finito, >= 0 y moneda explícita.

## 4. Binding

El carrier debe quedar ligado a:

- decision_id;
- scenario_id;
- data_snapshot_id;
- company_scope;
- article_id;
- evaluation_date;
- currency;
- PurchaseOperation exacta mediante hash determinista;
- source_ref;
- authority_ref;
- methodology_ref;
- trace_refs.

## 5. Evidence

Se exige `RecommendedPriceCeilingEvidence` y, cuando sea DEMONSTRATED:

```text
demonstration_ref == recommended_price_ceiling_ref(carrier)
```

Reference ajena o forjada → error estructural.

Evidence GAP/INVALID → NOT_EVALUABLE.

## 6. Moneda

La moneda del PMR debe coincidir exactamente con `PurchaseOperation.currency`.

No se autoriza FX.

## 7. Condición

```text
purchase.unit_price < ceiling_price  → TRUE
purchase.unit_price == ceiling_price → TRUE
purchase.unit_price > ceiling_price  → FALSE
```

No existe tolerancia implícita.

## 8. Evaluabilidad

Carrier en NOT_EVIDENCED, CONFLICTING_DATA o NOT_DETERMINABLE:

```text
Assessment.status = NOT_EVALUABLE
Assessment.outcome = null
```

Ausencia de PMR nunca equivale a cero ni a FALSE.

## 9. Parámetros

R-PRE-003 v0.1 no consume P-PRE-*.

No se reutilizan P-PRE-001, P-PRE-004 ni P-PRE-005.

## 10. Metadata

```text
R-PRE-003 → R3 / INFORMATIVA
```

No existe bloqueo ni escalada.

## 11. No-alcance

No se autoriza:

- calcular PMR dentro de Rules;
- redefinir PR como PMR;
- PMR = PR;
- PMR = PR * factor;
- introducir una fórmula PMR;
- FX;
- modificar R-PRE-001/R-PRE-002;
- modificar Price Intelligence;
- convertir R3 en decisión empresarial automática.

**Estado final: AUTORIZADA.**
