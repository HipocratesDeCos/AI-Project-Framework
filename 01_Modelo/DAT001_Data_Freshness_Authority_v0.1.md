# EIOS — DAT001 Data Freshness Authority v0.1

**Baseline de autorización:** `main @ b83ca2e22fd9dd11f4aab21c02a414273a76c50e`  
**Fecha:** 21/09/2026  
**Estado:** AUTORIZADO  
**Ámbito:** `R-DAT-001 — Datos actualizados`  
**Origen:** `DAT001_Data_Freshness_Authority_Proposal_v0.1.md`

## 1. Autoridad humana explícita

Se autoriza la semántica propuesta para `R-DAT-001` con la corrección de precisión indicada en esta versión: el productor factual de frescura y el evaluador de regla son responsabilidades separadas.

La autorización no valida el valor inicial de 6 semanas como política empresarial definitiva.

## 2. Ámbito autorizado

`R-DAT-001` evalúa exclusivamente la frescura del snapshot seleccionado por:

```text
DecisionContext.data_snapshot_id
```

No evalúa individualmente cada campo, evidencia o fuente y no determina suficiencia, integridad, consistencia o confianza global.

## 3. Identidad y tiempo

`data_snapshot_id` es identidad, no timestamp.

Queda prohibido inferir `source_updated_date` desde:

- `data_snapshot_id`;
- `Evidence.captured_at`;
- `Trace.created_at`;
- `DecisionInputPackage.effective_at`;
- el reloj del sistema;
- timestamps documentales o de Git.

## 4. Carrier factual autorizado

Carrier:

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

Invariantes:

- `AVAILABLE` requiere `source_updated_date`;
- cualquier otro estado requiere `source_updated_date = null`;
- el carrier debe quedar vinculado al snapshot y a la `PurchaseOperation` exactos.

## 5. Corrección autorizada — separación productor / regla

Se autoriza un productor factual independiente:

`DataSnapshotFreshnessProducer`

Su responsabilidad termina al construir el carrier desde metadata temporal explícita del snapshot.

El productor:

- puede aceptar únicamente metadata temporal ya disponible y referencias de provenance;
- no evalúa `P-DAT-001`;
- no calcula TRUE/FALSE;
- no decide si el dato es “reciente”;
- no selecciona otro snapshot;
- no inventa ni aproxima fechas;
- no usa fallback temporal implícito;
- no transforma `Evidence.captured_at` o `DIP.effective_at` en fecha de actualización.

El evaluador `R-DAT-001` consume el carrier ya construido y nunca produce ni corrige `source_updated_date`.

Si no existe metadata temporal inequívoca, el productor genera un estado no AVAILABLE; la regla no reconstruye la fecha.

## 6. Fecha base

```text
evaluation_date = PurchaseOperation.operation_date
```

No se usa el reloj del servidor.

## 7. Parámetro autorizado

`P-DAT-001` se consume mediante:

```text
ResolvedConfiguration(P-DAT-001)
+
ParameterConfigurationEvidence
```

Condiciones:

- `parameter_id == P-DAT-001`;
- unidad `semanas`;
- valor entero positivo;
- `parameters_version` coincidente;
- `company_scope` coincidente;
- configuración vigente para la evaluación;
- Evidence ligada a la configuración exacta.

No se hardcodea 6.

## 8. Semántica temporal

Una semana equivale a 7 días civiles.

```text
cutoff_date = evaluation_date - (P-DAT-001 × 7 días)
```

Rules opera sobre `date`.

Si una fuente original utiliza `datetime`, la conversión a fecha canónica pertenece al productor upstream y debe ser inequívoca y trazable. Si no puede demostrarse, el estado será `NOT_DETERMINABLE`.

## 9. Frontera de evaluación

```text
cutoff_date <= source_updated_date <= evaluation_date
    → EVALUABLE / TRUE

source_updated_date < cutoff_date
    → EVALUABLE / FALSE

source_updated_date > evaluation_date
    → NOT_EVALUABLE
```

La igualdad con el límite pertenece al periodo permitido.

## 10. Evidence y provenance

Evidence:

`DataSnapshotFreshnessEvidence`

Para Evidence `DEMONSTRATED`:

```text
demonstration_ref == data_snapshot_freshness_ref(observation)
```

Debe coincidir:

- `decision_id`;
- `scenario_id`;
- `data_snapshot_id`;
- `evaluation_date`;
- `purchase_operation_ref`;
- `company_scope`.

Binding estructural incompatible → error estructural.

Evidence GAP/INVALID → `NOT_EVALUABLE`.

## 11. Ausencia, contradicción y futuro

Estados:

```text
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

→ `NOT_EVALUABLE`.

Fecha futura respecto a `evaluation_date` → `NOT_EVALUABLE`.

No se permite elegir arbitrariamente una fecha entre varias, usar la más reciente, usar la más antigua, promediar ni convertir ausencia en FALSE.

## 12. Metadata de regla

```text
R-DAT-001 → R3 / INFORMATIVA
```

TRUE solo demuestra que el snapshot está dentro del horizonte P-DAT-001.

FALSE solo demuestra que no cumple la condición positiva de R-DAT-001.

No autoriza advertencia, bloqueo ni resultado empresarial adicional.

## 13. Separación de otras capacidades

Permanecen fuera de alcance:

- `R-DAT-002`;
- `R-DAT-003`;
- Quality & Trust Gate;
- scoring de calidad;
- selección de snapshot;
- política de suficiencia;
- validación empresarial del valor 6;
- decisión empresarial automática.

`datos recientes ≠ datos suficientes`.

## 14. Gates cerrados por esta autoridad

```text
DAT001-G01 → CERRADO
DAT001-G02 → CERRADO
DAT001-G03 → CERRADO
DAT001-G04 → CERRADO
DAT001-G05 → CERRADO
```

La autoridad habilita diseño técnico y materialización, pero no convierte su mera existencia documental en implementación.

## 15. Estado

**DAT001 Data Freshness Authority v0.1 — AUTORIZADO.**
