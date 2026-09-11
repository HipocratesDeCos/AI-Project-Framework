# EIOS — SUPPLIER EVIDENCE CORE · IMPLEMENTATION CONTRACT AUDIT 1 v0.1

**Estado:** COMPLETADA — DEPURACIÓN REQUERIDA  
**Fecha:** 11/09/2026  
**Objeto:** `Supplier_Evidence_Core_Implementation_Contract_v0.1.md`

---

## 1. Dictamen

El contrato v0.1 respeta la frontera metodológica y no introduce scoring, ranking, Rules ni cálculo de riesgo.

Sin embargo, **siete hallazgos técnicos** impiden cerrarlo todavía.

Todos son corregibles sin nueva política empresarial.

---

## 2. Hallazgos

### PROV-TC-A1-01 — Falta un contrato físico común para contradicciones

El contrato exige `CONFLICTING_DATA` en candidatos/observaciones, pero no define de forma cerrada cómo demostrar una contradicción.

La frase “o una referencia de contradicción explícita que el contrato deberá representar” deja una responsabilidad pendiente.

**Corrección:** introducir `SupplierDataIssueRef` con:

```text
issue_id
issue_type = MISSING_DATA | CONTRADICTION
issue_record_ref
evidence_refs
trace_refs
```

`CONFLICTING_DATA` deberá requerir al menos un `SupplierDataIssueRef` tipo `CONTRADICTION`, y una contradicción deberá contener al menos dos evidencias/referencias incompatibles identificables.

---

### PROV-TC-A1-02 — REFERENCE_ONLY necesita evidencia mínima

v0.1 permite `REFERENCE_ONLY` sin exigir materialmente `evidence_id/source_ref/captured_at`.

Eso permitiría crear una “referencia histórica” vacía.

**Corrección:** `REFERENCE_ONLY` requiere al menos:

```text
evidence_id
source_ref
captured_at
```

No requiere `applicability_ref` de operación actual.

---

### PROV-TC-A1-03 — Propiedad de observación demasiado ambigua

La regla:

> `candidate_id = None` solo puede utilizarse para hechos del proveedor actual o hechos no vinculados a candidatura concreta

permite observaciones de un proveedor alternativo sin `candidate_id`, dificultando reconstruir qué oferta/propuesta soporta la condición.

**Corrección:** dentro de `SupplierEvidenceInput`:

```text
candidate_id is None
    → supplier_id debe ser current_supplier_id

candidate_id is not None
    → candidate_id debe existir y su supplier_id debe coincidir
```

Las condiciones de proveedores alternativos para la operación actual deben estar vinculadas a una candidatura concreta.

---

### PROV-TC-A1-04 — Coherencia temporal insuficiente

Un resultado EIOS no debe utilizar silenciosamente evidencia capturada después de `evaluation_date` como si hubiera estado disponible en ese momento.

**Corrección:** para elementos que participan en la evaluación actual:

```text
captured_at <= evaluation_date
```

También:

```text
historical_fact.event_date <= evaluation_date
signal.observed_at <= evaluation_date
```

Esto preserva reproducibilidad y no constituye ventana de negocio.

---

### PROV-TC-A1-05 — ExternalSupplierMetric mezcla estado del dato y autoridad de uso

`usage_state` expresa autoridad, pero el modelo no puede representar:

- métrica no evidenciada;
- métrica contradictoria.

Esto contradice la obligación metodológica de preservar gaps/contradicciones.

**Corrección:** separar:

```text
data_state: ObservationState
usage_state: ExternalMetricUsageState
```

Reglas:

- `KNOWN` requiere valor + fuente + metodología + periodo;
- estado no `KNOWN` no publica valor determinado;
- `CONFLICTING_DATA` requiere incidencia de contradicción;
- `AUTHORIZED_EXTERNAL_METRIC` solo puede ser útil como autorizada cuando `data_state = KNOWN` y existe `usage_authority_ref`;
- la autoridad de uso no corrige un dato GAP/contradictorio.

---

### PROV-TC-A1-06 — Falta prohibición física de observaciones futuras y referencias temporales incoherentes

Además de A1-04, `valid_from/valid_to` debe permanecer coherente con el uso actual.

**Corrección:**

- `valid_to < valid_from` inválido;
- `CURRENT_OPERATION_DEMONSTRATED` no puede estar fuera de su vigencia explícita;
- una observación `KNOWN` con `valid_from > evaluation_date` no puede utilizarse en comparación actual;
- si `valid_to < evaluation_date`, tampoco participa como condición vigente actual;
- puede conservarse como histórico/referencia fuera de la matriz actual si el contrato lo permite, pero no simular vigencia.

---

### PROV-TC-A1-07 — Versión metodológica debe ser inequívoca

`methodology_version` “debe identificar la metodología cerrada” pero no fija la identidad permitida.

**Corrección:** v0.2 deberá fijar el literal contractual:

```text
SUPPLIER_EVIDENCE_METHODOLOGY_VERSION = "0.3"
```

y exigir que el contexto físico de este contrato utilice esa versión.

Una futura metodología deberá disponer de otro contrato/versionado explícito.

---

## 3. Verificaciones superadas

No requieren depuración adicional:

- paquete separado `eios/supplier`;
- DecisionContext canónico;
- PurchaseOperation como ancla de proveedor/artículo actual;
- `company_scope` propio sin ampliar C0;
- candidate_id separado de supplier_id;
- múltiples propuestas del mismo proveedor permitidas;
- comparación únicamente por requests explícitos;
- diferencia decimal descriptiva sin semántica mejor/peor;
- no cross-product;
- no cálculo de fiabilidad/cumplimiento/riesgo/concentración;
- no R-PROV;
- no Assessment;
- no CRC;
- no decisión;
- no mutación.

---

## 4. Decisión

**CONTRATO v0.1: NO CERRABLE.**

Depurar a v0.2 incorporando A1-01…A1-07 y volver a ejecutar Audit 2.
