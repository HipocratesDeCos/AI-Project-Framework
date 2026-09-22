# EIOS — R-PAG-001 Provenance-Safe Core Technical Contract v0.1

**Baseline:** `main @ 40b488bebc87d398f3dbbb879550bf95caa59f1e`  
**Fecha:** 22/09/2026  
**Estado:** MATERIALIZADO — CI PENDIENTE

## 1. Condición autorizada

```text
offered_payment_term_days < effective_threshold_days
```

donde:

```text
effective_threshold_days = P-PAG-002 - P-PAG-003
```

Igualdad con el umbral → FALSE.

## 2. Control P-PAG-004

```text
ENABLED  → continuar evaluación
DISABLED → NOT_EVALUABLE / criterio deshabilitado
invalid  → NOT_EVALUABLE
```

## 3. Provenance-safe assembly

La regla no acepta como autoridad suficiente resultados derivados desprendidos.

Reconstruye dentro de la misma invocación:

```text
SupplierEvidenceResult
+ PaymentTermSemanticAuthority
→ OfferedPaymentTermObservation

ResolvedConfiguration(P-PAG-002/P-PAG-003)
+ ParameterConfigurationEvidence
→ PaymentTermToleranceResolution

ResolvedConfiguration(P-PAG-004)
+ ParameterConfigurationEvidence
→ PaymentTermControlResolution
```

## 4. Identidad

Se exige coherencia exacta de:

- decision_id;
- scenario_id;
- rules_version;
- parameters_version;
- data_snapshot_id;
- article_id;
- supplier_id;
- evaluation_date.

## 5. P-PAG-005

No es input del core.

Su control económico puede ejecutarse separadamente y no altera TRUE/FALSE del comparador de plazo.

## 6. Estados

### TRUE

```text
offered < threshold
```

### FALSE

```text
offered >= threshold
```

### NOT_EVALUABLE

- P-PAG-004 deshabilitado;
- P-PAG-004 no utilizable;
- plazo ofrecido no disponible/conflictivo/no determinable;
- threshold no disponible/no evaluable.

## 7. Metadata

```text
R-PAG-001
effect = R2
severity = ALTA
active_result = NEGOCIAR
```

## 8. No alcance

- P-PAG-005 economic enrichment;
- R-PAG-002;
- multiquota normalization;
- CRC policy changes;
- finance equivalence.
