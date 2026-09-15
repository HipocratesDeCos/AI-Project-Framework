# EIOS — Finance · RDM P-FIN-002 → R-FIN-003 Reconciliation — Design v0.1

**Estado:** DISEÑAR — PROPUESTA ACOTADA  
**Baseline:** `main @ 61d462271107cda7d3cf907057318f91f853ab43`  
**Ámbito:** dependencia de `P-FIN-002` respecto de `R-FIN-003`

## 1. Hallazgo de partida

`Rule_Dependency_Matrix.md` contiene `P-FIN-004 → R-FIN-003`, pero no representa la dependencia de `P-FIN-002` que ya está demostrada por la autoridad Finance vigente.

`FIN-AUTH-07` autoriza:

```text
treasury_minimum = P-FIN-002

financial_safety_margin_pct
= (financial_capacity_forecast - treasury_minimum)
/ treasury_minimum
× 100

financial_safety_margin_pct < P-FIN-004
→ evaluación ordinaria posterior por R-FIN-003
```

Por tanto `P-FIN-002` interviene en el indicador que consume `R-FIN-003`; no constituye el umbral directo de la regla.

## 2. Relación propuesta

```text
Dependency_ID: DEP-FIN-002-RFIN-003
Rule_ID: R-FIN-003
Dependency_Type: DERIVED
Source_ID: P-FIN-002
Source_Domain: PARAMETER
Function: treasury_minimum autorizado utilizado en el cálculo de financial_safety_margin_pct consumido por R-FIN-003
Criticality: PENDING
Evidence_Source: 01_Modelo/Finance_Basic_Authority_v0.1.md
Evidence_Status: CONFIRMED
Evaluability_Impact: PENDING
Fallback: NONE
Affected_Component: NONE
```

## 3. Justificación del tipo DERIVED

La relación no se clasifica como `PARAMETER` directa porque la condición ordinaria autorizada de `R-FIN-003` compara `financial_safety_margin_pct` con `P-FIN-004`.

`P-FIN-002` participa aguas arriba mediante una transformación explícitamente autorizada por `FIN-AUTH-07`.

## 4. Fronteras

Esta unidad no autoriza:

- cambiar el valor vigente de `P-FIN-002` o `P-FIN-004`;
- modificar la fórmula financiera autorizada;
- modificar la condición, efecto o severidad de `R-FIN-003`;
- autorizar la escalada `R1 → R0` de `R-FIN-003`;
- introducir una dependencia de `R-FIN-002`;
- canonizar todavía `FinanceBasicResultEvidence` como dependencia `EVIDENCE`;
- modificar código, tests, CRC, Finance Basic o C0.

## 5. Materialización prevista

Si las dos auditorías resultan limpias, se actualizará exclusivamente la documentación canónica necesaria para representar la relación ya autorizada.

No se inferirán `Criticality` ni `Evaluability_Impact`.
