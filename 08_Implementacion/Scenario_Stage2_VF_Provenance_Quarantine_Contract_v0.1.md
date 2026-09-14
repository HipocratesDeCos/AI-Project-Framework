# EIOS — Scenario Stage 2 VF Provenance Quarantine Contract v0.1

**Estado:** 🔒 CERRADO — AUDITORÍA 2 SUPERADA — MATERIALIZADO — PENDIENTE CI  
**Baseline:** `main @ 9a762927a536d36db3ab852127318ec6628fc216`  
**Ámbito:** frontera pública Scenario Stage 2 ↔ Viability Frontier y wrappers públicos aguas abajo que dependan de esa afirmación de procedencia.

## 1. Propósito

Cerrar una contradicción objetiva de procedencia en la frontera pública de Scenario Stage 2 sin inventar un productor de Viability Frontier que el repositorio no contiene.

La unidad no modifica la semántica de Viability Frontier, O4, O2, O3, C0/Rules, Decision Twin core ni la autoridad decisional. Su efecto autorizado es impedir que un `ViabilityResult` construido por un caller pueda presentarse como material provenance-safe suficiente para completar O3 o para alimentar wrappers públicos aguas abajo que hereden esa misma afirmación.

## 2. Hallazgo objetivo

En el baseline indicado:

- `ProvenancedScenarioAnalyticsInput` acepta `viability_result: ViabilityResult`;
- `build_authorized_scenario_analytics_from_provenanced_assessments(...)` valida C0 `Assessment+Trace` con procedencia fuerte, pero para VF solo comprueba tipo, `decision_id`, `scenario_id` y versiones/snapshot;
- el antiguo `build_authorized_analytics_from_viability(...)` consumía un `ViabilityResult` ya producido y transportaba `status`, `assessment_ids`, `rule_ids`, `trace_references` y `limitation` suministrados por el caller;
- `ViabilityResult` es una dataclass públicamente construible;
- los tests de Stage 2, del E2E vertical y de la integración Decision Twin construían manualmente `ViabilityResult` y lo utilizaban como prueba de conformidad;
- el contrato de Stage 2 afirma, sin embargo, que un objeto Python construido por el caller no constituye por sí mismo prueba de procedencia.

Existe por tanto una asimetría: C0 demuestra procedencia de `Assessment+Trace`, mientras VF solo demuestra coherencia contextual del resultado desprendido. Todo wrapper que se autodenomine provenance-safe y dependa de esa salida Stage 2 hereda la misma insuficiencia.

## 3. Por qué no se reconstruye VF desde `FrontierAssessment`

`FrontierAssessment` está definido como representación técnica de una consecuencia de frontera **ya autorizada externamente**. `evaluate_viability(...)` valida estructura/contexto y aplica de forma determinista la precedencia cerrada, pero no crea ni autentica la autoridad de esas consecuencias.

No se ha identificado en el baseline un productor físico autorizado que materialice `FrontierAssessment` desde evidencia/autoridad verificable y lo vincule a la ejecución actual. Recalcular `ViabilityResult` a partir de `FrontierAssessment` arbitrario trasladaría el mismo problema una capa aguas arriba.

## 4. Diseño autorizado

### 4.1 Frontera pública `eios.rules`

Mientras no exista productor VF provenance-safe:

- `ProvenancedScenarioAnalyticsInput` deja de formar parte del API público;
- `build_authorized_scenario_analytics_from_provenanced_assessments` deja de formar parte del API público;
- `complete_provenanced_o4_o2_o3_orchestration` deja de formar parte del API público;
- `DecisionTwinInvoker`, `ProvenancedDecisionTwinAlternativeInput`, `build_provenanced_decision_twin_comparison` y `build_provenanced_decision_twin_invoker` dejan de formar parte del API público porque dependen de la frontera Stage 2 en cuarentena.

No se conserva alias legacy ni compatibilidad silenciosa. Un consumidor que intente importar esos símbolos desde `eios.rules` recibe el fallo visible nativo de Python.

### 4.2 Módulo `eios.rules.scenario_integration`

La anterior frontera pública queda en cuarentena. El módulo no exporta símbolos que permitan afirmar una finalización Stage 2 provenance-safe basada en un `ViabilityResult` desprendido.

No se sustituye por una función que siempre devuelva un estado artificial ni por una excepción de negocio nueva.

### 4.3 Integración pública Decision Twin dependiente de Stage 2

`eios.rules.decision_twin_integration` queda igualmente en cuarentena porque reconstruía Decision Twin a través de la frontera Stage 2 ahora bloqueada y le atribuía procedencia segura.

La cuarentena afecta solo al wrapper público provenance-safe. No modifica `eios.core.decision_twin`, `eios.core.decision_twin_engine`, `compare_alternatives(...)` ni la semántica descriptiva del Decision Twin cerrado.

### 4.4 Infraestructura interna

Se preservan:

- `AuthorizedScenarioAnalytics` como transporte interno cuya construcción no prueba procedencia;
- `_complete_o4_o2_o3_orchestration(...)` como función interna;
- `_build_context_bound_analytics_from_viability(...)` como helper interno, fuera de `__all__`, que acredita únicamente coherencia contextual y **no procedencia del productor VF**;
- `evaluate_viability(...)`, `FrontierAssessment`, `ViabilityResult` y todos los estados de VF;
- el comparador core de Decision Twin y sus contratos cerrados.

La existencia física de estas piezas internas no autoriza su exposición como frontera provenance-safe.

## 5. Fronteras preservadas

Esta unidad no modifica:

- semántica H/U/K/S ni precedencia de VF;
- `VIABLE`, `VIABLE_CON_CONDICIONES`, `NOT_VIABLE`, `NOT_EVALUABLE`;
- procedencia C0 `AssessmentTraceBinding` ni su validador;
- generación O4, materialización O2 o evaluación O3;
- cobertura exacta de escenarios dentro de la orquestación interna;
- semántica, comparación y autoridad del Decision Twin core;
- PRICE, TCO, QTG, Scenario Coordination, NI o Ladder;
- autoridad humana final.

No se exige igualdad entre IDs de Assessment C0 y IDs de FrontierAssessment/VF: son familias de artefactos distintas.

## 6. Tests exigidos

La materialización debe demostrar como mínimo:

1. los tres símbolos inseguros Stage 2 ya no se exportan desde `eios.rules`;
2. `eios.rules.scenario_integration.__all__` no publica una finalización Stage 2 provenance-safe;
3. los cuatro símbolos de integración Decision Twin dependientes de Stage 2 tampoco se exportan desde `eios.rules`;
4. `eios.rules.decision_twin_integration.__all__` queda vacío y el comparador Decision Twin core sigue disponible;
5. los tests ya no fabrican `ViabilityResult` para declarar una finalización provenance-safe válida;
6. el E2E vertical ya no fabrica trazas/IDs VF sintéticos para declarar conformidad Stage 2 completa;
7. la procedencia C0+Trace permanece validada por sus tests específicos;
8. la infraestructura interna O4/O2/O3, VF y Decision Twin core continúa verde;
9. la suite completa Python + validaciones SQL permanece verde.

Los puntos 1–7 han sido verificados por inspección y tests materializados. Los puntos 8–9 quedan condicionados a CI completa.

## 7. Condición futura de reapertura

Scenario Stage 2 y los wrappers provenance-safe que dependan de él solo podrán volver a exponerse cuando exista evidencia física suficiente para diseñar y auditar un productor VF que:

- reciba consecuencias de frontera desde una fuente/autoridad físicamente identificada;
- vincule dichas consecuencias a `decision_id`, `scenario_id`, reglas, parámetros y snapshot actuales;
- preserve o reconstruya trazabilidad verificable;
- ejecute `evaluate_viability(...)` dentro de la frontera confiable o produzca un resultado cuya procedencia sea demostrable;
- no confunda mera construcción de `FrontierAssessment` o `ViabilityResult` con autorización.

La reapertura de Decision Twin integration requiere además que la cadena positiva Stage 2 de la que depende haya superado previamente esa condición.

## 8. Gate de cierre

Audit 2 ha sido superada y la materialización está auditada. El cierre físico final continúa condicionado a CI pre-merge sobre el HEAD exacto de la rama, reconciliación `behind=0`, merge protegido por SHA exacto y CI post-merge sobre el SHA integrado.
