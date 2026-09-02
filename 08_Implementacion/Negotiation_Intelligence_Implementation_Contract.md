# EIOS — Negotiation Intelligence Implementation Contract

## 1. Identidad

**Documento:** Negotiation Intelligence Implementation Contract  
**Versión:** 1.3  
**Estado:** CERRADO — RECONCILIADO Y MATERIALIZADO  
**Baseline:** EIOS Vertical MVP

## 2. Propósito

Este contrato materializa el subconjunto definido de `Negotiation Intelligence` sin ampliar su autoridad funcional. NI determina y justifica contenido negociador; no decide, aprueba, ejecuta ni activa Strategy.

## 3. Frontera funcional

```text
Viability Frontier / Scenario Engine / Decision Twin / Rules / Evidence
                              ↓
                    Negotiation Intelligence
                              ↓
                 contenido negociador justificado
                              ↓
                    Negotiation Ladder
```

NI consume referencias upstream y no las sustituye ni recalcula.

## 4. Contexto autorizado

La entrada lógica utiliza `decision_context` y referencias a escenarios, viabilidad, Decision Twin, variables negociables, límites, evidencia y contexto previo de negociación.

Cada referencia conserva la identidad y las versiones autorizadas de su origen cuando existan.

## 5. Identidad y versionado — reconciliación

NI reutiliza únicamente las identidades autorizadas existentes:

```text
Decision_ID
Scenario_ID, cuando aplique
Rules_Version, cuando aplique
Parameters_Version, cuando aplique
Data_Snapshot_ID, cuando aplique
```

**`decision_version` no pertenece al contrato NI.** Decision Versioning no define una versión funcional con ese campo. Su registro físico utiliza `decision_state_record_id` como identificador técnico histórico y conserva referencias de C0.

NI no crea un sistema paralelo de Decision Versioning, Scenario Versioning, Trace o `input_fingerprint`.

`negotiation_result_id` identifica exclusivamente el artefacto NI y no sustituye ninguna identidad upstream.

Un nuevo contexto materialmente diferente genera un nuevo resultado NI; los resultados históricos no se sobrescriben.

## 6. Contenido negociador

La salida puede contener:

```text
objective
opening_request
moves
concessions
counterpart_requirements
tradeoffs
packages
alternatives
fallback
conditions
convenience_analysis
```

Estos elementos son contenido sustantivo y no representan una Ladder.

## 7. Epistemología y trazabilidad

Las afirmaciones pueden ser `FACT`, `OBSERVATION`, `INFERENCE`, `ESTIMATE`, `HYPOTHESIS` o `RECOMMENDATION`. La confianza, cuando exista, pertenece a la `NIAssertion` correspondiente. No existe un `confidence_score` global.

NI conserva referencias a las fuentes y no redefine Evidence, Rules, Parameters, C0, Trace, Scenario Engine o Decision Twin.

## 8. Fronteras upstream

NI puede consumir resultados de Viability Frontier y Decision Twin y formular hipótesis negociadoras, pero no determina viabilidad, modifica límites, crea escenarios formales ni recalcula el Twin.

## 9. Negotiation Ladder

Negotiation Intelligence determina el contenido; Negotiation Ladder lo estructura, representa y ordena. NI no crea `ladder_step`, `sequence_order`, transiciones, rutas ni niveles estructurales de Ladder.

## 10. CRC y decisión

NI no resuelve conflictos de autoridad y no sustituye CRC. Tampoco aprueba, decide o ejecuta.

```text
Negotiation content ≠ Strategy
Recommendation ≠ Business Decision
Business Decision ≠ Execution
```

## 11. Salida

```text
negotiation_result_id
context_references
negotiation_content
justification
traceability_references
```

## 12. Invariantes

1. Las referencias upstream conservan su autoridad de origen.
2. NI no crea ni modifica límites.
3. NI no determina viabilidad.
4. NI no crea escenarios formales.
5. NI no recalcula Decision Twin.
6. NI no redefine Decision Versioning.
7. NI no redefine C0, Trace ni `input_fingerprint`.
8. NI no estructura Ladder.
9. NI no resuelve conflictos de autoridad.
10. NI no gobierna Strategy.
11. NI no aprueba, decide ni ejecuta.
12. Las categorías epistemológicas permanecen diferenciadas.
13. Un resultado nuevo no sobrescribe uno histórico.
14. Una hipótesis negociadora no equivale a un escenario formal.
15. NI no introduce `decision_version` como identidad paralela.
16. NI no crea un segundo fingerprint o Trace.

## 13. Criterios de test

La implementación verifica identidad autorizada, rechazo de `decision_version`, conservación de contexto upstream, separación NI/Ladder, trazabilidad, inmutabilidad y ausencia de autoridades paralelas.

Cobertura materializada en `tests/test_negotiation_intelligence.py` y `eios/core/negotiation_intelligence.py`.

## 14. Estado

**Estado:** CERRADO — RECONCILIADO Y MATERIALIZADO.  
**Tipo de cambio:** corrección de frontera documental/técnica; sin nueva autoridad funcional.  
**C0:** NO ALTERADO.  
**Decision Versioning:** NO ALTERADO.  
**O2:** NO ALTERADO.  
**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI.
