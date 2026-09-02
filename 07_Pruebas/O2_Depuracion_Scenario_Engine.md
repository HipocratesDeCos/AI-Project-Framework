# EIOS — O2 · DEPURACIÓN SCENARIO ENGINE

**Estado:** DEPURADO
**Entrada:** `aac578ad0c416739eeaca13c24b5ef6d27a3d1b6`

## 1. Corrección D1 — Serialización canónica

Los cambios del escenario se normalizarán antes de calcular identidad/fingerprint mediante un orden determinista por:

1. `variable`
2. representación canónica del `value`
3. `unit`
4. `authorization`
5. `origin`

La representación canónica debe distinguir tipos y valores materialmente diferentes y no depender del orden de entrada.

## 2. Corrección D2 — Estados

O2 solo puede producir `DRAFT`, `VALID` o `INVALID`.

`EVALUATED` queda expresamente fuera de la creación/versionado O2 y solo podrá aparecer mediante una integración futura cuyo contrato lo autorice.

Reglas:

- cambios incompletos o no validados → `DRAFT`;
- cambios autorizados y contexto coherente → `VALID`;
- cambio no autorizado o contexto incompatible → `INVALID`;
- O2 no realiza evaluación analítica para producir `EVALUATED`.

## 3. Resultado de depuración

Las dos ambigüedades identificadas por la auditoría quedan resueltas sin ampliar la autoridad funcional de O2.

No se introducen scoring, ranking, recomendación, negociación ni ejecución de capacidades.

**Siguiente etapa:** AUDITAR 2.
