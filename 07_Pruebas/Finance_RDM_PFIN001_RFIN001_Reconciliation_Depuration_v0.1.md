# EIOS — Finance · RDM P-FIN-001 → R-FIN-001 Reconciliation — Depuration v0.1

**Estado:** DEPURAR — COMPLETADA  
**Origen:** Audit 1 v0.1  
**Hallazgos incorporados:** A1-01

## 1. Relación depurada

La relación a materializar queda fijada como:

```text
Dependency_ID: DEP-FIN-001-RFIN-001
Rule_ID: R-FIN-001
Dependency_Type: DERIVED
Source_ID: P-FIN-001
Source_Domain: PARAMETER
Function: Horizonte autorizado que acota la proyección financiera de la que deriva financial_capacity_forecast consumida por R-FIN-001
Criticality: PENDING
Evidence_Source: 01_Modelo/Finance_Basic_Authority_v0.1.md
Evidence_Status: CONFIRMED
Evaluability_Impact: PENDING
Fallback: NONE
Affected_Component: NONE
Notes: FIN-AUTH-01 documenta la cadena P-FIN-001 → horizonte Finance Basic → financial_capacity_forecast → R-FIN-001 y prohíbe tratar P-FIN-001 como parámetro directo. El contrato técnico declara horizon_days como valor ya resuelto de P-FIN-001. FIN-PROV-HORIZON-01 permanece abierto: esta arista no acredita por sí sola el binding físico de horizon_days a una ResolvedConfiguration/configuration_ref concreta.
```

## 2. FIN-PROV-HORIZON-01

Se formaliza como deuda separada:

> **FIN-PROV-HORIZON-01 — El runtime actual transporta `FinanceBasicInput.horizon_days` como valor numérico pre-resuelto, pero no incorpora ni verifica dentro de esa frontera una identidad individual de `P-FIN-001` ni una `configuration_ref`/resolución equivalente que demuestre el origen del valor.**

Consecuencias:

- la relación funcional/documental puede quedar `DERIVED / CONFIRMED`;
- la RDM no debe describir el binding físico como provenance-safe;
- `DecisionContext.parameters_version` no basta por sí solo para demostrar qué valor individual de `P-FIN-001` originó `horizon_days`;
- resolver este gap requerirá una unidad técnica separada con su propio ciclo EIOS;
- esta reconciliación no modifica el runtime.

## 3. Vista especializada depurada

`02_Parametros/Matriz_Parametros_Reglas_MVP.md` deberá representar `P-FIN-001` como:

```text
R-FIN-001 — relación derivada mediante horizonte Finance Basic → financial_capacity_forecast
```

Estado:

```text
CONFIRMADO — relación derivada / FIN-AUTH-01
```

No debe utilizar la expresión “parámetro directo de R-FIN-001”.

## 4. Fronteras finales

Permanecen fuera de alcance:

- valores vigentes o iniciales de `P-FIN-001`;
- código y tests;
- resolución de `FIN-PROV-HORIZON-01`;
- fórmula de proyección o de capacidad financiera;
- `P-FIN-002` y demás dependencias ya cerradas;
- nueva semántica de Rules/CRC;
- dependencias `DATA`, `EVIDENCE` o `COMPONENT` no demostradas;
- `Criticality` y `Evaluability_Impact` no autorizados.

## 5. Resultado de depuración

La unidad queda preparada para Audit 2 con una separación explícita entre:

```text
relación documental confirmada
        ≠
binding runtime provenance-safe
```

No se introduce autoridad funcional nueva.