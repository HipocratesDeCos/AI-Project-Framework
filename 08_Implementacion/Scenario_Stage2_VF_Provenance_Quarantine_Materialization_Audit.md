# EIOS — Scenario Stage 2 VF Provenance Quarantine — Materialization Audit

**Estado:** MATERIALIZACIÓN AUDITADA — PENDIENTE CI FINAL  
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
- `eios/rules/decision_twin_integration.py` queda como módulo de cuarentena sin wrapper público provenance-safe dependiente de Stage 2;
- `eios/rules/__init__.py` deja de exportar los tres símbolos inseguros Stage 2 y los cuatro símbolos Decision Twin dependientes;
- `eios/core/viability_scenario_integration.py` reclasifica el bridge como helper interno context-bound y lo retira de `__all__`.

Tests:

- `tests/test_scenario_stage2_provenance_boundary.py` verifica la cuarentena y preservación de C0 provenance;
- `tests/test_assessment_scenario_integration.py` deja de probar la ruta pública positiva retirada y verifica cuarentena Stage 2 + preservación C0;
- `tests/test_decision_twin_provenance_integration.py` verifica la cuarentena del wrapper dependiente y la disponibilidad del comparador core;
- `tests/test_rules_public_provenance_boundary.py` mantiene las entradas C0 seguras y verifica que los siete símbolos Stage 2/Decision Twin dependientes no estén expuestos;
- `tests/test_vertical_mvp_scenario_e2e_conformance.py` deja de fabricar VF para simular E2E provenance-safe;
- `tests/test_viability_scenario_integration.py` queda limitado a coherencia contextual del helper interno.

## 2. Hallazgos de CI y correcciones

La primera CI pre-merge detectó un import roto en `eios.rules.decision_twin_integration`: el wrapper todavía importaba símbolos Stage 2 retirados. La inspección confirmó además que su test construía manualmente `ViabilityResult` y elevaba esa ruta a provenance-safe.

La siguiente CI técnica reveló una segunda expectativa residual: `tests/test_rules_public_provenance_boundary.py` seguía exigiendo como pública y segura una función Stage 2 deliberadamente retirada.

Una tercera CI falló durante la colección porque `tests/test_assessment_scenario_integration.py` seguía importando los tres símbolos Stage 2 retirados y estaba construido alrededor de la antigua ruta pública positiva, incluida la fabricación de `ViabilityResult`.

Las correcciones no restauran Stage 2. Extienden el mismo fail-closed únicamente al wrapper dependiente de Decision Twin, reconcilian el test transversal del namespace público y convierten el test legado Assessment→Scenario en prueba explícita de cuarentena y preservación de C0. Se mantienen intactos `eios.core.decision_twin`, `eios.core.decision_twin_engine`, O4/O2/O3 y las entradas C0 provenance-safe.

Los tres hallazgos quedan absorbidos en Audit 1 y Audit 2 antes de la CI final.

## 3. Pasada preventiva posterior

Tras la tercera depuración se revisaron las fronteras vecinas más próximas:

- `tests/test_assessment_trace_provenance.py` continúa usando únicamente la frontera C0 provenance-safe;
- `tests/test_vertical_mvp_scenario_coordination.py` consume Scenario Coordination/O2 core y su invoker propio;
- `tests/test_vertical_mvp_scenario_support_presentation.py` consume soporte O2/presentación sin importar Stage 2 público;
- `tests/test_vertical_mvp_from_orchestration.py` usa deliberadamente `_complete_o4_o2_o3_orchestration(...)` como helper core interno y no representa una finalización pública provenance-safe.

No se identificó en esta pasada otro consumidor público obvio de los símbolos retirados. La CI completa sigue siendo el gate definitivo.

## 4. Invariantes verificadas por inspección

- no existe API pública que acepte `ViabilityResult` y proclame Stage 2 provenance-safe;
- no existe wrapper Decision Twin público que pueda heredar esa afirmación;
- los tests del antiguo límite público verifican la cuarentena en lugar de reconstruir la vía retirada;
- el test transversal de `eios.rules` exige la ausencia de ambas fronteras en cuarentena;
- no existe alias legacy;
- no existe productor VF inventado;
- no se ejecuta `evaluate_viability(...)` desde la frontera de cuarentena;
- no se modifica `viability_frontier.py`;
- no se modifica O4/O2/O3;
- no se modifica C0/Rules provenance;
- no se modifica Decision Twin core/comparator;
- no se modifica Vertical MVP ni presentación;
- no se introduce autoridad decisional ni estado de negocio nuevo.

## 5. Deuda explícitamente preservada

La integración positiva VF→Stage 2 continúa bloqueada. Esta no es una omisión de la materialización sino el estado correcto mientras falte el productor físico de consecuencias VF autorizadas.

El bridge interno puede validar contexto, pero no debe volver a exponerse como prueba de procedencia. Tampoco puede hacerlo ningún wrapper aguas abajo por mera composición.

## 6. Gate de CI

La inspección estática no sustituye la suite completa. La CI final debe verificar, entre otros posibles defectos:

- consumidores físicos residuales de los símbolos retirados;
- imports rotos;
- expectativas históricas residuales del namespace público;
- regresiones en Decision Twin core;
- regresiones en tests no identificados durante la auditoría;
- validaciones SQL/documentales globales.

No se declarará cierre físico hasta CI pre-merge y post-merge SUCCESS sobre los SHA exactos correspondientes.
