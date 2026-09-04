# EIOS — O2 Coordinated Decision Support

**Estado:** DISEÑO CERRADO PARA IMPLEMENTACIÓN
**Naturaleza:** evolución funcional sobre O1

## Propósito

O2 coordina resultados de múltiples escenarios pertenecientes a una misma decisión sin crear un motor autónomo de decisión.

## Invariantes

- `decision_id` común y `scenario_id` estable por escenario.
- aislamiento de resultados, evidencias, estados y trazas.
- reglas, parámetros y snapshot preservados por ejecución.
- degradación explícita: `BLOCKED`, `PARTIALLY_COMPLETED`, `NOT_EVALUABLE`, `FAILED`.
- comparación descriptiva, nunca ranking ni preferencia.
- no mutación silenciosa de `PurchaseOperation`.
- identidad de ejecución determinista para entradas materiales equivalentes.
- decisión humana fuera del paquete O2.

## Frontera

O2 puede coordinar capacidades ya autorizadas; no las redefine ni sustituye. No aprueba, rechaza, recomienda, selecciona, puntúa ni optimiza.

## Estados

`READY`, `RUNNING`, `COMPLETED`, `BLOCKED`, `PARTIALLY_COMPLETED`, `NOT_EVALUABLE`, `FAILED`.

`NOT_EVALUABLE ≠ FALSE` y `FAILED ≠ resultado empresarial negativo`.

## Comparación

Expone observaciones, diferencias, ausencias, estados, elementos no resueltos y trazabilidad por escenario. No genera score, ranking, selección automática ni recomendación.

**Estado:** DISEÑO CERRADO. Cualquier ampliación funcional requiere nuevo alcance y ciclo completo.