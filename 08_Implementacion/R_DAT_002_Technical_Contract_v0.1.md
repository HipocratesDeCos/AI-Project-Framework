# EIOS — R-DAT-002 Technical Contract v0.1

**Autoridad:** `01_Modelo/DAT002_Stale_Data_Authority_v0.1.md`  
**Estado:** DISEÑO TÉCNICO PARA MATERIALIZACIÓN

## Ejecución

R-DAT-002 reutiliza el mismo bundle factual de DAT001:

```text
DataSnapshotFreshnessObservation
+ DataSnapshotFreshnessEvidence
+ ResolvedConfiguration(P-DAT-001)
+ ParameterConfigurationEvidence
```

El orquestador ejecuta DAT001 y DAT002 sobre ese mismo bundle. No existe un segundo productor ni una segunda resolución del parámetro.

## Frontera

```text
updated < cutoff                  → TRUE
cutoff <= updated <= evaluation  → FALSE
updated > evaluation             → NOT_EVALUABLE
```

## Complementariedad

Solo se exige oposición TRUE/FALSE cuando ambos resultados son EVALUABLE sobre exactamente el mismo material.

Nunca se deriva un outcome desde el resultado de la otra regla.

## No alcance

- R-DAT-003;
- QualityTrustResult;
- bloqueo;
- fallback de snapshot;
- default 6 semanas.
