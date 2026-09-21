# EIOS — HIS001 Temporal Reference Authority Proposal v0.1

**Baseline:** `main @ 7a21bbd117714372d69c88bd6f55ab6f2af3a404`  
**Fecha:** 21/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** `R-HIS-001 — Referencia demasiado antigua`

## 1. Propósito

Cerrar únicamente la semántica temporal mínima necesaria para determinar si una referencia histórica de precio supera la antigüedad máxima configurada.

La regla no selecciona referencias, no determina comparabilidad, no calcula PR y no sustituye Price Intelligence.

## 2. Autoridad existente

`04_Reglas/Matriz_Reglas_MVP.md` define:

> La compra utilizada como referencia supera la antigüedad máxima configurada.

`04_Reglas/Especificacion_Reglas_Historico_MVP.md` y `02_Parametros/Matriz_Parametros_Reglas_MVP.md` demuestran:

```text
P-DAT-002 → R-HIS-001
```

`P-PRE-003` permanece como criterio/metodología histórica y NO es parámetro directo de `R-HIS-001`.

`P-DAT-002` tiene unidad `meses`. Su valor inicial de 12 meses continúa pendiente de validación empresarial y no puede hardcodearse.

## 3. Fecha base propuesta

La fecha base de evaluación será:

```text
evaluation_date = PurchaseOperation.operation_date
```

Motivo: `PurchaseOperation.operation_date` es la fecha canónica físicamente existente en el contrato C0 de la operación evaluada.

No se introduce una segunda fecha implícita ni se usa la fecha actual del sistema.

## 4. Referencia histórica evaluada

La regla evalúa una referencia histórica individual ya identificada upstream.

Datos mínimos requeridos:

```text
reference_id
reference_operation_date
reference_source_ref
reference_evidence_refs
purchase_operation_ref
decision_id
scenario_id
data_snapshot_id
```

La referencia no se selecciona dentro de Rules.

No se autoriza seleccionar automáticamente:

- la última compra;
- la compra más barata;
- el proveedor habitual;
- una referencia de Price Intelligence por conveniencia;
- una agregación de referencias.

## 5. Carrier temporal propuesto

Se propone un carrier independiente:

`HistoricalReferenceTemporalObservation`

Campos mínimos:

```text
decision_id
scenario_id
data_snapshot_id
purchase_operation_ref
reference_id
reference_operation_date
evaluation_date
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

Si `AVAILABLE`, ambas fechas deben ser determinables y la identidad/provenance debe coincidir con la operación y referencia exactas.

## 6. Evidence y provenance

Se exige evidencia determinista ligada al carrier exacto:

`HistoricalReferenceTemporalEvidence`

Si está en estado `DEMONSTRATED`:

```text
demonstration_ref == historical_reference_temporal_ref(carrier)
```

Evidence ausente, GAP, inválida o ligada a otra referencia produce `NOT_EVALUABLE`.

La ausencia de evidencia nunca se transforma en `FALSE`.

## 7. P-DAT-002

`P-DAT-002` se consume solo mediante:

```text
ResolvedConfiguration(P-DAT-002)
+
ParameterConfigurationEvidence
```

Validaciones propuestas:

- `parameter_id == P-DAT-002`;
- `unit == meses`;
- valor entero positivo;
- versión de parámetros identificada;
- empresa/ámbito coincidente;
- vigencia aplicable a `evaluation_date`;
- Evidence ligada a la configuración exacta.

No se hardcodea 12.

## 8. Semántica de meses calendario

El corte temporal se calcula desplazando `evaluation_date` N meses de calendario hacia atrás:

```text
cutoff_date = shift_calendar_months(evaluation_date, -N)
```

Regla de clipping:

- conservar el día del mes si existe en el mes destino;
- si no existe, utilizar el último día válido del mes destino.

No se utilizan duraciones fijas de 30, 365 o 365.25 días como sustituto de meses calendario.

## 9. Frontera propuesta

`R-HIS-001` dice que la referencia “supera” la antigüedad máxima.

Por tanto:

```text
reference_operation_date < cutoff_date
    → EVALUABLE / TRUE

reference_operation_date == cutoff_date
    → EVALUABLE / FALSE

cutoff_date < reference_operation_date <= evaluation_date
    → EVALUABLE / FALSE
```

La igualdad exacta con el corte NO activa la regla.

## 10. Fechas futuras y anomalías

Si:

```text
reference_operation_date > evaluation_date
```

el material temporal es incompatible con una referencia histórica ordinaria y la regla devuelve:

```text
NOT_EVALUABLE
```

No se corrige silenciosamente la fecha, no se toma valor absoluto y no se fuerza `FALSE`.

Fecha ausente, contradictoria o no determinable → `NOT_EVALUABLE`.

## 11. Resultado y metadata

Metadata vigente:

```text
R-HIS-001 → R3 / MEDIA
```

`TRUE` significa exclusivamente:

> la referencia evaluada supera la antigüedad máxima autorizada.

No significa automáticamente:

- eliminar físicamente la referencia;
- declarar la operación no comparable;
- bloquear la compra;
- producir `NO COMPRAR`;
- sustituir la CRC.

La acción funcional permanece: no utilizar automáticamente esa referencia como principal y buscar referencias más recientes.

## 12. Separación respecto a PRE001

PRE001 usa `P-PRE-001` para decidir si una referencia comparable es “reciente” dentro de su propia regla.

HIS001 usa `P-DAT-002` para determinar si una referencia histórica es “demasiado antigua”.

Aunque ambas semánticas utilizan meses calendario, son autoridades distintas:

```text
P-PRE-001 ≠ P-DAT-002
R-PRE-001 ≠ R-HIS-001
```

No existe sustitución entre parámetros.

## 13. Separación respecto a Price Intelligence

Price Intelligence conserva `PriceReference.operation_date` y puede recibir `TemporalStatus`, pero no produce por sí mismo la autoridad HIS001.

No se autoriza:

- reutilizar un `TemporalStatus` opaco como prueba suficiente;
- inferir provenance porque un resultado pertenece a Price Intelligence;
- modificar Price Intelligence para cerrar HIS001;
- usar `PriceIntelligenceResult.pr_value`.

## 14. Fail-closed

`R-HIS-001` devuelve `NOT_EVALUABLE` cuando:

- falta la referencia individual;
- falta su fecha;
- falta Evidence válida;
- la fecha es futura;
- existen fechas contradictorias sin resolución autorizada;
- falta `P-DAT-002`;
- la configuración de `P-DAT-002` no es válida o no está evidenciada;
- identity/provenance no coincide;
- el carrier no puede vincularse a la `PurchaseOperation` exacta.

`NOT_EVALUABLE ≠ FALSE`.

## 15. No-alcance

Esta propuesta no autoriza:

- selección de referencias;
- reglas de comparabilidad;
- representatividad;
- suficiencia;
- agregación;
- Price Intelligence;
- cambios en PRE001;
- valores empresariales definitivos;
- defaults temporales;
- FX;
- decisión empresarial automática.

## 16. Gates que resolvería una aprobación explícita

Si esta política recibe autorización humana explícita:

```text
HIS001-G01 → semántica temporal CERRADA
HIS001-G02 → productor temporal conceptual IDENTIFICADO
HIS001-G03 → binding provenance-safe DEFINIDO
HIS001-G04 → fail-closed CERRADO
```

La aprobación habilitaría el posterior diseño técnico; no equivale por sí sola a implementación.

## 17. Estado

**HIS001 Temporal Reference Authority v0.1 — PROPUESTA / NO AUTORIZADA.**

Una instrucción genérica como “continúa” no autoriza esta política.
