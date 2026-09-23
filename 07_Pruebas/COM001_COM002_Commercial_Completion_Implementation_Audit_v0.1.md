# EIOS — Commercial COM001/COM002 Implementation Audit v0.1

**Fecha:** 23/09/2026  
**Estado:** AUDIT DE IMPLEMENTACIÓN — SUPERADA PARA CI

## 1. COM001

Materializado `DiscountOpportunityEvidence` con estados separados de oportunidad y aplicabilidad.

Solo:

```text
AVAILABLE + CONFIRMED + refs DEMONSTRATED
→ EVALUABLE / TRUE
```

`NOT_AVAILABLE` exige demostración concluyente para FALSE.

Estados condicionados, conflictivos o indeterminados → NOT_EVALUABLE.

**Resultado:** CONFORME.

## 2. COM002

Materializado `RappelApplicabilityEvidence` y productor interno `build_rappel_effective_cost(...)`.

Fórmula exacta:

```text
rebate_amount = eligible_base_amount * rebate_rate_pct / 100
effective_cost_after_rappel = quantity * unit_price - rebate_amount
```

Decimal sin redondeo decisional implícito.

Currency, identidad y evidence binding se revalidan.

**Resultado:** CONFORME.

## 3. CRC

```text
R-COM-001 = R2 / MEDIA / NEGOCIAR
R-COM-002 = R3 / MEDIA / active_result=None
```

COM002 no modifica por sí solo el resultado consolidado.

**Resultado:** CONFORME.

## 4. Fronteras

No se reutilizan:

- COMMERCIAL_CONDITION como prueba automática;
- P-PAG-005;
- P-MGE-006;
- CEA/TCO archivado;
- Scenario Engine.

**Resultado:** PRESERVADO.

## 5. Orchestrator

Bundles opcionales separados:

- `CommercialDiscountRuleInputs`;
- `CommercialRappelRuleInputs`.

Sin bundle → omitted.

**Resultado:** CONFORME.

## 6. Dictamen

```text
EXPLORAR       ✅
CONSOLIDAR     ✅
AUTORIZAR      ✅
AUDITAR        ✅
MATERIALIZAR  ✅
CI            ⏳
```

**Bloqueadores estáticos: 0.**
