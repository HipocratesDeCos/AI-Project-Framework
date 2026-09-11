# EIOS — STK-M04 · Cierre de autoridad metodológica de cobertura v0.1

**Estado:** CERRADO — MATERIALIZADO — VALIDACIÓN LOCAL SUPERADA
**Baseline:** `287121fc940c98ec8d35d3a223608bef63e22bdf`
**Ámbito:** fórmula, unidad, evidencia, estados y gobierno de `coverage`; sin motor cuantitativo

## 1. DISEÑAR

Formalizar definición, relación base, dimensiones, fecha, fuentes, cero, ausencia, umbrales y vigencia de cobertura.

## 2. AUDITAR

La decisión se contrastó con STK-M01…M03, parámetros `STK-003`, `STK-004`, `STK-006`, reglas `R-STK-002…004` y variables canónicas de la matriz STK v0.4.

Existe autoridad suficiente para cerrar M04. No existe para validar 30/90 días, la ventana de 12 meses ni la composición detallada de stock disponible.

## 3. DEPURAR

- `stock_available` queda sujeto a evidencia y no incorpora pedidos, tránsito o compromisos por inferencia;
- la fuente y ventana del promedio deben declararse en la política;
- cero confirmado produce `UNBOUNDED / NOT_APPLICABLE`, no infinito numérico;
- ausencia produce `UNKNOWN / NOT_EVIDENCED`, nunca cero;
- `as_of_date` queda como fecha empresarial, pendiente de mapeo contractual no ambiguo con `evaluation_date`;
- evaluar umbrales no transfiere autoridad decisional a EIOS.

## 4. AUDITAR 2

Resultado:

- `5 passed` en las pruebas específicas M04;
- `298 passed` en la suite completa, con advertencias Pydantic y UserWarning promovidas a error;
- `STK-M05…M10` permanecen pendientes;
- STK continúa no apto para implementación cuantitativa;
- no cambia código ejecutable, SQL, reglas, parámetros ni contratos técnicos.

## 5. CERRAR

`STK-M04` queda cerrado como autoridad metodológica. Las políticas cuantitativas concretas deberán declarar fuente, ventana, composición del numerador, umbrales, versión y vigencia.

## 6. MATERIALIZAR

Se actualiza la matriz STK y se añaden autoridad M04 y pruebas de no regresión. No se modifican catálogo, reglas, contratos ni código ejecutable.

## 7. CI

La CI externa permanece pendiente hasta la publicación del SHA materializado.
