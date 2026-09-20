# EIOS — R-FIN-002 Materialization Audit v0.1

**Estado:** MATERIALIZADO — PENDIENTE CI

## 1. Superficie física

Se materializan:

- `eios/finance/post_operation.py`;
- exports de `eios/finance/__init__.py`;
- bridge `evaluate_r_fin_002`;
- catálogo R0/CRÍTICA;
- `FinanceWorkingCapitalRuleInputs`;
- integración en `run_domain_rules`;
- tests dedicados;
- reconciliación de tests históricos de catálogo/orquestador.

No se modifica Finance Basic engine, Finance provenance, CRC, MED ni SQL.

## 2. Audit 1 de implementación

### I1 — Carrier separado de Finance Basic

`PostOperationWorkingCapitalPosition` es una frontera factual independiente.

**PASS.**

### I2 — Purchase provenance

La posición porta SHA-256 canónico de la `PurchaseOperation` completa.

**PASS.**

### I3 — Evidence provenance

Evidence DEMONSTRATED debe referenciar el hash exacto del carrier.

**PASS.**

### I4 — Datos incompletos

Activo o pasivo ausente no se convierte a cero.

Resultado: `NOT_EVALUABLE`.

**PASS.**

### I5 — Parámetro

P-FIN-003 exige:

- ID exacto;
- version;
- company;
- fecha;
- vigencia;
- unidad monetaria;
- Evidence ligada a configuration_ref;
- Decimal finito.

**PASS.**

### I6 — Fórmula

```text
working_capital_after_operation
= assets_after - liabilities_after
```

```text
triggered = working_capital_after_operation < P-FIN-003
```

Igualdad → FALSE.

**PASS.**

### I7 — Metadata

`R-FIN-002 → R0 / CRÍTICA`.

No existe downgrade ni switch.

**PASS.**

### I8 — Orquestador

Bundle dedicado:

`FinanceWorkingCapitalRuleInputs`.

Ausente → omitted.

**PASS.**

### I9 — Separación decisional

El bridge produce Assessment; CRC conserva consolidación.

**PASS.**

### I10 — No-alcance

No hay:

- asientos;
- efecto contable inferido;
- FX;
- defaults;
- financiación;
- cambios R-FIN-001/003;
- cambios Finance Basic.

**PASS.**

## 3. Tests dedicados

Se cubren:

- TRUE bajo umbral;
- FALSE en igualdad/superior;
- thresholds y working capital negativos;
- magnitudes ausentes;
- Evidence GAP;
- refs forjadas;
- mismatch de identidad;
- P-FIN-003 ausente;
- ID/version/company/date incorrectos;
- configuración no vigente;
- unidad incompatible;
- alias € solo para EUR;
- threshold no numérico/no finito;
- parameter Evidence GAP/ref forjada;
- metadata;
- orquestación;
- omisión;
- inmutabilidad/trace uniqueness.

## 4. Audit 2 físico

No se observa ninguna ampliación de autoridad fuera de FIN002 v0.1.

**AUDIT 2 FÍSICO: SUPERADA — 0 bloqueadores observados antes de CI.**

## 5. Gate

Cierre condicionado a:

1. CI exact-head;
2. suite completa;
3. SQL SUCCESS;
4. depuración de cualquier regresión legítima;
5. merge protegido por SHA.
