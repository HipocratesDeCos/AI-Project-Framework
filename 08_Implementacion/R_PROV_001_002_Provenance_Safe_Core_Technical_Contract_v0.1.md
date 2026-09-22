# EIOS — R-PROV-001 / R-PROV-002 Provenance-Safe Core Technical Contract v0.1

**Baseline:** `main @ 08421400f62148d1513512f38e299fa0c1882f7a`  
**Fecha:** 22/09/2026  
**Estado:** CERRADO PARA MATERIALIZACIÓN  
**Autoridad funcional:** `01_Modelo/PROV_Supplier_Alternatives_Authority_v0.1.md`

## 1. Propósito

Materializar exclusivamente la semántica autorizada de `R-PROV-001` y `R-PROV-002` sin ampliar Supplier Evidence Core a valoración, ranking, scoring, selección ni recomendación de proveedor.

## 2. Frontera

```text
SupplierEvidenceInput
    ↓ reconstrucción obligatoria
evaluate_supplier_evidence
    ↓
SupplierEvidenceResult
    +
carriers PROV explícitos
    +
Evidence vinculada
    ↓
R-PROV-001 / R-PROV-002
    ↓
Assessment
```

La API pública de las reglas no acepta un `SupplierEvidenceResult` desprendido como autoridad.

## 3. Contratos autorizados

Se materializan:

- `SupplierAlternativeSetCoverage`
- `SupplierAlternativeOpportunityDetermination`
- `SupplierAlternativeComparabilityDetermination`
- `SupplierAlternativeSignificantImprovementDetermination`

Estados de cobertura:

```text
COMPLETE
PARTIAL
NOT_DETERMINABLE
```

Estados de oportunidad:

```text
POTENTIALLY_BETTER
NOT_POTENTIALLY_BETTER
NOT_DETERMINABLE
```

Estados de comparabilidad:

```text
COMPARABLE
NOT_COMPARABLE
NOT_DETERMINABLE
```

Estados de mejora significativa:

```text
SIGNIFICANT_IMPROVEMENT
NO_SIGNIFICANT_IMPROVEMENT
NOT_DETERMINABLE
```

Dimensiones autorizadas:

```text
PRICE
PAYMENT_TERM
COMMERCIAL_CONDITIONS
RELIABILITY
AVAILABILITY
```

## 4. Binding contextual

Toda cobertura se vincula como mínimo a:

```text
decision_id
scenario_id
data_snapshot_id
parameters_version
article_id
purchase_operation_ref
supplier_evidence_ref
authority_ref
methodology_ref
evidence_ids
trace_refs
```

Toda determinación por candidato se vincula además a:

```text
candidate_id
supplier_id
```

Los refs de operación, resultado Supplier y carriers se derivan determinísticamente de su contenido canónico.

## 5. Evidence binding

Una determinación concluyente exige evidencia `DEMONSTRATED` vinculada al carrier exacto mediante `demonstration_ref`.

`COMPLETE` exige evidencia explícita de cobertura.

Un carrier `NOT_DETERMINABLE` puede conservar gaps, pero nunca se promociona a una conclusión.

## 6. R-PROV-001

### TRUE

```text
existe CandidateResolution = EVIDENCED_CANDIDATE
AND la determinación del mismo candidate_id = POTENTIALLY_BETTER
→ TRUE
```

No requiere cobertura `COMPLETE`.

### FALSE

```text
coverage = COMPLETE
AND todo candidato del SupplierEvidenceInput está EVIDENCED_CANDIDATE
AND cada candidato tiene una determinación concluyente
AND todas = NOT_POTENTIALLY_BETTER
→ FALSE
```

### NOT_EVALUABLE

Cualquier hueco que impida la prueba positiva o la prueba negativa exhaustiva conserva `NOT_EVALUABLE`.

## 7. R-PROV-002

### TRUE

```text
existe CandidateResolution = EVIDENCED_CANDIDATE
AND mismo candidate_id:
    comparability = COMPARABLE
    significant_improvement = SIGNIFICANT_IMPROVEMENT
→ TRUE
```

### FALSE

```text
coverage = COMPLETE
AND todo candidato está EVIDENCED_CANDIDATE
AND cada candidato tiene comparabilidad concluyente
AND cada candidato tiene mejora concluyente
AND ningún candidato satisface COMPARABLE + SIGNIFICANT_IMPROVEMENT
→ FALSE
```

### NOT_EVALUABLE

Cobertura no completa, candidatura no evidenciada, carrier ausente o cualquier `NOT_DETERMINABLE` impide FALSE si no existe TRUE demostrado.

## 8. Independencia

Las reglas se ejecutan mediante bundles separados.

```text
R-PROV-001 no consume Assessment R-PROV-002
R-PROV-002 no consume Assessment R-PROV-001
```

Ambas reconstruyen Supplier Evidence de forma independiente.

## 9. Metadata

```text
R-PROV-001 → R2 / MEDIA
R-PROV-002 → R2 / ALTA
TRUE → NEGOCIAR
```

## 10. Prohibiciones

No se materializa:

- ranking;
- scoring;
- weights;
- proveedor ganador;
- proveedor recomendado;
- cambio automático de proveedor;
- umbrales numéricos;
- inferencia de `difference_decimal` a mejor/peor;
- promoción `STRUCTURALLY_COMPARABLE → COMPARABLE`;
- dependencia regla→regla;
- valoración mediante LLM;
- productor empresarial inventado de los carriers concluyentes.

## 11. Pruebas mínimas

Deben cubrir:

1. TRUE R-PROV-001 con cobertura parcial;
2. FALSE R-PROV-001 solo con COMPLETE + exhaustividad;
3. NOT_EVALUABLE por cobertura no completa;
4. NOT_EVALUABLE por candidato no evidenciado;
5. TRUE R-PROV-002 con mismo candidato;
6. FALSE R-PROV-002 solo con exhaustividad;
7. NOT_EVALUABLE por carrier indeterminado;
8. rechazo de candidate/supplier/context mismatch;
9. rechazo de `supplier_evidence_ref` falsificado;
10. rechazo de `purchase_operation_ref` falsificado;
11. rechazo de evidencia no vinculada al carrier exacto;
12. API sin `supplier_result` desprendido;
13. metadata de catálogo;
14. integración en orchestrator;
15. ausencia de scoring/ranking.

## 12. Dictamen

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ✅
AUDITAR 2     ✅
CERRAR        ✅
MATERIALIZAR  ▶
CI            ⏳
```
