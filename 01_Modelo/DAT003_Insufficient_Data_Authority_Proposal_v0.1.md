# EIOS — DAT003 Insufficient Data Authority Proposal v0.1

**Baseline:** `main @ 2ef6d47bb280fc37fbee5beb6a654f063e8dee10`  
**Fecha:** 21/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** `R-DAT-003 — Datos insuficientes`

## 1. Propósito

Definir la semántica mínima para evaluar cuándo la información disponible no permite sostener una evaluación fiable, sin:

- confundir antigüedad con insuficiencia;
- duplicar Quality & Trust Gate;
- convertir cualquier GAP en bloqueo global;
- inventar qué evidencias son críticas;
- inferir consumidores para `P-DAT-003` o `P-DAT-007`.

## 2. Autoridad vigente

La Matriz de Reglas define:

```text
R-DAT-003 — Datos insuficientes
Condición:
No existe información suficiente para realizar una evaluación fiable.

Resultado:
INFORMACIÓN INSUFICIENTE

Metadata:
R0 — BLOQUEO / CRÍTICA respecto a la fiabilidad
```

El Evidence Contract establece que la suficiencia es una propiedad de la evidencia respecto del requisito para el que se utiliza.

También establece:

```text
GAP ≠ TRUE
GAP ≠ FALSE
GAP ≠ NO COMPRAR
```

## 3. Gaps documentales confirmados

No existe actualmente un manifiesto canónico de requisitos críticos de evidencia para una decisión concreta.

No existe una relación autorizada:

```text
P-DAT-003 → R-DAT-003
P-DAT-007 → R-DAT-003
```

Además:

- `P-DAT-003` está expresamente sin consumidor directo demostrado;
- `P-DAT-007` permanece pendiente de cruce documental;
- QTG es una capacidad Core separada y su salida no es una evaluación de regla.

Por tanto, DAT003 no puede inferir ni consumidor de parámetro ni criticidad de evidencia por similitud semántica.

## 4. Carrier factual propuesto

Se propone:

`DecisionEvidenceSufficiencyObservation`

Campos mínimos:

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
unsatisfied_requirement_ids
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

## 5. Regla esencial de autoridad

El carrier NO decide qué requisito es necesario para una evaluación fiable.

Debe recibir un conjunto de requisitos ya declarado por una autoridad upstream explícita:

`DecisionEvidenceRequirementSet`

Ese conjunto debe estar vinculado a:

- decisión;
- escenario;
- snapshot;
- operación;
- company scope;
- versión/metodología.

El productor factual solo materializa cobertura respecto de ese conjunto.

## 6. Productor factual propuesto

`DecisionEvidenceSufficiencyProducer`

Responsabilidad:

- recibir un `DecisionEvidenceRequirementSet` explícito;
- recibir evidencias asociadas a cada requirement id;
- clasificar cada requisito como satisfecho, no satisfecho o indeterminado conforme al Evidence Contract;
- conservar provenance;
- no inventar requisitos;
- no asignar criticidad;
- no reutilizar una Evidence para otro requisito sin binding explícito;
- no resolver contradicciones mediante heurística;
- no consultar QTG para rellenar gaps.

## 7. Semántica propuesta de satisfacción

Un requisito puede considerarse satisfecho únicamente cuando:

- existe Evidence vinculada al requirement exacto;
- Evidence es admisible/VALID;
- su estado demuestra el requisito aplicable;
- identity/provenance coinciden con la decisión evaluada.

Un requisito no satisfecho es aquel requerido cuya Evidence vinculada existe pero no demuestra el requisito.

Un requisito indeterminado es aquel requerido cuya evaluación no puede resolverse por ausencia, contradicción o estado no determinable.

## 8. Frontera propuesta para R-DAT-003

Si el carrier es AVAILABLE:

```text
unsatisfied_requirement_ids != ∅
OR
undetermined_requirement_ids != ∅
    → EVALUABLE / TRUE

todos los required_requirement_ids están satisfechos
    → EVALUABLE / FALSE
```

Estados:

```text
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

→ `NOT_EVALUABLE`.

## 9. Interpretación funcional

TRUE significa exclusivamente:

> Existe al menos un requisito de evidencia previamente declarado como necesario para una evaluación fiable que no está satisfecho o no puede determinarse.

FALSE significa exclusivamente:

> Todos los requisitos del conjunto autorizado están satisfechos.

NOT_EVALUABLE significa:

> No puede determinarse de forma provenance-safe el estado de suficiencia.

## 10. Resultado y metadata

```text
R-DAT-003 → R0 / CRÍTICA
```

Un TRUE produce la condición funcional autorizada:

`INFORMACIÓN INSUFICIENTE`

pero DAT003 no debe convertir por sí misma ese resultado en una política QTG adicional ni inventar una recomendación empresarial sustantiva.

## 11. Relación con QTG

QTG y DAT003 tienen ámbitos distintos:

```text
QTG:
calidad/confianza global de entrada

DAT003:
regla normativa sobre cobertura de requisitos explícitamente requeridos para evaluación fiable
```

No se autoriza:

```text
QTG NO_APTO → R-DAT-003 TRUE
R-DAT-003 TRUE → QTG NO_APTO
```

sin una autoridad de integración específica.

## 12. Relación con DAT001/DAT002

```text
dato antiguo ≠ dato insuficiente
dato reciente ≠ dato suficiente
```

DAT003 no consume directamente el carrier de frescura salvo que un RequirementSet autorizado incluya explícitamente un requisito temporal y exista Evidence vinculada a él.

No se infiere esa inclusión.

## 13. Parámetros

En v0.1 se propone NO consumir:

- `P-DAT-003 — Nº mínimo de registros históricos`;
- `P-DAT-007 — Nivel mínimo de fiabilidad para recomendación`.

Razones:

- no existe relación parámetro → regla confirmada;
- `P-DAT-003` no sustituye mínimos especializados como `P-PRE-006`;
- `P-DAT-007` no tiene escala/transformación operativa cerrada para esta regla.

Su incorporación futura requerirá autoridad propia.

## 14. Fail-closed

DAT003 falla cerrado a `NOT_EVALUABLE` cuando:

- no existe RequirementSet autorizado;
- el RequirementSet no corresponde a la decisión/contexto;
- existe contradiction entre requirement sets;
- no puede demostrarse el binding Evidence → requirement;
- el carrier no puede construirse sin inferencia;
- provenance es incompatible.

## 15. No-alcance

Esta propuesta no autoriza:

- productor operacional universal de RequirementSet;
- QTG operacional;
- `P-DAT-003 → R-DAT-003`;
- `P-DAT-007 → R-DAT-003`;
- nuevas escalas de fiabilidad;
- conteos mínimos globales;
- inferencia de criticidad desde severidad;
- selección automática de datos alternativos;
- imputación o reparación de Evidence;
- decisión humana automática.

## 16. Gates propuestos

Si se autoriza:

```text
DAT003-G01 → semántica de suficiencia cerrada
DAT003-G02 → separación QTG cerrada
DAT003-G03 → carrier/produtor factual autorizado
DAT003-G04 → binding RequirementSet/Evidence cerrado
DAT003-G05 → fail-closed cerrado
DAT003-G06 → P-DAT-003/P-DAT-007 explícitamente fuera de consumo v0.1
```

## 17. Estado

**DAT003 Insufficient Data Authority v0.1 — PROPUESTA / NO AUTORIZADA.**

La propuesta habilitaría materialización técnica del carrier y evaluador, pero no crea por sí sola un productor operacional universal de `DecisionEvidenceRequirementSet`.
