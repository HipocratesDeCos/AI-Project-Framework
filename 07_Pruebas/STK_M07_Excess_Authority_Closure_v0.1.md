# EIOS — STK-M07 · Cierre de autoridad metodológica de exceso v0.1

**Estado:** CERRADO — MATERIALIZADO — VALIDACIÓN LOCAL SUPERADA
**Baseline:** `6fe3c61642667fca9f89dde084e6e428a4e6dc74`
**Ámbito:** umbral, tolerancia, estados, cantidad de exceso, evidencia y autoridad; sin motor cuantitativo

## 1. DISEÑAR

Formalizar referente, máximo, tolerancia, relaciones, estados de frontera, conversión por cobertura, ausencia y autoridad decisional.

## 2. AUDITAR

Se contrastó con STK-M04…M06, `R-STK-003/004`, parámetros `STK-004/005`, especificación funcional y capa de conflictos.

Existe autoridad suficiente para cerrar M07. Los valores iniciales 90 días y 10 % continúan pendientes de validación.

## 3. DEPURAR

- máximo y tolerancia deben compartir unidad antes de sumarse;
- una tasa porcentual se convierte respecto al máximo mediante política explícita;
- la banda tolerada no se clasifica como exceso;
- una proyección M05 no vuelve a sumar entradas M06;
- una cantidad propuesta solo participa dentro de un escenario explícito;
- ausencia nunca produce `NO_EXCESS`;
- M08 conserva la excepción por pedido confirmado;
- detectar exceso no autoriza actuaciones empresariales.

## 4. AUDITAR 2

Resultado:

- `6 passed` en las pruebas específicas M07;
- `314 passed` en la suite completa, con advertencias Pydantic y UserWarning promovidas a error;
- `STK-M08…M10` permanecen pendientes;
- STK continúa no apto para implementación cuantitativa;
- no cambia código ejecutable, SQL, reglas, parámetros ni contratos técnicos.

## 5. CERRAR

`STK-M07` queda cerrado como autoridad metodológica de exceso. Los valores concretos y cada versión de política requieren aprobación y trazabilidad propias.

## 6. MATERIALIZAR

Se actualiza la matriz y se añaden autoridad M07 y pruebas. No se modifican catálogo, reglas, contratos ni código ejecutable.

## 7. CI

La CI externa permanece pendiente hasta la publicación del SHA materializado.
