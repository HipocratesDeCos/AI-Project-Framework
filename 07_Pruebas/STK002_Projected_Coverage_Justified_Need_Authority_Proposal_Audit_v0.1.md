# EIOS — STK002 Projected Coverage & Justified Need Authority Proposal Audit v0.1

**Baseline:** `main @ 4988dba78c6fba92efc25040a5049cee8c3878a7`  
**Objeto:** auditar la propuesta previa a autorización humana.

## 1. Audit 1

### A1 — Reutilizar CoverageResult del corte

El resultado actual no demuestra cobertura posterior a la compra.

**Depuración:** carrier específico `ProjectedCoverageAfterPurchase`.

### A2 — Reutilizar ExcessResult M07

M07 cuantifica exceso contra máximo+tolerancia, no cobertura ni ausencia de necesidad.

**Depuración:** R-STK-002 conserva inputs propios.

### A3 — “supera ampliamente”

La frase podría introducir una tolerancia no documentada.

**Depuración:** la relación directa confirmada es `P-STK-004 → R-STK-002`; v0.1 propone condición estricta `coverage > P-STK-004` sin tolerancia adicional.

### A4 — Cobertura UNBOUNDED

Convertirla a un número arbitrario sería incorrecto.

**Depuración:** estado semántico separado; UNBOUNDED demostrado implica `coverage_high=TRUE`.

### A5 — ausencia de necesidad

No puede inferirse por ausencia de pedidos confirmados.

**Depuración:** carrier `JustifiedNeedState` con estado ABSENT expresamente demostrado.

### A6 — indeterminación de uno de los predicados

Una lógica de cortocircuito podría emitir FALSE aunque falte evidencia del segundo hecho.

**Depuración:** v0.1 exige ambos predicados determinados para cualquier TRUE/FALSE; si no, NOT_EVALUABLE.

### A7 — defaults

P-STK-004 = 90 días está pendiente de validación.

**Depuración:** solo ResolvedConfiguration + Evidence.

### A8 — escalada R0

La Matriz la permite bajo bloqueo empresarial explícito, pero no existe autoridad física cerrada.

**Depuración:** v0.1 fija R2/ALTA y excluye R0.

### A9 — relación con R-STK-004

Pedido confirmado es solo una clase de necesidad/mitigación y no demuestra ausencia global.

**Depuración:** R-STK-004 no se usa para fabricar JustifiedNeedState.

## 2. Contraste transversal

### M04

P-STK-004 como coverage_maximum permanece coherente.

**PASS.**

### M07 / R-STK-003

No se modifica ni reutiliza como proxy.

**PASS.**

### M08 / R-STK-004

No se redefine su excepción por pedido confirmado.

**PASS.**

### P-PYE

No se introduce consumidor directo nuevo.

**PASS.**

### Evidence

Los dos hechos de negocio requieren Evidence propia.

**PASS.**

### CRC

Sin cambios.

**PASS.**

## 3. Audit 2

La propuesta:

- no implementa Rules;
- no crea cobertura sintética;
- no inventa demanda;
- no asume ausencia de necesidad;
- no valida 90 días;
- no usa P-STK-005;
- no escala a R0;
- no reabre R-STK-003/R-STK-004;
- no altera la decisión humana.

**AUDIT 2: SUPERADA — 0 bloqueadores documentales.**

## 4. Dictamen

La propuesta es apta para decisión humana.

Hasta aprobación explícita:

```text
R-STK-002 → BLOCKED
```

Una instrucción genérica de continuar no equivale a autorización de esta semántica.
