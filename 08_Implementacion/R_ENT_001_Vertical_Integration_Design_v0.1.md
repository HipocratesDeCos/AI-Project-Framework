# EIOS — R-ENT-001 · Vertical Integration Design v0.1

**Estado:** DISEÑADO — PENDIENTE DE AUDIT 1  
**Fecha:** 11/09/2026  
**Baseline:** `main @ 6210e42fd251c55fb52701eb9619405385056473`

---

## 1. Propósito

Demostrar ejecutablemente que la cadena ya materializada para `R-ENT-001` puede atravesar los contratos existentes sin crear un nuevo motor ni ampliar autoridad:

```text
ENT factual analyzer
→ R-ENT-001 Rules bridge
→ Assessment
→ C0 Trace
→ C0 capability adapter
→ CRC-MVP
```

La unidad es inicialmente **test-only**. No se autoriza código productivo nuevo salvo que Audit 1 demuestre una ausencia objetiva.

---

## 2. Componentes existentes reutilizados

```text
eios.delivery.analyze_delivery_stockout
eios.rules.delivery.evaluate_r_ent_001
eios.core.c0_reproducibility.build_trace
eios.core.capability_adapters.adapt_c0
eios.core.crc_mvp.resolve_crc
```

No se reimplementará ninguna de estas responsabilidades.

---

## 3. Metadatos normativos de integración

Para `R-ENT-001`, la autoridad de la Matriz de Reglas establece:

```text
effect = R2
severity = ALTA
```

La prueba utilizará exclusivamente un fixture runtime:

```text
RuleMetadata(
    rule_id="R-ENT-001",
    version=context.rules_version,
    effect="R2",
    severity="ALTA",
)
```

Esto **no crea un registry global** ni una nueva fuente de autoridad. El fixture materializa en el test los metadatos ya autorizados para comprobar CRC.

---

## 4. Base result CRC

La unidad no define ni infiere `base_result`.

Cada test lo suministra de forma explícita como entrada de `CRCInput`.

Un fixture puede usar `COMPRAR` para demostrar que:

```text
R-ENT-001 TRUE + R2 → NEGOCIAR
R-ENT-001 FALSE      → conserva base_result
NOT_EVALUABLE        → INFORMACIÓN INSUFICIENTE
```

El valor usado en el test no se convierte en default productivo.

---

## 5. Trace

Tras obtener `Assessment`, se construirá:

```text
trace = build_trace(
    context,
    purchase,
    rule,
    tuple(assessment.evidence_ids),
    assessment,
)
```

Se verificará:

- `decision_id`;
- `scenario_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`;
- `rule_id`;
- `assessment_status`;
- `assessment_outcome`;
- `evidence_ids`;
- determinismo de `trace_id` para el mismo material.

`created_at` no se usa como componente de identidad determinista.

---

## 6. Capability adapter

Se reutiliza:

```text
adapt_c0((assessment,), (trace,))
```

Resultados esperados:

```text
Assessment EVALUABLE
→ capability C0 COMPLETED / result_available=True

Assessment NOT_EVALUABLE
→ capability C0 NOT_EVALUABLE / result_available=False
```

No se crea adapter ENT adicional porque `R-ENT-001` ya ha sido convertido al contrato C0 `Assessment`.

---

## 7. CRC

CRC recibe el `Assessment` original, no el `CapabilityExecution`.

Se preserva la separación:

```text
CapabilityExecution = estado operacional de una capacidad
Assessment          = resultado individual de regla
CRC                  = consolidación normativa de Assessment
```

La unidad no intenta reconstruir `Assessment` desde `ExecutionOutcome`.

---

## 8. Casos obligatorios

1. late + evidencia válida:
   - `Assessment EVALUABLE/TRUE`;
   - Trace coherente;
   - `adapt_c0 → COMPLETED`;
   - CRC con R2/ALTA → `NEGOCIAR`.

2. not-late + evidencia válida:
   - `Assessment EVALUABLE/FALSE`;
   - Trace coherente;
   - `adapt_c0 → COMPLETED`;
   - CRC conserva `base_result` explícito.

3. ENT no evaluable:
   - `Assessment NOT_EVALUABLE/None`;
   - Trace conserva `NOT_EVALUABLE`;
   - `adapt_c0 → NOT_EVALUABLE`;
   - CRC → `INFORMACIÓN INSUFICIENTE`.

4. trace reproducible:
   - mismas entradas materiales → mismo `trace_id`.

5. metadata de versión incompatible:
   - CRC rechaza con error de integridad.

6. metadata R2/ALTA no se copia al Assessment.

7. ningún objeto origen es mutado por la composición.

---

## 9. Exclusiones

Esta unidad no autoriza:

- nuevo Rule Registry;
- nuevo motor de reglas;
- nuevo adapter ENT;
- modificación de C0;
- modificación de CRC;
- modificación de Execution Boundary;
- definición de `base_result` productivo;
- persistencia;
- recomendación automática ejecutable;
- decisión empresarial.

---

## 10. Alcance físico previsto

Si Audit 1 y Audit 2 son limpios:

```text
tests/test_r_ent_001_vertical_integration.py
```

No se prevé cambio productivo.

---

## 11. Estado

**DISEÑO v0.1 COMPLETADO.**  
**Implementación productiva nueva:** NO prevista.  
**Pendiente:** AUDIT 1.
