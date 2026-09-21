# EIOS — HIS001 Temporal Reference Authority v0.1

**Estado:** AUTORIZADO  
**Fecha:** 21/09/2026  
**Origen:** `HIS001_Temporal_Reference_Authority_Proposal_v0.1.md`

## Autoridad humana explícita

Se autoriza la semántica propuesta para `R-HIS-001`.

- Fecha base: `PurchaseOperation.operation_date`.
- Parámetro efectivo: `P-DAT-002`.
- `P-DAT-002` se consume mediante `ResolvedConfiguration + ParameterConfigurationEvidence`.
- Unidad: meses; valor entero positivo; sin hardcodear 12.
- Meses calendario con clipping al último día válido del mes destino.
- `reference_operation_date < cutoff_date → TRUE`.
- Igualdad con `cutoff_date → FALSE`.
- Referencia posterior a `evaluation_date` → `NOT_EVALUABLE`.
- Fecha ausente, contradictoria o no determinable → `NOT_EVALUABLE`.
- Evidence/provenance debe vincular la referencia temporal exacta a la `PurchaseOperation`.
- Metadata: `R3 / MEDIA`.
- No se reutiliza `P-PRE-003`, un `TemporalStatus` desacoplado ni `PriceIntelligenceResult`.

La autorización no valida el valor inicial de 12 meses como política empresarial definitiva y no autoriza selección automática de referencias, comparabilidad, representatividad, suficiencia, agregación o decisión empresarial automática.
