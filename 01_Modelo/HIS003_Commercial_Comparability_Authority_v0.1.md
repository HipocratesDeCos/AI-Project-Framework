# EIOS — HIS003 Commercial Comparability Authority v0.1

**Baseline de autorización:** `main @ 0907d77e285b29a96fa575b744db4a90a718a722`  
**Fecha:** 22/09/2026  
**Estado:** AUTORIZADO Y CORREGIDO  
**Regla:** `R-HIS-003 — Operación no comparable`

## 1. Autoridad humana

Se autoriza la propuesta HIS003 Commercial Comparability Authority v0.1 con las correcciones de frontera y provenance de este documento.

## 2. Resultado y metadata

Se conserva:

```text
R-HIS-003
effect = R3
severity = MEDIA
active_result = none
```

R-HIS-003 TRUE significa exclusivamente:

```text
la referencia histórica no debe tratarse automáticamente
como comercialmente equivalente
```

No bloquea compra ni elimina automáticamente la referencia.

## 3. Carrier autorizado

```text
HistoricalCommercialComparabilityObservation
```

Identidad mínima:

```text
decision_id
scenario_id
data_snapshot_id
parameters_version
article_id
purchase_operation_ref
reference_id
reference_transaction_id
evaluation_date
reference_date
state
dimension_assessments
authority_ref
methodology_ref
evidence_ids
trace_refs
```

Estados globales:

```text
COMPARABLE
NON_COMPARABLE
NOT_DETERMINABLE
```

## 4. Dimensiones obligatorias

Deben estar presentes exactamente una vez las siete dimensiones:

```text
QUANTITY
SUPPLIER
COMMERCIAL_CONDITIONS
DISCOUNTS
RAPPELS
PAYMENT_TERM
ARTICLE_CHARACTERISTICS
```

Estados por dimensión:

```text
EQUIVALENT
MATERIALLY_DIFFERENT
NOT_DETERMINABLE
NOT_APPLICABLE
```

No se admiten dimensiones omitidas, duplicadas o desconocidas.

## 5. Autoridad de relevancia material

R-HIS-003 no define por sí misma:

- tolerancias de cantidad;
- equivalencia de proveedor;
- equivalencia de plazo;
- equivalencia de descuentos/rappels;
- taxonomía de condiciones;
- similitud técnica del artículo.

`MATERIALLY_DIFFERENT`, `EQUIVALENT` y `NOT_APPLICABLE` requieren autoridad/metodología especializada y evidencia/traza explícita para esa dimensión.

`NOT_APPLICABLE` no puede usarse como valor por defecto para evitar una evaluación no disponible.

Si no existe autoridad suficiente para una dimensión:

```text
NOT_DETERMINABLE
```

## 6. Agregación autorizada

### NON_COMPARABLE

Si al menos una dimensión demuestra:

```text
MATERIALLY_DIFFERENT
```

entonces:

```text
state = NON_COMPARABLE
```

Esto permanece cierto aunque otras dimensiones estén `NOT_DETERMINABLE`, porque ya existe una causa suficiente y autorizada de no comparabilidad.

### COMPARABLE

Solo si las siete dimensiones están presentes y todas están en:

```text
EQUIVALENT
NOT_APPLICABLE
```

con autoridad/evidencia válida, entonces:

```text
state = COMPARABLE
```

### NOT_DETERMINABLE

Si no existe ninguna `MATERIALLY_DIFFERENT` demostrada y al menos una dimensión es:

```text
NOT_DETERMINABLE
```

entonces:

```text
state = NOT_DETERMINABLE
```

## 7. Mapping R-HIS-003

```text
NON_COMPARABLE
→ R-HIS-003 TRUE
```

```text
COMPARABLE
→ R-HIS-003 FALSE
```

```text
NOT_DETERMINABLE
→ R-HIS-003 NOT_EVALUABLE
```

La incertidumbre nunca se convierte en TRUE o FALSE.

## 8. Price Intelligence boundary

```text
PriceReferenceAssessment.comparability
≠
HistoricalCommercialComparabilityObservation.state
```

La comparabilidad actual de Price Intelligence solo cubre identidad primaria del artículo y evidencia válida.

No se autoriza:

```text
PriceReferenceAssessment.NO_COMPARABLE → R-HIS-003 TRUE
```

ni:

```text
PriceReferenceAssessment.COMPARABLE → R-HIS-003 FALSE
```

sin una cadena HIS003 específica que cubra las siete dimensiones.

## 9. Provenance

La observación debe estar vinculada a:

- PurchaseOperation exacta;
- referencia histórica exacta;
- misma decisión/escenario/snapshot/versiones;
- misma fecha de evaluación;
- referencia temporal no futura;
- evidencias de dimensión exactas.

No se aceptan observaciones desprendidas como autoridad suficiente.

La futura frontera ejecutable debe reconstruir o revalidar la observación desde determinaciones dimensionales autorizadas.

## 10. Evidencia por dimensión

Para `EQUIVALENT`, `MATERIALLY_DIFFERENT` o `NOT_APPLICABLE` se requiere:

```text
authority_ref
methodology_ref
evidence_ids >= 1
trace_refs >= 1
```

Para `NOT_DETERMINABLE` se requiere una causa explícita y trazable.

Contradicción de evidencia:

```text
NOT_DETERMINABLE
```

salvo que otra dimensión independiente ya demuestre `MATERIALLY_DIFFERENT`; en ese caso el estado global sigue siendo `NON_COMPARABLE`.

## 11. Producer boundary

Se autoriza materializar:

- contrato de dimensión;
- carrier agregado;
- agregador determinista;
- validator provenance-safe;
- bridge R-HIS-003.

No se autoriza inventar productores empresariales para las siete dimensiones.

Hasta que cada dimensión disponga de fuente/autoridad upstream suficiente, debe entrar como `NOT_DETERMINABLE`.

## 12. No alcance

No se autoriza:

- porcentajes o tolerancias nuevas;
- scoring;
- ponderaciones;
- fuzzy matching;
- LLM para equivalencia;
- inferencia desde texto libre;
- equivalencia automática por proveedor;
- equivalencia automática de SKU;
- normalización de descuentos/rappels/plazo;
- exclusión automática de referencias de Price Intelligence;
- modificación de representativeness;
- bloqueo de compra.

## 13. Gates

```text
HIS003-G01 → CLOSED — carrier específico
HIS003-G02 → CLOSED — siete dimensiones obligatorias
HIS003-G03 → CLOSED — no scoring/weights
HIS003-G04 → CLOSED — material difference requiere autoridad
HIS003-G05 → CLOSED — cualquier MATERIAL_DIFFERENT basta
HIS003-G06 → CLOSED — unresolved => NOT_DETERMINABLE salvo causa material ya demostrada
HIS003-G07 → CLOSED — mapping TRUE/FALSE/NOT_EVALUABLE
HIS003-G08 → CLOSED — Price comparability no se promueve
HIS003-G09 → CLOSED — provenance-safe boundary
HIS003-G10 → CLOSED — NOT_APPLICABLE requiere autoridad/evidencia
```

## 14. Estado

**HIS003 Commercial Comparability Authority v0.1 — AUTORIZADO Y CORREGIDO.**
