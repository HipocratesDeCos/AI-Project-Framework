# EIOS — STK-M06 · Cierre de autoridad metodológica logística v0.1

**Estado:** CERRADO — MATERIALIZADO — INTEGRADO EN `main` — CI VALIDADO
**Baseline:** `97a0bee524f912dc503799ad795eafb071f64a8c`
**Ámbito:** pedidos pendientes, tránsito, evidencia, transiciones y no duplicación; sin motor cuantitativo

## 1. DISEÑAR

Formalizar estados logísticos, evidencia mínima, fecha prevista, uso proyectivo, exclusión mutua, transiciones, recepción, ausencia y autoridad.

## 2. AUDITAR

La decisión se contrastó con STK-M04/M05, variables `pending_orders`, `in_transit`, `expected_receipt_date`, parámetros `PYE-002/003`, especificación funcional y reglas STK.

Existe autoridad suficiente para cerrar M06. Los “Sí” del catálogo no se convierten en inclusión incondicional.

## 3. DEPURAR

- cada cantidad conserva identidad y origen documental suficientes para deduplicación;
- pedido pendiente y tránsito son mutuamente excluyentes;
- el historial no incrementa la cantidad proyectada;
- recepción parcial retira únicamente la parte confirmada;
- fechas, cancelaciones y cambios requieren evidencia;
- una recepción prevista no equivale a recepción confirmada;
- ausencia y contradicción no se resuelven como cero ni por inferencia;
- la evidencia logística no autoriza comprar o reponer.

## 4. AUDITAR 2

Resultado:

- `5 passed` en las pruebas específicas M06;
- `308 passed` en la suite completa, con advertencias Pydantic y UserWarning promovidas a error;
- `STK-M07…M10` permanecen pendientes;
- STK continúa no apto para implementación cuantitativa;
- no cambia código ejecutable, SQL, reglas, parámetros ni contratos técnicos.

## 5. CERRAR

`STK-M06` queda cerrado como autoridad metodológica logística. La implementación futura deberá preservar identidad, estado vigente, historial y no duplicación.

## 6. MATERIALIZAR

Se actualiza la matriz STK y se añaden autoridad M06 y pruebas. No se modifican catálogo, reglas, contratos ni código ejecutable.

## 7. CI

La unidad quedó validada mediante la siguiente cadena de evidencia:

- materialización: `80ffe960a7392075e7d35b65e4bd225952d581b5`;
- pull request de integración: `#52`;
- CI sobre la cabeza del pull request: ejecución `34567780725`, `SUCCESS`;
- integración en `main`: `6fe3c61642667fca9f89dde084e6e428a4e6dc74`;
- CI posterior a la integración: ejecución `34567933930`, `SUCCESS`;
- reconciliación local posterior: `308 passed`, con advertencias Pydantic y UserWarning promovidas a error.

La cadena DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI queda completa para `STK-M06`.
