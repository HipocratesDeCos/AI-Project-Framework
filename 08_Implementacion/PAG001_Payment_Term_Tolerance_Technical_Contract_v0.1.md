# EIOS — PAG001 Payment-Term Tolerance Technical Contract v0.1

**Autoridad:** `01_Modelo/PAG001_Payment_Term_Tolerance_Authority_v0.1.md`  
**Estado:** DISEÑO TÉCNICO MATERIALIZADO — CI PENDIENTE

## 1. Componente

Se materializa `resolve_payment_term_tolerance` como transformación independiente de Rules.

Consume:

- `DecisionContext`;
- company_scope;
- evaluation_date;
- `ResolvedConfiguration(P-PAG-002)`;
- `ParameterConfigurationEvidence(P-PAG-002)`;
- `ResolvedConfiguration(P-PAG-003)`;
- `ParameterConfigurationEvidence(P-PAG-003)`.

Produce `PaymentTermToleranceResolution`.

## 2. Fórmula

```text
effective_threshold_days = target_days - tolerance_days
```

No se ejecuta `R-PAG-001` en este componente.

## 3. Estados

```text
AVAILABLE
NOT_EVALUABLE
```

Códigos de razón:

- AVAILABLE;
- MISSING_CONFIGURATION;
- INVALID_CONFIGURATION;
- INCOHERENT_CONFIGURATION;
- INVALID_EVIDENCE.

## 4. Coherencia obligatoria

P-PAG-002 y P-PAG-003 deben compartir:

- company_id = company_scope;
- parameters_version = DecisionContext.parameters_version;
- effective_at exacto;
- effective_at.date = evaluation_date.

Cada configuración se revalida contra valid_from/valid_to.

## 5. Evidencia

Cada configuración exige Evidence:

```text
source_type = ParameterConfigurationEvidence
state       = DEMONSTRATED
captured_at = evaluation_date
demonstration_ref = resolved.configuration_ref
```

Los evidence_id deben ser distintos.

## 6. Dominio

Requiere:

```text
unit(target)    = días
unit(tolerance) = días
target >= 0
tolerance >= 0
tolerance <= target
```

No se convierten unidades ni se corrigen valores.

## 7. Límites

No implementa:

- OfferedPaymentTerm comparator;
- R-PAG-001;
- P-PAG-004;
- P-PAG-005;
- R-PAG-002;
- multicuota;
- valores empresariales concretos.
