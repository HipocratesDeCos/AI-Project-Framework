# EIOS — PRE003 Recommended Price Ceiling Authority Proposal Audit v0.1

**Baseline:** `main @ f6bd7a978f8e02e5d207d282d2e74b911b2ce4a4`

## 1. Audit 1

### A1 — PR vs PMR

La metodología Price Intelligence declara `PR ≠ PMR`.

**Depuración:** carrier PMR independiente; no se reutiliza `pr_value`.

### A2 — fórmula de PMR

No existe autoridad cerrada para derivar PMR.

**Depuración:** la Rule consume PMR ya producido por una fuente autorizada; no lo calcula.

### A3 — parámetros PRE

R-PRE-003 no dispone de dependencia PARAMETER confirmada.

**Depuración:** no se introduce P-PRE-* nuevo ni se reciclan P-PRE-004/005.

### A4 — moneda

Comparar importes de monedas distintas sería incorrecto.

**Depuración:** moneda exacta; sin FX.

### A5 — ausencia de PMR

No puede convertirse a cero/FALSE.

**Depuración:** estados no determinados → NOT_EVALUABLE.

### A6 — igualdad

La Matriz dice “igual o inferior”.

**Depuración:** operador `<=`.

### A7 — efecto

R3 es informativo.

**Depuración:** metadata fija R3/INFORMATIVA; sin escalada.

## 2. Contraste transversal

### Price Intelligence

No se modifica y se preserva `PR ≠ PMR`.

**PASS.**

### RDM / Matriz de Parámetros

No se inventa una dependencia de parámetro.

**PASS.**

### Evidence

Carrier + Evidence determinista.

**PASS.**

### CRC

No se modifica.

**PASS.**

## 3. Audit 2

La propuesta:

- no implementa la Rule;
- no calcula PMR;
- no convierte PR en PMR;
- no hardcodea valores;
- no introduce P-PRE-*;
- no aplica FX;
- no modifica R-PRE-001/002;
- no altera autoridad decisional humana.

**AUDIT 2: SUPERADA — 0 bloqueadores documentales.**

## 4. Dictamen

La propuesta es apta para decisión humana.

Hasta aprobación explícita:

```text
R-PRE-003 → BLOCKED
```

Una instrucción genérica de continuar no debe interpretarse como aprobación de esta semántica.
