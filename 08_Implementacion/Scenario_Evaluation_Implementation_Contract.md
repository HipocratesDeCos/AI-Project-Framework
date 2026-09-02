# EIOS — O3 · SCENARIO EVALUATION IMPLEMENTATION CONTRACT

**Estado:** IMPLEMENTACIÓN CONTRACTUAL — MATERIALIZACIÓN EN RAMA DE TRABAJO
**Diseño:** `79e28522c09b4c0a7b2ce40ce16641b4a4478b6d`
**Depuración:** `70784bfee4e29ed42b4ebbcadcc5c6cfa719f2f8`
**Auditoría 2:** `60c63b3c6d538bd26b2f207f339b4a43eca3cc08`
**Cierre:** `2fddfebfab4dbeee3ff55df7e7ece6cde05e3d9e`

## 1. Propósito

Definir la frontera técnica mínima para evaluar un `ScenarioVersion` válido sin modificar el escenario ni las fuentes históricas.

## 2. Modelo de implementación

La primera materialización será un evaluador puro que reciba funciones/autoridades analíticas ya existentes y produzca un resultado derivado.

No se crea un segundo motor de reglas ni de viabilidad.

## 3. Entrada

El evaluador recibirá:

- `ScenarioVersion` válido;
- contexto de decisión asociado;
- resultados Assessment producidos para el escenario;
- resultado de Viability Frontier cuando exista;
- referencias de trazabilidad;
- estado técnico explícito.

## 4. Salida

`ScenarioEvaluationResult` deberá conservar:

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

O3 consume `ScenarioVersion` y no altera su contrato. La marca `ScenarioStatus.EVALUATED` solo podrá utilizarse mediante una integración futura explícitamente aprobada; esta primera implementación no mutará el objeto escenario.

## 11. Criterio de pruebas

Las pruebas deberán cubrir al menos:

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
11. determinismo de la representación resultante.

## 12. Fuera de alcance

No se implementan aquí generación automática, optimización, scoring, ranking, selección, recomendación, negociación, persistencia SQL ni API.
