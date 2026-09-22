# EIOS — R-HIS-003 Provenance-Safe Core Implementation Audit v0.1

**Fecha:** 22/09/2026  
**Estado:** AUDIT 1 SUPERADA — CI PENDIENTE

## A1 — Semántica

La implementación conserva:

- siete dimensiones autorizadas;
- any MATERIAL_DIFFERENT → NON_COMPARABLE;
- all EQUIVALENT/NOT_APPLICABLE → COMPARABLE;
- unresolved sin diferencia material → NOT_DETERMINABLE;
- mapping TRUE/FALSE/NOT_EVALUABLE;
- R3 / MEDIA.

## A2 — No semántica inventada

No existen:

- umbrales;
- porcentajes;
- scoring;
- pesos;
- similitud textual;
- equivalencia automática de proveedor;
- transformación de descuentos/rappels/plazo.

## A3 — Provenance

La observación global se reconstruye dentro del bridge.

Las dimensiones determinadas requieren Evidence ligada al hash exacto de la determinación.

## A4 — Price boundary

No se usa `PriceReferenceAssessment.comparability` como autoridad de R-HIS-003.

## A5 — Tests

Cobertura añadida para:

- una diferencia material → TRUE;
- diferencia material + otra dimensión indeterminada → TRUE;
- EQUIVALENT/NOT_APPLICABLE → FALSE;
- unresolved → NOT_EVALUABLE;
- NOT_APPLICABLE sin evidencia rechazado;
- siete dimensiones obligatorias;
- Evidence falsificada rechazada;
- referencia futura → NOT_EVALUABLE;
- metadata R3/MEDIA;
- API sin observation desprendida;
- integración de orquestador;
- Price comparability ausente de la API HIS003.

## A6 — Integración

- catálogo previsto: 22 reglas;
- `run_domain_rules` integra `HistoryComparabilityRuleInputs`;
- R-HIS-003 no define active_result CRC.

## Dictamen

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ⏳ CI
AUDITAR 2     ⏳
CERRAR        ⏳
MATERIALIZAR  ✅
CI            ⏳
```

**0 bloqueadores estáticos identificados antes de CI.**
