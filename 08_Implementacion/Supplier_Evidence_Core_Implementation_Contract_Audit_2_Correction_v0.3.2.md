# EIOS — SUPPLIER EVIDENCE CORE · IMPLEMENTATION CONTRACT AUDIT 2 CORRECTION v0.3.2

**Estado:** CORRECCIÓN FÍSICA FINAL REQUERIDA  
**Fecha:** 11/09/2026  
**Objeto:** `Supplier_Evidence_Core_Implementation_Contract_v0.3.1.md`

---

## 1. Hallazgos

### PROV-TC-A2F-02 — Validación post-parse no garantiza bool/int/Decimal estrictos

v0.3.1 exige que INTEGER no acepte bool y BOOLEAN sea bool real, pero indica validación “después del parseo”.

Con Pydantic, determinados valores pueden ser coaccionados antes de un `model_validator(mode="after")`.

**Corrección:** el contrato debe exigir validación `mode="before"` o campos strict equivalentes para impedir semánticamente:

```text
True  → 1
False → 0
True  → Decimal("1")
```

cuando el value_kind no lo autoriza.

El contrato no necesita prohibir parsing normal de strings/ints a Decimal cuando no sean booleanos; sí debe rechazar bool antes de coerción.

### PROV-TC-A2F-03 — unresolved/conflicting agregados necesitan namespace

Los IDs solo son únicos dentro de cada colección.

Por tanto:

```text
candidate_id = "X"
observation_id = "X"
```

es válido, pero un agregado `unresolved_items=("X",)` sería ambiguo.

**Corrección:** introducir referencia estructurada:

```text
SupplierItemRef
    item_type: CANDIDATE | OBSERVATION | METRIC | COMPARISON
    item_id: str
```

`unresolved_items` y `conflicting_items` deben ser `tuple[SupplierItemRef, ...]`.

La deduplicación estable se aplica sobre `(item_type, item_id)`.

---

## 2. Alcance

No cambia metodología, estados empresariales, comparación, PRICE, Rules ni outputs decisionales.

Son correcciones de tipado y trazabilidad física.
