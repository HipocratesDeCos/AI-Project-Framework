# EIOS — DAT003 Insufficient Data Authority v0.1

**Baseline de autorización:** `main @ 2ef6d47bb280fc37fbee5beb6a654f063e8dee10`  
**Fecha:** 21/09/2026  
**Estado:** AUTORIZADO  
**Ámbito:** `R-DAT-003 — Datos insuficientes`

## 1. Autoridad humana explícita

Se autoriza la semántica propuesta para `R-DAT-003`, con la corrección de precisión definida en este documento.

No se autoriza por esta versión ninguna relación directa:

```text
P-DAT-003 → R-DAT-003
P-DAT-007 → R-DAT-003
```

## 2. Principio normativo

`R-DAT-003` evalúa exclusivamente si el conjunto de requisitos de evidencia previamente declarado como necesario para una evaluación fiable está suficientemente cubierto.

DAT003 no inventa qué requisitos son necesarios.

La autoridad sobre qué requisitos integran el conjunto pertenece al `DecisionEvidenceRequirementSet` aplicable.

## 3. Requirement Set

`DecisionEvidenceRequirementSet` debe identificar, como mínimo:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
purchase_operation_ref
effective_date
requirement_set_id
requirement_set_version
requirement_ids
authority_ref
methodology_ref
trace_refs
```

El conjunto debe ser explícito, estable, trazable y vinculado a la operación/contexto exactos.

Un conjunto vacío no constituye por sí solo prueba de suficiencia. Si la autoridad aplicable no define requisitos, DAT003 no debe fabricar una conclusión favorable.

## 4. Carrier factual

`DecisionEvidenceSufficiencyObservation`:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
purchase_operation_ref
evaluation_date
requirement_set_ref
required_requirement_ids
satisfied_requirement_ids
failed_requirement_ids
undetermined_requirement_ids
state
source_ref
authority_ref
methodology_ref
trace_refs
```

Estados:

```text
AVAILABLE
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

## 5. Corrección autorizada — failed vs undetermined

La propuesta inicial utilizaba `unsatisfied_requirement_ids`.

Se corrige por precisión semántica a:

```text
failed_requirement_ids
undetermined_requirement_ids
```

### failed_requirement_ids

Se usa solo cuando existe evidencia válida y suficiente para demostrar que el requisito exigido **no se cumple**.

No representa ausencia de evidencia.

### undetermined_requirement_ids

Se usa cuando el requisito no puede determinarse de forma fiable por:

- Evidence ausente;
- Evidence en GAP;
- contradicción;
- provenance no demostrable;
- estado no determinable;
- otra causa que impida concluir cumplimiento o incumplimiento.

Por tanto:

```text
GAP ≠ failed
GAP → undetermined
```

Esta separación evita convertir ausencia de evidencia en un FALSE encubierto.

## 6. Productor factual

`DecisionEvidenceSufficiencyProducer`:

- recibe un RequirementSet explícito;
- recibe bindings explícitos requirement → Evidence;
- valida identidad/provenance;
- clasifica cada requirement como satisfied, failed o undetermined;
- no inventa requirements;
- no asigna criticidad;
- no reutiliza Evidence para otro requisito sin binding explícito;
- no consulta QTG para completar gaps;
- no resuelve contradicciones con promedio, prioridad arbitraria o último valor.

## 7. Invariantes del carrier

Para `AVAILABLE`:

- `required_requirement_ids` debe ser no vacío;
- los tres subconjuntos deben ser disjuntos;
- su unión debe ser exactamente igual a `required_requirement_ids`;
- no puede existir requirement desconocido;
- no puede omitirse requirement requerido.

Para estados distintos de `AVAILABLE`, no se publica una clasificación parcial como si fuera completa.

## 8. Frontera autorizada de R-DAT-003

Con carrier `AVAILABLE` y provenance válida:

```text
failed_requirement_ids != ∅
OR
undetermined_requirement_ids != ∅
    → EVALUABLE / TRUE

satisfied_requirement_ids == required_requirement_ids
AND failed_requirement_ids == ∅
AND undetermined_requirement_ids == ∅
    → EVALUABLE / FALSE
```

Carrier no AVAILABLE → `NOT_EVALUABLE`.

RequirementSet ausente, vacío, contradictorio, incompatible o no trazable → `NOT_EVALUABLE`.

## 9. Significado de resultados

TRUE:

> Existe al menos un requisito explícitamente necesario para una evaluación fiable que está demostrado como incumplido o no puede determinarse de forma fiable.

FALSE:

> Todos los requisitos explícitamente necesarios del RequirementSet aplicable están demostrados como satisfechos.

NOT_EVALUABLE:

> No puede evaluarse de forma provenance-safe la suficiencia del conjunto.

## 10. Resultado funcional y metadata

```text
R-DAT-003 → R0 / CRÍTICA
```

TRUE representa la condición funcional:

`INFORMACIÓN INSUFICIENTE`.

No equivale a `NO COMPRAR`.

La CRC conserva autoridad sobre el resultado consolidado.

## 11. Relación con QTG

QTG y DAT003 permanecen separados.

No se autoriza:

```text
QTG NO_APTO → R-DAT-003 TRUE
R-DAT-003 TRUE → QTG NO_APTO
```

sin autoridad específica de integración.

## 12. Relación con DAT001/DAT002

```text
dato antiguo ≠ dato insuficiente
dato reciente ≠ dato suficiente
```

DAT003 no consume automáticamente resultados de DAT001/DAT002.

## 13. Parámetros fuera de alcance v0.1

No se consumen:

- `P-DAT-003`;
- `P-DAT-007`.

Su relación futura con DAT003 requerirá autoridad separada.

## 14. Fail-closed

DAT003 devuelve `NOT_EVALUABLE` si:

- falta RequirementSet autorizado;
- RequirementSet vacío;
- binding de identidad incompatible;
- existen dos RequirementSets incompatibles;
- no puede verificarse requirement → Evidence;
- el carrier no puede cerrarse sin inferencia;
- provenance es inválida.

## 15. No-alcance

No autoriza:

- productor operacional universal de RequirementSet;
- QTG operacional;
- parámetros DAT003;
- escalas de fiabilidad nuevas;
- conteos mínimos globales;
- inferir criticidad;
- imputar Evidence;
- seleccionar datos alternativos;
- sustituir CRC;
- automatizar la decisión humana.

## 16. Gates

```text
DAT003-G01 → CERRADO
DAT003-G02 → CERRADO
DAT003-G03 → CERRADO
DAT003-G04 → CERRADO
DAT003-G05 → CERRADO
DAT003-G06 → CERRADO
```

## 17. Estado

**DAT003 Insufficient Data Authority v0.1 — AUTORIZADO Y CORREGIDO.**
