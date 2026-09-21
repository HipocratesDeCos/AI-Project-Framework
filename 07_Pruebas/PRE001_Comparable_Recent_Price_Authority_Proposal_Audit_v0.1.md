# EIOS — PRE001 Comparable Recent Price Authority Proposal Audit v0.1

**Baseline:** `main @ 2bb9eac45c69908122abc6468fab93ddb5314498`

## 1. Audit 1

### A1 — PR agregado vs referencia individual

R-PRE-001 habla de “una operación comparable reciente”, no de PR agregado.

**Depuración:** carrier individual separado; no se usa `pr_value`.

### A2 — selección de referencia

“Última compra” o “mejor referencia” no están autorizadas.

**Depuración:** la Rule recibe una única referencia ya seleccionada upstream.

### A3 — P-PRE-001 en meses

La metodología temporal C1 no define aritmética calendaria.

**Depuración:** se propone resta de meses calendario con clipping fin de mes y frontera inclusiva.

### A4 — P-PRE-004

El catálogo confirma unidad % pero no fija fórmula ejecutable.

**Depuración:** se propone uplift relativo sobre reference_price.

### A5 — igualdad del umbral

La redacción “supera ... en el porcentaje configurado” es ambigua.

**Depuración:** se propone `uplift_pct >= threshold`, coherente con “diferencia para activar alerta”, sometido a autorización humana.

### A6 — reference_price cero

División imposible.

**Depuración:** reference_price debe ser > 0; en otro caso NOT_EVALUABLE.

### A7 — referencia no reciente

No debe fabricarse alerta.

**Depuración:** comparable pero fuera del horizonte → EVALUABLE/FALSE.

### A8 — comparabilidad no demostrada

No equivale a FALSE.

**Depuración:** estado distinto de COMPARABLE → NOT_EVALUABLE.

### A9 — defaults

3 meses y 5% siguen pendientes de validación.

**Depuración:** solo ResolvedConfiguration + Evidence.

### A10 — metadata

Se conserva R2/ALTA, sin escalada.

**PASS.**

## 2. Contraste transversal

- Matriz de Reglas: condición preservada.
- Matriz de Parámetros: P-PRE-001 y P-PRE-004 confirmados.
- GAP-PI-TEMP-01: P-PRE-001 gobierna “reciente”.
- Price Temporal Matrix: no se altera C1 ni se introduce ponderación.
- Price Intelligence: no se usa PR como referencia individual.
- CRC: sin cambios.

## 3. Audit 2

La propuesta:

- no implementa la Rule;
- no fija 3 meses;
- no fija 5%;
- no selecciona automáticamente referencias;
- no usa PR agregado;
- no aplica FX;
- no introduce ponderación;
- no modifica R-PRE-002/003;
- no altera decisión humana final.

**AUDIT 2: SUPERADA — 0 bloqueadores documentales.**

## 4. Dictamen

La propuesta es apta para decisión humana.

Hasta aprobación explícita:

```text
R-PRE-001 → BLOCKED
```

Una instrucción genérica de continuar no equivale a autorización de esta semántica.
