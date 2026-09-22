# EIOS — PROV Supplier Alternatives Authority v0.1

**Baseline de autorización:** `main @ 61d54646871e2b2f7a9fcab861180289da54c65e`  
**Fecha:** 22/09/2026  
**Estado:** AUTORIZADO Y CORREGIDO  
**Reglas:** `R-PROV-001`, `R-PROV-002`

## 1. Autoridad humana

Se autoriza la propuesta `PROV Supplier Alternatives Authority v0.1` con las correcciones y salvaguardas de este documento.

La autoridad cubre exclusivamente la semántica mínima necesaria para evaluar existencia de alternativas, oportunidad potencial, comparabilidad comercial y mejora significativa sin crear ranking, scoring ni recomendación automática de proveedor.

## 2. Frontera con Supplier Evidence Core

Supplier Evidence Core puede demostrar hechos, candidaturas y comparabilidad estructural.

No autoriza por sí solo:

- que una alternativa sea mejor;
- que una mejora sea significativa;
- ranking o scoring;
- completitud del universo;
- recomendación o selección de proveedor.

Se conserva:

```text
STRUCTURALLY_COMPARABLE ≠ COMPARABLE
difference_decimal ≠ BETTER
EVIDENCED_CANDIDATE ≠ POTENTIALLY_BETTER
POTENTIALLY_BETTER ≠ SIGNIFICANT_IMPROVEMENT
```

## 3. Cobertura del conjunto de alternativas

Carrier autorizado:

```text
SupplierAlternativeSetCoverage
```

Estados:

```text
COMPLETE
PARTIAL
NOT_DETERMINABLE
```

`COMPLETE` exige autoridad upstream explícita que demuestre que el conjunto evaluado cubre el universo aplicable definido para la operación.

Supplier Evidence Core no puede fabricar `COMPLETE`.

La ausencia de candidatos conocidos nunca equivale por sí sola a ausencia demostrada de alternativas.

## 4. R-PROV-001 — Oportunidad potencial

Carrier autorizado:

```text
SupplierAlternativeOpportunityDetermination
```

Estados:

```text
POTENTIALLY_BETTER
NOT_POTENTIALLY_BETTER
NOT_DETERMINABLE
```

Cada determinación debe quedar vinculada al mismo:

```text
decision_id
scenario_id
data_snapshot_id
parameters_version
article_id
purchase_operation_ref
candidate_id
supplier_id
supplier_evidence_ref
authority_ref
methodology_ref
evidence_ids
trace_refs
```

### TRUE

```text
>= 1 EVIDENCED_CANDIDATE
AND misma candidatura = POTENTIALLY_BETTER
→ R-PROV-001 TRUE
→ NEGOCIAR
```

No requiere cobertura COMPLETE.

### FALSE

Solo si:

```text
coverage = COMPLETE
AND todos los candidatos aplicables están resueltos
AND todos = NOT_POTENTIALLY_BETTER
→ R-PROV-001 FALSE
```

### NOT_EVALUABLE

Si no existe TRUE demostrado y ocurre cualquiera de:

- cobertura distinta de COMPLETE;
- candidato aplicable no resuelto;
- oportunidad NOT_DETERMINABLE;
- determinación ausente;
- contradicción de evidencia;
- identidad o provenance incongruente.

## 5. R-PROV-002 — Comparabilidad comercial

Carrier autorizado:

```text
SupplierAlternativeComparabilityDetermination
```

Estados:

```text
COMPARABLE
NOT_COMPARABLE
NOT_DETERMINABLE
```

No se autoriza:

```text
STRUCTURALLY_COMPARABLE → COMPARABLE
```

de forma automática.

Toda promoción a `COMPARABLE` requiere autoridad específica y trazable.

## 6. R-PROV-002 — Mejora significativa

Carrier autorizado:

```text
SupplierAlternativeSignificantImprovementDetermination
```

Estados:

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

La determinación debe indicar qué dimensiones justifican su estado.

No se autoriza inventar:

- umbral porcentual;
- días mínimos;
- pesos;
- score;
- reglas de preferencia;
- interpretación semántica libre.

## 7. Semántica R-PROV-002

### TRUE

```text
>= 1 EVIDENCED_CANDIDATE
AND misma candidatura:
    comparability = COMPARABLE
    significant_improvement = SIGNIFICANT_IMPROVEMENT
→ R-PROV-002 TRUE
→ NEGOCIAR
```

### FALSE

Solo si:

```text
coverage = COMPLETE
AND todos los candidatos aplicables están determinados
AND ninguno satisface simultáneamente:
    COMPARABLE
    + SIGNIFICANT_IMPROVEMENT
→ R-PROV-002 FALSE
```

Para cerrar FALSE no puede quedar ningún candidato aplicable con comparabilidad o mejora en `NOT_DETERMINABLE`.

### NOT_EVALUABLE

Si no existe TRUE demostrado y ocurre cualquiera de:

- cobertura distinta de COMPLETE;
- candidatura aplicable no resuelta;
- comparabilidad NOT_DETERMINABLE;
- mejora NOT_DETERMINABLE;
- determinaciones ausentes;
- contradicción;
- provenance inválido.

## 8. Independencia entre reglas

R-PROV-001 y R-PROV-002 permanecen independientes.

No se autoriza derivar el Assessment de una regla desde el Assessment de la otra.

```text
R-PROV-001 TRUE ≠ R-PROV-002 TRUE
R-PROV-002 TRUE no se copia como R-PROV-001 TRUE
```

Cada regla reconstruye y valida su propia autoridad desde las entradas autorizadas.

## 9. Provenance

La futura frontera ejecutable debe reconstruir o revalidar internamente:

```text
SupplierEvidenceInput
→ evaluate_supplier_evidence
→ SupplierEvidenceResult
```

más las determinaciones PROV aplicables.

Debe verificarse identidad estricta entre:

- operación;
- artículo;
- candidato;
- proveedor;
- decisión;
- escenario;
- snapshot;
- versión de parámetros;
- evidencia;
- autoridad;
- metodología.

No se aceptan carriers desprendidos o pertenecientes a otra operación/candidatura como autoridad suficiente.

## 10. Regla de suficiencia para FALSE

Esta salvaguarda queda cerrada de forma transversal:

```text
FALSE requiere prueba exhaustiva negativa
```

Por tanto:

```text
PARTIAL / NOT_DETERMINABLE coverage
→ nunca FALSE
```

y:

```text
cualquier candidato aplicable sin determinación concluyente
→ nunca FALSE
```

salvo que ya exista un TRUE positivo demostrado para la regla correspondiente.

## 11. Resultado oficial

Para ambas reglas:

```text
TRUE → NEGOCIAR
```

No se crea ningún nuevo resultado oficial de CRC.

La evaluación de proveedores puede existir como soporte explicativo, pero no como decisión automática de selección o cambio.

## 12. No alcance

No se autoriza:

- ranking;
- scoring;
- ponderaciones;
- ganador;
- proveedor recomendado;
- cambio automático de proveedor;
- umbrales numéricos nuevos;
- interpretación libre de textos;
- LLM para valorar condiciones;
- inferir better/significant desde un delta bruto;
- asumir universo completo;
- inferir FALSE por ausencia de candidatos;
- dependencia regla → regla.

## 13. Materialización autorizada

Se autoriza materializar:

- contratos de cobertura y determinaciones;
- enums y validadores;
- agregadores deterministas;
- fronteras provenance-safe;
- bridges para R-PROV-001 y R-PROV-002;
- tests positivos, negativos y de mismatch.

No se autoriza inventar productores empresariales de `POTENTIALLY_BETTER`, `COMPARABLE` o `SIGNIFICANT_IMPROVEMENT` cuando no exista autoridad upstream.

En ausencia de dicha autoridad, el estado correspondiente debe ser `NOT_DETERMINABLE`.

## 14. Gates

```text
PROV-G01 → CLOSED — candidate existence usa EVIDENCED_CANDIDATE
PROV-G02 → CLOSED — cobertura explícita
PROV-G03 → CLOSED — R-PROV-001 usa determinación explícita
PROV-G04 → CLOSED — FALSE R-PROV-001 exige COMPLETE + exhaustividad
PROV-G05 → CLOSED — comparabilidad PROV explícita
PROV-G06 → CLOSED — mejora significativa explícita
PROV-G07 → CLOSED — FALSE R-PROV-002 exige COMPLETE + exhaustividad
PROV-G08 → CLOSED — delta estructural no se promociona
PROV-G09 → CLOSED — sin ranking/scoring
PROV-G10 → CLOSED — frontera provenance-safe
PROV-G11 → CLOSED — reglas independientes
PROV-G12 → CLOSED — mismatch de identidad falla cerrado
```

## 15. Estado

**PROV Supplier Alternatives Authority v0.1 — AUTORIZADO Y CORREGIDO.**
