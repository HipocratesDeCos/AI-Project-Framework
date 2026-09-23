# EIOS — Shadow Mode Observation Completion Package v0.1

**Baseline:** `main @ 30e69833c663769ae1015d991da215556382b0f6`  
**Fecha:** 23/09/2026  
**Estado:** PROPUESTA CONSOLIDADA — NO AUTORIZADA / NO VIGENTE

## 1. Objetivo

Materializar una primera capacidad Shadow Mode de Assurance que permita:

- conservar una evaluación EIOS ya producida;
- conservar posteriormente una decisión empresarial humana observada;
- mantener ambas separadas;
- producir una comparación descriptiva;
- medir cobertura operativa sin modificar reglas, parámetros ni modelos.

Shadow Mode no ejecuta compras, no sustituye al decisor humano y no aprende automáticamente de discrepancias.

## 2. Principio

```text
EIOS result ≠ human business decision
difference ≠ system error
match ≠ system correctness
human override ≠ training label
shadow observation ≠ execution authority
```

## 3. Taxonomía común de resultado

Para permitir comparación literal sin inventar equivalencias se propone reutilizar exactamente la taxonomía CRC ya autorizada:

```text
COMPRAR
NEGOCIAR
COMPRAR CONDICIONADO
NO COMPRAR
INFORMACIÓN INSUFICIENTE
```

Esta reutilización se limita a Shadow Mode.

No afirma que CRC y decisión humana tengan la misma autoridad ni el mismo significado jurídico/operativo.

## 4. Carrier de decisión humana observada

```text
ObservedHumanDecision
├── decision_id
├── scenario_id
├── observed_result
├── decision_ref
├── decided_at
├── decision_authority_ref
├── evidence_refs
├── trace_refs
└── source_state
```

`source_state`:

```text
OBSERVED
NOT_OBSERVED
NOT_DETERMINABLE
CONFLICTING
```

Solo `OBSERVED` puede participar en una comparación descriptiva.

## 5. Carrier Shadow

```text
ShadowObservation
├── decision_id
├── scenario_id
├── rules_version
├── parameters_version
├── data_snapshot_id
├── system_result
├── human_result?
├── comparison_state
├── execution_ref
├── decision_ref?
├── system_trace_refs
├── human_trace_refs
└── limitations
```

## 6. Estados de comparación

Se propone únicamente:

```text
MATCH
DIFFERENT
SYSTEM_INSUFFICIENT
HUMAN_NOT_OBSERVED
NOT_COMPARABLE
```

Semántica:

```text
system == human
→ MATCH

system != human
→ DIFFERENT

system == INFORMACIÓN INSUFICIENTE
→ SYSTEM_INSUFFICIENT

human source_state != OBSERVED
→ HUMAN_NOT_OBSERVED

identidad/versiones/procedencia incompatibles
→ NOT_COMPARABLE / fail closed según tipo de incompatibilidad
```

`MATCH` y `DIFFERENT` son comparación literal, no juicio de calidad.

## 7. Procedencia del resultado EIOS

Shadow Mode no acepta un string libre como sistema.

Debe consumir un `CRCResult` ya producido y vinculado al mismo `DecisionContext`.

Adicionalmente debe recibir una referencia de ejecución:

```text
execution_ref
```

que identifique la ejecución O1/Vertical observada.

v0.1 no crea un sistema nuevo de recibos operativos.

## 8. Procedencia de la decisión humana

Para `source_state=OBSERVED` se exige:

- decision_authority_ref explícita;
- decision_ref explícita;
- evidence_refs no vacías;
- Evidence DEMONSTRATED;
- trace_refs no vacías;
- identidad decision/scenario exacta.

El software no verifica por sí mismo facultades empresariales, firma, identidad personal o mandato.

Esas comprobaciones siguen siendo actos operativos externos.

## 9. Orden temporal

Se propone exigir:

```text
decided_at >= shadow_evaluation_recorded_at
```

cuando ambas marcas estén disponibles.

Esto solo ordena hechos registrados.

No demuestra que la persona decisora no haya visto la evaluación EIOS.

## 10. Visibilidad

Para no inventar una prueba de ocultación se propone:

```text
system_visibility_state:
WITHHELD_DECLARED
EXPOSED
UNKNOWN
```

Solo `WITHHELD_DECLARED` permite etiquetar la observación como `SHADOW_ELIGIBLE`.

Esto sigue siendo una declaración de proceso, no una verificación técnica de interfaz o conducta humana.

## 11. Elegibilidad Shadow

```text
SHADOW_ELIGIBLE
NOT_SHADOW_ELIGIBLE
NOT_DETERMINABLE
```

`SHADOW_ELIGIBLE` requiere:

- decisión humana OBSERVED;
- system_visibility_state = WITHHELD_DECLARED;
- identidad/contexto compatibles;
- CRCResult trazable;
- decisión humana trazable.

No requiere MATCH.

## 12. Resultado

```text
ShadowModeResult
├── observation_id
├── observation
├── eligibility
├── comparison_state
├── limitations
└── trace_refs
```

No contiene:

- accuracy score;
- model score;
- winner;
- correctness;
- recommendation change;
- parameter update;
- retraining instruction.

## 13. observation_id

Identidad determinista:

```text
shadow:{decision_id}:{scenario_id}:{fingerprint}
```

El fingerprint cubre:

- DecisionContext;
- CRCResult;
- execution_ref;
- decisión humana observada;
- visibilidad declarada;
- timestamps;
- refs.

## 14. Productor

API propuesta:

```text
produce_shadow_mode_result(
    context,
    crc_result,
    execution_ref,
    shadow_evaluation_recorded_at,
    human_decision,
    system_visibility_state,
    evidences
) -> ShadowModeResult
```

Debe:

1. validar CRCResult contra DecisionContext;
2. validar decisión humana contra contexto;
3. validar Evidence;
4. determinar elegibilidad;
5. producir comparación literal;
6. preservar limitaciones;
7. no modificar ningún input.

## 15. Métricas agregables posteriores

v0.1 permite conservar resultados individuales para que una capa posterior pueda contar:

- número de observaciones;
- número elegible;
- MATCH;
- DIFFERENT;
- SYSTEM_INSUFFICIENT;
- HUMAN_NOT_OBSERVED.

No se autoriza todavía:

- accuracy;
- precision/recall;
- confidence calibration;
- policy tuning;
- automatic threshold adjustment;
- aprendizaje online.

## 16. Relación con piloto real

Este paquete permite ensayar Shadow Mode con datos sintéticos y preparar captura real.

No convierte por sí mismo el Finance Pilot ni QTG operacional en aptos.

QTG operacional continúa bloqueado hasta disponer de material operacional real autorizado.

## 17. Relación con O1

Shadow Mode se ejecuta **después** de la evaluación analítica.

No se incorpora al `MVP_CAPABILITY_ORDER` v0.1 porque no es una capacidad decisional del pipeline, sino Assurance posterior.

No puede modificar `ExecutionOutcome`.

## 18. No alcance

No autoriza:

- ejecución automática;
- override automático;
- recomendación adaptativa;
- feedback learning;
- cambio de Rule;
- cambio de Parameter;
- scoring de personas;
- evaluación de desempeño humano;
- inferencia de intención;
- identificación biométrica;
- IAM;
- autenticación;
- firma digital;
- verificación automática de mandato.

## 19. Tests mínimos

1. MATCH literal;
2. DIFFERENT literal;
3. system insufficient;
4. human not observed;
5. decision/scenario mismatch → fail closed;
6. CRC context mismatch → fail closed;
7. observed human decision requires evidence;
8. GAP does not demonstrate decision;
9. visibility WITHHELD_DECLARED → eligible;
10. EXPOSED → not eligible;
11. UNKNOWN → not determinable;
12. temporal inversion → fail closed;
13. deterministic observation_id;
14. no scoring fields;
15. no O1 mutation;
16. synthetic rehearsal never claims operational authority.

## 20. Efecto de autorización

```text
AUTORIZAR
→ AUDITAR
→ MATERIALIZAR
   - ObservedHumanDecision
   - ShadowModeResult
   - producer
   - tests
   - synthetic rehearsal
→ CI
→ merge
→ CI main
```

## 21. Estado

**SHADOW MODE OBSERVATION COMPLETION PACKAGE v0.1 — PROPUESTA / NO VIGENTE.**
