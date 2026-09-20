# EIOS — MGE Rules Authority & Technical Contract Audit v0.1

**Baseline:** `main @ 6ad89d0bc70900a14cb7a11c4b8fa7660d0bae6e`

## 1. Audit 1

### A1 — Solapamiento por parámetros contradictorios

Si `minimum > target`, R-MGE-001 y R-MGE-003 podrían ser TRUE simultáneamente.

**Depuración:** las tres reglas comparten un bundle completo; `minimum > target` → `NOT_EVALUABLE` para todo el bloque.

### A2 — Tolerancia negativa

Una tolerancia negativa invertiría la semántica autorizada.

**Depuración:** `tolerance < 0` → `NOT_EVALUABLE`.

### A3 — Tolerancia mayor que target-minimum

No es necesariamente contradicción. La fórmula autorizada ya exige `m >= minimum`, por lo que el límite efectivo queda acotado sin inventar clamp.

**PASS sin corrección.**

### A4 — Cada Rule con parámetros distintos

Permitir que R-MGE-001 use una versión/configuración y R-MGE-003 otra rompería G03.

**Depuración:** único `ProfitabilityRuleInputs` con las tres resoluciones y evidencias para las tres reglas.

### A5 — Result desprendido

Un `ProfitabilityResult` aislado no prueba provenance.

**Depuración:** solo `ProvenancedProfitabilityExecution`; revalidación obligatoria.

### A6 — Defaults de catálogo

20/30/3 figuran pendientes de validación.

**Depuración:** ningún literal de negocio en engine/bridges; solo `ResolvedConfiguration`.

### A7 — R0

La Matriz menciona escalada posible de R-MGE-001, pero la autorización actual la excluye.

**Depuración:** catálogo fija exclusivamente R1/ALTA.

### A8 — Missing parameter

Tratar una ausencia como 0 haría evaluable indebidamente una regla.

**Depuración:** ausencia/resolution/evidence inválida → `NOT_EVALUABLE`.

### A9 — Evidencia de Profitability

Las trace refs internas no sustituyen al Evidence Contract de Rules.

**Depuración:** evidencia explícita `ProfitabilityResultEvidence` ligada por hash determinista al resultado exacto.

## 2. Audit 2

- autorización humana específica de Rules: PASS;
- fórmula R-MGE-002 exacta: PASS;
- interacción G03: PASS;
- provenance-safe result: PASS;
- parámetros sin defaults: PASS;
- units exactas: PASS;
- estados no determinados fail-closed: PASS;
- metadata sin R0: PASS;
- CRC sin cambios: PASS;
- P-MGE-004/005/006 fuera: PASS;
- PRICE/TCO fuera: PASS;
- no I/O/clock: PASS.

## 3. Dictamen

**AUDIT 1 → DEPURACIÓN → AUDIT 2: SUPERADAS.**

**0 bloqueadores documentales para materializar Rules MGE v0.1.**
