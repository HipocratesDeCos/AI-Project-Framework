# EIOS — Scenario Stage 2 VF Provenance Quarantine Contract v0.1

**Estado:** DISEÑADO — AUDIT 1 SUPERADA — PENDIENTE DE MATERIALIZACIÓN  
**Baseline:** `main @ 9a762927a536d36db3ab852127318ec6628fc216`  
**Ámbito:** frontera pública Scenario Stage 2 ↔ Viability Frontier.

## 1. Propósito

Cerrar una contradicción objetiva de procedencia en la frontera pública de Scenario Stage 2 sin inventar un productor de Viability Frontier que el repositorio no contiene.

La unidad no modifica la semántica de Viability Frontier, O4, O2, O3, C0/Rules ni la autoridad decisional. Su único efecto autorizado es impedir que un `ViabilityResult` construido por un caller pueda presentarse como material provenance-safe suficiente para completar O3.

## 2. Hallazgo objetivo

En el baseline indicado:

- `ProvenancedScenarioAnalyticsInput` acepta `viability_result: ViabilityResult`;
- `build_authorized_scenario_analytics_from_provenanced_assessments(...)` valida C0 `Assessment+Trace` con procedencia fuerte, pero para VF solo comprueba tipo, `decision_id`, `scenario_id` y versiones/snapshot;
- `build_authorized_analytics_from_viability(...)` consume un `ViabilityResult` ya producido y transporta `status`, `assessment_ids`, `rule_ids`, `trace_references` y `limitation` suministrados por el caller;
- `ViabilityResult` es una dataclass públicamente construible;
- los tests de Stage 2 y del E2E vertical construyen manualmente `ViabilityResult` y lo utilizan como prueba de conformidad;
- el contrato de Stage 2 afirma, sin embargo, que un objeto Python construido por el caller no constituye por sí mismo prueba de procedencia.

Existe por tanto una asimetría: C0 demuestra procedencia de `Assessment+Trace`, mientras VF solo demuestra coherencia contextual del resultado desprendido.

## 3. Por qué no se reconstruye VF desde `FrontierAssessment`

`FrontierAssessment` está definido como representación técnica de una consecuencia de frontera **ya autorizada externamente**. `evaluate_viability(...)` valida estructura/contexto y aplica de forma determinista la precedencia cerrada, pero no crea ni autentica la autoridad de esas consecuencias.

No se ha identificado en el baseline un productor físico autorizado que materialice `FrontierAssessment` desde evidencia/autoridad verificable y lo vincule a la ejecución actual. Recalcular `ViabilityResult` a partir de `FrontierAssessment` arbitrario trasladaría el mismo problema una capa aguas arriba.

## 4. Diseño autorizado

### 4.1 Frontera pública `eios.rules`

Mientras no exista productor VF provenance-safe:

- `ProvenancedScenarioAnalyticsInput` deja de formar parte del API público;
- `build_authorized_scenario_analytics_from_provenanced_assessments` deja de formar parte del API público;
- `complete_provenanced_o4_o2_o3_orchestration` deja de formar parte del API público.

No se conserva alias legacy ni compatibilidad silenciosa. Un consumidor que intente importar esos símbolos desde `eios.rules` recibirá el fallo visible nativo de Python.

### 4.2 Módulo `eios.rules.scenario_integration`

La anterior frontera pública se pone en cuarentena. El módulo no debe seguir exportando símbolos que permitan afirmar una finalización Stage 2 provenance-safe basada en un `ViabilityResult` desprendido.

No se sustituye por una función que siempre devuelva un estado artificial ni por una excepción de negocio nueva.

### 4.3 Infraestructura interna

Se preservan:

- `AuthorizedScenarioAnalytics` como transporte interno cuya construcción no prueba procedencia;
- `_complete_o4_o2_o3_orchestration(...)` como función interna;
- `build_authorized_analytics_from_viability(...)` únicamente como bridge context-bound interno, documentado expresamente como **no prueba de procedencia del productor VF**;
- `evaluate_viability(...)`, `FrontierAssessment`, `ViabilityResult` y todos los estados de VF.

La existencia física de estas piezas internas no autoriza su exposición como frontera provenance-safe.

## 5. Fronteras preservadas

Esta unidad no modifica:

- semántica H/U/K/S ni precedencia de VF;
- `VIABLE`, `VIABLE_CON_CONDICIONES`, `NOT_VIABLE`, `NOT_EVALUABLE`;
- procedencia C0 `AssessmentTraceBinding` ni su validador;
- generación O4, materialización O2 o evaluación O3;
- cobertura exacta de escenarios dentro de la orquestación interna;
- Decision Twin, PRICE, TCO, QTG, Scenario Coordination, NI o Ladder;
- autoridad humana final.

No se exige igualdad entre IDs de Assessment C0 y IDs de FrontierAssessment/VF: son familias de artefactos distintas.

## 6. Tests exigidos

La materialización deberá demostrar como mínimo:

1. los tres símbolos inseguros ya no se exportan desde `eios.rules`;
2. `eios.rules.scenario_integration.__all__` no publica una finalización Stage 2 provenance-safe;
3. el test de Stage 2 ya no fabrica `ViabilityResult` para declarar una finalización provenance-safe válida;
4. el E2E vertical ya no fabrica trazas/IDs VF sintéticos para declarar conformidad Stage 2 completa;
5. la procedencia C0+Trace permanece validada por sus tests específicos;
6. la infraestructura interna O4/O2/O3 y VF continúa verde;
7. la suite completa Python + validaciones SQL permanece verde.

## 7. Condición futura de reapertura

Scenario Stage 2 solo podrá volver a exponer una finalización provenance-safe cuando exista evidencia física suficiente para diseñar y auditar un productor VF que:

- reciba consecuencias de frontera desde una fuente/autoridad físicamente identificada;
- vincule dichas consecuencias a `decision_id`, `scenario_id`, reglas, parámetros y snapshot actuales;
- preserve o reconstruya trazabilidad verificable;
- ejecute `evaluate_viability(...)` dentro de la frontera confiable o produzca un resultado cuya procedencia sea demostrable;
- no confunda mera construcción de `FrontierAssessment` o `ViabilityResult` con autorización.

## 8. Gate de cierre

La unidad solo podrá cerrarse tras Audit 2, materialización, CI pre-merge sobre el HEAD exacto de la rama, reconciliación `behind=0`, merge protegido por SHA exacto y CI post-merge sobre el SHA integrado.
