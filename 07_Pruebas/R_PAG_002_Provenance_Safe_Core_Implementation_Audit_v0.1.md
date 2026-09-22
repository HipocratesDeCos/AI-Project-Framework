# EIOS — R-PAG-002 Provenance-Safe Core Implementation Audit v0.1

**Fecha:** 22/09/2026  
**Estado:** AUDIT 1 SUPERADA — CI PENDIENTE

## A1 — Semántica

La implementación utiliza solo condiciones ya autorizadas:

- P-PAG-004;
- offered vs P-PAG-001;
- baseline PAG002 financial state;
- minimum-term PAG002 financial state;
- resultado R1 / ALTA / COMPRAR CONDICIONADO.

## A2 — Provenance

Todos los carriers derivados se reconstruyen dentro de la misma ejecución.

No se aceptan:

- OfferedPaymentTermObservation desprendida;
- MinimumPaymentTermResolution desprendida;
- CounterfactualPaymentSchedule desprendido desde orquestador;
- PAG002FinancialStateResolution desprendida.

## A3 — Finance baseline

`ProvenancedFinanceBasicExecution` se revalida siempre, incluso en ramas de short-circuit.

## A4 — Counterfactual

Solo se construye si:

```text
offered < P-PAG-001
AND baseline = PAG002_FINANCIALLY_NON_VIABLE
```

## A5 — FALSE autorizado

- offered >= minimum;
- baseline ya viable;
- minimum-term sigue no viable.

## A6 — NOT_EVALUABLE

- control deshabilitado/no utilizable;
- terms no disponibles;
- baseline financiero no determinable;
- schedule no materializable;
- scenario financiero no determinable;
- multicuota.

## A7 — Integración

- catálogo: R-PAG-002 R1/ALTA/COMPRAR CONDICIONADO;
- `run_domain_rules`: nueva entrada `PaymentFinancialRuleInputs`;
- cobertura esperada: 21 reglas implementadas.

## A8 — Tests

Pruebas explícitas:

- TRUE baseline non-viable → scenario viable;
- FALSE plazo ya suficiente;
- FALSE baseline viable;
- FALSE scenario sigue no viable;
- P-PAG-004 disabled;
- multicuota;
- metadata.

## Dictamen

**AUDIT 1 SUPERADA — 0 BLOQUEADORES ESTÁTICOS PARA CI.**


## CI #1136 — depuración de fixture

CI #1136 sobre `a27a3e66649c6134506e9b228ba87d0cdb675e3c`: **FAILURE**.

Resultado:

- 2048 tests passed;
- 6 tests failed;
- SQL no ejecutado por fallo previo de Python.

Los seis fallos comparten una única causa en el fixture de `tests/test_rule_payment_risk.py`:

```text
Configuration.model_copy
→ AttributeError
```

`Configuration` es un dataclass, no un modelo Pydantic.

Corrección:

```text
dataclasses.replace(Configuration, value=...)
```

No se modifica:

- código productivo;
- fórmula;
- autoridad;
- provenance;
- estados TRUE/FALSE/NOT_EVALUABLE;
- integración del orquestador.

**DEPURACIÓN 1 APLICADA — NUEVA CI REQUERIDA.**
