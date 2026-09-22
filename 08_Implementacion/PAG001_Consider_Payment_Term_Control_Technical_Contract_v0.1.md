# EIOS — PAG001 Consider Payment-Term Control Technical Contract v0.1

**Autoridad:** `01_Modelo/PAG001_Consider_Payment_Term_Control_Authority_v0.1.md`  
**Estado:** DISEÑO TÉCNICO MATERIALIZADO — CI PENDIENTE

## 1. Componente

Se materializa `resolve_payment_term_control`.

Consume:

- `DecisionContext`;
- company_scope;
- evaluation_date;
- `ResolvedConfiguration(P-PAG-004)`;
- `ParameterConfigurationEvidence(P-PAG-004)`.

Produce `PaymentTermControlResolution`.

## 2. Estados

```text
ENABLED
DISABLED
NOT_EVALUABLE
```

## 3. Códigos de razón

```text
PAYMENT_TERM_CRITERION_ENABLED
PAYMENT_TERM_CRITERION_DISABLED
MISSING_CONTROL_CONFIGURATION
INVALID_CONTROL_CONFIGURATION
INVALID_CONTROL_EVIDENCE
```

## 4. Valores autorizados

```text
Sí → ENABLED
No → DISABLED
```

No existen aliases.

## 5. Provenance

Se valida:

- parameter_id exacto;
- company_scope;
- parameters_version;
- effective_at.date = evaluation_date;
- vigencia;
- Evidence DEMONSTRATED;
- source_type exacto;
- captured_at exacto;
- demonstration_ref exacto.

## 6. Semántica

DISABLED es una configuración válida de política.

No crea outcome FALSE.

NOT_EVALUABLE se reserva para ausencia, configuración inválida o evidencia inválida.

## 7. No alcance

No implementa:

- comparator R-PAG-001;
- bundle conjunto PAG001;
- P-PAG-005;
- R-PAG-002;
- multicuota;
- CRC.
