# EIOS — R-DAT-001 Technical Contract v0.1

**Autoridad:** `01_Modelo/DAT001_Data_Freshness_Authority_v0.1.md`  
**Estado:** DISEÑO TÉCNICO PARA MATERIALIZACIÓN

## Frontera

```text
explicit snapshot metadata
        ↓
DataSnapshotFreshnessProducer
        ↓
DataSnapshotFreshnessObservation + Evidence
        ↓
evaluate_r_dat_001
        +
ResolvedConfiguration(P-DAT-001) + Evidence
```

El productor factual y el evaluador normativo permanecen separados.

## Invariantes

- no timestamp desde `data_snapshot_id`;
- no timestamp desde `Evidence.captured_at`;
- no timestamp desde `DecisionInputPackage.effective_at`;
- no reloj del sistema;
- no selección de snapshot;
- no default de 6 semanas;
- semana = 7 días;
- igualdad con cutoff → TRUE;
- fecha futura/ausente/contradictoria → NOT_EVALUABLE;
- R3 / INFORMATIVA;
- R-DAT-002 y R-DAT-003 fuera de alcance.
