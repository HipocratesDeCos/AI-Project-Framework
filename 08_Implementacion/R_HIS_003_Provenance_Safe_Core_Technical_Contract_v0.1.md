# EIOS — R-HIS-003 Provenance-Safe Core Technical Contract v0.1

**Authority:** `01_Modelo/HIS003_Commercial_Comparability_Authority_v0.1.md`  
**Baseline:** `main @ c9e845ebb449a978be6688d0eeb1a7cd6f02bc3f`  
**Fecha:** 22/09/2026  
**Estado:** MATERIALIZADO — CI PENDIENTE

## 1. Componentes

- `HistoricalComparabilityDimensionAuthority`
- `HistoricalComparabilityDimensionDetermination`
- `HistoricalCommercialComparabilityObservation`
- `aggregate_historical_comparability`
- `build_historical_commercial_comparability_observation`
- `evaluate_r_his_003`

## 2. Frontera provenance-safe

El bridge R-HIS-003 no acepta un carrier agregado desprendido.

Reconstruye en la misma invocación:

```text
PurchaseOperation
+ DecisionContext
+ PriceReference
+ 7 dimension determinations
+ dimension Evidence
→ HistoricalCommercialComparabilityObservation
→ R-HIS-003
```

## 3. Dimensiones obligatorias

Exactamente una vez:

```text
QUANTITY
SUPPLIER
COMMERCIAL_CONDITIONS
DISCOUNTS
RAPPELS
PAYMENT_TERM
ARTICLE_CHARACTERISTICS
```

## 4. Autoridad dimensional

Cada determinación declara explícitamente:

```text
dimension
state
authority_ref
methodology_ref
version
evidence_ids
trace_refs
```

El core no interpreta hechos empresariales ni inventa tolerancias.

## 5. Evidencia

Para:

```text
EQUIVALENT
MATERIALLY_DIFFERENT
NOT_APPLICABLE
```

se requiere Evidence:

- source_type canónico;
- captured_at = evaluation_date;
- DEMONSTRATED;
- demonstration_ref ligado al hash exacto de la determinación.

`NOT_DETERMINABLE` exige reason + trace y puede representar ausencia de evidencia sin convertirla en FALSE.

## 6. Agregación

```text
any MATERIALLY_DIFFERENT
→ NON_COMPARABLE

all seven in {EQUIVALENT, NOT_APPLICABLE}
→ COMPARABLE

otherwise
→ NOT_DETERMINABLE
```

No scoring. No weights.

## 7. Rule mapping

```text
NON_COMPARABLE → TRUE
COMPARABLE → FALSE
NOT_DETERMINABLE → NOT_EVALUABLE
```

Metadata:

```text
R3 / MEDIA
active_result = none
```

## 8. Price Intelligence boundary

No se consume ni promociona `PriceReferenceAssessment.comparability`.

La referencia histórica se usa como identidad factual de la transacción; la comparabilidad comercial se reconstruye por la cadena HIS003.

## 9. No alcance

- creación de autoridades dimensionales empresariales;
- umbrales de cantidad;
- fuzzy matching;
- LLM;
- normalización comercial;
- exclusión automática de referencias;
- modificación de Price Intelligence;
- decisión de compra.
