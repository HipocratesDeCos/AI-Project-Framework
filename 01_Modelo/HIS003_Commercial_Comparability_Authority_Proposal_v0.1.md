# EIOS — HIS003 Commercial Comparability Authority Proposal v0.1

**Baseline:** `main @ 0907d77e285b29a96fa575b744db4a90a718a722`  
**Fecha:** 22/09/2026  
**Estado:** PROPUESTA — REQUIERE AUTORIDAD HUMANA  
**Regla:** `R-HIS-003 — Operación no comparable`

## 1. Regla documental vigente

R-HIS-003 se activa cuando una operación histórica presenta diferencias relevantes en:

- cantidad;
- proveedor;
- condiciones;
- descuentos;
- rappels;
- plazo de pago;
- características del artículo.

Resultado:

```text
reducir el nivel de fiabilidad de la referencia
```

Metadata:

```text
R3 / MEDIA
```

## 2. Hallazgo de arquitectura

Price Intelligence ya contiene:

```text
COMPARABLE / NO_COMPARABLE / PENDING
```

pero su comparabilidad actual solo verifica:

- identidad de artículo;
- presencia de evidencia;
- validación de evidencia.

No demuestra por sí misma comparabilidad comercial material en las dimensiones exigidas por R-HIS-003.

Por tanto, R-HIS-003 no debe reutilizar automáticamente ese estado como si cubriera cantidad, proveedor, condiciones, descuentos, rappels o plazo.

## 3. Propuesta de carrier específico

Se propone:

```text
HistoricalCommercialComparabilityObservation
```

con identidad mínima:

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

Estados:

```text
COMPARABLE
NON_COMPARABLE
NOT_DETERMINABLE
```

## 4. Dimensiones

Cada observación debe cubrir explícitamente:

```text
QUANTITY
SUPPLIER
COMMERCIAL_CONDITIONS
DISCOUNTS
RAPPELS
PAYMENT_TERM
ARTICLE_CHARACTERISTICS
```

Cada dimensión usa:

```text
EQUIVALENT
MATERIALLY_DIFFERENT
NOT_DETERMINABLE
NOT_APPLICABLE
```

## 5. Autoridad de relevancia

R-HIS-003 **no define** por sí misma:

- tolerancia porcentual de cantidad;
- si proveedor distinto invalida comparabilidad;
- equivalencia de plazo;
- equivalencia de descuentos/rappels;
- taxonomía de condiciones;
- similitud técnica del artículo.

La clasificación `MATERIALLY_DIFFERENT` debe venir de una autoridad/metodología especializada y trazable.

No se permite inferir relevancia por:

- simple desigualdad;
- texto libre;
- distancia numérica no autorizada;
- proveedor diferente por sí solo;
- ausencia de dato.

## 6. Agregación propuesta

```text
si cualquier dimensión = MATERIALLY_DIFFERENT
→ state = NON_COMPARABLE

si ninguna dimensión = MATERIALLY_DIFFERENT
AND todas las dimensiones están en {EQUIVALENT, NOT_APPLICABLE}
→ state = COMPARABLE

si no hay diferencia material demostrada
pero al menos una dimensión = NOT_DETERMINABLE
→ state = NOT_DETERMINABLE
```

No existe scoring ni ponderación.

## 7. Semántica R-HIS-003 propuesta

```text
HistoricalCommercialComparabilityObservation = NON_COMPARABLE
→ R-HIS-003 TRUE
```

```text
HistoricalCommercialComparabilityObservation = COMPARABLE
→ R-HIS-003 FALSE
```

```text
HistoricalCommercialComparabilityObservation = NOT_DETERMINABLE
→ R-HIS-003 NOT_EVALUABLE
```

Nunca convertir incertidumbre en TRUE/FALSE.

## 8. Alcance del resultado

R-HIS-003 TRUE significa exclusivamente:

```text
la referencia histórica no debe tratarse automáticamente como comercialmente equivalente
```

No significa:

- eliminar físicamente la referencia;
- invalidar toda la historia;
- bloquear compra;
- recalcular precio automáticamente;
- declarar fraude/anomalía;
- modificar representativeness por inferencia.

## 9. Relación con Price Intelligence

Price Intelligence puede aportar hechos y referencias, pero:

```text
Price comparability ≠ HIS003 commercial comparability
```

R-HIS-003 requiere su propio carrier o un adapter autorizado que demuestre las siete dimensiones.

No se autoriza mapear automáticamente:

```text
PriceReferenceAssessment.NO_COMPARABLE
→ R-HIS-003 TRUE
```

salvo que la causa documentada pertenezca al contrato HIS003 autorizado.

## 10. Evidencia

Para `COMPARABLE` o `NON_COMPARABLE`:

- cada dimensión evaluada debe portar evidencia/traza suficiente;
- el carrier debe estar vinculado a la referencia histórica exacta;
- no se admiten evidencias de otra transacción;
- contradicción → NOT_DETERMINABLE.

## 11. Producer boundary

La regla no acepta observaciones desprendidas como autoridad suficiente.

La futura implementación debe:

1. recibir hechos upstream autorizados;
2. reconstruir o validar el carrier dentro de una frontera provenance-safe;
3. verificar identidad de referencia/operación/contexto;
4. emitir Assessment R-HIS-003.

Mientras no exista productor especializado de dimensión, esa dimensión queda `NOT_DETERMINABLE`.

## 12. No alcance

No se autoriza:

- umbral cuantitativo;
- scoring;
- pesos;
- fuzzy matching;
- LLM para determinar equivalencia;
- comparación semántica de texto libre;
- equivalencia automática de proveedor;
- equivalencia automática de SKU distinto;
- normalización de descuentos/rappels;
- normalización de plazo;
- exclusión automática de referencias del PR.

## 13. Metadata

Se conserva:

```text
R-HIS-003
effect = R3
severity = MEDIA
active_result = none
```

Resultado informativo: reducción de confianza / advertencia de no comparabilidad.

## 14. Gates propuestos

```text
HIS003-G01 → carrier específico
HIS003-G02 → 7 dimensiones explícitas
HIS003-G03 → no scoring/weights
HIS003-G04 → material difference requires specialized authority
HIS003-G05 → any MATERIAL_DIFFERENT => NON_COMPARABLE
HIS003-G06 → unresolved dimension => NOT_DETERMINABLE unless another dimension already proves NON_COMPARABLE
HIS003-G07 → TRUE/FALSE/NOT_EVALUABLE mapping
HIS003-G08 → Price comparability not promoted automatically
HIS003-G09 → provenance-safe producer required
```

## 15. Decisión requerida

Autorizar o corregir esta semántica antes de materializar R-HIS-003.
