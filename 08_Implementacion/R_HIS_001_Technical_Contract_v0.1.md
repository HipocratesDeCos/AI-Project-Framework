# EIOS — R-HIS-001 Technical Contract v0.1

**Autoridad:** `01_Modelo/HIS001_Temporal_Reference_Authority_v0.1.md`  
**Estado:** DISEÑO TÉCNICO PARA MATERIALIZACIÓN

## Contratos

Carrier:
`HistoricalReferenceTemporalObservation`

Evidence:
`HistoricalReferenceTemporalEvidence`

Parámetro:
`ResolvedConfiguration(P-DAT-002) + ParameterConfigurationEvidence`

## Binding

El carrier conserva `decision_id`, `scenario_id`, `data_snapshot_id`, `company_scope`, `purchase_operation_ref`, `reference_id`, `reference_operation_date` y `evaluation_date`.

`purchase_operation_ref` es SHA-256 determinista de la `PurchaseOperation` completa.

## Evaluación

```text
cutoff = evaluation_date - N meses calendario, con clipping

reference_date < cutoff                       → EVALUABLE / TRUE
cutoff <= reference_date <= evaluation_date  → EVALUABLE / FALSE
reference_date > evaluation_date              → NOT_EVALUABLE
```

Estados distintos de `AVAILABLE`, Evidence inválida, parámetro ausente/no utilizable o provenance incompatible → `NOT_EVALUABLE`.

## Fronteras

- No reloj del sistema.
- No P-PRE-003.
- No TemporalStatus desacoplado.
- No PriceIntelligenceResult.
- No selección de referencia.
- No defaults.
- No escalada decisional.
