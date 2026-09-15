# EIOS — Rotation · RDM Evidence Reconciliation — Design v0.1

**Estado:** DISEÑAR — PROPUESTA ACOTADA  
**Baseline:** `main @ fb93f85bd5906ec3a19de6878b56b4e383755aa8`  
**Ámbito:** `R-ROT-002` / Track A — Sales Activity Window

## 1. Objeto

Reconciliar en `04_Reglas/Rule_Dependency_Matrix.md` únicamente la dependencia `EVIDENCE` que ya está demostrada por el cierre metodológico de Rotation Track A.

No se pretende cerrar `ROT-G01` ni completar por inferencia dependencias `DATA` o `PARAMETER`.

## 2. Evidencia de autoridad

`01_Modelo/Rotation_Track_A_Methodological_Closure_v0.1.md` cierra la semántica factual de `SalesActivityWindowEvidence` y establece que Track A entrega soporte factual para evaluar la condición de `R-ROT-002`: “No existen ventas durante el periodo configurado”.

`01_Modelo/Rotation_Methodological_Audit_2_Final_v0.3.md` confirma:

- evidencia positiva de ausencia de ventas válidas;
- semántica de fuente explícita;
- completitud de ventana explícita;
- ventana autorizada obligatoria;
- Track A no produce Assessment ni decisión;
- los estados de Track A no sustituyen `Evidence` ni `EvidenceValidation`.

## 3. Relación canónica propuesta

```text
Dependency_ID: DEP-ROT-SAW-RROT-002
Rule_ID: R-ROT-002
Dependency_Type: EVIDENCE
Source_ID: SalesActivityWindowEvidence
Source_Domain: ROTATION / TRACK A METHODOLOGY
Function: Soporte factual para demostrar actividad o ausencia demostrada de ventas válidas en la ventana aplicable
Criticality: PENDING
Evidence_Source: 01_Modelo/Rotation_Track_A_Methodological_Closure_v0.1.md
Evidence_Status: CONFIRMED
Evaluability_Impact: PENDING
Fallback: NONE
Affected_Component: NONE
```

## 4. Límites

Esta reconciliación NO autoriza:

- crear un parámetro para el periodo de `R-ROT-002`;
- reutilizar `P-STK-006` u otro parámetro por similitud;
- declarar dependencias `DATA` no identificadas por autoridad suficiente;
- cerrar `ROT-G01`;
- declarar `ROT-G04-A` totalmente resuelto;
- implementar Rotation Track A;
- aplicar excepciones de `R-ROT-002`;
- producir `Assessment`, CRC o decisión.

## 5. Efecto esperado

`ROT-G04-A` queda **reducido**, no cerrado:

- EVIDENCE → canonizable ahora;
- DATA → pendiente;
- PARAMETER → pendiente por `ROT-G01`.

## 6. Criterio de éxito

La unidad es correcta si la RDM incorpora exactamente una relación `EVIDENCE` demostrada para `R-ROT-002`, sin alterar ninguna otra regla, dependencia, parámetro, estado de Track A ni autoridad empresarial.
