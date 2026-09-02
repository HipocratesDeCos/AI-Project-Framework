# EIOS — Reconciliación Decision Versioning ↔ NI ↔ Ladder

**Fecha:** 2026-09-02  
**Estado:** 🔒 CERRADO — MATERIALIZADO — CI VALIDADO

## 1. Alcance

Reconciliación de la identidad y versionado entre `DecisionContext`, C0, Decision Versioning, Negotiation Intelligence (NI), Negotiation Ladder (NL) y Scenario Engine (O2).

## 2. Hallazgo

NI y NL exigían un campo `decision_version` que no pertenece al modelo autorizado de Decision Versioning ni a `DecisionContext`.

La materialización física de Decision Versioning utiliza `decision_state_record_id` como identificador técnico del registro histórico y no crea una versión funcional paralela.

## 3. Corrección

Se elimina `decision_version` de NI y NL y se añade cobertura de prueba que rechaza su reintroducción como identidad paralela.

Se conservan las identidades autorizadas:

```text
Decision_ID
Scenario_ID
Rules_Version
Parameters_Version
Data_Snapshot_ID
input_fingerprint / Trace (C0)
negotiation_result_id (NI)
ladder_id (NL)
```

O2 mantiene su fingerprint propio de escenario, sin sustituir el fingerprint C0.

## 4. Límites

No se modifica:

- C0;
- DecisionContext;
- Decision Versioning SQL;
- input_fingerprint;
- Trace;
- Scenario Engine;
- Scenario fingerprint;
- O1;
- ninguna autoridad empresarial.

No se introduce E2E contractual nuevo.

## 5. Auditoría 2

**SUPERADA.**

Verificaciones: ausencia de `decision_version` en los modelos NI/NL, rechazo explícito mediante `extra="forbid"` y tests, preservación de identidad upstream y ausencia de nueva autoridad de versionado.

## 6. Materialización

Cambios materializados y fusionados en `main` mediante PR #5:

- `eios/core/negotiation_intelligence.py`
- `tests/test_negotiation_intelligence.py`
- `eios/core/negotiation_ladder.py`
- `tests/test_negotiation_ladder.py`
- contratos de implementación NI/NL.

**Merge commit:** `f82bee9a8567dbb22319fac6d72e2cd5d7e0ed7c`

## 7. CI

**EIOS Tests #360** — run `33608380850`  
**Job:** `test` — `100177532561`  
**HEAD:** `f82bee9a8567dbb22319fac6d72e2cd5d7e0ed7c`  
**Resultado:** **SUCCESS**

Validaciones completadas satisfactoriamente:

- ejecución de tests Python;
- validación SQL Server de C0;
- validación SQL Server de Decision Versioning;
- validación SQL Server de Parameter Configuration.

No se detectaron fallos en los pasos del workflow.

## 8. Dictamen final

**CERRADO — RECONCILIADO — MATERIALIZADO — CI VALIDADO — SIN EXPANSIÓN DE AUTORIDAD.**

La discrepancia queda corregida sin crear una nueva versión funcional de decisión. `Decision Versioning` permanece como autoridad de versionado histórico definida; NI y NL utilizan únicamente las identidades autorizadas y no introducen `decision_version` como identidad paralela.

**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI.
