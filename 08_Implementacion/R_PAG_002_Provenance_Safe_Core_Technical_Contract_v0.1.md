# EIOS — R-PAG-002 Provenance-Safe Core Technical Contract v0.1

**Baseline:** `main @ 26232c98e78d0052243c8f82c0f1d390f8f8c224`  
**Fecha:** 22/09/2026  
**Estado:** MATERIALIZADO — CI PENDIENTE

## 1. Autoridad

- `PAG002_Financial_Viability_Counterfactual_Authority_v0.1`
- `PAG002_Counterfactual_Due_Date_Authority_v0.1`

## 2. Resultado activo

```text
R-PAG-002
effect = R1
severity = ALTA
active_result = COMPRAR CONDICIONADO
```

## 3. Ensamblaje provenance-safe

El core no acepta estados de plazo ni escenarios contrafactuales desprendidos.

Reconstruye dentro de la misma invocación:

```text
P-PAG-004 + Evidence
→ PaymentTermControlResolution

SupplierEvidenceResult + PaymentTermSemanticAuthority
→ OfferedPaymentTermObservation

P-PAG-001 + Evidence
→ MinimumPaymentTermResolution

ProvenancedFinanceBasicExecution + FinanceBasicResultEvidence + P-FIN-002 + Evidence
→ baseline PAG002FinancialStateResolution

DocumentaryPaymentCapture + baseline Finance + term sources
→ CounterfactualPaymentSchedule

CounterfactualPaymentSchedule
→ O2 ScenarioVersion
→ PAG002CounterfactualFinanceExecution

PAG002CounterfactualFinanceExecution + P-FIN-002
→ scenario PAG002FinancialStateResolution
```

## 4. Orden autorizado

```text
P-PAG-004 DISABLED/invalid
→ NOT_EVALUABLE

offered/minimum unavailable
→ NOT_EVALUABLE

offered >= P-PAG-001
→ FALSE

baseline financial state NOT_DETERMINABLE
→ NOT_EVALUABLE

baseline financial state VIABLE
→ FALSE

baseline financial state NON_VIABLE
→ construir minimum-term scenario

scenario unavailable / non-determinable
→ NOT_EVALUABLE

scenario VIABLE
→ TRUE

scenario NON_VIABLE
→ FALSE
```

## 5. Cambio único

La ejecución scenario-only conserva toda entrada material salvo la due_date autorizada del único PAYMENT vinculado.

## 6. Multicuota

```text
NOT_EVALUABLE
```

No hay promedio, reparto ni consolidación.

## 7. P-PAG-005

No es dependencia del core.

## 8. Metadata/CRC

`TRUE` activa `COMPRAR CONDICIONADO` mediante metadata de catálogo.

No se modifica CRC.
