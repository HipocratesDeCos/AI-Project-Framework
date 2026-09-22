# EIOS — R-HIS-003 Provenance-Safe Core Implementation Audit v0.1

**Fecha:** 22/09/2026  
**Estado:** AUDIT 2 SUPERADA — CERRADO / MATERIALIZADO / CI VALIDATED

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


## CI #1146 — depuración de invariantes legacy

CI #1146 sobre `b7b83175f4b2e24ab15b88d18c365a25d2399b55`: **FAILURE**.

Resultado:

- 2064 tests passed;
- 3 tests failed;
- SQL omitido por el fallo Python previo.

Los tres fallos no pertenecen al carrier ni al bridge HIS003. Eran invariantes legacy que utilizaban `R-HIS-003` como identificador deliberadamente no catalogado.

Tras materializar R-HIS-003, ese supuesto deja de ser válido.

Corrección aplicada:

```text
R-HIS-003
→ R-UNKNOWN-001
```

en los tests de:

- runtime same-execution fail-closed;
- execution boundary unknown rule;
- rules-engine facade unknown binding.

No se modifica código productivo ni semántica HIS003.

**DEPURACIÓN 1 APLICADA — NUEVA CI REQUERIDA.**


## Audit 2 final

CI #1149 sobre `d980b59d7ce5bdc2537fc9437782ab555cade156`: **SUCCESS**.

Validado:

- suite Python completa → SUCCESS;
- SQL → SUCCESS;
- 22 reglas implementadas en catálogo/orquestador;
- carrier HIS003 reconstruido dentro del bridge;
- siete dimensiones obligatorias;
- NOT_APPLICABLE gobernado por evidencia;
- any MATERIAL_DIFFERENT → NON_COMPARABLE;
- unresolved sin causa material → NOT_DETERMINABLE;
- Price Intelligence comparability no se promociona;
- no scoring, pesos ni umbrales nuevos.

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ✅
AUDITAR 2     ✅
CERRAR        ✅
MATERIALIZAR  ✅
CI            ✅ #1149
```

**DICTAMEN: R-HIS-003 PROVENANCE-SAFE CORE v0.1 — CERRADO, sujeto únicamente a CI del HEAD documental final y merge.**
