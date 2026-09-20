# EIOS — FIN002 Post-Operation Working Capital Authority v0.1

**Estado:** AUTORIZADO  
**Fecha:** 20/09/2026  
**Baseline de propuesta:** `main @ d2d28c2bfff095d96387dcebc082f4b53025be9e`  
**Origen:** `FIN002_Post_Operation_Working_Capital_Authority_Proposal_v0.1.md`  
**Autorización humana explícita:** `autorizo`

## 1. Alcance autorizado

Se autoriza la semántica conservadora necesaria para evaluar:

```text
R-FIN-002:
working_capital_after_operation < resolved(P-FIN-003)
```

sin que EIOS invente el efecto contable de la compra.

## 2. Magnitudes autorizadas

Una fuente competente debe suministrar y demostrar:

```text
current_assets_after_operation
current_liabilities_after_operation
```

para la operación evaluada.

EIOS queda autorizado únicamente a calcular:

```text
working_capital_after_operation
=
current_assets_after_operation
-
current_liabilities_after_operation
```

No se autoriza transformar por inferencia el precio, impuestos, inventario, proveedor, plazo, tesorería, pagos, descuentos o rappels en movimientos contables.

## 3. Identidad y provenance

La posición post-operación debe estar ligada de forma explícita a:

- `decision_id`;
- `scenario_id`;
- `data_snapshot_id`;
- `company_scope`;
- `article_id`;
- `evaluation_date`;
- moneda;
- referencia determinista de la `PurchaseOperation`;
- `post_operation_snapshot_ref`;
- `source_ref`;
- `authority_ref`;
- trazas.

Una etiqueta textual “post-operation” no constituye provenance.

## 4. Corte y compatibilidad

Los dos importes deben pertenecer a:

- la misma sociedad;
- la misma moneda;
- el mismo corte post-operación;
- la misma evaluación/escenario.

EIOS no reclasifica cuentas, no mezcla fechas/sociedades y no aplica FX implícito.

## 5. P-FIN-003

`P-FIN-003` se consume exclusivamente mediante:

```text
ResolvedConfiguration(P-FIN-003)
+
ParameterConfigurationEvidence
```

con:

- `parameters_version` coincidente;
- `company_id` coincidente;
- vigencia en la fecha aplicable;
- unidad monetaria compatible;
- Decimal finito;
- Evidence vinculada a `configuration_ref`.

No se autoriza ningún default.

## 6. Condición y frontera

```text
working_capital_after_operation < P-FIN-003
→ TRUE
```

```text
working_capital_after_operation >= P-FIN-003
→ FALSE
```

Por tanto, igualdad exacta con el umbral → `FALSE`.

No existe tolerancia implícita.

## 7. Metadata

Se conserva la autoridad vigente:

```text
R-FIN-002 → R0 / CRÍTICA
```

La mención histórica a “bloqueo configurable” no autoriza un switch ordinario que desactive R0. Excepciones o desactivaciones requieren autoridad separada.

## 8. Fail closed

Ante cualquiera de estos casos:

- posición post-operación no demostrada;
- falta una de las dos magnitudes;
- datos contradictorios;
- identity/provenance incompatible;
- moneda o corte incompatibles;
- `P-FIN-003` ausente, no evidenciada, no vigente o no numérica;

la Rule debe producir:

```text
Assessment.status = NOT_EVALUABLE
Assessment.outcome = null
```

Nunca `FALSE` por ausencia de evidencia.

## 9. No-alcance

No se autoriza:

- creación de asientos;
- cálculo contable causal de la compra;
- inferencia de IVA;
- reclasificación;
- FX;
- financiación;
- escenarios contables fabricados por EIOS;
- modificación de Finance Basic;
- modificación de R-FIN-001/R-FIN-003;
- excepción o degradación de R0;
- decisión empresarial automática.

## 10. Gate técnico

Con esta autoridad quedan cerrados documentalmente:

- `FIN002-G01`;
- `FIN002-G02`;
- `FIN002-G03`;
- `FIN002-G05`.

`FIN002-G04` debe cerrarse físicamente mediante el binding provenance-safe de `P-FIN-003`.

**Estado final de autoridad: AUTORIZADA.**
