# EIOS — DELIVERY / STOCKOUT ANALYZER · IMPLEMENTATION AUDIT 1 v0.1

**Estado:** AUDIT 1 COMPLETADA — 2 HALLAZGOS DEPURABLES  
**Fecha:** 11/09/2026  
**HEAD auditado:** `cfd6ced09a01db45e5e0feaad0f3491a86bb1cab`

---

## 1. Alcance físico

Diff contra baseline `ee4e149c42fe8f1c6619fb62387397dc63767ea8`:

- documentación ENT contractual/metodológica;
- `eios/delivery/__init__.py`;
- `eios/delivery/models.py`;
- `eios/delivery/engine.py`;
- `tests/test_delivery_stockout.py`.

No se modifican C0, STK, Supplier, Rules, RDM, parámetros ni SQL.

**Frontera física: SUPERADA.**

---

## 2. ENT-IMPL-A1-01 — SAME_DAY insuficientemente cerrado en construcción directa

`DeliveryStockoutAnalysisResult.validate_result()` comprueba correctamente la igualdad cuando:

```text
state = NOT_LATE_DEMONSTRATED
```

pero no prohíbe que un consumidor construya manualmente, por ejemplo:

```text
state = NOT_DETERMINABLE
limitation_codes = (SAME_DAY_ORDER_NOT_DEMONSTRATED,)
```

El engine nunca produce esa combinación, pero el contrato exige que el propio modelo físico impida estados incompatibles.

### Corrección

`SAME_DAY_ORDER_NOT_DEMONSTRATED` solo será válido si simultáneamente:

```text
state = NOT_LATE_DEMONSTRATED
expected_delivery_date == depletion_date
```

En cualquier otro estado/fecha → validation error.

**Severidad:** HIGH.

---

## 3. ENT-IMPL-A1-02 — Provenance directa de métricas STK consumidas

El engine transforma correctamente:

```text
projection.issue_refs[].issue_record_ref
→ result.issue_refs
```

pero consume directamente también:

```text
projection.depletion_date
projection.horizon
```

Sus `issue_refs` y `trace_refs` pueden ser físicamente válidos aunque no hayan sido duplicados en el envelope `StockProjectionResult` por un productor externo que respete los modelos Pydantic.

Para evitar pérdida de provenance, ENT debe preservar referencias de los tres niveles que realmente consume:

```text
projection.issue_refs
projection.depletion_date.issue_refs
projection.horizon.issue_refs
```

y sus `trace_refs` correspondientes.

La transformación de cada `DataIssueRef` sigue siendo exclusivamente:

```text
issue.issue_record_ref
```

sin reinterpretación.

**Severidad:** MEDIUM.

---

## 4. Puntos superados

Se confirma:

1. engine puro y determinista;
2. precedencia contractual respetada;
3. mismatch contextual → NOT_DETERMINABLE;
4. malformed baseline → validación;
5. baseline no inferido desde scenario_id;
6. delivery KNOWN exige applicability;
7. NOT_EVIDENCED preserva valor declarado sin compararlo;
8. fecha pasada indeterminada conserva limitation autorizada;
9. depletion NOT_EVIDENCED → NOT_DETERMINABLE;
10. horizonte sin extrapolación;
11. misma fecha no se considera posterior;
12. no lead_time;
13. no Supplier adapter;
14. no Assessment/CRC/NEGOCIAR;
15. no persistencia;
16. modelos frozen/extra forbid;
17. tests cubren ramas contractuales principales.

---

## 5. Dictamen

```text
AUDIT 1 IMPLEMENTACIÓN    COMPLETADA
HALLAZGOS HIGH            1
HALLAZGOS MEDIUM          1
BLOQUEADORES DE DISEÑO    0
POLÍTICA NUEVA            0
```

Procede DEPURAR únicamente `models.py`, `engine.py` y tests asociados; no se reabre el contrato funcional.
