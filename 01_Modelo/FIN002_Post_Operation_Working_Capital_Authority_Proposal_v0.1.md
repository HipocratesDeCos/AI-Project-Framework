# EIOS — FIN002 Post-Operation Working Capital Authority Proposal v0.1

**Baseline:** `main @ d2d28c2bfff095d96387dcebc082f4b53025be9e`  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** `R-FIN-002 — Fondo de maniobra insuficiente`

## 1. Propósito

Cerrar únicamente la semántica necesaria para que EIOS pueda evaluar, en una futura unidad técnica:

```text
working_capital_after_operation < resolved(P-FIN-003)
```

sin inventar el efecto contable de la compra.

Esta propuesta no implementa `R-FIN-002`, no valida el valor inicial de `P-FIN-003` y no modifica Finance Basic, CRC ni MED.

## 2. Problema actual

La regla vigente exige:

> después de considerar la operación, el fondo de maniobra queda por debajo del límite configurado.

Finance Basic ya autoriza:

```text
working_capital = current_assets - current_liabilities
```

pero su `WorkingCapitalInput` actual no demuestra por sí solo que los importes correspondan a una posición contable **posterior a la operación evaluada**.

Por tanto:

```text
FinanceBasicResult.working_capital
!=
working_capital_after_operation
```

salvo que una fuente/binding adicional demuestre esa semántica.

## 3. Principio conservador propuesto

Para FIN002 v0.1, EIOS **no derivará** el efecto contable de la compra.

El valor post-operación deberá proceder de una fuente autorizada que suministre o demuestre explícitamente:

```text
current_assets_after_operation
current_liabilities_after_operation
```

para la misma operación evaluada.

EIOS podrá aplicar únicamente:

```text
working_capital_after_operation
=
current_assets_after_operation
-
current_liabilities_after_operation
```

No podrá transformar por sí mismo:

- importe de compra;
- IVA/impuestos;
- plazo de pago;
- alta de existencias;
- proveedor;
- tesorería;
- pagos futuros;
- descuentos;
- rappels;

en movimientos de activo/pasivo corriente.

## 4. Binding obligatorio a la operación

La fuente post-operación deberá quedar ligada, como mínimo, a:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
operation/article identity
evaluation_date
post_operation_snapshot_ref
source_ref
authority_ref
trace_refs
```

El binding debe demostrar que el escenario contable incorpora específicamente la `PurchaseOperation` evaluada.

Una cifra etiquetada manualmente como “post-operation” sin provenance no es admisible.

## 5. Corte temporal

Para v0.1 se propone:

- `evaluation_date` identifica la fecha de evaluación EIOS;
- el productor externo declara el corte contable post-operación aplicable;
- dicho corte debe estar asociado a la misma evaluación/escenario;
- EIOS no desplaza fechas ni crea un asiento futuro implícito.

Si la fuente usa otra fecha/corte sin una relación explícita con la evaluación, el dato es `NOT_EVALUABLE`.

## 6. Moneda y scope

`current_assets_after_operation` y `current_liabilities_after_operation` deben:

- pertenecer al mismo `company_scope`;
- usar la misma moneda;
- usar el mismo corte;
- estar clasificados contablemente por la fuente autorizada.

EIOS no:

- reclasifica cuentas;
- mezcla sociedades;
- convierte FX;
- agrega balances de fechas distintas.

## 7. Estados de evidencia

La futura frontera deberá distinguir al menos:

```text
DEMONSTRATED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Solo `DEMONSTRATED` con ambas magnitudes válidas permite calcular el fondo de maniobra post-operación.

Ausencia o conflicto nunca equivalen a cero.

## 8. P-FIN-003

`P-FIN-003 — Fondo de maniobra mínimo` se consumirá exclusivamente mediante:

```text
ResolvedConfiguration(P-FIN-003)
+
ParameterConfigurationEvidence
```

Obligaciones:

- `parameters_version` coincidente;
- empresa coincidente;
- vigencia en la fecha aplicable;
- unidad monetaria compatible;
- valor Decimal finito;
- evidence vinculada a `configuration_ref`.

El valor inicial del catálogo no constituye default.

## 9. Condición ordinaria propuesta de R-FIN-002

Una vez demostrados ambos lados:

```text
triggered =
working_capital_after_operation
<
resolved(P-FIN-003)
```

Frontera exacta:

```text
working_capital_after_operation == P-FIN-003
→ FALSE
```

No se introduce tolerancia implícita.

## 10. Metadata

La Matriz de Reglas vigente declara:

```text
R-FIN-002 → R0 / CRÍTICA
```

La propuesta conserva esa metadata sin crear otro efecto.

La frase histórica “bloqueo configurable” no autoriza que un parámetro ordinario desactive R0. Cualquier mecanismo de desactivación/excepción exige autoridad separada.

## 11. NOT_EVALUABLE

La futura rule deberá producir:

```text
Assessment.status = NOT_EVALUABLE
Assessment.outcome = null
```

cuando ocurra cualquiera de estos casos:

- posición post-operación no demostrada;
- una de las dos magnitudes falta;
- conflicto de datos;
- mismatch de empresa/escenario/snapshot/operación;
- moneda incompatible;
- corte temporal incompatible;
- P-FIN-003 ausente/no evidenciada/no vigente/no numérica.

No se permite `FALSE` por falta de evidencia.

## 12. No-alcance

Esta propuesta no autoriza:

- cálculo contable del efecto de la compra dentro de EIOS;
- creación de asientos;
- inferencia de IVA;
- reclasificación contable;
- FX;
- financiación;
- escenarios contables generados por EIOS;
- modificación de Finance Basic;
- modificación de R-FIN-001/R-FIN-003;
- excepciones a R0;
- decisión empresarial automática.

## 13. Gates que resolvería la aprobación

Si se autoriza expresamente este documento:

```text
FIN002-G01 → semántica de valor post-operación CERRADA
FIN002-G02 → clase de productor/fuente CERRADA
FIN002-G03 → obligaciones de provenance DEFINIDAS
FIN002-G05 → fail-closed DEFINIDO
```

`FIN002-G04` se cerrará físicamente en el contrato/implementación mediante `ResolvedConfiguration(P-FIN-003) + Evidence`.

## 14. Consecuencia de aprobación

La aprobación permitiría abrir:

```text
FIN002 Technical Contract
→ Audit 1
→ Depuración
→ Audit 2
→ Materialización
→ CI
```

sin modificar Finance Basic ni inventar un productor contable.

## 15. Estado

**FIN002 Post-Operation Working Capital Authority v0.1 — PROPUESTA / NO AUTORIZADA.**
