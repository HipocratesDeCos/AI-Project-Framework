# EIOS — PRE002 Critical Price Authority v0.1

**Estado:** AUTORIZADO  
**Fecha:** 21/09/2026  
**Baseline:** `main @ 6a37a95510537b253fea75608c27eebef71b5b22`  
**Origen:** `PRE002_Critical_Price_Authority_Proposal_v0.1.md`

## 1. Autoridad humana explícita

Se autoriza la semántica propuesta para `R-PRE-002`:

```text
critical_price_limit =
baseline_price * (1 + resolved(P-PRE-005) / 100)

triggered =
purchase.unit_price > critical_price_limit
```

La igualdad exacta con el límite crítico NO activa la regla.

## 2. Baseline crítico

R-PRE-002 consumirá un carrier factual independiente:

`CriticalPriceBaseline`

No se autoriza reutilizar automáticamente:

- ComparablePriceReference;
- RecommendedPriceCeiling;
- PriceIntelligenceResult.pr_value;
- última compra;
- precio mínimo.

La selección/producción del baseline pertenece a un productor upstream autorizado.

## 3. P-PRE-005

Se consume únicamente mediante:

```text
ResolvedConfiguration(P-PRE-005)
+
ParameterConfigurationEvidence
```

Unidad: `%`.

Valor Decimal finito y >= 0.

No se valida ni hardcodea el valor inicial 10%.

## 4. Evaluabilidad

La Rule devuelve `NOT_EVALUABLE` si:

- baseline no AVAILABLE;
- Evidence del baseline no es válida;
- baseline_price <= 0;
- moneda incompatible;
- P-PRE-005 ausente/no válida/no evidenciada;
- identity/provenance no coincide.

Ausencia de baseline nunca equivale a cero ni a FALSE.

## 5. Metadata

```text
R-PRE-002 → R1 / ALTA
```

La eventual escalada a R0 por límite no negociable queda fuera de v0.1 y requiere autoridad separada.

## 6. No-alcance

No se autoriza:

- calcular o seleccionar baseline dentro de Rules;
- usar PRE001/PRE003/PR por analogía;
- hardcodear 10%;
- FX;
- normalización implícita;
- R0 automático;
- modificar R-PRE-001/003;
- modificar Price Intelligence;
- decisión empresarial automática.

**Estado final: AUTORIZADA.**
