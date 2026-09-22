# EIOS — PROV Supplier Alternatives Authority Proposal v0.1

**Baseline:** `main @ dc24eca3c652736115e259a827b86d7dfd7d206f`  
**Fecha:** 22/09/2026  
**Estado:** PROPUESTA — REQUIERE AUTORIDAD HUMANA  
**Reglas:** `R-PROV-001`, `R-PROV-002`

## 1. Reglas documentales vigentes

### R-PROV-001 — Existencia de proveedor alternativo

Condición:

```text
existe uno o más proveedores alternativos
con condiciones potencialmente mejores
```

Resultado:

```text
NEGOCIAR
```

Metadata:

```text
R2 / MEDIA
```

### R-PROV-002 — Proveedor actual con condiciones claramente desfavorables

Condición:

```text
existe una alternativa comparable
que mejora significativamente
precio / plazo / condiciones / fiabilidad / disponibilidad
```

Resultado:

```text
NEGOCIAR
```

Metadata:

```text
R2 / ALTA
```

## 2. Frontera con Supplier Evidence Core

Supplier Evidence Core ya puede demostrar:

- candidaturas alternativas actuales;
- identidad proveedor/artículo/contexto;
- observaciones factuales;
- comparabilidad estructural;
- deltas Decimal descriptivos cuando son compatibles.

Supplier Evidence Core **no autoriza**:

- que una diferencia sea mejor;
- que una mejora sea significativa;
- ranking;
- scoring;
- pesos;
- completitud del universo de proveedores;
- recomendación de proveedor.

Por tanto:

```text
STRUCTURALLY_COMPARABLE ≠ COMPARABLE PARA R-PROV-002
difference_decimal ≠ BETTER
EVIDENCED_CANDIDATE ≠ POTENTIALLY_BETTER
```

## 3. Cobertura del conjunto de alternativas

Se propone un carrier explícito:

```text
SupplierAlternativeSetCoverage
```

Estados:

```text
COMPLETE
PARTIAL
NOT_DETERMINABLE
```

`COMPLETE` significa únicamente que una autoridad upstream demuestra que el conjunto de candidatos evaluado cubre el universo aplicable definido para esa operación.

Supplier Evidence Core no puede fabricar `COMPLETE`.

Sin cobertura COMPLETE no se puede demostrar la inexistencia de una alternativa mejor.

## 4. Determinación de oportunidad por candidato — R-PROV-001

Se propone:

```text
SupplierAlternativeOpportunityDetermination
```

Estados:

```text
POTENTIALLY_BETTER
NOT_POTENTIALLY_BETTER
NOT_DETERMINABLE
```

Cada determinación debe estar vinculada a:

- candidate_id;
- supplier_id;
- PurchaseOperation exacta;
- SupplierEvidenceResult exacto;
- authority_ref;
- methodology_ref;
- evidence_ids;
- trace_refs.

La determinación puede usar dimensiones autorizadas, pero el core PROV no infiere signo ni preferencia.

## 5. Semántica propuesta R-PROV-001

### TRUE

```text
existe >= 1 CandidateResolution = EVIDENCED_CANDIDATE
AND existe una SupplierAlternativeOpportunityDetermination
    = POTENTIALLY_BETTER
para ese mismo candidato
→ TRUE
→ NEGOCIAR
```

No se exige cobertura COMPLETE para TRUE porque una alternativa mejor demostrada basta para probar existencia.

### FALSE

Solo si:

```text
SupplierAlternativeSetCoverage = COMPLETE
AND todos los candidatos aplicables están resueltos
AND ninguno = POTENTIALLY_BETTER
AND todos = NOT_POTENTIALLY_BETTER
→ FALSE
```

### NOT_EVALUABLE

Si no existe TRUE demostrado y ocurre cualquiera de:

- cobertura PARTIAL/NOT_DETERMINABLE;
- candidato no evidenciado/conflictivo;
- oportunidad NOT_DETERMINABLE;
- faltan determinaciones;
- contradicción de evidencia.

La ausencia de candidatos conocidos no implica FALSE salvo cobertura COMPLETE explícita.

## 6. Comparabilidad para R-PROV-002

Se propone un carrier:

```text
SupplierAlternativeComparabilityDetermination
```

Estados:

```text
COMPARABLE
NOT_COMPARABLE
NOT_DETERMINABLE
```

Puede consumir hechos estructurales del Supplier Evidence Core, pero la promoción a `COMPARABLE` requiere una autoridad específica.

No se autoriza:

```text
STRUCTURALLY_COMPARABLE → COMPARABLE
```

automáticamente.

## 7. Mejora significativa para R-PROV-002

Se propone:

```text
SupplierAlternativeSignificantImprovementDetermination
```

Estados:

```text
SIGNIFICANT_IMPROVEMENT
NO_SIGNIFICANT_IMPROVEMENT
NOT_DETERMINABLE
```

Dimensiones permitidas por la regla:

```text
PRICE
PAYMENT_TERM
COMMERCIAL_CONDITIONS
RELIABILITY
AVAILABILITY
```

La determinación global debe incluir las dimensiones que justifican su estado.

El core R-PROV-002 no decide:

- qué porcentaje de precio es significativo;
- cuántos días de plazo son significativos;
- qué cambio de condiciones es mejor;
- qué diferencia de fiabilidad/disponibilidad es material.

Eso pertenece a autoridades especializadas upstream.

## 8. Semántica propuesta R-PROV-002

### TRUE

```text
existe >= 1 EVIDENCED_CANDIDATE
AND comparability = COMPARABLE
AND significant_improvement = SIGNIFICANT_IMPROVEMENT
para el mismo candidato
→ TRUE
→ NEGOCIAR
```

No se crea ranking ni “mejor proveedor”.

### FALSE

Solo con cobertura:

```text
SupplierAlternativeSetCoverage = COMPLETE
AND todos los candidatos aplicables están determinados
AND ninguno satisface simultáneamente:
    COMPARABLE
    + SIGNIFICANT_IMPROVEMENT
→ FALSE
```

### NOT_EVALUABLE

Si no existe TRUE demostrado y:

- cobertura no COMPLETE;
- comparabilidad indeterminada;
- mejora significativa indeterminada;
- candidato no evidenciado/conflictivo;
- determinaciones faltantes o contradictorias.

## 9. Independencia entre R-PROV-001 y R-PROV-002

```text
POTENTIALLY_BETTER ≠ SIGNIFICANT_IMPROVEMENT
```

Por tanto:

- R-PROV-001 puede ser TRUE y R-PROV-002 FALSE;
- R-PROV-001 puede ser TRUE y R-PROV-002 NOT_EVALUABLE;
- R-PROV-002 TRUE implica necesariamente una alternativa relevante para negociación, pero el core no deriva automáticamente el Assessment de R-PROV-001 desde R-PROV-002; cada regla reconstruye su propia autoridad.

No se crea dependencia regla → regla.

## 10. Evidencia y provenance

Las futuras reglas deben reconstruir o revalidar internamente desde:

```text
SupplierEvidenceInput
→ evaluate_supplier_evidence
→ SupplierEvidenceResult
```

más:

- SupplierAlternativeSetCoverage;
- OpportunityDetermination;
- ComparabilityDetermination;
- SignificantImprovementDetermination;

todos vinculados al mismo contexto y candidatos exactos.

No se aceptan resultados Supplier Evidence desprendidos como única autoridad si la frontera pública exige reconstrucción provenance-safe.

## 11. Dimensiones y Supplier Evidence

Mapeo conceptual permitido, no valorativo:

```text
PRICE                 ↔ PRICE_REFERENCE
PAYMENT_TERM          ↔ PAYMENT_TERM
COMMERCIAL_CONDITIONS ↔ COMMERCIAL_CONDITION
RELIABILITY           ↔ RELIABILITY_REFERENCE
AVAILABILITY          ↔ AVAILABILITY
```

El mapeo solo identifica dominio factual.

No autoriza el criterio “better/significant”.

## 12. Resultado oficial

Para ambas reglas:

```text
TRUE → NEGOCIAR
```

La “evaluación de proveedor alternativo” permanece acción secundaria, no resultado oficial adicional.

## 13. No alcance

No se autoriza:

- ranking de proveedores;
- puntuación;
- pesos;
- ganador;
- recomendación de proveedor;
- umbral numérico de mejora;
- conversión de difference_decimal a mejor/peor;
- LLM para valorar condiciones;
- comparación de texto libre;
- asumir universo completo de proveedores;
- inferir FALSE por ausencia de candidatos;
- ejecutar cambio de proveedor.

## 14. Gates propuestos

```text
PROV-G01 → candidate existence uses EVIDENCED_CANDIDATE
PROV-G02 → explicit alternative-set coverage
PROV-G03 → R-PROV-001 uses explicit opportunity determination
PROV-G04 → R-PROV-001 FALSE requires COMPLETE coverage
PROV-G05 → explicit PROV comparability determination
PROV-G06 → explicit significant-improvement determination
PROV-G07 → R-PROV-002 FALSE requires COMPLETE coverage
PROV-G08 → structural delta never promoted to better/significant
PROV-G09 → no ranking/scoring
PROV-G10 → provenance-safe reconstruction boundary
```

## 15. Decisión requerida

Autorizar o corregir esta propuesta antes de materializar R-PROV-001 / R-PROV-002.
