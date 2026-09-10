# EIOS — STK-M02 · Cierre de autoridad metodológica de stock mínimo v0.1

**Estado:** CERRADO — MATERIALIZADO — VALIDACIÓN LOCAL SUPERADA
**Baseline:** `6d417e6f40505609c5d086deb5a3e6913b2a91a3`
**Ámbito:** definición y relaciones de `stock_minimum`; sin fórmula ni implementación cuantitativa

## 1. DISEÑAR

Formalizar la decisión humana sobre el significado, unidad, procedencia autorizada y relaciones de `stock_minimum` con `safety_stock`, cobertura y demanda.

El alcance cierra `STK-M02` sin fijar fórmula, valor inicial, fechas de recálculo ni automatización de reposición.

## 2. AUDITAR

La decisión se contrastó con la matriz STK v0.2, `STK-M01`, el parámetro `STK-001`, los parámetros relacionados y las reglas `R-STK-001…004`.

Resultado: existe autoridad suficiente para cerrar la semántica y las relaciones conceptuales de M02. No existe autoridad suficiente para una fórmula o valor cuantitativo, que permanecen fuera de la materialización.

## 3. DEPURAR

Se hacen explícitas las siguientes fronteras:

- `safety_stock` puede formar parte de `stock_minimum`, pero no es equivalente;
- cobertura expresa protección combinando el umbral con demanda, sin definir todavía la fórmula M04;
- una variación de demanda requiere recálculo o autorización trazable y no altera silenciosamente el valor vigente;
- `UNKNOWN / NOT_EVIDENCED` nunca se convierte en cero o estimación implícita;
- alcanzar el umbral no constituye una orden automática de reposición.

## 4. AUDITAR 2

Resultado:

- `4 passed` en las pruebas específicas M02;
- `289 passed` en la suite completa, con advertencias Pydantic y UserWarning promovidas a error;
- `STK-M03…M10` permanecen pendientes;
- STK continúa no apto para implementación cuantitativa;
- no existe modificación de código ejecutable, SQL, reglas, parámetros o contratos técnicos.

## 5. CERRAR

`STK-M02` queda cerrado como autoridad metodológica semántica. La política o fórmula cuantitativa concreta deberá disponer de autoridad y trazabilidad propias antes de ser utilizada.

## 6. MATERIALIZAR

La materialización actualiza la matriz STK, añade `STK_M02_Minimum_Stock_Authority.md` y pruebas de no regresión. No modifica el catálogo ni asigna un valor a `STK-001`.

## 7. CI

La validación local reproduce el job Python vigente. GitHub Actions sobre el SHA materializado y sobre su eventual integración constituye el gate externo final.
