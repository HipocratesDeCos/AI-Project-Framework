# EIOS — PAG001 Offered Payment Term Adapter Technical Contract v0.1

**Autoridad:** `01_Modelo/PAG001_Offered_Payment_Term_Authority_v0.1.md`  
**Estado:** DISEÑO TÉCNICO PARA MATERIALIZACIÓN

## 1. Componentes

Se materializan:

- `PaymentTermSemanticAuthority`;
- `OfferedPaymentTermObservation`;
- `PaymentTermObservationAdapter`.

No se modifica Supplier Evidence Core.

## 2. Fuente factual

El adapter consume exclusivamente un `SupplierEvidenceResult` ya producido.

Solo considera observaciones del proveedor actual con:

```text
candidate_id = None
dimension    = PAYMENT_TERM
object_id    = identity.article_id
```

## 3. Autoridad semántica

La interpretación como plazo ofrecido en días requiere:

```text
observation.semantic_ref == semantic_authority.semantic_ref
semantic_authority.meaning == OFFERED_PAYMENT_TERM_DAYS
```

No existe literal semantic_ref hardcodeado.

## 4. Estados

```text
0 observaciones             → NOT_EVIDENCED
1 NOT_EVIDENCED             → NOT_EVIDENCED
1 CONFLICTING_DATA          → CONFLICTING_DATA
1 KNOWN válida              → AVAILABLE
1 KNOWN no utilizable       → NOT_DETERMINABLE
>1 PAYMENT_TERM candidatas  → CONFLICTING_DATA
```

## 5. Valor

`INTEGER` se convierte exactamente a Decimal.

`DECIMAL` se conserva sin redondeo.

No existen conversiones de unidad.

## 6. Fail-closed

Tipo, unidad, semantic authority, fecha, vigencia o valor incompatibles nunca producen AVAILABLE.

La multiplicidad nunca se resuelve por orden o valor.

## 7. No alcance

No se implementan:

- R-PAG-001;
- R-PAG-002;
- P-PAG-003;
- P-PAG-004 como ejecución de regla;
- P-PAG-005;
- normalización multicuota;
- derivación desde due_date;
- QTG.
