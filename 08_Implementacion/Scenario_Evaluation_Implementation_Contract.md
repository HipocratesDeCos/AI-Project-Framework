# EIOS — O3 · SCENARIO EVALUATION IMPLEMENTATION CONTRACT

**Estado:** CERRADO — MATERIALIZADO — CI VALIDADO
**Diseño:** `79e28522c09b4c0a7b2ce40ce16641b4a4478b6d`
**Depuración:** `70784bfee4e29ed42b4ebbcadcc5c6cfa719f2f8`
**Auditoría 2 corregida:** `b8e34a47e6ab48d37d4fcfd2247170c3bc157a62`
**Cierre:** `62b921be38a37bb56d09d9deaf293064654d060f`
**Materialización / merge:** `1c323c1855577b4200f76ecb0d36db1e0fe2c1c4`

## 1. Propósito

Definir la frontera técnica mínima para evaluar un `ScenarioVersion` válido sin modificar el escenario ni las fuentes históricas.

## 2. Modelo de implementación

La materialización es un evaluador puro que recibe resultados analíticos ya existentes y produce un resultado derivado.

O3 no ejecuta ni duplica un segundo motor de reglas o de viabilidad; consume los resultados proporcionados por las autoridades analíticas existentes.

## 3. Entrada

El evaluador recibe:

- `ScenarioVersion` válido;
- contexto de decisión asociado;
- resultados Assessment producidos para el escenario;
- resultado de Viability Frontier cuando exista;
- referencias de trazabilidad;
- estado técnico explícito.

## 4. Salida

`ScenarioEvaluationResult` conserva:

- `scenario_id`;
- `decision_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`;
- estado técnico;
- Assessment derivados;
- resultado de viabilidad opcional;
- limitaciones;
- referencias de trazabilidad.

## 5. Estados

```text
NOT_STARTED
RUNNING
COMPLETED
PARTIALLY_COMPLETED
NOT_EVALUABLE
FAILED
```

`FAILED` requiere causa explícita.

## 6. Inmutabilidad

El evaluador no modifica `PurchaseOperation`, `ScenarioVersion`, evidencia, reglas, parámetros ni Assessment históricos.

## 7. Semántica

```text
COMPLETED           ≠ VIABLE
PARTIALLY_COMPLETED ≠ NOT_VIABLE
NOT_EVALUABLE       ≠ NOT_VIABLE
FAILED              ≠ NOT_VIABLE
```

## 8. Autoridad

El componente no puede seleccionar, recomendar, aprobar, rechazar, comprar, negociar, puntuar, rankear u optimizar.

Assessment y Viability Frontier mantienen sus propias autoridades.

## 9. Versionado

Se reutiliza el `DecisionContext` del escenario. No se introduce `decision_version`, un snapshot alternativo ni un fingerprint paralelo de decisión.

## 10. Integración O2

O3 consume `ScenarioVersion` y no altera su contrato. La marca `ScenarioStatus.EVALUATED` solo podrá utilizarse mediante una integración futura explícitamente aprobada; esta implementación no muta el objeto escenario.

## 11. Criterio de pruebas

Las pruebas cubren:

1. escenario válido;
2. escenario no válido rechazado;
3. preservación de identidad y versiones;
4. resultado completo;
5. resultado parcial;
6. no evaluable;
7. fallo técnico con causa;
8. no mutación;
9. separación de Assessment y Viability;
10. ausencia de autoridad decisional;
11. determinismo de la representación resultante;
12. rechazo de `COMPLETED` sin Assessment;
13. rechazo de `COMPLETED` sin Viability;
14. rechazo de `COMPLETED` con limitaciones pendientes.

## 12. Fuera de alcance

No se implementan aquí generación automática, optimización, scoring, ranking, selección, recomendación, negociación, persistencia SQL ni API.

## 13. Estado de cierre

**DICTAMEN:** CERRADO — MATERIALIZADO — CI VALIDADO.

**CI de rama:** Run #365 — SUCCESS.

**Merge:** PR #6 → `main`, commit `1c323c1855577b4200f76ecb0d36db1e0fe2c1c4`.

**CI post-merge `main`:** Run #366 — SUCCESS.

La implementación contractual queda cerrada para el alcance O3 vigente. Cualquier ampliación sobre ejecución analítica, activación de `EVALUATED`, generación de escenarios, optimización o persistencia requiere un nuevo alcance explícito.
