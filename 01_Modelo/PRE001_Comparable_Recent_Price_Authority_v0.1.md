# EIOS — PRE001 Comparable Recent Price Authority v0.1

**Estado:** AUTORIZADO  
**Fecha:** 21/09/2026  
**Baseline:** `main @ b58b8b61f87fd66269e8f55ede5242efdf69ef29`  
**Origen:** `PRE001_Comparable_Recent_Price_Authority_Proposal_v0.1.md`

## 1. Autoridad humana explícita

Se autoriza la semántica propuesta para `R-PRE-001`:

```text
uplift_pct =
((purchase.unit_price - reference_price) / reference_price) * 100

triggered =
reference_is_recent
AND
uplift_pct >= resolved(P-PRE-004)
```

La referencia debe estar demostrada como comparable.

## 2. Referencia

R-PRE-001 consume una referencia individual `ComparablePriceReference`.

No se autoriza:

- usar `PriceIntelligenceResult.pr_value`;
- seleccionar automáticamente la última compra;
- seleccionar precio mínimo;
- seleccionar proveedor habitual;
- agregar múltiples referencias dentro de Rules.

La selección corresponde a un productor upstream autorizado.

## 3. P-PRE-001

`P-PRE-001` gobierna la recencia y se consume solo mediante:

```text
ResolvedConfiguration(P-PRE-001)
+
ParameterConfigurationEvidence
```

Unidad: `meses`.

Valor entero positivo.

No se valida ni hardcodea el valor inicial 3.

## 4. Semántica temporal

```text
cutoff_date =
evaluation_date desplazada N meses de calendario hacia atrás
```

Regla de clipping:

- conservar el día si existe en el mes destino;
- si no existe, usar el último día del mes destino.

La referencia es reciente cuando:

```text
cutoff_date <= reference_date <= evaluation_date
```

La igualdad con cutoff cuenta como reciente.

Una referencia futura respecto a evaluation_date es incompatible y fail-closed.

## 5. P-PRE-004

`P-PRE-004` gobierna la diferencia porcentual de alerta.

Se consume solo mediante:

```text
ResolvedConfiguration(P-PRE-004)
+
ParameterConfigurationEvidence
```

Unidad: `%`.

Valor Decimal finito y >= 0.

No se valida ni hardcodea el valor inicial 5%.

## 6. Fórmula y frontera

```text
uplift_pct =
((purchase.unit_price - reference_price) / reference_price) * 100
```

No existe redondeo previo.

La alerta se activa cuando:

```text
uplift_pct >= P-PRE-004
```

La igualdad exacta activa la regla.

## 7. Evaluabilidad

La Rule devuelve `NOT_EVALUABLE` cuando:

- comparabilidad no está demostrada;
- Evidence de referencia no es válida;
- reference_price <= 0;
- moneda incompatible;
- reference_date futura;
- P-PRE-001/P-PRE-004 ausentes, no válidos o no evidenciados;
- identity/provenance no coincide.

Referencia comparable pero fuera del horizonte:

```text
EVALUABLE / FALSE
```

## 8. Metadata

```text
R-PRE-001 → R2 / ALTA
```

Sin R0.

## 9. No-alcance

No se autoriza:

- PR agregado;
- selección implícita;
- FX;
- normalización económica implícita;
- ponderación;
- cambios en R-PRE-002/003;
- cambios en Price Intelligence;
- decisión empresarial automática.

**Estado final: AUTORIZADA.**
