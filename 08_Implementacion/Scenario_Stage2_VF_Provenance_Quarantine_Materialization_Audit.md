# EIOS — Scenario Stage 2 VF Provenance Quarantine — Materialization Audit

**Estado:** MATERIALIZACIÓN AUDITADA — PENDIENTE CI  
**Baseline:** `main @ 9a762927a536d36db3ab852127318ec6628fc216`

## 1. Artefactos materializados

Documentación:

- `Scenario_Stage2_VF_Provenance_Quarantine_Contract_v0.1.md`;
- `Scenario_Stage2_VF_Provenance_Quarantine_Audit_1.md`;
- `Scenario_Stage2_VF_Provenance_Quarantine_Audit_2.md`;
- `Scenario_Stage2_VF_Provenance_Quarantine_Reconciliation.md`;
- `Scenario_Stage2_VF_Provenance_Quarantine_Closure.md`;
- este Materialization Audit.

Código:

- `eios/rules/scenario_integration.py` queda como módulo de cuarentena sin API pública Stage 2;
- `eios/rules/__init__.py` deja de exportar los tres símbolos inseguros;
- `eios/core/viability_scenario_integration.py` reclasifica el bridge como helper interno context-bound y lo retira de `__all__`.

Tests:

- `tests/test_scenario_stage2_provenance_boundary.py` verifica la cuarentena y preservación de C0 provenance;
- `tests/test_vertical_mvp_scenario_e2e_conformance.py` deja de fabricar VF para simular E2E provenance-safe;
- `tests/test_viability_scenario_integration.py` queda limitado a coherencia contextual del helper interno.

## 2. Invariantes verificadas por inspección

- no existe API pública que acepte `ViabilityResult` y proclame Stage 2 provenance-safe;
- no existe alias legacy;
- no existe productor VF inventado;
- no se ejecuta `evaluate_viability(...)` desde la frontera de cuarentena;
- no se modifica `viability_frontier.py`;
- no se modifica O4/O2/O3;
- no se modifica C0/Rules provenance;
- no se modifica Vertical MVP ni presentación;
- no se introduce autoridad decisional ni estado de negocio nuevo.

## 3. Deuda explícitamente preservada

La integración positiva VF→Stage 2 continúa bloqueada. Esta no es una omisión de la materialización sino el estado correcto mientras falte el productor físico de consecuencias VF autorizadas.

El bridge interno puede validar contexto, pero no debe volver a exponerse como prueba de procedencia.

## 4. Gate de CI

La inspección estática no sustituye la suite completa. CI deberá detectar, entre otros posibles defectos:

- consumidores físicos residuales de los símbolos retirados;
- imports rotos;
- regresiones en tests no identificados durante la auditoría;
- validaciones SQL/documentales globales.

No se declarará cierre físico hasta CI pre-merge y post-merge SUCCESS sobre los SHA exactos correspondientes.
