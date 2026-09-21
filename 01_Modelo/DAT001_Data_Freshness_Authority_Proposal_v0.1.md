# EIOS — DAT001 Data Freshness Authority Proposal v0.1

**Baseline:** `main @ b83ca2e22fd9dd11f4aab21c02a414273a76c50e`  
**Fecha:** 21/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** `R-DAT-001 — Datos actualizados`

## 1. Propósito

Cerrar únicamente la semántica mínima necesaria para determinar si el snapshot de datos seleccionado para una evaluación está dentro del periodo máximo permitido.

La regla no determina suficiencia, integridad, consistencia ni confianza global. Tampoco sustituye Quality & Trust Gate.

## 2. Autoridad existente

`04_Reglas/Matriz_Reglas_MVP.md` define:

> Los datos se encuentran dentro del periodo máximo permitido.

`02_Parametros/Matriz_Parametros_Reglas_MVP.md` y la RDM confirman:

```text
P-DAT-001 → R-DAT-001
```

`P-DAT-001` se denomina:

```text
Antigüedad máxima de datos operativos
```

Unidad vigente: `semanas`.

Su valor inicial de 6 semanas permanece pendiente de validación empresarial y no puede hardcodearse.

## 3. Ámbito de frescura propuesto

R-DAT-001 v0.1 evalúa exclusivamente la frescura del **snapshot de datos seleccionado por el DecisionContext**, identificado por:

```text
DecisionContext.data_snapshot_id
```

No evalúa por separado cada campo, evidencia o fuente.

La composición interna del snapshot y qué datos deben incluirse siguen perteneciendo a sus productores y contratos especializados.

## 4. Identidad no equivale a timestamp

`data_snapshot_id` identifica el snapshot, pero no contiene ni implica su fecha de actualización.

Por tanto está prohibido inferir frescura a partir de:

- el nombre o formato de `data_snapshot_id`;
- `Evidence.captured_at`;
- `Trace.created_at`;
- `DecisionInputPackage.effective_at`;
- fecha de ejecución del sistema;
- fecha de creación de un documento o commit.

## 5. Carrier factual propuesto

Se define un carrier independiente:

`DataSnapshotFreshnessObservation`

Campos mínimos:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
purchase_operation_ref
evaluation_date
source_updated_date
state
source_ref
authority_ref
methodology_ref
trace_refs
```

Estados:

```text
AVAILABLE
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Si `AVAILABLE`:

- `source_updated_date` es obligatorio;
- debe representar la fecha canónica de actualización del snapshot exacto;
- debe provenir de metadata/source lineage autorizado upstream.

Los demás estados requieren `source_updated_date = null`.

## 6. Productor propuesto

Se identifica como productor conceptual específico:

`DataSnapshotFreshnessProducer`

Su única responsabilidad será construir `DataSnapshotFreshnessObservation` a partir de metadata temporal explícita del snapshot seleccionado.

El productor:

- NO inventa timestamps;
- NO usa el reloj del sistema como fecha de origen;
- NO transforma `Evidence.captured_at` en fecha de actualización;
- NO selecciona otro snapshot;
- NO juzga suficiencia o calidad global;
- debe conservar source_ref, authority_ref y binding a `data_snapshot_id`.

Si la fuente no proporciona una fecha canónica demostrable, produce `NOT_EVIDENCED` o `NOT_DETERMINABLE`, no una fecha estimada.

## 7. Fecha base

La fecha de evaluación será:

```text
evaluation_date = PurchaseOperation.operation_date
```

No se utilizará la fecha actual del servidor.

## 8. Semántica de P-DAT-001

`P-DAT-001` se consume únicamente mediante:

```text
ResolvedConfiguration(P-DAT-001)
+
ParameterConfigurationEvidence
```

Validaciones propuestas:

- `parameter_id == P-DAT-001`;
- `unit == semanas`;
- valor entero positivo;
- parameters_version coincidente;
- company_scope coincidente;
- vigencia aplicable a `evaluation_date`;
- Evidence ligada a la configuración exacta.

No se hardcodea 6.

## 9. Semántica temporal

En DAT001, una semana se define como una duración exacta de 7 días civiles.

```text
cutoff_date = evaluation_date - (P-DAT-001 * 7 días)
```

Se utiliza calendario gregoriano sobre valores `date`.

No existe aritmética de zona horaria dentro de Rules.

Si una fuente original usa `datetime`, el productor upstream debe aportar una fecha canónica inequívoca conforme a la fuente/empresa. Si esa conversión no está demostrada, el estado será `NOT_DETERMINABLE`.

## 10. Frontera propuesta

R-DAT-001 es una regla positiva: “datos actualizados”.

```text
cutoff_date <= source_updated_date <= evaluation_date
    → EVALUABLE / TRUE

source_updated_date < cutoff_date
    → EVALUABLE / FALSE

source_updated_date > evaluation_date
    → NOT_EVALUABLE
```

La igualdad exacta con el corte cuenta como dentro del periodo máximo permitido.

## 11. Evidence y provenance

Se exige:

`DataSnapshotFreshnessEvidence`

Si está `DEMONSTRATED`:

```text
demonstration_ref == data_snapshot_freshness_ref(observation)
```

El carrier debe coincidir con:

- `DecisionContext.decision_id`;
- `DecisionContext.scenario_id`;
- `DecisionContext.data_snapshot_id`;
- `PurchaseOperation.operation_date`;
- referencia determinista a la `PurchaseOperation` exacta;
- company_scope aplicable.

Evidence ausente/GAP/INVALID o binding incompatible → `NOT_EVALUABLE` o error estructural según corresponda.

## 12. Ausencia y contradicción

```text
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

producen:

```text
R-DAT-001 → NOT_EVALUABLE
```

No se permite:

- escoger el timestamp más reciente;
- escoger el más antiguo;
- promediar fechas;
- usar “último recibido”;
- convertir ausencia en FALSE.

## 13. Metadata

La Matriz vigente autoriza:

```text
R-DAT-001 → R3 / INFORMATIVA
```

TRUE significa únicamente que el snapshot evaluado está dentro del horizonte P-DAT-001.

FALSE significa únicamente que no cumple la condición positiva de R-DAT-001.

R-DAT-001 no produce por sí sola una advertencia ni sustituye `R-DAT-002`.

## 14. Separación respecto a R-DAT-002 y R-DAT-003

### R-DAT-002

Permanece fuera de este alcance.

Aunque conceptualmente trata datos antiguos, DAT001 v0.1 no materializa ni presume su política, efecto operativo o relación con R-DAT-001.

### R-DAT-003

Permanece fuera de este alcance.

Frescura no equivale a suficiencia:

```text
datos recientes ≠ datos suficientes
```

## 15. Separación respecto a Quality & Trust

QTG puede considerar temporalidad como una dimensión de calidad, pero DAT001 es una Rule individual.

No se autoriza:

- convertir QualityTrustResult en evidencia DAT001 por similitud;
- duplicar la matriz normativa de QTG;
- hacer que DAT001 determine APTO/NO_APTO;
- usar DAT001 como sustituto del gate operacional QTG.

## 16. Fail-closed

R-DAT-001 devuelve `NOT_EVALUABLE` cuando:

- no existe observación temporal;
- el estado no es AVAILABLE;
- no existe fecha canónica;
- la fecha es futura;
- existe contradicción no resuelta;
- falta P-DAT-001;
- P-DAT-001 no es válido o no está evidenciado;
- identity/provenance no coincide con el snapshot y operación exactos.

`NOT_EVALUABLE ≠ FALSE`.

## 17. No-alcance

Esta propuesta no autoriza:

- R-DAT-002;
- R-DAT-003;
- scoring de calidad;
- decisión APTO/NO_APTO;
- reconstrucción de timestamp desde IDs;
- timestamp por reloj del sistema;
- selección de snapshot;
- validación empresarial del valor 6;
- decisión empresarial automática.

## 18. Gates que resolvería una aprobación explícita

Si se autoriza expresamente:

```text
DAT001-G01 → ámbito de frescura CERRADO
DAT001-G02 → fecha canónica del snapshot DEFINIDA
DAT001-G03 → productor conceptual provenance-safe DEFINIDO
DAT001-G04 → binding snapshot/decisión DEFINIDO
DAT001-G05 → fail-closed CERRADO
```

La aprobación habilitaría diseño técnico y materialización del productor/carrier/regla; no constituye por sí sola implementación.

## 19. Estado

**DAT001 Data Freshness Authority v0.1 — PROPUESTA / NO AUTORIZADA.**

Una instrucción genérica de continuar no equivale a autorización de esta política.
