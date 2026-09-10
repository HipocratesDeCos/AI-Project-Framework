# EIOS — STK-M03 · Cierre de autoridad metodológica de stock de seguridad v0.1

**Estado:** CERRADO — MATERIALIZADO — VALIDACIÓN LOCAL SUPERADA
**Baseline:** `fe8aefa46c2f33cf7f15a7a9f82ba1ba22438d7c`
**Ámbito:** definición y gobierno de `safety_stock`; sin fórmula ni implementación cuantitativa

## 1. DISEÑAR

Formalizar significado, unidad, incertidumbre, evidencia, relación con `stock_minimum`, ausencia, recálculo y vigencia.

## 2. AUDITAR

Se contrastó con matriz STK v0.3, `STK-M01`, `STK-M02`, `STK-002` y reglas `R-STK-001…004`. Existe autoridad semántica suficiente. El 15 % del catálogo sigue pendiente y no es fórmula autorizada.

## 3. DEPURAR

Se preserva la distinción con `stock_minimum`; las bases requieren política autorizada; los cambios materiales no activan valores silenciosamente; ausencia nunca equivale a cero; y no se autoriza fórmula, porcentaje ni reposición automática.

## 4. AUDITAR 2

Resultado:

- `4 passed` en las pruebas específicas M03;
- `293 passed` en la suite completa, con advertencias Pydantic y UserWarning promovidas a error;
- `STK-M04…M10` permanecen pendientes;
- STK continúa no apto para implementación cuantitativa;
- no cambia código ejecutable, SQL, reglas, parámetros ni contratos técnicos.

## 5. CERRAR

`STK-M03` queda cerrado como autoridad metodológica. Cada método cuantitativo deberá tener autoridad, versión, evidencia y vigencia propias.

## 6. MATERIALIZAR

Se actualiza la matriz y se añaden autoridad M03 y pruebas. No se modifica el catálogo ni valida `STK-002`.

## 7. CI

La validación local reproduce el job vigente. GitHub Actions sobre materialización e integración constituye el gate externo final.
