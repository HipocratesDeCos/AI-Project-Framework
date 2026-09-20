# EIOS — Profitability Core Technical Contract Audit v0.1

**Baseline:** `main @ 3f4cad32b544d78f721d6179876f24fbaebfc067`  
**Objeto:** `Profitability Core Technical Contract v0.1`

## 1. Audit 1

### A1 — Riesgo de usar TCO directamente

Un `TCOResult` tiene semántica propia y no prueba que sea base de coste de margen.

**Depuración:** el contrato exige `AuthorizedCostBasis` distinto y no incluye adapter TCO.

### A2 — Riesgo de usar PRICE como base

Price Intelligence produce PR, no precio de venta ni coste autorizado.

**Depuración:** no existe adapter PRICE en el core.

### A3 — Identidad insuficiente

Conservar solo `decision_id` permitiría mezclar escenario, snapshot o artículo.

**Depuración:** cada base conserva decision/scenario/snapshot/company/article/evaluation_date y se verifica igualdad exacta.

### A4 — sale=0 y estado único

MGE-AUTH permite amount determinado pero percentage no determinable.

**Depuración:** `NOT_DETERMINABLE + SALE_BASIS_ZERO` es la única excepción que permite amount publicado sin percentage.

### A5 — valores negativos de base

MGE-AUTH no define semántica de una base económica negativa.

**Depuración:** v0.1 rechaza bases negativas como restricción conservadora; una extensión exige autoridad propia.

### A6 — parámetros MGE

La existencia de P-MGE-001/002/003 podría tentar a ejecutarlos dentro del core.

**Depuración:** el contrato prohíbe todos los parámetros MGE; Rules quedan downstream.

### A7 — discounts/rappels

P-MGE-005/006 existen en catálogo pero no tienen consumidor demostrado.

**Depuración:** no existen campos/switches en core; solo bases ya transformadas externamente.

### A8 — temporalidad implícita

Usar `date.today()` crearía semántica temporal oculta.

**Depuración:** `evaluation_date` es input explícito y debe coincidir con las bases.

### A9 — provenance desprendida

Un resultado con solo números perdería autoridad/source refs.

**Depuración:** resultado conserva las dos bases autorizadas completas.

## 2. Audit 2

### B1 — MGE-AUTH

Fórmulas, denominador y cero están alineados.

**PASS.**

### B2 — PRICE/TCO

No se redefinen ni adaptan.

**PASS.**

### B3 — C0

Se reutilizan `DecisionContext` y `PurchaseOperation`; no se modifican.

**PASS.**

### B4 — Rules / CRC

No se ejecutan ni producen Assessment/outcomes.

**PASS.**

### B5 — Parametrización

No se consume ningún P-MGE-*.

**PASS.**

### B6 — Fail-closed

Ausencia, contradicción, no determinabilidad e incompatibilidad no producen fallback.

**PASS.**

### B7 — Determinismo

Sin I/O, clock, red, SQL o estado global.

**PASS.**

### B8 — Provenance

Las bases se retienen completas y las trace refs se agregan sin crear una Trace paralela.

**PASS.**

## 3. Matriz mínima de tests para materialización

| Caso | Resultado |
|---|---|
| bases KNOWN compatibles, sale>0 | DETERMINED + amount + percentage |
| cost > sale | percentage negativo permitido |
| sale = cost | amount=0, percentage=0 |
| sale=0 | amount=-cost, percentage=null, NOT_DETERMINABLE |
| sale/cost currency distinta | NOT_DETERMINABLE |
| economic_basis_ref distinto | NOT_DETERMINABLE |
| sale NOT_EVIDENCED | NOT_EVIDENCED |
| cost NOT_EVIDENCED | NOT_EVIDENCED |
| conflicto en cualquiera | CONFLICTING_DATA |
| NOT_DETERMINABLE | NOT_DETERMINABLE |
| identity mismatch | error estructural |
| KNOWN sin source/trace/value | error estructural |
| base negativa | error estructural v0.1 |
| input mutability | frozen / no mutation |
| extra fields | forbidden |
| no PRICE/TCO adapters | guard estático |
| no Rules/CRC imports | guard estático |
| no I/O/clock | guard estático |

## 4. Dictamen

**AUDIT 1 → DEPURACIÓN → AUDIT 2: SUPERADAS.**

**0 bloqueadores técnicos/documentales para materializar Profitability Core v0.1.**

La materialización deberá permanecer estrictamente dentro de este contrato.
