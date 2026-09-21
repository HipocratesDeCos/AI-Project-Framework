# EIOS — R-DAT-003 Technical Contract v0.1

**Autoridad:** `01_Modelo/DAT003_Insufficient_Data_Authority_v0.1.md`  
**Estado:** DISEÑO TÉCNICO PARA MATERIALIZACIÓN

## 1. Componentes

Se materializan:

- `DecisionEvidenceRequirementSet`;
- `RequirementEvidenceBinding`;
- `DecisionEvidenceSufficiencyObservation`;
- `DecisionEvidenceSufficiencyProducer`;
- `evaluate_r_dat_003`.

No se materializa un productor operacional universal de RequirementSet.

## 2. Clasificación factual

Cada requirement se clasifica explícitamente como:

```text
SATISFIED
FAILED
UNDETERMINED
```

`FAILED` exige Evidence demostrada y `classification_ref` explícita.

`GAP` no puede producir `FAILED`.

`GAP → UNDETERMINED`.

## 3. Evaluador

```text
failed != ∅ OR undetermined != ∅ → TRUE
todos satisfechos                → FALSE
carrier no AVAILABLE             → NOT_EVALUABLE
```

## 4. Resultado CRC

La Matriz de Reglas autoriza:

```text
R-DAT-003 TRUE → INFORMACIÓN INSUFICIENTE
```

Por ello el catálogo incorpora un `active_result` explícito para DAT003.

Las reglas existentes sin resultado explícito conservan el mapeo normal por efecto.

## 5. Conflicto R0 no resuelto

La autoridad vigente no define precedencia entre:

```text
R-DAT-003 TRUE → INFORMACIÓN INSUFICIENTE
otro R0 TRUE   → NO COMPRAR
```

La CRC falla cerrada ante resultados distintos con el mismo efecto dominante.

No se decide el empate por orden de ejecución.

## 6. Parámetros

DAT003 v0.1 no consume `P-DAT-003` ni `P-DAT-007`.

## 7. No alcance

- QTG;
- productor operacional universal de RequirementSet;
- política de precedencia DAT003 vs otros R0;
- parámetros DAT003;
- imputación o reparación de Evidence.
