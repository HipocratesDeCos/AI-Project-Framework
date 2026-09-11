# EIOS — DELIVERY / STOCKOUT ANALYZER · CONTRACT CORRECTION v0.3.2

**Estado:** CORRECCIÓN PRE-AUDIT 2 FINAL  
**Fecha:** 11/09/2026  
**Base compuesta:** v0.3 + Correction v0.3.1

---

## 1. Preservación de limitaciones upstream

`BaselineStockoutQualification.limitations` no puede desaparecer al producir el resultado ENT.

Se añade al modelo físico previsto:

```text
DeliveryStockoutAnalysisResult
└── upstream_limitations: tuple[str, ...]
```

Semántica:

- copia/deduplica las limitaciones declaradas por baseline;
- no las transforma en `DeliveryLimitationCode`;
- no les asigna severidad;
- no las interpreta como regla;
- no las utiliza para decidir el estado ENT salvo que otra parte del contrato ya lo autorice expresamente.

Por tanto:

```text
upstream_limitations ≠ limitation_codes
```

El merge de salida queda:

```text
upstream_limitations:
    baseline.limitations
```

preservando orden y eliminando duplicados exactos.

---

## 2. Provenance de fecha declarada `NOT_EVIDENCED`

Cuando:

```text
delivery.state = NOT_EVIDENCED
AND expected_delivery_date is not None
```

la fecha representa un valor declarado insuficientemente evidenciado, no un literal libre.

Se exige al menos:

```text
source_ref != None
```

Además se conservan, cuando existan:

- `evidence_refs`;
- `trace_refs`;
- `captured_at`;
- `delivery_semantic_ref`.

La fecha sigue sin poder utilizarse en comparación temporal.

Si no existe `source_ref`, el modelo no puede publicar una fecha declarada `NOT_EVIDENCED`.

---

## 3. Tests añadidos al contrato

Se incorporan como obligatorios:

1. baseline limitations aparecen exactamente en `upstream_limitations`;
2. `upstream_limitations` no se convierten en `DeliveryLimitationCode`;
3. `NOT_EVIDENCED + fecha + source_ref` es representable y no se compara;
4. `NOT_EVIDENCED + fecha sin source_ref` es rechazado;
5. deduplicación estable de `upstream_limitations`.

---

## 4. Resto del contrato

Todo el contenido de v0.3 y Correction v0.3.1 permanece vigente salvo donde esta corrección lo amplía defensivamente.

No se cambia:

- condición temporal;
- precedencia;
- estados;
- parámetros;
- STK;
- Supplier;
- Assessment;
- RDM;
- persistencia.

---

## 5. Estado

**CORRECCIÓN v0.3.2 MATERIALIZADA.**

Objeto de Audit 2 final:

```text
v0.3
+ Correction v0.3.1
+ Correction v0.3.2
```
