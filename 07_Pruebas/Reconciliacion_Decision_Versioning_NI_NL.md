# EIOS — Reconciliación Decision Versioning ↔ NI ↔ Ladder

**Fecha:** 2026-09-02  
**Estado:** 🔒 CERRADO — MATERIALIZADO — PENDIENTE CI

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

Cambios materializados en la rama de reconciliación:

- `eios/core/negotiation_intelligence.py`
- `tests/test_negotiation_intelligence.py`
- `eios/core/negotiation_ladder.py`
- `tests/test_negotiation_ladder.py`
- contratos de implementación NI/NL.

## 7. Dictamen

**CERRADO — RECONCILIADO — SIN EXPANSIÓN DE AUTORIDAD.**

La discrepancia queda corregida sin crear una nueva versión funcional de decisión.

**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI.
