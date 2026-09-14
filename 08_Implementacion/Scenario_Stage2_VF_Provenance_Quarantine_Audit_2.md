# EIOS — Scenario Stage 2 VF Provenance Quarantine — Audit 2

**HEAD técnico auditado:** `3b42487a9fc9a95fb3493788a18cb6a3baaa7a85`  
**Baseline:** `main @ 9a762927a536d36db3ab852127318ec6628fc216`  
**Dictamen:** SUPERADA — SIN BLOQUEADORES DE DISEÑO

## 1. Alcance físico

El diff técnico/documental auditado queda limitado a:

- contrato, Audit 1 y reconciliación de la cuarentena;
- `eios/rules/scenario_integration.py`;
- `eios/rules/decision_twin_integration.py`, únicamente para retirar el wrapper público dependiente de Stage 2;
- exports de `eios/rules/__init__.py`;
- reclasificación interna de `eios/core/viability_scenario_integration.py`;
- tests específicos Stage 2, VF→Scenario, E2E Scenario, frontera Decision Twin provenance y namespace público de `eios.rules`.

No existen cambios en O4, O2, O3, `viability_frontier.py`, C0 core, Rules Engine, CRC, Decision Twin core/comparator, Vertical MVP, presentación, SQL, parámetros ni reglas empresariales.

## 2. Frontera pública Stage 2

Verificado:

- `ProvenancedScenarioAnalyticsInput` ya no forma parte de `eios.rules`;
- `build_authorized_scenario_analytics_from_provenanced_assessments` ya no forma parte de `eios.rules`;
- `complete_provenanced_o4_o2_o3_orchestration` ya no forma parte de `eios.rules`;
- `eios.rules.scenario_integration.__all__` queda vacío;
- no existe alias legacy ni fallback silencioso.

La retirada es deliberadamente incompatible con consumidores de la frontera insegura y coincide con el patrón fail-closed ya aplicado a QTG.

## 3. Propagación controlada a Decision Twin integration

La primera CI pre-merge reveló un consumidor físico residual: `eios.rules.decision_twin_integration` importaba dos símbolos Stage 2 ya retirados y exponía cuatro símbolos que heredaban la misma afirmación provenance-safe.

La depuración queda acotada a esa envoltura:

- `DecisionTwinInvoker` deja de exportarse públicamente desde `eios.rules`;
- `ProvenancedDecisionTwinAlternativeInput` deja de exportarse públicamente;
- `build_provenanced_decision_twin_comparison` deja de exportarse públicamente;
- `build_provenanced_decision_twin_invoker` deja de exportarse públicamente;
- `eios.rules.decision_twin_integration.__all__` queda vacío;
- el test específico deja de fabricar `ViabilityResult` y verifica la cuarentena;
- `eios.core.decision_twin`, `eios.core.decision_twin_engine` y `compare_alternatives(...)` permanecen intactos.

Esto no reabre Decision Twin: elimina únicamente una frontera pública que dependía de una garantía Stage 2 ahora invalidada.

## 4. Namespace público transversal reconciliado

La segunda CI técnica reveló una expectativa histórica residual en `tests/test_rules_public_provenance_boundary.py`: el test aún exigía `build_authorized_scenario_analytics_from_provenanced_assessments` como entrada pública segura.

Se ha reconciliado el test para que:

- mantenga como públicas las entradas C0 provenance-safe existentes;
- exija ausencia de los tres símbolos Stage 2 en cuarentena;
- exija ausencia de los cuatro símbolos Decision Twin dependientes;
- compruebe también que esos siete nombres no figuran en `rules.__all__`.

No se ha añadido ningún comportamiento de producción para satisfacer el test; se corrige la expectativa para reflejar el contrato vigente.

## 5. Bridge VF interno

Verificado:

- el bridge se denomina `_build_context_bound_analytics_from_viability`;
- queda fuera de `__all__`;
- su documentación afirma expresamente que valida coherencia contextual, no procedencia del productor ni autoridad de consecuencias VF;
- conserva validaciones de decisión, escenario, versiones y snapshot;
- no ejecuta `evaluate_viability(...)` ni crea consecuencias H/K/U/S;
- no se convierte en token de autorización.

## 6. O4/O2/O3 preservado

`AuthorizedScenarioAnalytics` y `_complete_o4_o2_o3_orchestration(...)` permanecen físicamente sin cambios.

Por tanto:

- no se altera la cobertura 1:1 de escenarios O2 VALID;
- no se altera el orden determinista;
- no se altera la representación O3;
- no se modifica el mapping de estados técnicos;
- el transporte interno sigue sin proclamarse prueba de procedencia.

## 7. VF preservado

`eios/core/viability_frontier.py` no se modifica.

Se preservan:

- `FrontierAssessment`;
- `evaluate_viability(...)`;
- precedencia H→U→K→VIABLE;
- `VIABLE`, `VIABLE_CON_CONDICIONES`, `NOT_VIABLE`, `NOT_EVALUABLE`;
- tratamiento de insuficiencia y conflicto de autoridad;
- separación entre evaluación técnica y autoridad externa.

No se inventa productor VF.

## 8. C0 provenance preservado

La cuarentena no modifica `AssessmentTraceBinding`, `validate_assessment_trace_binding(...)`, construcción/reproducibilidad de Trace ni la frontera provenance-safe C0.

Los tests verifican expresamente que C0 provenance continúa exportado y disponible.

No se exige igualdad entre IDs C0 y VF.

## 9. Tests de conformidad depurados

Se elimina de los tests de Stage 2, E2E y Decision Twin integration la construcción manual de `ViabilityResult` usada para afirmar procedencia pública.

El estado físico verdadero queda representado así:

- O4→O2 Stage 1 sigue materializable;
- la cadena no puede cruzar una finalización pública Stage 2 mientras VF carezca de productor provenance-safe;
- ningún wrapper Decision Twin puede saltarse ese bloqueo heredando material Stage 2 no acreditado;
- el test transversal del namespace público exige la ausencia de todas esas entradas en cuarentena;
- C0 provenance permanece disponible;
- Decision Twin core permanece disponible;
- no se fabrica un resultado VF para simular que el blocker está resuelto.

Los tests del bridge VF quedan identificados como tests internos de coherencia contextual y ya no como prueba E2E/provenance-safe.

## 10. Autoridad y semántica

No se introducen:

- score;
- ranking;
- recomendación;
- selección;
- aprobación/rechazo;
- decisión empresarial;
- mapping VF→O3;
- estado artificial `VF_BLOCKED`;
- nueva excepción de negocio;
- token o firma de autoridad ficticios.

La autoridad humana final y `NOT_EVALUABLE` permanecen intactos.

## 11. Contratos históricos

Los contratos cerrados anteriores se conservan como evidencia histórica, pero la reconciliación nueva supersede exclusivamente su afirmación de que un `ViabilityResult` tipado/contextualmente consistente acredita procedencia VF suficiente para Stage 2 público y cualquier wrapper provenance-safe que dependa de esa afirmación.

No se crea BL-004 ni se altera ningún SHA histórico.

## 12. Dictamen

La corrección elimina la contradicción detectada, sus consumidores aguas abajo y las expectativas transversales desactualizadas sin desplazar el problema, sin inventar infraestructura ausente y sin reabrir componentes core cerrados.

**AUDIT 2: SUPERADA — SIN BLOQUEADORES DE DISEÑO.**

El cierre físico sigue condicionado a CI pre-merge sobre el HEAD exacto final de la rama, reconciliación `behind=0`, merge protegido por SHA exacto y CI post-merge sobre el SHA integrado.
