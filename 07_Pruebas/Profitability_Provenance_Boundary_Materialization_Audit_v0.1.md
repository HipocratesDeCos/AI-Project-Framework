# EIOS — Profitability Provenance Boundary Materialization Audit v0.1

**Baseline:** `main @ 946606320b639d9aa4d062faa69ec4b67d13a841`  
**Estado:** AUDITORÍA FÍSICA SUPERADA — PENDIENTE CI

## 1. Superficie materializada

- `eios/profitability/provenance.py`;
- export público en `eios/profitability/__init__.py`;
- `tests/test_profitability_provenance.py`.

## 2. Depuración M1 — revalidación de modelos anidados

El diseño inicial exigía deep snapshot + recomputación.

Durante materialización se identificó que `DecisionContext` y `PurchaseOperation` no son frozen; además, Python permite bypass deliberado de modelos frozen mediante mecanismos de bajo nivel.

Recomputar sobre el mismo objeto interno podría no volver a ejecutar todos los validators de `ProfitabilityInput`.

### Corrección

La frontera utiliza:

```python
ProfitabilityInput.model_validate(
    payload.model_dump(mode="python")
)
```

antes de ejecutar y también antes de revalidar.

Esto fuerza reconstrucción completa y vuelve a ejecutar:

- identidad context ↔ purchase;
- identidad de sale basis;
- identidad de cost basis;
- invariantes KNOWN/non-KNOWN;
- restricciones físicas del modelo.

**Resultado:** hardening provenance-safe superior a una simple copia profunda.

## 3. Verificaciones

### M2 — factory única

`run_provenanced_profitability` recibe solo `ProfitabilityInput`.

No acepta result externo.

**PASS.**

### M3 — snapshot aislado

La ejecución retiene un nuevo árbol de modelos, separado de los objetos originales.

**PASS.**

### M4 — recomputación exacta

El validator reconstruye el input y recalcula `calculate_profitability`.

Resultado distinto → `ProfitabilityProvenanceError`.

**PASS.**

### M5 — resultado manipulado

Un `ProfitabilityResult` alterado no supera revalidación.

**PASS.**

### M6 — contexto/compra manipulados

Mutaciones internas posteriores en decision/scenario/article son detectadas por la reconstrucción de `ProfitabilityInput`.

**PASS.**

### M7 — bases manipuladas

Cambios de identidad o eliminación de refs obligatorias en las bases son detectados.

**PASS.**

### M8 — result desprendido

Un `ProfitabilityResult` aislado no es una ejecución provenance-safe y es rechazado por el validator.

**PASS.**

### M9 — dependencias

No hay imports de Rules, CRC, PRICE o TCO.

No hay I/O, red, SQL ni clock implícito.

**PASS.**

## 4. No-alcance preservado

La materialización no:

- ejecuta R-MGE;
- consume P-MGE-*;
- adapta PRICE/TCO;
- selecciona bases;
- crea Trace paralela;
- modifica Profitability Core.

## 5. Dictamen

**AUDITORÍA DE MATERIALIZACIÓN: SUPERADA — 0 bloqueadores observados.**

Cierre condicionado a CI exact-head satisfactoria y merge protegido por SHA.
