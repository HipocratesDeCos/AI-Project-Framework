# EIOS — Finance · RDM P-FIN-002 → R-FIN-003 Reconciliation — Depuration v0.1

**Estado:** DEPURAR — COMPLETADA  
**Origen:** Audit 1 v0.1

## 1. Ajuste aplicado

Se incorpora al alcance documental de materialización la reconciliación de `02_Parametros/Matriz_Parametros_Reglas_MVP.md` como vista especializada parámetro ↔ regla.

La relación se representará como:

```text
P-FIN-002 → R-FIN-003
Tipo especializado: derivada
```

En la RDM permanecerá:

```text
Dependency_Type = DERIVED
Evidence_Source = 01_Modelo/Finance_Basic_Authority_v0.1.md
Evidence_Status = CONFIRMED
Criticality = PENDING
Evaluability_Impact = PENDING
Fallback = NONE
Affected_Component = NONE
```

## 2. Razón

`P-FIN-002` define `treasury_minimum`, que forma parte del cálculo autorizado de `financial_safety_margin_pct`; `R-FIN-003` compara posteriormente ese indicador con `P-FIN-004`.

La reconciliación documental no convierte `P-FIN-002` en el umbral directo de la regla.

## 3. No cambios

No se modifican:

- Catálogo de Parámetros;
- valores de configuración;
- Matriz de Reglas;
- FIN-AUTH-v0.1;
- código o tests;
- C0, CRC o Finance Basic;
- escalada R1→R0;
- dependencias `EVIDENCE` todavía no demostradas documentalmente.

**Alcance ampliado por política:** 0.  
**Autoridad nueva inventada:** 0.
