# EIOS — MATRIZ DE EVIDENCIA DE BASE ECONÓMICA — PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.0  
**Estado:** CERRADA — METODOLOGÍA ESPECIALIZADA  
**Autoridad:** subordinada a `Price_Intelligence_Methodological_Matrix.md`

## 1. Propósito

Define cómo C1 demuestra, mediante evidencia autorizada, el estado de cada dimensión de la base económica necesaria para normalizar una referencia.

No modifica C0 y no convierte la ausencia de información en un hecho económico.

## 2. Unidad de evaluación

Cada evaluación corresponde a una dimensión económica concreta de una `PriceReference`.

Dimensiones:

```text
UNIT
QUANTITY
CURRENCY
TAX
TRANSPORT
DISCOUNT
SURCHARGE
COMMERCIAL
```

## 3. Estados

```text
RESOLVED
NOT_APPLICABLE
PENDING
NOT_RESOLVABLE
```

### RESOLVED

Existe evidencia suficiente y una regla autorizada que permiten determinar el hecho económico y, cuando corresponda, ejecutar la normalización.

### NOT_APPLICABLE

La dimensión no forma parte de la base económica de la referencia/contexto según una regla autorizada y existe trazabilidad de esa determinación.

`NOT_APPLICABLE` nunca significa simplemente "no tenemos el dato".

### PENDING

La dimensión es potencialmente resoluble, pero falta información, evidencia o validación necesaria.

### NOT_RESOLVABLE

Con la evidencia y reglas autorizadas disponibles no es metodológicamente posible resolver la dimensión para esa referencia.

## 4. Evidencia mínima

Un estado `RESOLVED` o `NOT_APPLICABLE` debe conservar:

```text
DIMENSION
STATUS
EVIDENCE_REFS
RULE_REFERENCE
TRACE_REFERENCE
```

Una referencia de evidencia debe apuntar a evidencia existente y validada. La validación genérica de evidencia no sustituye la demostración del hecho económico concreto.

## 5. Regla por dimensión

### EB-E01 — UNIT

`RESOLVED` cuando la unidad de la referencia y la unidad objetivo son directamente iguales o existe una conversión autorizada y demostrable.

### EB-E02 — QUANTITY

`RESOLVED` cuando la base de precio está determinada y cualquier conversión necesaria es demostrable. No se presume proporcionalidad si pueden existir componentes fijos, mínimos o escalados.

### EB-E03 — CURRENCY

`RESOLVED` cuando la moneda coincide con la moneda objetivo o existe una conversión autorizada con tasa, criterio temporal y trazabilidad.

### EB-E04 — TAX

`RESOLVED` cuando el tratamiento fiscal relevante está demostrado respecto de la base objetivo. No se presume inclusión o exclusión de impuestos.

### EB-E05 — TRANSPORT

`RESOLVED` cuando puede determinarse si el transporte forma parte de la base objetivo y, si requiere transformación, existe evidencia y regla autorizada. No se estima su importe.

### EB-E06 — DISCOUNT

`RESOLVED` cuando el tratamiento del descuento es conocido y cualquier descuento aplicado está demostrado y es atribuible a la operación. No se supone descuento cero.

### EB-E07 — SURCHARGE

`RESOLVED` cuando el tratamiento de recargos es conocido y cualquier transformación está autorizada y demostrada. No se supone recargo cero.

### EB-E08 — COMMERCIAL

`RESOLVED` cuando las condiciones comerciales materialmente relevantes están identificadas y son compatibles con la base objetivo o pueden normalizarse mediante regla autorizada.

## 6. Regla de no inferencia

Nunca se permite obtener `RESOLVED` mediante:

- ausencia de dato interpretada como cero;
- valor por defecto;
- estimación no autorizada;
- media o mediana;
- último precio;
- proveedor habitual;
- frecuencia;
- proximidad al PR;
- inferencia circular a partir del resultado.

## 7. Relación con EvidenceValidation

```text
EvidenceValidation = ¿la evidencia es válida?

EconomicBasisEvidence = ¿qué hecho económico demuestra esa evidencia?
```

Una evidencia `VALID` puede ser insuficiente para resolver una dimensión económica concreta.

## 8. Relación con normalización

```text
Evidence
  ↓
EconomicBasisEvidence
  ↓
EconomicBasisAssessment
  ↓
Normalization
```

La evidencia demuestra hechos; la evaluación determina estados; la normalización ejecuta transformaciones autorizadas.

## 9. Regla de cierre

```text
TODAS LAS DIMENSIONES APLICABLES
→ RESOLVED / NOT_APPLICABLE
→ NORMALIZED
```

Si una dimensión necesaria queda `PENDING` o `NOT_RESOLVABLE`, la referencia no puede alcanzar `NORMALIZED`.

## 10. No contaminación de C0

Esta matriz no añade hechos económicos a `PurchaseOperation` ni altera los valores originales de C0.

La información complementaria pertenece a la evidencia y al contrato C1.

## 11. Trazabilidad

Toda decisión sobre una dimensión debe poder remontarse a:

```text
PriceReference
→ EconomicBasisEvidence
→ EvidenceValidation
→ Rule
→ Trace
```

## 12. Invariantes

1. Ausencia de dato ≠ NOT_APPLICABLE.
2. Evidencia válida ≠ dimensión resuelta.
3. RESOLVED requiere evidencia y regla.
4. NOT_APPLICABLE requiere regla y justificación.
5. PENDING no puede convertirse silenciosamente en RESOLVED.
6. NOT_RESOLVABLE no puede convertirse silenciosamente en PENDING.
7. No se modifica C0.
8. No se estima fiscalidad, transporte, descuento o recargo.
9. No se presume proporcionalidad.
10. La evidencia económica no determina representatividad.
11. La evidencia económica no determina suficiencia.
12. La evidencia económica no determina el PR.
