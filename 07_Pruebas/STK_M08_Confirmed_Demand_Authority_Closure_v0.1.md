# EIOS — STK-M08 · Cierre de autoridad metodológica de absorción de exceso v0.1

**Estado:** CERRADO — MATERIALIZADO — INTEGRADO EN `main` — CI VALIDADO
**Baseline:** `de29dc7dd920a198a529e63ad244df62da2ae41a`
**Ámbito:** pedido confirmado, absorción, estados, evidencia y autoridad; sin motor cuantitativo

## 1. DISEÑAR

Formalizar evidencia de pedido firme, cantidad aplicable, fórmulas de absorción, estados, deduplicación, cambios y autoridad.

## 2. AUDITAR

Se contrastó con STK-M07, `R-STK-004`, `R-CON-004` y la capa de resolución de conflictos.


Existe autoridad suficiente para cerrar M08 sin convertir un booleano aislado en evidencia ni transformar mitigación en autorización.

## 3. DEPURAR

- el pedido exige identidad y evidencia vigente completa;
- artículo, unidad y horizonte deben ser compatibles;
- solo se usa cantidad pendiente de servir;
- una cantidad no se asigna dos veces;
- se conservan exceso original, absorción y residual;
- `NO_VERIFICABLE` y `NO_APLICABLE` no reducen el exceso;
- cambios y entregas parciales requieren reevaluación trazable;
- la excepción no decide comprar, cancelar o reducir stock.

## 4. AUDITAR 2

Resultado:

- `6 passed` en las pruebas específicas M08;
- `320 passed` en la suite completa, con advertencias Pydantic y UserWarning promovidas a error;
- `STK-M09…M10` permanecen pendientes;
- STK continúa no apto para implementación cuantitativa;
- no cambia código ejecutable, SQL, reglas, parámetros ni contratos técnicos.

## 5. CERRAR

`STK-M08` queda cerrado como autoridad metodológica de mitigación contextual.

## 6. MATERIALIZAR

Se actualiza la matriz y se añaden autoridad M08 y pruebas. No se modifican reglas, contratos ni código ejecutable.

## 7. CI

La unidad quedó validada mediante la siguiente cadena de evidencia:

- materialización: `f987a8dc664a71ba50be85943c3bfbb096af5f89`;
- pull request de integración: `#56`;
- CI sobre la cabeza del pull request: ejecución `34569289217`, `SUCCESS`;
- integración en `main`: `63801d017701e9556997a7d09b225a3fc2b2be2b`;
- CI posterior a la integración: ejecución `34569490490`, `SUCCESS`;
- reconciliación local posterior: `320 passed`, con advertencias Pydantic y UserWarning promovidas a error.

La cadena DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI queda completa para `STK-M08`.
