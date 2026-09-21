# EIOS — PRE001 Comparable Recent Price Authority Proposal v0.1

**Baseline:** `main @ 2bb9eac45c69908122abc6468fab93ddb5314498`  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** `R-PRE-001 — Precio superior a compra comparable reciente`

## 1. Propósito

Cerrar únicamente la semántica mínima necesaria para evaluar:

```text
purchase.unit_price
vs.
comparable_reference_price
```

cuando la referencia:

- está demostrada como comparable;
- está dentro del horizonte `P-PRE-001`;
- y la diferencia porcentual alcanza el umbral `P-PRE-004`.

No se reutiliza el PR agregado de Price Intelligence ni se selecciona automáticamente la “última compra”.

## 2. Autoridad documental existente

La Matriz de Reglas establece:

> El precio propuesto supera el precio de una operación comparable reciente en el porcentaje configurado.

La RDM confirma:

```text
P-PRE-001 → R-PRE-001
P-PRE-004 → R-PRE-001
```

`GAP-PI-TEMP-01` confirma que “reciente” para R-PRE-001 se gobierna por `P-PRE-001`.

Los valores iniciales 3 meses y 5% permanecen pendientes de validación empresarial y no constituyen defaults.

## 3. Carrier factual propuesto

Se define un carrier independiente:

`ComparablePriceReference`

Campos mínimos:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
evaluation_date
currency
purchase_operation_ref
reference_operation_ref
reference_date
reference_price
comparability_state
source_ref
authority_ref
methodology_ref
trace_refs
```

Estados de comparabilidad:

```text
COMPARABLE
NOT_COMPARABLE
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Solo `COMPARABLE` permite seguir evaluando la regla.

## 4. Precio de referencia

`reference_price` debe ser:

- Decimal finito;
- estrictamente mayor que 0;
- ya normalizado/comparable por el productor autorizado;
- expresado en la misma moneda que la compra evaluada.

R-PRE-001 no realiza:

- FX;
- normalización de unidades;
- ajustes de transporte;
- impuestos;
- descuentos;
- rappels;
- selección de proveedor;
- agregación de múltiples referencias.

## 5. Binding a la operación

El carrier debe quedar ligado a:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
evaluation_date
purchase_operation_ref
```

`purchase_operation_ref` debe ser SHA-256 determinista de la `PurchaseOperation` completa.

La referencia histórica debe portar además `reference_operation_ref` no vacío y trazable.

## 6. Evidence

Se exige:

```text
ComparablePriceReferenceEvidence
```

Si Evidence es DEMONSTRATED:

```text
demonstration_ref == comparable_price_reference_ref(carrier)
```

Evidence GAP/INVALID → `NOT_EVALUABLE`.

Referencia forjada o ajena → error estructural.

## 7. P-PRE-001 — horizonte de recencia

`P-PRE-001` se consume únicamente mediante:

```text
ResolvedConfiguration(P-PRE-001)
+
ParameterConfigurationEvidence
```

Unidad exacta:

```text
meses
```

El valor debe ser entero positivo.

No se hardcodea 3.

### Semántica temporal propuesta

Se define:

```text
cutoff_date =
evaluation_date desplazada hacia atrás N meses de calendario
```

con regla de clipping de fin de mes:

- conservar el día cuando exista en el mes destino;
- si no existe, usar el último día del mes destino.

Ejemplos:

```text
31 mayo - 3 meses → 28/29 febrero
30 noviembre - 1 mes → 30 octubre
```

Una referencia es reciente cuando:

```text
cutoff_date <= reference_date <= evaluation_date
```

La igualdad exacta con `cutoff_date` cuenta como reciente.

Una referencia futura respecto a `evaluation_date` es incompatible y no evaluable.

## 8. P-PRE-004 — diferencia de alerta

`P-PRE-004` se consume únicamente mediante:

```text
ResolvedConfiguration(P-PRE-004)
+
ParameterConfigurationEvidence
```

Unidad exacta:

```text
%
```

Valor Decimal finito y >= 0.

No se hardcodea 5%.

## 9. Fórmula porcentual propuesta

Con una referencia comparable y reciente:

```text
uplift_pct =
((purchase.unit_price - reference_price) / reference_price) * 100
```

No se aplica redondeo previo a la comparación.

## 10. Condición propuesta

```text
triggered =
uplift_pct >= resolved(P-PRE-004)
```

La igualdad exacta con el umbral activa la alerta.

Motivo: `P-PRE-004` se denomina “Diferencia para activar alerta de precio”; alcanzar el umbral se interpreta como alcanzar la condición configurada.

Esta frontera requiere autorización explícita y no se infiere automáticamente de la redacción histórica.

## 11. Evaluabilidad conservadora

La Rule devuelve `NOT_EVALUABLE` cuando:

- comparability_state != COMPARABLE;
- Evidence de referencia no es válida;
- reference_price <= 0;
- moneda incompatible;
- P-PRE-001 ausente/no válida/no evidenciada;
- P-PRE-004 ausente/no válida/no evidenciada;
- reference_date futura;
- no puede determinarse el cutoff temporal;
- identity/provenance no coincide.

Una referencia comparable pero no reciente produce:

```text
EVALUABLE / FALSE
```

porque la condición conjunta “comparable reciente + diferencia” no se cumple con una referencia temporalmente fuera del horizonte.

## 12. Selección de referencia

R-PRE-001 v0.1 evalúa **una referencia explícitamente suministrada**.

No autoriza seleccionar automáticamente:

- la última compra;
- el precio mínimo;
- el proveedor habitual;
- el PR agregado;
- la referencia más favorable/desfavorable.

Si existen múltiples referencias candidatas, la selección corresponde a un productor/metodología upstream autorizado.

## 13. Relación con Price Intelligence

La propuesta no modifica C1.

Price Intelligence puede ser, en el futuro, una fuente upstream de hechos de comparabilidad/normalización si se define un bridge específico, pero R-PRE-001 no consume:

```text
PriceIntelligenceResult.pr_value
```

ni reconstruye Price Intelligence desde resultados desprendidos.

## 14. Metadata

Se conserva:

```text
R-PRE-001 → R2 / ALTA
```

No se introduce R0.

## 15. No-alcance

No se autoriza:

- usar PR agregado como reference_price;
- elegir automáticamente una referencia;
- hardcodear 3 meses;
- hardcodear 5%;
- FX;
- normalización implícita;
- ponderación;
- modificar R-PRE-002/003;
- modificar Price Intelligence;
- decisión empresarial automática.

## 16. Gates que resolvería la aprobación

Si se autoriza expresamente:

```text
PRE-G01 → semántica temporal P-PRE-001 CERRADA para R-PRE-001
PRE-G02 → semántica ejecutable P-PRE-004 CERRADA
PRE001-G01 → carrier comparable DEFINIDO
PRE001-G02 → provenance DEFINIDA
PRE001-G03 → fórmula porcentual CERRADA
PRE001-G04 → frontera >= CERRADA
PRE001-G05 → fail-closed CERRADO
```

El bridge físico podrá materializarse sin inventar selección de referencias.

## 17. Estado

**PRE001 Comparable Recent Price Authority v0.1 — PROPUESTA / NO AUTORIZADA.**
