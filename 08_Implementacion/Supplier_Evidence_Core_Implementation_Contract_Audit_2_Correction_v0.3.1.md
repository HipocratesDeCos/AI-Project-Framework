# EIOS — SUPPLIER EVIDENCE CORE · IMPLEMENTATION CONTRACT AUDIT 2 CORRECTION v0.3.1

**Estado:** CORRECCIÓN FINAL REQUERIDA  
**Fecha:** 11/09/2026  
**Objeto:** `Supplier_Evidence_Core_Implementation_Contract_v0.3.md`

---

## 1. Hallazgo único

### PROV-TC-A2F-01 — Precedencia incorrecta de autoridad PRICE frente a incompatibilidad de dimensión

En v0.3, §22 comprueba `PRICE_COMPARABILITY_AUTHORITY_REQUIRED` antes de verificar que `dimension` coincida entre observaciones.

Caso:

```text
current.dimension   = PRICE_REFERENCE
candidate.dimension = DELIVERY_DATE
comparison_authority_ref = None
```

El algoritmo v0.3 podría producir:

```text
UNKNOWN / PRICE_COMPARABILITY_AUTHORITY_REQUIRED
```

cuando la incompatibilidad de dimensión ya es suficiente para determinar:

```text
NOT_STRUCTURALLY_COMPARABLE
```

La autoridad PRICE solo es necesaria cuando **ambas observaciones son PRICE_REFERENCE** y han superado las comprobaciones estructurales básicas necesarias para poder intentar una comparación de precio.

---

## 2. Corrección autorizada

Reordenar §22 así:

1. candidatura actual;
2. estado de observaciones;
3. vigencia;
4. identidad estructural básica:
   - dimension;
   - value_kind;
   - semantic_ref;
   - object_id;
   - unit aplicable;
5. si la dimensión común es PRICE_REFERENCE, exigir comparison_authority_ref;
6. declarar STRUCTURALLY_COMPARABLE;
7. calcular diferencia Decimal descriptiva cuando proceda.

La ausencia de autoridad PRICE no convierte dimensiones incompatibles en UNKNOWN.

---

## 3. Alcance

No modifica:

- metodología v0.3;
- estados;
- modelos;
- autoridad PRICE;
- Rules;
- scoring;
- outputs decisionales.

Es exclusivamente una corrección de precedencia determinista.
