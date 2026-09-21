# EIOS — DAT002 Stale Data Authority Proposal v0.1

**Baseline:** `main @ 59845dff0000722a69eea36d20159cb826e04b19`  
**Fecha:** 21/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** `R-DAT-002 — Datos antiguos`

## 1. Propósito

Definir la semántica mínima para determinar si el snapshot de datos seleccionado supera el periodo máximo permitido de antigüedad y, en tal caso, activar la regla informativa correspondiente.

Esta propuesta no modifica `R-DAT-001`, no materializa `R-DAT-003` y no sustituye Quality & Trust Gate.

## 2. Autoridad vigente y gap

`04_Reglas/Matriz_Reglas_MVP.md` define:

> La fecha de actualización supera el periodo establecido.

Resultado:

> Mostrar advertencia.

Metadata vigente:

```text
R-DAT-002 → R3 / MEDIA
```

La matriz de parámetros y la RDM vigentes solo confirman actualmente:

```text
P-DAT-001 → R-DAT-001
```

No existe una relación autorizada `P-DAT-001 → R-DAT-002`.

Por tanto, esta propuesta SOMETE A AUTORIDAD HUMANA una nueva relación directa:

```text
P-DAT-001 → R-DAT-002
```

La relación no debe registrarse como CONFIRMED antes de aprobación explícita.

## 3. Reutilización factual autorizada propuesta

DAT001 ya materializa un carrier factual provenance-safe:

`DataSnapshotFreshnessObservation + DataSnapshotFreshnessEvidence`

DAT002 propone reutilizar exactamente ese carrier porque representa el mismo hecho factual:

- snapshot exacto;
- fecha canónica explícita de actualización;
- operación/contexto exactos;
- provenance demostrable.

No se propone un segundo productor temporal ni un segundo timestamp canónico.

## 4. Separación entre hecho y regla

`DataSnapshotFreshnessProducer` continúa siendo factual.

No conoce R-DAT-001 ni R-DAT-002.

DAT002 consume la observación ya construida; no fabrica fechas, no selecciona snapshots y no corrige metadata.

## 5. Parámetro propuesto

Se propone que `R-DAT-002` consuma:

```text
ResolvedConfiguration(P-DAT-001)
+
ParameterConfigurationEvidence
```

con las mismas invariantes ya autorizadas para DAT001:

- `parameter_id == P-DAT-001`;
- unidad `semanas`;
- valor entero positivo;
- `parameters_version` coincidente;
- `company_scope` coincidente;
- vigencia aplicable a `evaluation_date`;
- Evidence ligada a la configuración exacta.

No se hardcodea 6 semanas.

## 6. Fecha base y semántica temporal

Se propone mantener:

```text
evaluation_date = PurchaseOperation.operation_date
```

Una semana = 7 días civiles.

```text
cutoff_date = evaluation_date - (P-DAT-001 × 7 días)
```

Rules opera sobre `date`.

## 7. Frontera propuesta

R-DAT-002 expresa que la fecha de actualización **supera** el periodo permitido.

Por tanto:

```text
source_updated_date < cutoff_date
    → EVALUABLE / TRUE

cutoff_date <= source_updated_date <= evaluation_date
    → EVALUABLE / FALSE

source_updated_date > evaluation_date
    → NOT_EVALUABLE
```

La igualdad exacta con el cutoff NO activa R-DAT-002.

## 8. Relación con DAT001

Bajo esta propuesta, para material completamente evaluable y la misma configuración:

```text
R-DAT-001 == TRUE  ↔  R-DAT-002 == FALSE
R-DAT-001 == FALSE ↔  R-DAT-002 == TRUE
```

Esta complementariedad solo aplica cuando:

- ambos evaluadores consumen el mismo carrier;
- ambos consumen la misma resolución de P-DAT-001;
- la fecha no es futura;
- Evidence y provenance son válidos;
- el estado factual es AVAILABLE.

No se aplica a `NOT_EVALUABLE`.

`NOT_EVALUABLE` no se convierte en TRUE/FALSE para forzar complementariedad.

## 9. Estados no evaluables

```text
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

→ `NOT_EVALUABLE`.

Fecha futura → `NOT_EVALUABLE`.

Evidence GAP/INVALID → `NOT_EVALUABLE`.

Binding estructural incompatible → error estructural.

Parámetro ausente o no utilizable → `NOT_EVALUABLE`.

## 10. Resultado funcional

TRUE significa exclusivamente:

> el snapshot evaluado supera el periodo máximo permitido.

FALSE significa exclusivamente:

> no se demuestra que supere ese periodo.

La regla puede aportar una advertencia informativa conforme a su definición funcional, pero no produce por sí sola:

- `NO_APTO`;
- bloqueo;
- `INFORMACIÓN INSUFICIENTE`;
- sustitución de snapshot;
- selección de fuente alternativa;
- decisión empresarial automática.

## 11. Metadata

```text
R-DAT-002 → R3 / MEDIA
```

No se autoriza escalada de efecto por inferencia.

## 12. Separación respecto a QTG

QTG puede considerar temporalidad como dimensión de calidad global.

DAT002 no produce `QualityTrustResult`.

No se autoriza convertir automáticamente:

```text
R-DAT-002 TRUE → QTG NO_APTO
```

ni ninguna otra combinación.

Cualquier impacto sobre QTG requiere autoridad específica.

## 13. Separación respecto a R-DAT-003

R-DAT-003 sigue fuera de alcance.

```text
dato antiguo ≠ dato insuficiente
```

Una observación puede ser antigua y aun así existir.

La suficiencia requiere política independiente.

## 14. No-alcance

Esta propuesta no autoriza:

- R-DAT-003;
- QTG operacional;
- thresholds nuevos;
- parámetros nuevos;
- defaults;
- timestamp implícito;
- selección automática de snapshot;
- reglas de sustitución o fallback;
- decisión empresarial automática.

## 15. Gates propuestos

Si recibe autorización explícita:

```text
DAT002-G01 → carrier factual reutilizable CONFIRMADO
DAT002-G02 → P-DAT-001 → R-DAT-002 AUTORIZADO
DAT002-G03 → frontera temporal CERRADA
DAT002-G04 → fail-closed CERRADO
DAT002-G05 → separación QTG/R-DAT-003 CERRADA
```

## 16. Estado

**DAT002 Stale Data Authority v0.1 — PROPUESTA / NO AUTORIZADA.**

Una instrucción genérica como “continúa” no autoriza la nueva relación `P-DAT-001 → R-DAT-002`.
