# EIOS — PAG001 Offered Payment Term Authority v0.1

**Baseline de autorización:** `main @ 283ad74e6cc253fd533e2ff2a6884cf2443bf2c2`  
**Fecha:** 21/09/2026  
**Estado:** AUTORIZADO Y CORREGIDO  
**Ámbito:** carrier factual canónico para el “plazo ofrecido” consumible por `R-PAG-001`.

## 1. Autoridad humana explícita

Se autoriza la propuesta `PAG001 Offered Payment Term Authority v0.1`, con una corrección de seguridad: una `semantic_ref` no tiene autoridad por su literal.

## 2. Frontera autorizada

```text
SupplierEvidenceResult
  ↓
PaymentTermObservationAdapter
  ↓
OfferedPaymentTermObservation
```

Esta autoridad cierra únicamente el carrier factual de plazo ofrecido.

No implementa todavía la condición completa de `R-PAG-001`.

## 3. Autoridad semántica explícita

El adapter debe recibir una autoridad semántica explícita:

`PaymentTermSemanticAuthority`

con, como mínimo:

```text
semantic_ref
meaning = OFFERED_PAYMENT_TERM_DAYS
authority_ref
methodology_ref
version
```

La coincidencia textual del `semantic_ref` no basta.

El adapter solo puede aceptar una observación cuando:

```text
observation.semantic_ref == semantic_authority.semantic_ref
AND semantic_authority.meaning == OFFERED_PAYMENT_TERM_DAYS
```

No se autoriza una registry global implícita ni hardcodear `SEM-PAYMENT-DAYS`.

## 4. Carrier factual

`OfferedPaymentTermObservation`:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
supplier_id
evaluation_date
source_observation_id
offered_payment_term_days
state
source_ref
evidence_id
semantic_ref
semantic_authority_ref
authority_ref
methodology_ref
trace_refs
```

Estados:

```text
AVAILABLE
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

## 5. AVAILABLE

Solo puede publicarse cuando existe exactamente una observación aplicable que:

- pertenece al resultado Supplier Evidence del contexto exacto;
- corresponde al proveedor actual y al artículo exacto;
- tiene `candidate_id is None`;
- tiene `dimension == PAYMENT_TERM`;
- tiene `state == KNOWN`;
- usa `INTEGER` o `DECIMAL`;
- publica valor finito y no negativo;
- usa `unit == days`;
- dispone de `source_ref`, `evidence_id`, `captured_at`;
- no contiene contradicción no resuelta;
- no es futura;
- está vigente en evaluation_date;
- está cubierta por `PaymentTermSemanticAuthority` explícita.

## 6. Cero / una / múltiples observaciones

```text
0 aplicables → NOT_EVIDENCED
1 válida      → AVAILABLE
>1 aplicables → CONFLICTING_DATA
```

No se selecciona por orden, fecha, máximo, mínimo, promedio o coincidencia de valor.

Incluso dos observaciones con el mismo valor permanecen conflictivas sin autoridad específica de deduplicación.

## 7. Valor canónico

INTEGER:

```text
Decimal(value_integer)
```

DECIMAL:

```text
value_decimal
```

No se redondea.

No se convierten semanas o meses.

No se interpreta texto.

## 8. Corrección adicional — observación aplicable vs observación inválida

Una observación que pertenezca al proveedor/artículo/contexto y declare `dimension=PAYMENT_TERM` pero no cumpla tipo, unidad, semantic authority, evidencia o vigencia no se trata como “ausente”.

Si es única:

```text
NOT_DETERMINABLE
```

Si coexiste con otra candidata aplicable o existe contradicción:

```text
CONFLICTING_DATA
```

Esto evita ocultar datos presentes pero semánticamente no utilizables bajo `NOT_EVIDENCED`.

## 9. Multicuota

No se autoriza derivar un escalar desde vencimientos/cuotas.

No se autoriza:

- promedio;
- promedio ponderado;
- primer/último vencimiento;
- mínimo/máximo;
- días desde pedido o confirmación;
- equivalencia financiera.

## 10. Relación con PAG

Esta autoridad no cierra:

- fórmula exacta de `P-PAG-003`;
- tratamiento completo de `P-PAG-004`;
- cálculo económico de `P-PAG-005`;
- binding completo de parámetros PAG;
- `R-PAG-001`;
- `R-PAG-002`.

## 11. Fail-closed

Toda identidad incompatible o provenance no demostrable debe rechazarse o producir estado no AVAILABLE según la naturaleza del defecto.

No se fabrican días de pago.

## 12. Gates

```text
PAG001-TERM-G01 → CLOSED
PAG001-TERM-G02 → CLOSED
PAG001-TERM-G03 → CLOSED
PAG001-TERM-G04 → CLOSED
PAG001-TERM-G05 → CLOSED
PAG001-TERM-G06 → CLOSED
PAG001-TERM-G07 → semantic_ref requiere autoridad explícita
PAG001-TERM-G08 → dato presente pero no utilizable ≠ NOT_EVIDENCED
```

## 13. Estado

**PAG001 Offered Payment Term Authority v0.1 — AUTORIZADO Y CORREGIDO.**
