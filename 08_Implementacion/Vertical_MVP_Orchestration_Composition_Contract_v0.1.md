# EIOS — O4 → O2 → O3 → Vertical MVP Composition Contract v0.1

**Estado:** CERRADO PARA IMPLEMENTACIÓN  
**Baseline:** `main @ d41c4ab6316c973f2aace188726651ec9c38c126`  
**Ámbito:** composición técnica de una orquestación O4→O2→O3 ya completada dentro del Vertical MVP mediante la capacidad cerrada `SCENARIO_COORDINATION`.

## 1. Propósito

Cerrar la continuidad funcional desde `O4O2O3OrchestrationResult` hasta `VerticalMVPSupportResult` sin reejecutar generación, materialización, evaluación ni análisis.

## 2. Entrada pública

La operación recibe exclusivamente:

- `PurchaseOperation`;
- `O4O2O3OrchestrationResult` ya completado;
- `policy_version` del límite de ejecución Vertical MVP.

No acepta `DecisionContext` separado. El contexto autorizado se obtiene únicamente de `orchestration_result.preparation.context`.

No acepta `ScenarioEvaluationResult` sueltos ni `O2SupportPackage` externo.

## 3. Composición autorizada

La operación ejecuta únicamente esta cadena:

1. snapshot profundo de entradas;
2. `build_o2_support_from_orchestration(...)`;
3. `run_mvp_execution(..., scenario_coordination_result=support)`;
4. construcción de `VerticalMVPSupportResult` con:
   - `execution` resultante;
   - `rules=None`;
   - `scenario_support=support`.

## 4. Autoridades preservadas

- O4 conserva autoridad sobre generación.
- O2 Scenario Engine conserva identidad/versionado/canonicalización.
- O3 conserva evaluación derivada.
- el puente Orchestration→O2 Support conserva adaptación ya autorizada.
- `scenario_coordination_adapter` conserva semántica de la capacidad Vertical.
- `run_mvp_execution` conserva orden y agregación de estado del Vertical MVP.

Esta fachada no añade mappings de estado.

## 5. Fail-closed

Se conserva literalmente el fail-closed del puente Orchestration→O2 Support:

- sin evaluaciones O3 no existe materialización Vertical de `SCENARIO_COORDINATION`;
- O4 terminal o DRAFT-only no se transforma en estado Vertical inventado;
- O3 `NOT_STARTED` sigue sin equivalencia O2 autorizada;
- compra de otra decisión o escenario base se rechaza;
- contexto externo no puede sustituir el contexto congelado en la orquestación.

## 6. Semántica de estados

Los estados ya autorizados fluyen sin reinterpretación:

- `COMPLETED` permanece soporte completado;
- `PARTIALLY_COMPLETED` permanece parcial;
- `NOT_EVALUABLE` permanece no evaluable;
- `FAILED` permanece fallo técnico.

Ninguno implica aprobación, rechazo, viabilidad empresarial ni selección.

## 7. Alcance deliberadamente estrecho

Esta unidad no acepta ni ejecuta:

- Rules/CRC;
- Price Intelligence;
- TCO;
- QTG;
- Decision Twin;
- Negotiation Intelligence;
- Negotiation Ladder.

Esos componentes conservan sus fachadas e integraciones cerradas. La finalidad de esta unidad es exclusivamente cerrar el hilo de escenarios de extremo a extremo.

## 8. Inmutabilidad y determinismo

- entradas copiadas profundamente;
- el contexto se deriva del snapshot de orquestación;
- no se mutan compra ni orquestación;
- ejecuciones repetidas con mismas entradas producen la misma estructura de soporte/capacidad salvo identificadores que las autoridades cerradas definan explícitamente de otra forma.

## 9. Autoridad decisional prohibida

La fachada no produce:

- score;
- ranking;
- recomendación;
- selección;
- aprobación;
- rechazo empresarial;
- `best_scenario`;
- decisión del CEO.

## 10. Salida

Salida exacta: `VerticalMVPSupportResult`.

Debe contener:

- `execution` con `SCENARIO_COORDINATION` como única capacidad de esta fachada;
- `rules=None`;
- `scenario_support` igual semánticamente al paquete O2 derivado de la orquestación.

## 11. Criterios de aceptación

Las pruebas deben demostrar:

1. orquestación COMPLETED → Vertical MVP con `SCENARIO_COORDINATION`;
2. preservación de contexto/versiones/snapshot;
3. preservación de scenario_support;
4. `NOT_EVALUABLE` no se transforma en falso/no viable;
5. `FAILED` sigue siendo técnico;
6. compra de otra decisión/escenario base falla cerrada;
7. DRAFT-only / O4 terminal sin evaluaciones falla cerrada;
8. la firma pública no acepta `context` separado;
9. inmutabilidad;
10. ausencia de autoridad decisional y de capacidades no solicitadas.

**DICTAMEN DE DISEÑO:** APTO PARA IMPLEMENTACIÓN. Fachada aditiva, estrecha y de procedencia estructuralmente vinculada a la orquestación.