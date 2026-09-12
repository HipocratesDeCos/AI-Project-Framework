# EIOS — O4 → O2 → O3 → O2 Support Integration Contract v0.1

**Estado:** CERRADO PARA IMPLEMENTACIÓN  
**Baseline:** `main @ 5462ae829d5fb44e3d613d5db5527b911e0385bb`  
**Ámbito:** enlace técnico desde una orquestación O4→O2→O3 ya completada hacia el `O2SupportPackage` consumido por `SCENARIO_COORDINATION`.

## 1. Propósito

Cerrar la continuidad técnica entre la orquestación controlada O4→O2→O3 y la capacidad Vertical `SCENARIO_COORDINATION`, sin introducir una nueva semántica de estados ni reejecutar componentes cerrados.

La integración debe reutilizar exclusivamente:

- `O4O2O3OrchestrationResult` como fuente ya materializada/evaluada;
- `build_o2_support_from_o3` como puente autorizado O3→O2;
- `O2SupportPackage` como único sobre de soporte de escenarios;
- `scenario_coordination_adapter` como autoridad posterior de adaptación al Vertical MVP.

## 2. Autoridad y fronteras

Esta integración no puede:

- ejecutar O4;
- volver a materializar O2 Scenario Engine;
- ejecutar O3;
- ejecutar Assessment ni Viability Frontier;
- reinterpretar estados O3;
- fabricar escenarios cuando no existen evaluaciones;
- crear ranking, score, recomendación, selección, aprobación, rechazo o decisión.

## 3. Entrada

La operación pública recibe únicamente:

1. `PurchaseOperation`;
2. `O4O2O3OrchestrationResult` ya producido.

El `DecisionContext` no se suministra como argumento separado. Se toma exclusivamente de `orchestration_result.preparation.context`, evitando que un consumidor pueda asociar el resultado a un contexto externo distinto.

## 4. Condición mínima de materialización de soporte

La integración exige `orchestration_result.evaluations` no vacío.

Si no existe al menos una evaluación O3, falla cerrada.

Esto incluye, entre otros:

- O4 `EMPTY`;
- O4 `BLOCKED`;
- O4 `NOT_EVALUABLE`;
- O4 `FAILED`;
- materialización O2 compuesta solo por escenarios `DRAFT`;
- cualquier resultado que legítimamente finalice sin O3.

Esos estados permanecen en su autoridad de origen y no se convierten artificialmente en estados O2 Support.

## 5. Identidad y procedencia

La integración conserva el `DecisionContext` incluido en la preparación O4→O2→O3.

La coherencia con `PurchaseOperation` se delega al puente cerrado `build_o2_support_from_o3`, que exige:

- mismo `decision_id`;
- mismo `scenario_id` base.

La coherencia de cada evaluación O3 con decisión, reglas, parámetros y snapshot también permanece delegada al mismo puente cerrado.

No existe argumento de contexto alternativo ni mecanismo de override.

## 6. Estados

Los estados O3 se trasladan únicamente mediante la equivalencia literal ya autorizada en `adapt_o3_result_for_o2`.

Por tanto:

- `COMPLETED` → `COMPLETED`;
- `PARTIALLY_COMPLETED` → `PARTIALLY_COMPLETED`;
- `NOT_EVALUABLE` → `NOT_EVALUABLE`;
- `FAILED` → `FAILED`;
- otros estados solo pasan si el puente O3→O2 ya dispone de equivalencia literal autorizada.

No se añade ningún mapping nuevo.

## 7. Trazabilidad y contenido

Assessments, Viability Frontier, trazas, limitaciones y causa de fallo se conservan exclusivamente mediante el puente O3→O2 existente.

La integración no inspecciona su significado de negocio ni altera su contenido.

## 8. Determinismo e inmutabilidad

- El resultado de orquestación y la compra se copian profundamente antes de consumo.
- El orden incidental de evaluaciones no crea semántica nueva; O2 conserva su orden determinista por `scenario_id`.
- La integración no muta entradas.
- La salida es un `O2SupportPackage` ordinario, sin tipo paralelo.

## 9. Salida y siguiente frontera

La salida pública es exactamente `O2SupportPackage`.

Ese objeto puede ser entregado sin adaptación adicional de significado a:

- `validate_scenario_coordination_context`;
- `adapt_scenario_coordination`;
- `run_mvp_execution(..., scenario_coordination_result=...)`.

La presente integración no modifica esos componentes cerrados.

## 10. Criterios de aceptación

Las pruebas deben demostrar:

1. cadena válida Orquestación → O2 Support;
2. preservación de identidad/versiones/snapshot;
3. preservación de Assessment y Viability;
4. preservación de estados, trazas, limitaciones y fallos;
5. determinismo con varios escenarios;
6. rechazo de `PurchaseOperation` de otra decisión;
7. rechazo de `PurchaseOperation` con otro escenario base;
8. rechazo fail-closed cuando no hay evaluaciones O3;
9. rechazo de estados O3 sin equivalencia O2 ya autorizada;
10. inmutabilidad de entradas;
11. ausencia de autoridad decisional;
12. compatibilidad directa con `SCENARIO_COORDINATION` existente.

**DICTAMEN DE DISEÑO:** APTO PARA IMPLEMENTACIÓN. El enlace es estrictamente adaptativo y no abre semántica nueva.