# EIOS — PRE Temporal Dependency Reconciliation — Design v0.1

## Estado

**Fase:** DISEÑAR  
**Unidad:** PRE-TEMP-DEP-01  
**Baseline:** `main @ d6494fb809e188875be11f0c8074ae8e9c10fa9e`  
**Naturaleza:** reconciliación documental; sin cambio funcional ni runtime.

## 1. Hallazgo objetivo

`01_Modelo/Price_Intelligence_Specification_Gaps.md` resolvió explícitamente `GAP-PI-TEMP-01`:

```text
R-PRE-001: “reciente” = dentro de P-PRE-001 en el diseño MVP.
```

Sin embargo:

- `02_Parametros/Matriz_Parametros_Reglas_MVP.md` mantiene `P-PRE-001` como pendiente de cruce;
- `04_Reglas/Rule_Dependency_Matrix.md` no contiene la dependencia canónica `P-PRE-001 → R-PRE-001`.

Existe por tanto una divergencia documental entre una decisión metodológica ya resuelta y sus vistas de dependencias.

## 2. Objetivo

Reconciliar esa relación ya autorizada sin crear semántica nueva.

La materialización prevista es:

1. actualizar la vista especializada Parámetro ↔ Regla para marcar `P-PRE-001 → R-PRE-001` como confirmada;
2. incorporar en la RDM una dependencia canónica explícita;
3. preservar el resto de relaciones y estados sin modificación.

## 3. Dependencia propuesta para la RDM

| Campo | Valor |
|---|---|
| `Dependency_ID` | `DEP-PRE-001-RPRE-001` |
| `Rule_ID` | `R-PRE-001` |
| `Dependency_Type` | `PARAMETER` |
| `Source_ID` | `P-PRE-001` |
| `Source_Domain` | `PARAMETER` |
| `Function` | Horizonte temporal autorizado que define “reciente” para la operación comparable de `R-PRE-001` |
| `Criticality` | `PENDING` |
| `Evidence_Source` | `01_Modelo/Price_Intelligence_Specification_Gaps.md` |
| `Evidence_Status` | `CONFIRMED` |
| `Evaluability_Impact` | `PENDING` |
| `Fallback` | `NONE` |
| `Affected_Component` | `NONE` |

## 4. Límites de autoridad

Esta reconciliación:

- no implementa `R-PRE-001`;
- no modifica Price Intelligence C1;
- no introduce algoritmos, percentiles, ponderaciones, selección ni agregación;
- no convierte `P-PRE-001 = 3 meses` en política empresarial definitiva; el catálogo conserva ese valor como inicial y pendiente de validación;
- no modifica `P-PRE-002`, cuya función ampliada no demuestra por sí sola un consumidor directo adicional;
- no altera `P-PRE-004 → R-PRE-001` ni `P-PRE-005 → R-PRE-002`;
- no asigna `Criticality` ni `Evaluability_Impact` sin autoridad documental;
- no crea dependencias `DATA`, `EVIDENCE`, `COMPONENT`, `DERIVED` o `CONTROL` adicionales;
- no modifica código, tests ejecutables, C0, CRC, QTG ni arquitectura.

## 5. Clasificación del vínculo

La relación se registra como `PARAMETER`, no como `DERIVED`: `P-PRE-001` es el parámetro configurable que define directamente el horizonte temporal de “reciente” utilizado por la condición de `R-PRE-001`. No se ha documentado una transformación intermedia que justifique clasificarla como `DERIVED`.

## 6. Invariantes

1. PRICE/PR continúa siendo una evaluación económica separada de la decisión empresarial.
2. Temporalidad determina pertinencia temporal; no representatividad ni peso.
3. La relación documental confirmada no equivale a implementación runtime.
4. Valor inicial de catálogo ≠ política empresarial definitiva.
5. Ningún campo pendiente se completa por inferencia.

## 7. Criterio de avance

Solo se podrá pasar a MATERIALIZAR si Audit 1, Depuración y Audit 2 confirman que la relación está expresamente autorizada, que no altera semántica funcional y que el delta documental queda limitado a las dos matrices afectadas más los artefactos de control del método EIOS.
