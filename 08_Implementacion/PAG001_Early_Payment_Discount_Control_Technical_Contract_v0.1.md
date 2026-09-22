# EIOS — PAG001 Early-Payment Discount Control Technical Contract v0.1

**Authority:** `01_Modelo/PAG001_Early_Payment_Discount_Control_Authority_v0.1.md`  
**State:** MATERIALIZED — CI PENDING

## Component

`resolve_early_payment_discount_control`

Inputs:

- DecisionContext;
- company_scope;
- evaluation_date;
- ResolvedConfiguration(P-PAG-005);
- ParameterConfigurationEvidence(P-PAG-005).

Output:

`EarlyPaymentDiscountControlResolution`.

## States

```text
ENABLED
DISABLED
NOT_EVALUABLE
```

## Canonical values

```text
Sí → ENABLED
No → DISABLED
```

No aliases.

## Provenance

Validates exact parameter identity, company, parameters_version, effective date, active interval, evidence type, capture date, evidence validity and exact configuration reference.

## Architectural boundary

This component does not calculate or expose:

- discount percentage;
- discount amount;
- annualized yield;
- effective cost;
- payment-term equivalence.

Its state is independent from the core R-PAG-001 comparator.
