# EIOS — CRC DAT003 vs R0 Precedence Technical Contract v0.1

**Autoridad:** `01_Modelo/CRC_DAT003_R0_Precedence_Authority_v0.1.md`  
**Estado:** DISEÑO TÉCNICO PARA MATERIALIZACIÓN

## 1. Activación

La precedencia especial se activa solo cuando existe:

```text
R-DAT-003 / EVALUABLE / TRUE
```

entre los candidatos del efecto dominante `R0`.

## 2. Resultado

Si los resultados dominantes son exactamente:

```text
INFORMACIÓN INSUFICIENTE
NO COMPRAR
```

y uno corresponde a `R-DAT-003 EVALUABLE/TRUE`:

```text
consolidated_result = INFORMACIÓN INSUFICIENTE
dominant_reason     = R-DAT-003.reason
```

## 3. Preservación de R0 concurrentes

Todo Assessment activo distinto de DAT003 se conserva en:

- `relevant_factors`;
- `conflicts`;
- `traceability.assessment_rule_ids`.

No se mutan Assessments.

## 4. DAT003 FALSE / NOT_EVALUABLE

No activan precedencia.

Si existe otro R0 evaluable/TRUE, conserva su resultado normal.

## 5. No ranking general

Si existe conflicto entre resultados del mismo efecto dominante y no satisface exactamente la excepción DAT003 autorizada, CRC mantiene fail-closed mediante error estructural.

## 6. No alcance

- no cambia evaluadores;
- no cambia metadata;
- no crea scoring;
- no crea ranking general R0;
- no transforma `INFORMACIÓN INSUFICIENTE` en decisión empresarial.
