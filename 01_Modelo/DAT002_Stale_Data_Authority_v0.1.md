# EIOS — DAT002 Stale Data Authority v0.1

**Baseline de autorización:** `main @ 59845dff0000722a69eea36d20159cb826e04b19`  
**Fecha:** 21/09/2026  
**Estado:** AUTORIZADO  
**Ámbito:** `R-DAT-002 — Datos antiguos`  
**Origen:** `DAT002_Stale_Data_Authority_Proposal_v0.1.md`

## 1. Autoridad humana explícita

Se autoriza la semántica propuesta para `R-DAT-002`, incluida la nueva relación:

```text
P-DAT-001 → R-DAT-002
```

La autorización no valida el valor inicial de 6 semanas como política empresarial definitiva.

## 2. Carrier factual

`R-DAT-002` reutiliza exclusivamente:

`DataSnapshotFreshnessObservation + DataSnapshotFreshnessEvidence`

ya materializados para DAT001.

No se crea un segundo productor temporal ni un segundo timestamp canónico.

## 3. Parámetro autorizado

`P-DAT-001` se consume mediante:

```text
ResolvedConfiguration(P-DAT-001)
+
ParameterConfigurationEvidence
```

con las mismas invariantes de identidad, versión, company_scope, vigencia, unidad `semanas` y valor entero positivo.

No se hardcodea 6.

## 4. Fecha base y periodo

```text
evaluation_date = PurchaseOperation.operation_date
cutoff_date = evaluation_date - (P-DAT-001 × 7 días)
```

Una semana equivale a 7 días civiles.

## 5. Frontera autorizada

```text
source_updated_date < cutoff_date
    → EVALUABLE / TRUE

cutoff_date <= source_updated_date <= evaluation_date
    → EVALUABLE / FALSE

source_updated_date > evaluation_date
    → NOT_EVALUABLE
```

La igualdad con el límite no activa `R-DAT-002`.

## 6. Corrección autorizada — complementariedad estrictamente evaluable

DAT001 y DAT002 pueden considerarse complementarias solo cuando:

- consumen la misma `DataSnapshotFreshnessObservation`;
- consumen la misma resolución de `P-DAT-001`;
- Evidence y provenance son válidos;
- `state == AVAILABLE`;
- `source_updated_date <= evaluation_date`;
- ambas reglas resultan `EVALUABLE`.

En ese dominio:

```text
R-DAT-001 TRUE  ↔ R-DAT-002 FALSE
R-DAT-001 FALSE ↔ R-DAT-002 TRUE
```

Fuera de ese dominio no se autoriza inferencia cruzada.

En particular:

```text
NOT_EVALUABLE en una regla
≠
TRUE/FALSE inferido en la otra
```

Cada evaluador debe fallar cerrado por sus propias validaciones.

## 7. Ausencia, contradicción y futuro

```text
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

→ `NOT_EVALUABLE`.

Fecha futura → `NOT_EVALUABLE`.

Evidence GAP/INVALID → `NOT_EVALUABLE`.

Binding incompatible → error estructural.

Parámetro ausente/no utilizable → `NOT_EVALUABLE`.

## 8. Metadata

```text
R-DAT-002 → R3 / MEDIA
```

TRUE significa únicamente que el snapshot supera el periodo máximo autorizado.

FALSE significa únicamente que no se demuestra esa condición.

## 9. Separación de capacidades

No se autoriza:

- convertir `R-DAT-002 TRUE` en `QTG NO_APTO`;
- materializar `R-DAT-003`;
- sustituir snapshot;
- seleccionar otra fuente;
- crear fallback temporal;
- decisión empresarial automática.

`dato antiguo ≠ dato insuficiente`.

## 10. Gates cerrados

```text
DAT002-G01 → CERRADO
DAT002-G02 → CERRADO
DAT002-G03 → CERRADO
DAT002-G04 → CERRADO
DAT002-G05 → CERRADO
```

## 11. Estado

**DAT002 Stale Data Authority v0.1 — AUTORIZADO.**
