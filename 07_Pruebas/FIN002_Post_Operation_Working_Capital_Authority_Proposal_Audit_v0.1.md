# EIOS — FIN002 Post-Operation Working Capital Authority Proposal Audit v0.1

**Baseline:** `main @ d2d28c2bfff095d96387dcebc082f4b53025be9e`  
**Objeto:** auditar la propuesta de autoridad previa a cualquier aprobación humana.

## 1. Audit 1

### A1 — riesgo de reutilizar working capital actual

El nombre `working_capital` podría llevar a reutilizar el resultado Finance Basic corriente.

**Depuración:** se declara expresamente que no prueba semántica post-operación.

### A2 — riesgo de que EIOS derive el asiento de compra

Restar el importe de compra o añadir existencias sería una política contable no autorizada.

**Depuración:** v0.1 exige magnitudes post-operación suministradas/evidenciadas externamente.

### A3 — riesgo de aceptar una cifra final sin fórmula

FIN-AUTH-04 autoriza `current_assets - current_liabilities`.

**Depuración:** el productor debe suministrar/demostrar ambas magnitudes; EIOS aplica solo la resta autorizada.

### A4 — riesgo temporal

“Después de la operación” podría interpretarse como cualquier fecha futura.

**Depuración:** el productor declara el corte y lo vincula explícitamente a la misma evaluación/escenario.

### A5 — riesgo de defaults P-FIN-003

El catálogo contiene valores/configuración, pero una rule no debe hardcodearlos.

**Depuración:** `ResolvedConfiguration + ParameterConfigurationEvidence` obligatorio.

### A6 — riesgo de convertir ausencia en FALSE

**Depuración:** ausencia/conflicto/incompatibilidad → `NOT_EVALUABLE`.

### A7 — riesgo de desactivar R0

“Bloqueo configurable” podría convertirse en switch ordinario.

**Depuración:** la propuesta conserva R0/CRÍTICA y no autoriza desactivación/excepción.

## 2. Contraste transversal

### Finance Basic

La propuesta no modifica sus fórmulas ni contratos.

**PASS.**

### RDM / Matriz de Parámetros

`P-FIN-003 → R-FIN-002` ya está confirmado.

**PASS.**

### Matriz de Reglas

Condición y metadata permanecen coherentes.

**PASS.**

### CRC

No se modifica.

**PASS.**

### Provenance

Se exige binding explícito a operación/escenario/snapshot/fuente.

**PASS.**

## 3. Audit 2

La propuesta:

- no escribe código;
- no crea datos post-operación;
- no asume asientos;
- no valida valores empresariales;
- no cambia Finance Basic;
- no habilita excepciones;
- no usa material sintético como operacional;
- no altera decisión humana final.

**AUDIT 2: SUPERADA — 0 bloqueadores documentales.**

## 4. Dictamen

La propuesta es apta para decisión humana.

Hasta aprobación explícita:

```text
R-FIN-002 → BLOCKED
```

Una instrucción genérica de continuar no debe interpretarse como aprobación de esta política contable.
