# EIOS — STK002 Projected Coverage & Justified Need Authority v0.1

**Estado:** AUTORIZADO  
**Fecha:** 20/09/2026  
**Baseline:** `main @ 4128771f58aa446d61ad28cb1a8ec96c4f3817a0`  
**Origen:** `STK002_Projected_Coverage_Justified_Need_Authority_Proposal_v0.1.md`

## 1. Autoridad humana explícita

Se autoriza expresamente la semántica propuesta para `R-STK-002`:

```text
coverage_high
AND
justified_need_state == ABSENT
```

donde:

```text
coverage_high =
    projected_coverage_after_purchase > resolved(P-STK-004)
```

y una cobertura `UNBOUNDED` demostrada implica `coverage_high = TRUE`.

## 2. Frontera exacta

```text
coverage_days == P-STK-004
→ FALSE
```

No existe tolerancia implícita.

## 3. Evaluabilidad

Para emitir TRUE/FALSE deben estar determinados:

- cobertura proyectada post-compra;
- estado de necesidad justificada;
- P-STK-004.

Cualquier estado no evidenciado, contradictorio o no determinable produce:

```text
NOT_EVALUABLE / outcome=null
```

## 4. Justified Need

`ABSENT` solo puede proceder de un productor autorizado que haya evaluado el ámbito de necesidades aplicable.

No se autoriza inferir ABSENT desde:

- ausencia de pedidos confirmados;
- R-STK-004 FALSE;
- ausencia de reservas;
- ausencia de movimientos conocidos.

## 5. Separación

No se autoriza:

- reutilizar `CoverageResult` del corte como cobertura post-compra;
- usar `ExcessResult`/R-STK-003 como proxy;
- fusionar R-STK-002 con R-STK-003;
- usar R-STK-004 como productor general de necesidad;
- usar P-STK-005;
- usar P-PYE-* como consumidor directo.

## 6. P-STK-004

Se consume únicamente mediante:

```text
ResolvedConfiguration(P-STK-004)
+
ParameterConfigurationEvidence
```

sin hardcodear 90 días.

## 7. Metadata

```text
R-STK-002 → R2 / ALTA
```

No se autoriza escalada automática R0.

**Estado final: AUTORIZADA.**
