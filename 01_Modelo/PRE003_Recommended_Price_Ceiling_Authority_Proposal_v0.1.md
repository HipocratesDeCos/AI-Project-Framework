# EIOS — PRE003 Recommended Price Ceiling Authority Proposal v0.1

**Baseline:** `main @ f6bd7a978f8e02e5d207d282d2e74b911b2ce4a4`  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** `R-PRE-003 — Precio inferior o igual al objetivo`

## 1. Propósito

Cerrar únicamente la semántica mínima necesaria para evaluar:

```text
purchase.unit_price <= recommended_price_ceiling
```

sin convertir `PriceIntelligenceResult.pr_value` en “precio máximo recomendado” por similitud nominal.

## 2. Autoridad existente

La Matriz de Reglas define:

> El precio propuesto es igual o inferior al precio máximo recomendado.

Metadata vigente:

```text
R-PRE-003 → R3 / INFORMATIVA
```

Price Intelligence define explícitamente:

```text
PR ≠ PMR
```

y deja PMR fuera de su metodología cerrada.

Por tanto:

```text
PriceIntelligenceResult.pr_value
!=
recommended_price_ceiling
```

salvo que una autoridad posterior lo demuestre expresamente.

## 3. Principio conservador propuesto

R-PRE-003 v0.1 consumirá un carrier factual independiente:

`RecommendedPriceCeiling`

producido por una fuente/metodología autorizada.

Estados mínimos:

```text
AVAILABLE
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Si `AVAILABLE`:

- `ceiling_price` obligatorio;
- Decimal finito;
- `ceiling_price >= 0`;
- moneda explícita.

En cualquier otro estado:

- `ceiling_price = null`;
- la Rule no puede fabricar un valor.

## 4. Binding a la compra

El carrier debe estar ligado explícitamente a:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
evaluation_date
currency
purchase_operation_ref
source_ref
authority_ref
methodology_ref
trace_refs
```

`purchase_operation_ref` debe ser una huella determinista de la `PurchaseOperation` completa.

Coincidencia parcial por artículo/proveedor no es suficiente.

## 5. Evidence

La Rule exige Evidence explícita:

```text
RecommendedPriceCeilingEvidence
```

Si Evidence es DEMONSTRATED:

```text
demonstration_ref
==
recommended_price_ceiling_ref(carrier)
```

Una referencia forjada/ajena es error estructural.

Evidence GAP/INVALID → `NOT_EVALUABLE`.

## 6. Moneda

La moneda del carrier debe coincidir exactamente con:

```text
PurchaseOperation.currency
```

R-PRE-003 v0.1 no aplica FX.

## 7. Condición propuesta

Con carrier AVAILABLE + Evidence válida:

```text
triggered =
purchase.unit_price <= ceiling_price
```

Fronteras:

```text
purchase.unit_price < ceiling_price → TRUE
purchase.unit_price == ceiling_price → TRUE
purchase.unit_price > ceiling_price → FALSE
```

No se introduce tolerancia implícita.

## 8. Evaluabilidad

Si el carrier está:

- NOT_EVIDENCED;
- CONFLICTING_DATA;
- NOT_DETERMINABLE;

la Rule devuelve:

```text
Assessment.status = NOT_EVALUABLE
Assessment.outcome = null
```

Ausencia de PMR nunca equivale a cero ni a `FALSE`.

## 9. Relación con Price Intelligence

La propuesta no modifica Price Intelligence.

Una fuente de PMR podría, en el futuro, consumir PR como uno de sus inputs si una metodología específica lo autoriza, pero v0.1 no autoriza:

```text
PMR = PR
```

ni:

```text
PMR = PR * factor
```

ni cualquier otra transformación implícita.

Price Intelligence permanece:

```text
PR = referencia de precio
```

y R-PRE-003 consume:

```text
PMR = recommended price ceiling
```

como hecho independiente.

## 10. Parámetros

R-PRE-003 no tiene actualmente una dependencia PARAMETER confirmada en la Matriz de Parámetros/RDM.

Esta propuesta no crea una nueva relación P-PRE-*.

No se reutilizan:

- P-PRE-004;
- P-PRE-005;
- P-PRE-001.

## 11. Metadata

Se conserva exclusivamente:

```text
R-PRE-003 → R3 / INFORMATIVA
```

No produce bloqueo ni escalada.

## 12. No-alcance

Esta propuesta no autoriza:

- redefinir PR como PMR;
- calcular PMR dentro de la Rule;
- introducir fórmula de PMR;
- usar P-PRE-004/005;
- aplicar FX;
- alterar R-PRE-001/002;
- modificar Price Intelligence;
- convertir R3 en recomendación decisional automática.

## 13. Gates que resolvería la aprobación

Si se autoriza expresamente este documento:

```text
PRE-G04 → definición autorizada de precio máximo recomendado CERRADA
PRE003-G01 → carrier factual DEFINIDO
PRE003-G02 → provenance DEFINIDA
PRE003-G03 → fail-closed DEFINIDO
PRE003-G04 → metadata R3/INFORMATIVA CERRADA
```

`PRE-G05` seguirá abierto para las reglas que necesiten un bridge específico desde Price Intelligence; R-PRE-003 v0.1 no depende directamente de `PriceIntelligenceResult`.

## 14. Estado

**PRE003 Recommended Price Ceiling Authority v0.1 — PROPUESTA / NO AUTORIZADA.**
