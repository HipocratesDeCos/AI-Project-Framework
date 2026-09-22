# EIOS — PAG002 Minimum-Term & Financial-State Technical Contract v0.1

**Authority:** `01_Modelo/PAG002_Financial_Viability_Counterfactual_Authority_v0.1.md`  
**State:** MATERIALIZED — CI PENDING

## 1. P-PAG-001 resolver

`resolve_minimum_payment_term` consumes:

```text
DecisionContext
ResolvedConfiguration(P-PAG-001)
ParameterConfigurationEvidence(P-PAG-001)
```

and emits:

```text
MinimumPaymentTermResolution
AVAILABLE / NOT_EVALUABLE
```

No hardcodes 60 days.

## 2. PAG002 financial-state classifier

`classify_pag002_financial_state` consumes:

```text
ProvenancedFinanceBasicExecution
FinanceBasicResultEvidence
ResolvedConfiguration(P-FIN-002)
ParameterConfigurationEvidence(P-FIN-002)
```

and emits only:

```text
PAG002_FINANCIALLY_VIABLE
PAG002_FINANCIALLY_NON_VIABLE
PAG002_FINANCIAL_STATE_NOT_DETERMINABLE
```

## 3. Comparator

```text
capacity >= P-FIN-002 → PAG002_FINANCIALLY_VIABLE
capacity <  P-FIN-002 → PAG002_FINANCIALLY_NON_VIABLE
```

No viabilidad global is published.

## 4. Boundary

This materialization does not:

- generate minimum-term due dates;
- build the baseline/minimum-term counterfactual pair;
- certify single-change provenance;
- execute R-PAG-002;
- normalize installments.

`PAG002-CF-DUE-DATE` remains OPEN.
