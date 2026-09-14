# EIOS — Scenario Stage 2 VF Provenance Quarantine — Audit 1

**Baseline auditado:** `main @ 9a762927a536d36db3ab852127318ec6628fc216`  
**Dictamen:** SUPERADA CON DEPURACIÓN OBLIGATORIA

## 1. Evidencia auditada

Se contrastaron físicamente:

- `eios/rules/scenario_integration.py`;
- `eios/rules/decision_twin_integration.py`;
- `eios/rules/__init__.py`;
- `eios/core/viability_scenario_integration.py`;
- `eios/core/viability_frontier.py`;
- `eios/core/o4_o2_o3_orchestration.py`;
- `eios/core/decision_twin.py` y `eios/core/decision_twin_engine.py` como frontera preservada;
- `tests/test_scenario_stage2_provenance_boundary.py`;
- `tests/test_decision_twin_provenance_integration.py`;
- `tests/test_rules_public_provenance_boundary.py`;
- `tests/test_vertical_mvp_scenario_e2e_conformance.py`;
- `tests/test_viability_scenario_integration.py`;
- `08_Implementacion/Scenario_Stage2_Provenance_Boundary_Contract_v0.1.md`;
- `08_Implementacion/Viability_Frontier_Scenario_Analytics_Integration_Contract_v0.1.md`;
- `08_Implementacion/Viability_Frontier_Implementation_Contract.md`;
- `05_Motor/Viability_Frontier.md`;
- precedente `Vertical_MVP_QTG_Provenance_Quarantine_Contract_v0.1.md`.

## 2. Hallazgo A1 — resultado VF desprendido

`ViabilityResult` puede construirse directamente por un caller. La integración comprueba identidad y versiones, pero no acredita el productor de `status`, `assessment_ids`, `rule_ids`, `trace_references` o `limitation`.

**Clasificación:** BLOQUEADOR de la afirmación “Stage 2 provenance-safe”.

**Depuración:** retirar la vía pública mientras no exista productor VF provenance-safe.

## 3. Hallazgo A2 — reconstrucción desde FrontierAssessment no resuelve procedencia

`FrontierAssessment` representa una consecuencia ya autorizada externamente. El evaluador VF no autentica esa autoridad.

**Clasificación:** BLOQUEADOR para una falsa solución por simple recálculo.

**Depuración:** no crear `viability_invoker`, token, firma ni productor ficticio; mantener la integración bloqueada.

## 4. Hallazgo A3 — asimetría C0/VF

La frontera pública valida `AssessmentTraceBinding` contra PurchaseOperation + DecisionContext y reconstruye el trace. Para VF solo existe coherencia contextual del terminal result.

**Clasificación:** contradicción objetiva de frontera.

**Depuración:** conservar C0+Trace y retirar únicamente la afirmación/API de finalización Stage 2 provenance-safe dependiente de VF.

## 5. Hallazgo A4 — E2E sobredeclara conformidad

Los tests actuales fabrican `ViabilityResult` y material VF sintético, y después consideran la ruta válida como E2E provenance-safe.

**Clasificación:** test de conformidad inválido respecto al requisito de procedencia.

**Depuración:** sustituir esas expectativas por pruebas de cuarentena/no exposición pública, sin eliminar tests internos del evaluador VF.

## 6. Hallazgo A5 — no reabrir O4/O2/O3

`AuthorizedScenarioAnalytics` declara expresamente que su construcción no prueba procedencia y `_complete_o4_o2_o3_orchestration(...)` es interno. La contradicción está en la frontera pública que eleva material VF desprendido a provenance-safe.

**Clasificación:** fuera de alcance para modificación funcional.

**Depuración:** mantener estos componentes intactos.

## 7. Hallazgo A6 — patrón de fail-closed

El precedente QTG elimina la vía insegura de la firma/API y no crea estados artificiales ni compatibilidad silenciosa.

**Clasificación:** patrón reutilizable.

**Depuración:** aplicar retirada explícita de los símbolos públicos Stage 2 inseguros; no crear un `VF_BLOCKED` ni una excepción de negocio permanente.

## 8. Hallazgo A7 — consumidor aguas abajo Decision Twin

La primera CI de la materialización detectó que `eios.rules.decision_twin_integration` seguía importando `ProvenancedScenarioAnalyticsInput` y `complete_provenanced_o4_o2_o3_orchestration`, ambos retirados por la cuarentena Stage 2. Además, ese wrapper se denominaba explícitamente provenance-safe y su test fabricaba manualmente `ViabilityResult`.

**Clasificación:** BLOQUEADOR de integración y propagación directa de la misma contradicción de procedencia, no defecto del Decision Twin core.

**Depuración:** extender la cuarentena exclusivamente al wrapper público `eios.rules.decision_twin_integration` y a sus cuatro exports; sustituir su test positivo sintético por prueba de no exposición; preservar `eios.core.decision_twin`, `eios.core.decision_twin_engine` y `compare_alternatives(...)`.

## 9. Hallazgo A8 — test transversal del namespace público desactualizado

La siguiente CI técnica mostró que `tests/test_rules_public_provenance_boundary.py` seguía exigiendo como pública y segura `build_authorized_scenario_analytics_from_provenanced_assessments`, pese a que la cuarentena la había retirado deliberadamente.

**Clasificación:** BLOQUEADOR de CI por expectativa histórica incompatible con la nueva frontera; no defecto funcional de producción.

**Depuración:** retirar ese símbolo del conjunto de entradas seguras y verificar explícitamente la ausencia de los tres símbolos Stage 2 y de los cuatro wrappers Decision Twin dependientes, manteniendo intactas las entradas C0 provenance-safe.

## 10. Resultado de Audit 1

El diseño queda depurado con estas restricciones obligatorias:

1. cuarentena por retirada de API pública, no por resultado artificial;
2. ningún `ViabilityResult` externo puede volver a ser presentado como prueba de procedencia;
3. ningún `FrontierAssessment` arbitrario puede elevarse a input provenance-safe por simple recálculo;
4. C0+Trace permanece cerrado e intacto;
5. O4/O2/O3 y VF permanecen funcionalmente intactos;
6. todo wrapper público aguas abajo que dependa de la afirmación Stage 2 provenance-safe debe quedar bloqueado, sin reabrir su core;
7. todos los tests transversales del namespace público deben reflejar la cuarentena real;
8. una reapertura futura exige productor físico y auditable de consecuencias VF.

Con estas depuraciones, la unidad puede pasar a materialización técnica y posteriormente a Audit 2.
