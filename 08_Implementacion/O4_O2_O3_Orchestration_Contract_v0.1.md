# EIOS — O4 → O2 → O3 Orchestration Contract v0.1

**Estado:** CERRADO PARA IMPLEMENTACIÓN TRAS AUDITORÍA 1
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

## 3. Orquestación en dos etapas

La cadena se cierra mediante dos operaciones explícitas para evitar una dependencia circular sobre `scenario_id`.

### Etapa 1 — preparación O4→O2

`prepare_o4_o2_o3_orchestration(...)` recibe:

- `DecisionContext`;
- variables y política O4;
- padre/profundidad opcionales.

Ejecuta exclusivamente `run_o4_o2_materialization` y devuelve `O4O2O3Preparation`, que conserva:

- snapshot inmutable del `DecisionContext`;
- resultado O4→O2 completo;
- los `scenario_id` reales creados por O2.

No ejecuta O3.

### Etapa 2 — finalización O3

Una vez que las autoridades analíticas externas hayan producido resultados para esos `scenario_id`, `complete_o4_o2_o3_orchestration(...)` recibe:

- la preparación exacta de Etapa 1;
- una secuencia de `AuthorizedScenarioAnalytics`.

No vuelve a ejecutar O4 ni O2.

## 4. Paquete analítico autorizado

Cada `AuthorizedScenarioAnalytics` debe contener:

- `scenario_id` exacto de un `ScenarioVersion VALID` de la preparación;
- `assessments` explícito y no vacío;
- `viability_result` explícito y presente;
- estado técnico O3 explícito o `COMPLETED` por defecto;
- limitaciones, trazas y causa de fallo cuando correspondan.

El paquete representa resultados ya producidos/autorizados; no confiere a la orquestación autoridad para calcularlos.

## 5. Condición obligatoria de evaluación

O3 **solo puede invocarse** para un escenario `VALID` cuando existe exactamente un paquete analítico asociado y ese paquete contiene explícitamente:

1. al menos un Assessment ya producido/autorizado;
2. un resultado de Viability Frontier ya producido/autorizado.

La orquestación no puede:

- fabricar Assessment;
- fabricar Viability Frontier;
- sustituir su ausencia por `NOT_EVALUABLE`, `FAILED` u otro estado;
- copiar análisis de otro escenario;
- aceptar paquetes sin identidad de escenario.

Si falta cualquiera de los dos artefactos, el paquete se rechaza antes de cualquier llamada a O3.

## 6. Correspondencia exacta

En Etapa 2:

- se identifican exclusivamente los `ScenarioVersion` con estado `VALID`;
- debe existir exactamente un paquete analítico por cada `scenario_id VALID`;
- no se admiten IDs duplicados;
- no se admiten paquetes para escenarios ausentes de la preparación;
- no se admiten paquetes sobrantes;
- si falta un paquete, la operación falla cerrada antes de evaluar;
- el orden de salida sigue el orden determinista de escenarios O2, no el orden incidental de los paquetes analíticos.

## 7. Procedencia y contexto

`O4O2O3Preparation` conserva el `DecisionContext` usado en la materialización.

Al construir la preparación se verifica que cada escenario O2 conserve:

- `decision_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`.

La Etapa 2 utiliza exclusivamente ese snapshot; no acepta un `DecisionContext` alternativo.

## 8. Escenarios DRAFT

Un candidato O4 sin cambios puede materializarse por O2 como `DRAFT`.

Ese escenario:

- se conserva en la preparación;
- no se entrega a O3;
- no requiere paquete analítico;
- no se fuerza a `VALID` ni a `EVALUATED`.

## 9. Estados O4 no generativos

`EMPTY`, `BLOCKED`, `NOT_EVALUABLE` y `FAILED` se conservan mediante la preparación O4→O2 y producen `evaluations=()`.

En esos casos no se aceptan paquetes analíticos sobrantes.

## 10. Estados O3

La orquestación conserva el estado técnico solicitado en el paquete analítico y delega su validación final a `evaluate_scenario`.

No transforma:

- `COMPLETED` en viable;
- `PARTIALLY_COMPLETED` en rechazo;
- `NOT_EVALUABLE` en no viable;
- `FAILED` en rechazo empresarial.

## 11. Trazabilidad e inmutabilidad

- Etapa 1 usa exclusivamente `run_o4_o2_materialization`.
- Etapa 2 usa exclusivamente `evaluate_scenario`.
- No hay reejecución oculta de O4/O2 en Etapa 2.
- Contexto, preparación y paquetes analíticos se copian profundamente antes de consumo.
- No se modifica O4, O2 ni O3.
- No se introduce identidad paralela.

## 12. Salida

`O4O2O3OrchestrationResult` contiene:

- la `preparation` completa O4→O2;
- `evaluations`: resultados O3 en orden de escenarios O2 válidos.

La salida no contiene ranking, score, recomendación, selección, aprobación, rechazo ni decisión.

## 13. Fuera de alcance

- ejecución de motores de reglas;
- ejecución de Viability Frontier;
- cálculo de Assessment;
- ranking, optimización o selección;
- negociación;
- persistencia, SQL o API;
- Vertical MVP;
- modificación de O4/O2/O3.

## 14. Criterios de aceptación

Las pruebas deben demostrar:

1. Etapa 1 materializa y expone IDs reales O2;
2. Etapa 2 completa la cadena con escenario `VALID` y análisis explícito;
3. rechazo si falta paquete para un escenario válido;
4. rechazo de Assessment vacío;
5. rechazo de Viability ausente;
6. rechazo de ID analítico desconocido o sobrante;
7. rechazo de IDs duplicados;
8. `DRAFT` preservado sin evaluación;
9. estados O4 no generativos sin evaluación;
10. preservación de estados/limitaciones/trazas O3;
11. determinismo independiente del orden de paquetes analíticos;
12. inmutabilidad;
13. ausencia de autoridad decisional;
14. Etapa 2 no reejecuta O4/O2.

## 15. Auditoría 1

La primera versión proponía recibir paquetes identificados por `scenario_id` dentro de la misma llamada que aún debía crear esos IDs mediante O2. Aunque la identidad O2 es determinista, esa interfaz obligaba a predecir o repetir la materialización y creaba una dependencia circular innecesaria.

**Corrección:** la orquestación queda dividida en preparación O4→O2 y finalización O3. Los análisis se producen entre ambas etapas sobre IDs reales ya materializados. La Etapa 2 no reejecuta O4/O2.

**DICTAMEN TRAS DEPURACIÓN:** APTO PARA MATERIALIZACIÓN. La condición de no fabricar análisis es una invariante contractual fail-closed.
