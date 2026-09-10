# EIOS — STK-M01 · Cierre de autoridad metodológica de consumo v0.1

**Estado:** CERRADO — MATERIALIZADO — INTEGRADO EN `main` — CI VALIDADO
**Baseline:** `c03f3e4c5a19a106736caf3cc077e01f55195e75`
**Ámbito:** definición metodológica de `consumption`; sin implementación cuantitativa STK

## 1. DISEÑAR

Formalizar la decisión humana expresa sobre la magnitud `consumption`, su unidad, agregación mensual, tratamiento de ausencia y vigencia, preservando la separación frente a ventas y demanda prevista.

El alcance cierra solo `STK-M01`. No fija horizonte, media, fechas de corte, cobertura, stock de seguridad, exceso, proyección ni consumidores regla-parámetro.

## 2. AUDITAR

La decisión se contrastó con:

- `Stock_Demand_Methodological_Matrix.md` v0.1;
- Especificación Funcional;
- parámetros `STK-001…006` y `PYE-001…006`;
- reglas `R-STK-001…004`;
- frontera de no invención y estado no apto para implementación.

Resultado: la decisión aporta magnitud, unidad, granularidad, agregación, ausencia y vigencia suficientes para cerrar M01, sin cerrar los gaps cuantitativos posteriores.

## 3. DEPURAR

La expresión inicial “periodos mensuales” no se reinterpretó como “mes natural”. La autoridad materializada declara que las fechas de corte y el número de meses permanecen pendientes.

Se explicitan además dos consecuencias necesarias de las salvaguardas vigentes:

- sin conversión demostrada a la unidad base, el valor normalizado permanece `UNKNOWN`;
- la aplicación retrospectiva conserva el hecho fuente, su fecha, procedencia y versión metodológica.

## 4. AUDITAR 2

Resultado:

- `4 passed` en las pruebas específicas M01;
- `285 passed` en la suite completa, con advertencias Pydantic y UserWarning promovidas a error;
- `STK-M02…M10` permanecen pendientes;
- la matriz continúa declarando STK no apto para implementación cuantitativa;
- no existe modificación de código ejecutable, SQL, reglas, parámetros o contratos técnicos.

## 5. CERRAR

`STK-M01` queda cerrado como autoridad metodológica. La decisión humana queda preservada en `01_Modelo/STK_M01_Consumption_Authority.md`.

## 6. MATERIALIZAR

La materialización actualiza la matriz metodológica, añade la fuente especializada de M01 y pruebas de no regresión semántica. No materializa un motor STK.

## 7. CI

La validación local reproduce el job Python vigente.

- Materialización: `850166d5ae12fc25d905e29d54d3af31d79252c3`.
- Pull request: #42.
- CI del head materializado: run `34521971064` — SUCCESS.
- Integración en `main`: `31cdb61242425c1aeaaadb65fd3cf13d922d26cd`.
- CI post-merge: run `34522503879` — SUCCESS.

STK-M01 queda validado por CI sobre el commit materializado y sobre el merge efectivo en `main`.
