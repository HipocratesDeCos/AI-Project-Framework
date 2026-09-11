# EIOS — STK-M05 · Cierre de autoridad metodológica de proyección v0.1

**Estado:** CERRADO — MATERIALIZADO — VALIDACIÓN LOCAL SUPERADA
**Baseline:** `f8b261ab9778b70475b6e079b90ae1410d217153`
**Ámbito:** relación proyectiva, evidencia, temporalidad, ausencia y autoridad; sin motor cuantitativo

## 1. DISEÑAR

Formalizar estado inicial, relación de proyección, horizonte, entradas, salidas, `lead_time`, fecha, ausencia, resultados, versión y autoridad decisional.

## 2. AUDITAR

La decisión se contrastó con STK-M01…M04, reglas `R-STK-001…004`, parámetros `PYE-001…006`, variables canónicas y especificación funcional.

Existe autoridad suficiente para cerrar M05. Los valores iniciales del catálogo y la mecánica de pedidos pendientes y tránsito continúan sin autoridad definitiva.

## 3. DEPURAR

- solo movimientos con existencia, cantidad y fecha evidenciadas participan como entradas;
- `lead_time` no crea una compra ni recepción;
- salidas de distinta semántica no se mezclan sin regla;
- un elemento desconocido no se omite ni convierte en cero;
- M06 conserva la incorporación y no duplicación de pedidos y tránsito;
- M09 conserva el impacto global de ausencia;
- una proyección no decide comprar ni reponer.

## 4. AUDITAR 2

Resultado:

- `5 passed` en las pruebas específicas M05;
- `303 passed` en la suite completa, con advertencias Pydantic y UserWarning promovidas a error;
- `STK-M06…M10` permanecen pendientes;
- STK continúa no apto para implementación cuantitativa;
- no cambia código ejecutable, SQL, reglas, parámetros ni contratos técnicos.

## 5. CERRAR

`STK-M05` queda cerrado como autoridad metodológica proyectiva. Las políticas concretas deben declarar horizonte, granularidad, fuentes, movimientos, versión y vigencia.

## 6. MATERIALIZAR

Se actualiza la matriz STK y se añaden autoridad M05 y pruebas de no regresión. No se modifican catálogo, reglas, contratos ni código ejecutable.

## 7. CI

La CI externa permanece pendiente hasta la publicación del SHA materializado.
