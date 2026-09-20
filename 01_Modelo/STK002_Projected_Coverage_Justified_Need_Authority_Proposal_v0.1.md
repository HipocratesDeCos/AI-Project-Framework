# EIOS — STK002 Projected Coverage & Justified Need Authority Proposal v0.1

**Baseline:** `main @ 4988dba78c6fba92efc25040a5049cee8c3878a7`  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** `R-STK-002 — Compra innecesaria por stock suficiente`

## 1. Propósito

Cerrar únicamente la semántica mínima necesaria para evaluar, en una futura unidad técnica:

```text
projected_coverage_after_purchase > resolved(P-STK-004)
AND
justified_need_state == ABSENT
```

sin reutilizar indebidamente `CoverageResult`, sin reinterpretar `ExcessResult` y sin duplicar `R-STK-003`.

## 2. Autoridad documental existente

La Matriz de Reglas define:

> La cobertura prevista supera ampliamente el nivel configurado y no existen necesidades justificadas.

La especificación STK confirma:

```text
P-STK-004 → R-STK-002
```

como dependencia directa.

`P-STK-004` tiene unidad canónica `días`. Su valor inicial de catálogo permanece pendiente de validación y no puede convertirse en default.

## 3. Problema actual

El `CoverageResult` físico existente representa cobertura en el corte de evaluación:

```text
stock_available / daily_demand
```

No demuestra por sí mismo cobertura **posterior a incorporar la compra evaluada**.

`ExcessResult` M07 sí exige `stock_reference.reference_kind = PROJECTED`, pero responde a otra pregunta:

```text
stock proyectado > máximo + tolerancia
```

y no demuestra por sí mismo:

- cobertura proyectada en días;
- ausencia de necesidades justificadas.

Por tanto:

```text
CoverageResult != ProjectedCoverageAfterPurchase
ExcessResult != R-STK-002
```

## 4. Principio conservador propuesto

R-STK-002 v0.1 consumirá dos carriers factuales independientes:

### A. ProjectedCoverageAfterPurchase

Debe ser producido por una fuente/metodología autorizada y ligado a la `PurchaseOperation` exacta.

Estados mínimos:

```text
FINITE
UNBOUNDED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Si `FINITE`:

- `coverage_days >= 0`;
- Decimal finito;
- unidad semántica = días.

Si `UNBOUNDED`:

- no se publica un número arbitrario;
- significa cobertura ilimitada bajo la metodología autorizada, por ejemplo por demanda aplicable igual a cero;
- el productor debe demostrar esa semántica.

La Rule no reconstruye ni recalcula el método de cobertura en v0.1.

### B. JustifiedNeedState

Carrier independiente con estados:

```text
PRESENT
ABSENT
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

`ABSENT` significa:

> una fuente autorizada ha evaluado el ámbito de necesidades justificadas aplicable y ha demostrado que no existe ninguna necesidad que justifique la compra evaluada.

`PRESENT` significa:

> existe al menos una necesidad justificada demostrada para la compra evaluada.

EIOS no deduce `ABSENT` por mera ausencia de pedidos confirmados, reservas o movimientos conocidos.

## 5. Binding a la operación

Ambos carriers deberán quedar ligados a:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
evaluation_date
purchase_operation_ref
source_ref
authority_ref
trace_refs
```

`purchase_operation_ref` debe ser un hash determinista de la `PurchaseOperation` completa.

No basta coincidencia parcial por artículo o escenario.

## 6. Evidence

Cada carrier tendrá Evidence explícita:

```text
ProjectedCoverageAfterPurchaseEvidence
JustifiedNeedStateEvidence
```

Una Evidence DEMONSTRATED debe apuntar a una referencia determinista del carrier completo.

Evidence GAP/INVALID → `NOT_EVALUABLE`.

Una referencia forjada o ajena → error estructural.

## 7. P-STK-004

`P-STK-004` se consumirá solo mediante:

```text
ResolvedConfiguration(P-STK-004)
+
ParameterConfigurationEvidence
```

Validaciones:

- parameter_id exacto;
- parameters_version coincidente;
- company_id coincidente;
- vigencia;
- fecha aplicable coincidente;
- unidad exacta `días`;
- Decimal finito y no negativo;
- Evidence ligada a `configuration_ref`.

No se autoriza hardcodear `90`.

## 8. Condición propuesta

Con ambos carriers válidos y P-STK-004 válida:

### Cobertura FINITE

```text
coverage_high =
coverage_days > P-STK-004
```

### Cobertura UNBOUNDED

```text
coverage_high = TRUE
```

siempre que el estado UNBOUNDED esté demostrado por su Evidence.

### Condición final

```text
triggered =
coverage_high
AND justified_need_state == ABSENT
```

Frontera exacta:

```text
coverage_days == P-STK-004
→ coverage_high = FALSE
```

No existe tolerancia implícita.

## 9. Evaluabilidad conservadora

Para emitir TRUE o FALSE deben estar determinados:

- el estado de cobertura proyectada;
- el estado de necesidad justificada;
- P-STK-004.

Si cualquiera es:

- NOT_EVIDENCED;
- CONFLICTING_DATA;
- NOT_DETERMINABLE;

la Rule devuelve:

```text
Assessment.status = NOT_EVALUABLE
Assessment.outcome = null
```

Incluso cuando uno de los otros predicados bastaría lógicamente para FALSE, v0.1 exige ambos hechos determinados para evitar una falsa sensación de evidencia completa.

## 10. Resultado según combinación

Con información completamente evaluable:

```text
coverage_high = TRUE + need = ABSENT  → TRUE
coverage_high = TRUE + need = PRESENT → FALSE
coverage_high = FALSE + need = ABSENT → FALSE
coverage_high = FALSE + need = PRESENT → FALSE
```

## 11. Separación de R-STK-003

R-STK-002 y R-STK-003 responden a preguntas distintas.

### R-STK-002

```text
cobertura proyectada alta
+
ninguna necesidad justificada
```

### R-STK-003

```text
stock proyectado por encima del máximo/tolerancia M07
```

No se autoriza:

- mapear `ExcessResult.state == EXCESS` directamente a R-STK-002;
- usar R-STK-003 como proxy de cobertura;
- suprimir R-STK-003 cuando R-STK-002 sea TRUE;
- fusionar ambas reglas.

## 12. Relación con R-STK-004

R-STK-004 demuestra mitigación por pedido confirmado sobre un exceso M07.

No equivale a un productor general de `JustifiedNeedState`.

La propuesta no autoriza:

```text
R-STK-004 FALSE
→ JustifiedNeedState.ABSENT
```

ni:

```text
sin pedido confirmado
→ ABSENT
```

## 13. Metadata propuesta

La Matriz vigente declara:

```text
R-STK-002 → R2 / ALTA
```

La propuesta conserva únicamente:

```text
R2 / ALTA
```

No se autoriza escalada automática a R0.

La frase histórica “podrá escalar a R0 si existe bloqueo empresarial explícito” queda fuera de v0.1 y requerirá autoridad separada.

## 14. No-alcance

Esta propuesta no autoriza:

- generar cobertura proyectada dentro de la Rule;
- convertir ventas históricas en demanda;
- interpretar ausencia de confirmed demand como ausencia de necesidad;
- usar P-PYE-* como consumidor directo;
- usar P-STK-005 en R-STK-002;
- fusionar R-STK-002 con M07/R-STK-003;
- escalada R0;
- decisión empresarial automática.

## 15. Gates que resolvería la aprobación

Si este documento recibe autorización explícita:

```text
STK002-G01 → semántica de cobertura proyectada post-compra CERRADA
STK002-G02 → binding de P-STK-004 DEFINIDO
STK002-G03 → semántica de necesidad justificada CERRADA
STK002-G04 → fail-closed CERRADO
STK002-G05 → separación de R-STK-003 CERRADA
```

Los productores concretos podrán materializarse como carriers provenance-safe sin inferir hechos empresariales.

## 16. Estado

**STK002 Projected Coverage & Justified Need Authority v0.1 — PROPUESTA / NO AUTORIZADA.**
