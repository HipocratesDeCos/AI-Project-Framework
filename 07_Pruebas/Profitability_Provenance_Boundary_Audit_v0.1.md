# EIOS — Profitability Provenance Boundary Audit v0.1

**Baseline:** `main @ d3b72e33752bc5111f89f4112f461f505b805247`

## 1. Audit 1

### A1 — ¿Hace falta wrapper si result ya contiene bases?

Sí. El resultado conserva bases, pero una instancia puede construirse/manipularse fuera de la factory del engine. La revalidación debe recomputar.

**Depuración:** wrapper + validator público.

### A2 — ¿Debe retener parámetros?

No. Profitability Core no consume P-MGE-*.

**Depuración:** wrapper contiene solo input + result.

### A3 — ¿Debe aceptar result externo?

No.

**Depuración:** única factory recibe `ProfitabilityInput`.

### A4 — ¿Debe generar nueva Trace?

No.

**Depuración:** las trace refs ya viven en las bases/result. El wrapper no crea entidad Trace.

### A5 — ¿Debe validar authority_ref semánticamente?

No más allá de las invariantes del `ProfitabilityInput`. El wrapper no conoce autoridad upstream adicional.

**Depuración:** reejecuta el core; no inventa validación empresarial.

## 2. Audit 2

- MGE-AUTH: preservada.
- Core contract: preservado.
- Result desprendido: bloqueado.
- Deep snapshot: requerido.
- Rules/CRC: fuera de alcance.
- PRICE/TCO adapters: fuera de alcance.
- I/O/clock: ausentes.
- Segunda identidad empresarial: no creada.

**AUDIT 2: SUPERADA — 0 bloqueadores.**

## 3. Dictamen

Puede materializarse `ProvenancedProfitabilityExecution` como frontera técnica pura antes de cualquier integración Rules.
