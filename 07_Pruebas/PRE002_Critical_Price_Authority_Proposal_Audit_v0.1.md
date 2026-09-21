# EIOS — PRE002 Critical Price Authority Proposal Audit v0.1

**Baseline:** `main @ 5bba5b6c6219dc6ecc55db038bfc7eff48bb8e11`  
**Fecha:** 21/09/2026

## 1. Audit 1

### A1 — baseline crítico ausente

P-PRE-005 es porcentaje, pero la documentación no define base.

**Depuración:** carrier `CriticalPriceBaseline` independiente.

### A2 — reutilizar PRE001

PRE001 usa referencia comparable reciente, pero no existe autoridad para afirmar que también sea el baseline crítico.

**Depuración:** prohibido por defecto.

### A3 — reutilizar PRE003 PMR

PMR es otra semántica.

**Depuración:** prohibido.

### A4 — reutilizar PR

Price Intelligence PR no es límite crítico.

**Depuración:** prohibido.

### A5 — fórmula P-PRE-005

El parámetro expresa una diferencia porcentual.

**Propuesta:** `baseline * (1 + pct/100)`.

### A6 — frontera

R-PRE-002 dice “supera”.

**Propuesta:** operador estricto `>`; igualdad → FALSE.

### A7 — valor inicial

10% está pendiente de validación.

**Depuración:** solo ResolvedConfiguration + Evidence.

### A8 — R0

La Matriz condiciona R0 a que el límite sea no negociable.

No existe productor de esa condición en el scope actual.

**Depuración:** v0.1 queda R1/ALTA sin escalada.

## 2. Contraste transversal

- Matriz de Reglas: condición preservada.
- Matriz de Parámetros: P-PRE-005 confirmado.
- RDM: dependencia directa confirmada.
- PRE001/PRE003: no reutilizados.
- Price Intelligence: no modificado.
- CRC: sin cambios.

## 3. Audit 2

La propuesta:

- no implementa la Rule;
- no inventa baseline concreto;
- no hardcodea 10%;
- no aplica FX;
- no usa PR/PMR/comparable ref como sustitutos;
- no autoriza R0;
- no modifica PRE001/PRE003;
- no altera decisión humana final.

**AUDIT 2: SUPERADA — 0 bloqueadores documentales.**

## 4. Dictamen

La propuesta es apta para decisión humana.

Hasta aprobación explícita:

```text
R-PRE-002 → BLOCKED
```
