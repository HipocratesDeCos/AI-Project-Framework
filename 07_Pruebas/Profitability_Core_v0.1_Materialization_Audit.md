# EIOS — Profitability Core v0.1 Materialization Audit

**Baseline:** `main @ 0aa0c52e7019546eacbb3f68fa0d1e3b2509b57a`  
**Estado:** AUDITORÍA DE MATERIALIZACIÓN — SIN BLOQUEADORES DE CÓDIGO, PENDIENTE CI

## 1. Superficie materializada

- `eios/profitability/models.py`;
- `eios/profitability/engine.py`;
- `eios/profitability/__init__.py`;
- `tests/test_profitability_core.py`.

No se modifican C0, PRICE, TCO, Finance, Rules, CRC, SQL o parámetros.

## 2. Verificaciones

### M1 — tipos físicos distintos

`AuthorizedSaleBasis` y `AuthorizedCostBasis` son tipos distintos y no aliases de Decimal/TCO/PRICE.

**PASS.**

### M2 — identity binding

`ProfitabilityInput` valida decision, scenario, snapshot, company, article y evaluation_date para ambas bases.

**PASS.**

### M3 — known-state contract

Una base `KNOWN` exige value, currency, economic_basis_ref, authority_ref, source_ref y trace refs.

Una base no `KNOWN` no puede publicar value.

**PASS.**

### M4 — base negativa

v0.1 rechaza bases negativas, preservando la restricción conservadora del contrato técnico.

**PASS.**

### M5 — cálculo autorizado

El engine ejecuta únicamente:

```text
amount = sale - cost
percentage = amount / sale × 100
```

con sale > 0.

**PASS.**

### M6 — venta cero

`sale=0` conserva `amount=-cost`, percentage null, estado `NOT_DETERMINABLE` y limitación `SALE_BASIS_ZERO`.

**PASS.**

### M7 — precedencia fail-closed

`CONFLICTING_DATA > NOT_EVIDENCED > NOT_DETERMINABLE`.

No existe fallback favorable.

**PASS.**

### M8 — incompatibilidad

Moneda o basis incompatibles no producen cálculo ni conversión.

**PASS.**

### M9 — provenance retenida

El resultado conserva `sale_basis` y `cost_basis` completas y agrega trace refs de manera ordenada/deduplicada.

**PASS.**

### M10 — aislamiento

El engine no importa ni invoca PRICE, TCO, Rules, CRC, filesystem, red o clock.

**PASS.**

### M11 — decisión

No existen campos Assessment/outcome/recommendation/CRC/decision.

**PASS.**

### M12 — parámetros

El core no consume P-MGE-*.

**PASS.**

## 3. Cobertura automatizada prevista

La suite dedicada cubre:

- happy path;
- margen negativo;
- margen cero;
- sale=0;
- todos los estados fail-closed;
- currency/basis incompatible;
- identity mismatch por seis dimensiones;
- KNOWN incompleto;
- trace ausente;
- valor en estado no KNOWN;
- valor negativo/no finito;
- frozen/extra forbid;
- tipo de payload;
- retención de bases;
- deduplicación de traces;
- guard estático de dependencias;
- ausencia de outputs decisionales.

## 4. Dictamen

**AUDITORÍA DE MATERIALIZACIÓN: SUPERADA — 0 bloqueadores de código observados.**

Cierre físico condicionado a:

1. tests dedicados verdes;
2. suite completa verde;
3. SQL validations verdes;
4. CI exact-head;
5. merge protegido por SHA.


## 5. Depuración CI #994

La primera CI de materialización detectó 6 fallos exclusivamente en el harness parametrizado de estados no `KNOWN`.

Causa:

- los casos de control con estado `KNOWN` se construían accidentalmente con `value=None`, `source_ref=None` y sin traces;
- el modelo físico los rechazó correctamente según el contrato `KNOWN`.

Corrección:

- el harness construye una base `KNOWN` válida cuando corresponde;
- solo la base no `KNOWN` utiliza `value=None`;
- no se modifica engine, modelo, autoridad ni semántica fail-closed.

**Clasificación:** defecto de test, no defecto del core.
