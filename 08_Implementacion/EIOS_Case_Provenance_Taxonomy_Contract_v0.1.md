# EIOS — Case Provenance Taxonomy Contract v0.1

**Baseline:** `main @ 5ab59780d861b6e04d08db3a7039c6851acf777e`  
**Fecha:** 23/09/2026  
**Estado:** DISEÑADO → AUDITADO → MATERIALIZADO EN RAMA / CI PENDIENTE

## 1. Propósito

Separar tres finalidades de caso sin mezclar procedencia, naturaleza documental,
modo de ejecución QTG ni autoridad:

1. `SYNTHETIC_TEST`;
2. `REFERENCE_OPERATIONAL_SIMULATION`;
3. `PRESENTED_OPERATIONAL`.

La taxonomía clasifica artefactos ya construidos. No autentica documentos, no
cambia su naturaleza, no ejecuta QTG, no crea Evidence y no concede autoridad.

## 2. Regla arquitectónica principal

`case_kind` y `execution_mode` son dimensiones diferentes.

`REFERENCE_OPERATIONAL_SIMULATION` **no** es un tercer modo QTG.

El productor QTG conserva exclusivamente:

- `SYNTHETIC_TEST`;
- `OPERATIONAL`.

La nueva taxonomía se sitúa por encima de esa frontera.

## 3. Semántica canónica

| Case kind | Fuente canónica | Naturaleza material | Modo QTG aplicable | Ruta operacional | Efecto por clasificación | Finalidad |
|---|---|---|---|---|---|---|
| `SYNTHETIC_TEST` | `ProjectionMockDataset` | `SYNTHETIC` | `SYNTHETIC_TEST` | `FORBIDDEN` | `NO_OPERATIONAL_EFFECT` | prueba técnica |
| `REFERENCE_OPERATIONAL_SIMULATION` | `ProjectionOnlySyntheticMaterialBundle` | `SYNTHETIC` | `SYNTHETIC_TEST` | `FORBIDDEN` | `NO_OPERATIONAL_EFFECT` | validación E2E de producto |
| `PRESENTED_OPERATIONAL` | `OperationalExpedientIntakeManifest` | `PRESENTED_OPERATIONAL` | `OPERATIONAL` solo tras admisión | `REQUIRES_ADMISSION` | `NOT_GRANTED_BY_CLASSIFICATION` | caso presentado por empresa |

## 4. SYNTHETIC_TEST

Representa material fabricado para validar una propiedad técnica.

No pretende reproducir necesariamente una empresa completa.

Invariantes:

- origen sintético;
- naturaleza `SYNTHETIC`;
- `SYNTHETIC_TEST`;
- ningún efecto operacional;
- ninguna autoridad decisional;
- ruta operacional prohibida.

## 5. REFERENCE_OPERATIONAL_SIMULATION

Representa una operación empresarial ficticia, completa y económicamente
coherente, diseñada para validar EIOS como producto de extremo a extremo.

La palabra `OPERATIONAL` describe el **tipo de escenario simulado**, no la
naturaleza de los datos ni el efecto del runtime.

Invariantes:

- parte de un `ProjectionOnlySyntheticMaterialBundle` ya validado;
- el bundle original continúa declarando `SYNTHETIC`;
- el envelope debe conservar `contains_synthetic_material=true`;
- QTG solo puede ejecutarse como `SYNTHETIC_TEST`;
- la ruta `OPERATIONAL` permanece prohibida;
- no utiliza `OperationalAdmissionPreflight` para promover el material;
- no puede producir autoridad decisional ni efecto operacional;
- su finalidad es `PRODUCT_REFERENCE_E2E`.

La simulación podrá, en una unidad posterior, recorrer más componentes del MVP,
pero cualquier outcome deberá quedar causalmente encerrado en una fachada de
simulación sin efecto empresarial.

## 6. PRESENTED_OPERATIONAL

Representa material presentado como perteneciente a una organización y
operación empresarial reales.

La clasificación:

- no autentica los documentos;
- no demuestra suficiencia;
- no equivale a `STRUCTURALLY_ADMISSIBLE`;
- no equivale a `APTO`;
- no concede efecto operacional;
- exige atravesar la frontera de admisión antes de ejecutar QTG en modo
  `OPERATIONAL`.

Por ello su `effect_scope` en esta capa es
`NOT_GRANTED_BY_CLASSIFICATION`.

## 7. Prohibición de promoción

No existe transición automática:

```text
SYNTHETIC_TEST
    ─X→ PRESENTED_OPERATIONAL

REFERENCE_OPERATIONAL_SIMULATION
    ─X→ PRESENTED_OPERATIONAL
```

Cambiar una etiqueta no cambia la procedencia.

La implementación pública no expone funciones genéricas `promote` ni
`convert`.

Cada clasificación exige un tipo de fuente distinto:

- dataset validado para `SYNTHETIC_TEST`;
- bundle sintético completo para `REFERENCE_OPERATIONAL_SIMULATION`;
- intake operacional para `PRESENTED_OPERATIONAL`.

## 8. Fingerprint y reproducibilidad

`CaseProvenance` es factory-built e inmutable.

Su fingerprint liga, como mínimo:

- versión de esquema;
- `case_kind`;
- tipo de fuente;
- fingerprint exacto de la fuente;
- naturaleza material;
- modo QTG;
- ruta operacional;
- alcance de efectos;
- alcance de validación;
- necesidad de preflight;
- identificador de caso de referencia, cuando proceda;
- limitaciones;
- `decision_authority=false`.

Misma fuente + misma clasificación + mismo identificador → mismo fingerprint.

## 9. Relación con contratos cerrados

Esta unidad **no modifica**:

- `ProjectionMockDataset`;
- `ProjectionOnlySyntheticMaterialBundle`;
- `ProjectionMaterialEnvelope`;
- `ProjectionQualityProducer`;
- `ProjectionQualityConsumer`;
- `OperationalAdmissionPreflight`;
- `Projection Quality ↔ O1 Causal Binding`;
- `run_mvp_execution`.

En particular, el binding causal operacional continúa aceptando únicamente
consumo `OPERATIONAL/OPERATIONAL`.

## 10. AUDITAR

### A1 — tercer execution_mode accidental

Rechazado. `REFERENCE_OPERATIONAL_SIMULATION` no se añade al tipo
`ExecutionMode`.

### A2 — relabel de material sintético

Rechazado. La simulación exige un bundle cuyo `case_kind` continúa siendo
`SYNTHETIC` y cuyo envelope recompone material sintético.

### A3 — clasificación operacional = admisión

Rechazado. `PRESENTED_OPERATIONAL` queda en
`operational_path=REQUIRES_ADMISSION`.

### A4 — autoridad por procedencia

Rechazado. Las tres clasificaciones conservan
`decision_authority=false`.

### A5 — nueva vía lateral hacia O1 operacional

Rechazado. Esta unidad no llama ni modifica el binding O1.

### A6 — convertir Mock Data en expediente real

Rechazado. No existe API pública de promoción/conversión y los clasificadores
son tipados por fuente.

## 11. MATERIALIZACIÓN

- `eios/core/case_provenance.py`;
- `tests/test_case_provenance.py`;
- este contrato.

## 12. Criterio de cierre

La unidad podrá cerrarse cuando CI demuestre:

- suite focal satisfactoria;
- suite completa sin regresión;
- taxonomía reproducible;
- fuente sintética preservada en la simulación de referencia;
- ausencia de promoción pública;
- `PRESENTED_OPERATIONAL` sin admisión ni efecto concedidos;
- ninguna modificación de los contratos cerrados de QTG/O1.

## 13. Unidad posterior

Tras el cierre de esta taxonomía, la siguiente unidad será:

**Reference Operational Simulation Execution v0.1**

Su diseño deberá usar `REFERENCE_OPERATIONAL_SIMULATION` para recorrer el
MVP con material sintético realista, preservando en todo momento:

```text
material_nature = SYNTHETIC
qtg_execution_mode = SYNTHETIC_TEST
operational_path = FORBIDDEN
effect_scope = NO_OPERATIONAL_EFFECT
decision_authority = false
```

No se reutilizará la vía `PRESENTED_OPERATIONAL` para conseguir ese E2E.
