# EIOS — MGE Rules v0.1 Materialization Audit

**Baseline:** `main @ 1fb6381f2ee45bc1e51deb4ff05b7b9bf4fa15ea`  
**Estado:** AUDITORÍA DE MATERIALIZACIÓN — SIN BLOQUEADORES OBSERVADOS, PENDIENTE CI

## 1. Superficie materializada

- `eios/rules/profitability.py`;
- ampliación autorizada de `eios/rules/catalog.py`;
- integración de bundle MGE en `eios/rules/orchestrator.py`;
- `tests/test_rules_profitability.py`.

Profitability Core, CRC y Centro de Parametrización no se modifican.

## 2. Hallazgo de depuración documental M1

El contrato técnico cerrado exigía cuatro `evidence_ids` incluso cuando una evidencia podía estar ausente.

Eso es físicamente imposible sin inventar un ID.

### Corrección

El contrato se aclara:

- conservar todos los IDs de evidencias realmente suministradas;
- bundle completo → cuatro IDs;
- evidencia ausente → no se inventa ID;
- la rule queda `NOT_EVALUABLE`.

No cambia autoridad ni semántica de negocio.

## 3. Audit 1 de implementación

### I1 — Result desprendido

Cada evaluator llama primero a:

`validate_provenanced_profitability_execution`.

**PASS.**

### I2 — Identity binding

Se exige igualdad entre:

- PurchaseOperation ↔ DecisionContext;
- Rule ↔ rules_version;
- ProfitabilityInput.context ↔ DecisionContext;
- ProfitabilityInput.purchase_operation ↔ PurchaseOperation;
- ProfitabilityResult ↔ decision/scenario/snapshot/parameters/company/article/date.

**PASS.**

### I3 — Evidence de Profitability

`ProfitabilityResultEvidence` se liga por hash determinista del resultado completo.

Una reference DEMONSTRATED ajena es error estructural.

**PASS.**

### I4 — Parameter bundle

Los tres parámetros se validan por:

- ID;
- parameters_version;
- company_scope;
- effective_at/evaluation_date;
- vigencia;
- Evidence source/ref;
- Decimal finito;
- unidad exacta.

**PASS.**

### I5 — Ausencia / GAP

Missing resolution/evidence o Evidence INVALID → `NOT_EVALUABLE`.

No existe 20/30/3 como fallback.

**PASS.**

### I6 — coherencia

`minimum > target` → `NOT_EVALUABLE`.  
`tolerance < 0` → `NOT_EVALUABLE`.

**PASS.**

### I7 — fórmulas

```text
R-MGE-001 = m < minimum
R-MGE-002 = m >= minimum AND m >= target - tolerance AND m < target
R-MGE-003 = m >= target
```

**PASS.**

### I8 — metadata

```text
R-MGE-001 → R1 / ALTA
R-MGE-002 → R2 / MEDIA
R-MGE-003 → R3 / INFORMATIVA
```

No existe R0.

**PASS.**

### I9 — orquestador

Un único `ProfitabilityRuleInputs` produce las tres assessments dentro de la misma ejecución.

Bundle ausente → las tres permanecen omitted.

**PASS.**

### I10 — alcance

No se consumen:

- P-MGE-004/005/006;
- PRICE;
- TCO;
- filesystem;
- red;
- SQL;
- clock implícito.

**PASS.**

## 4. Tests materializados

La suite dedicada cubre:

- fronteras exactas minimum / tolerance / target;
- hueco legítimo sin regla MGE activa;
- tolerance=0;
- minimum=target;
- minimum>target;
- tolerance<0;
- Profitability no DETERMINED;
- Evidence GAP;
- Evidence ausente sin fake ID;
- units incompatibles;
- thresholds alternativos para demostrar ausencia de defaults;
- IDs de evidencia;
- wrong parameter ID/version/company/date/ref;
- configuración no vigente;
- evidence de Profitability forjada;
- ejecución Profitability manipulada;
- metadata exacta;
- ejecución conjunta de las tres Rules;
- omisión conjunta cuando el bundle falta.

## 5. Dictamen

**AUDITORÍA DE MATERIALIZACIÓN: SUPERADA — 0 bloqueadores observados antes de CI.**

Cierre condicionado a:

1. CI exact-head satisfactoria;
2. suite completa;
3. SQL validations;
4. reconciliación de cualquier test histórico afectado legítimamente por el nuevo catálogo;
5. merge protegido por SHA.


## 6. CI y depuración

### CI #1006 — FAILURE controlado

Resultado:

```text
4 failed
1679 passed
8 warnings
```

Los cuatro fallos correspondían a tests históricos que fijaban el conjunto anterior de reglas implementadas:

- `tests/test_rule_metadata_catalog.py`;
- `tests/test_rules_domain_orchestrator.py`.

No se detectó fallo en la suite funcional MGE.

### Depuración

Se reconciliaron exclusivamente las expectativas históricas para:

- incluir R-MGE-001/002/003 en el catálogo implementado;
- considerar las tres reglas como `omitted` cuando no existe bundle MGE;
- incluir el bundle MGE en el test de ejecución total del orquestador.

No se modificaron:

- fórmulas;
- metadata;
- provenance;
- política de parámetros;
- semántica `NOT_EVALUABLE`;
- CRC.

### CI #1007 — SUCCESS

HEAD validado:

```text
37aafbaeb5c0f2733a534ae49ac5d7ed903a83d6
```

Resultado:

```text
1686 passed
8 warnings
SQL validations SUCCESS
```

PR #244 integrada mediante SHA protegido.

Merge commit:

```text
b3fdb6275a6cc6a33ecca55bbd9af49816ce5776
```

## 7. Estado final

**Rules MGE v0.1: CERRADAS / MATERIALIZADAS / CI VALIDADA.**
