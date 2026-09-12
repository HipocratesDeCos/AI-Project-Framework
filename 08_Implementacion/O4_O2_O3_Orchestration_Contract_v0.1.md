# EIOS — O4 → O2 → O3 Orchestration Contract v0.1

**Estado:** CERRADO PARA IMPLEMENTACIÓN
**Baseline:** `main @ e8cdc8a04bdeed3abbf48e0b1573feea3ac0b280`
**Ámbito:** orquestación técnica de generación O4, materialización O2 y evaluación O3 sin producir análisis nuevos.

## 1. Propósito

Cerrar la cadena técnica `O4 → O2 → O3` reutilizando exclusivamente las autoridades ya cerradas de cada componente.

La orquestación no ejecuta reglas analíticas, no calcula Assessment, no ejecuta Viability Frontier y no crea resultados sustitutivos cuando dichos artefactos faltan.

## 2. Autoridad

- O4 conserva generación finita, determinista y estructural.
- O2 conserva identidad, fingerprint, canonicalización, versionado y estado estructural del escenario.
- O3 conserva la construcción del resultado derivado de evaluación.
- Assessment y Viability Frontier siguen siendo producidos por sus autoridades analíticas existentes.
- La decisión empresarial continúa fuera de esta orquestación.

## 3. Entrada

La operación recibe:

- `DecisionContext`;
- variables y política O4;
- padre/profundidad O4 opcionales;
- una secuencia de paquetes `AuthorizedScenarioAnalytics` ya producidos externamente.

Cada paquete analítico debe contener:

- `scenario_id` exacto de un `ScenarioVersion VALID` creado por O2 en esta misma ejecución;
- `assessments` no vacío;
- `viability_result` presente;
- estado técnico O3 explícito o `COMPLETED` por defecto;
- limitaciones, trazas y causa de fallo cuando correspondan.

## 4. Condición obligatoria de evaluación

O3 **solo puede invocarse** para un escenario `VALID` cuando existe exactamente un paquete analítico asociado y ese paquete contiene explícitamente:

1. al menos un Assessment ya producido/autorizado;
2. un resultado de Viability Frontier ya producido/autorizado.

La orquestación no puede:

- fabricar Assessment;
- fabricar Viability Frontier;
- sustituir su ausencia por `NOT_EVALUABLE`, `FAILED` u otro estado;
- copiar análisis de otro escenario;
- aceptar paquetes sin identidad de escenario.

Si falta cualquiera de los dos artefactos, la operación falla cerrada antes de llamar a O3.

## 5. Correspondencia exacta

Tras O4→O2:

- se identifican exclusivamente los `ScenarioVersion` con estado `VALID`;
- debe existir exactamente un paquete analítico por cada `scenario_id VALID`;
- no se admiten IDs duplicados;
- no se admiten paquetes para escenarios no creados en la misma ejecución;
- no se admiten paquetes sobrantes;
- el orden de salida sigue el orden determinista de escenarios O2, no el orden incidental de los paquetes analíticos.

## 6. Escenarios DRAFT

Un candidato O4 sin cambios puede materializarse por O2 como `DRAFT`.

Ese escenario:

- se conserva en el resultado O4→O2;
- no se entrega a O3;
- no requiere paquete analítico;
- no se fuerza a `VALID` ni a `EVALUATED`.

## 7. Estados O4 no generativos

`EMPTY`, `BLOCKED`, `NOT_EVALUABLE` y `FAILED` se conservan mediante el resultado O4→O2 y producen `evaluations=()`.

En esos casos no se aceptan paquetes analíticos sobrantes.

## 8. Estados O3

La orquestación conserva literalmente el estado técnico solicitado en el paquete analítico y delega su validación final a `evaluate_scenario`.

No transforma:

- `COMPLETED` en viable;
- `PARTIALLY_COMPLETED` en rechazo;
- `NOT_EVALUABLE` en no viable;
- `FAILED` en rechazo empresarial.

## 9. Trazabilidad e inmutabilidad

- O4 y O2 se ejecutan mediante `run_o4_o2_materialization`.
- O3 se ejecuta exclusivamente mediante `evaluate_scenario`.
- `DecisionContext` y entradas son copiadas profundamente antes de consumo.
- Los paquetes analíticos se copian profundamente antes de O3.
- No se modifica O4, O2 ni O3.
- No se introduce identidad paralela.

## 10. Salida

`O4O2O3OrchestrationResult` contiene:

- `materialization`: resultado O4→O2 completo;
- `evaluations`: resultados O3 en orden de escenarios O2 válidos.

La salida no contiene ranking, score, recomendación, selección, aprobación, rechazo ni decisión.

## 11. Fuera de alcance

- ejecución de motores de reglas;
- ejecución de Viability Frontier;
- cálculo de Assessment;
- ranking, optimización o selección;
- negociación;
- persistencia, SQL o API;
- Vertical MVP;
- modificación de O4/O2/O3.

## 12. Criterios de aceptación

Las pruebas deben demostrar:

1. cadena completa con escenario `VALID` y análisis explícito;
2. rechazo si falta paquete para un escenario válido;
3. rechazo de Assessment vacío;
4. rechazo de Viability ausente;
5. rechazo de ID analítico desconocido o sobrante;
6. rechazo de IDs duplicados;
7. `DRAFT` preservado sin evaluación;
8. estados O4 no generativos sin evaluación;
9. preservación de estados/limitaciones/trazas O3;
10. determinismo independiente del orden de paquetes analíticos;
11. inmutabilidad;
12. ausencia de autoridad decisional.

**DICTAMEN DE DISEÑO:** APTO PARA IMPLEMENTACIÓN. La condición de no fabricar análisis es una invariante contractual y fail-closed, no una convención opcional.
