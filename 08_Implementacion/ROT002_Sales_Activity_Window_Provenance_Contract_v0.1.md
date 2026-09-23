# EIOS — ROT002 Sales Activity Window Provenance Contract v0.1

**Baseline:** `main @ d0e94c47eb8d1622c2fbb3125c7e1da63756e4fc`  
**Fecha:** 23/09/2026  
**Estado:** DISEÑAR — PROPUESTA TÉCNICA ACOTADA  
**Autoridad:** `01_Modelo/ROT002_Configured_Sales_Inactivity_Period_Authority_v0.1.md`  
**Metodología:** `01_Modelo/Rotation_Track_A_Methodological_Closure_v0.1.md`  
**Regla relacionada:** `R-ROT-002`

## 1. Propósito

Materializar la frontera técnica mínima y provenance-safe que une:

```text
PurchaseOperation
+
DecisionContext
+
ResolvedConfiguration(P-ROT-001)
+
fuente factual autorizada de ventas
↓
ventana temporal exacta
↓
SalesActivityWindowEvidence
```

Esta unidad no materializa todavía el bridge decisional completo de `R-ROT-002`, no aplica excepciones y no modifica CRC.

## 2. Alcance autorizado

La unidad implementable debe cubrir exclusivamente:

1. validación de `P-ROT-001`;
2. derivación determinista de la ventana;
3. binding exacto a `PurchaseOperation.article_id` y `operation_date`;
4. construcción/revalidación de `SalesActivityWindowEvidence`;
5. conservación de provenance factual;
6. estados Track A autorizados.

No cubre:

- `R-ROT-001`;
- métrica general de rotación;
- excepciones de `R-ROT-002`;
- escalada R1 → R0;
- resultado CRC;
- `Assessment`;
- recomendación empresarial.

## 3. Carrier físico autorizado

El carrier físico se denomina exactamente:

```text
SalesActivityWindowEvidence
```

Debe ser inmutable y conservar, como mínimo, los campos ya autorizados documentalmente:

```text
article_id
evaluation_date
window_start
window_end
window_authority_ref
source_ref
source_semantics_ref
completeness_ref
evidence_refs
trace_refs
state
```

No se añaden campos decisionales.

## 4. Estados

`state` solo puede utilizar los estados cerrados de Track A:

```text
SALES_ACTIVITY_PRESENT
ZERO_VALID_SALES_DEMONSTRATED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

No se autoriza:

```text
TRUE
FALSE
COMPRAR
NEGOCIAR
NO_COMPRAR
```

dentro de este carrier.

## 5. Derivación de ventana

La ventana debe derivarse exclusivamente de:

```text
evaluation_date = PurchaseOperation.operation_date
period_days = ResolvedConfiguration(P-ROT-001).value
window_end = evaluation_date
window_start = evaluation_date - (period_days - 1 días)
```

La ventana es inclusiva:

```text
window_start <= sale_event_date <= window_end
```

No existe fallback a otro parámetro ni a un valor hardcoded.

## 6. Validación de P-ROT-001

Antes de construir la ventana debe verificarse:

1. `parameter_id == "P-ROT-001"`;
2. `parameters_version == DecisionContext.parameters_version`;
3. scope/company compatible con la configuración requerida por la operación;
4. configuración vigente en `effective_at`;
5. unidad canónica `días`;
6. valor entero, finito y positivo;
7. ausencia de conversión implícita desde meses/años;
8. `configuration_ref` disponible para `window_authority_ref`.

La ausencia o invalidez de configuración no autoriza inventar ventana.

## 7. Binding de identidad

Debe cumplirse:

```text
SalesActivityWindowEvidence.article_id
=
PurchaseOperation.article_id

SalesActivityWindowEvidence.evaluation_date
=
PurchaseOperation.operation_date

SalesActivityWindowEvidence.window_end
=
PurchaseOperation.operation_date

SalesActivityWindowEvidence.window_start
=
derived_window_start(P-ROT-001)
```

Además:

```text
DecisionContext.decision_id == PurchaseOperation.decision_id
DecisionContext.scenario_id == PurchaseOperation.scenario_id
```

Cualquier mismatch falla cerrado.

## 8. Provenance factual

El carrier debe conservar:

```text
window_authority_ref
source_ref
source_semantics_ref
completeness_ref
evidence_refs
trace_refs
```

`window_authority_ref` debe derivarse de la configuración resuelta de `P-ROT-001`.

`source_semantics_ref` identifica la autoridad que determina qué cuenta como venta válida.

`completeness_ref` demuestra la cobertura factual de la ventana.

Un literal de referencia no sustituye la autoridad upstream correspondiente.

## 9. Semántica de estados

### SALES_ACTIVITY_PRESENT

Solo cuando existe al menos un evento de venta válido demostrado dentro de la ventana exacta y scope aplicable.

### ZERO_VALID_SALES_DEMONSTRATED

Solo cuando la fuente autorizada y la evidencia de completitud demuestran cobertura suficiente de toda la ventana y ausencia de eventos de venta válidos.

No puede derivarse de:

- cero filas;
- GAP;
- suma neta cero;
- ventana parcial.

### NOT_EVIDENCED

Cuando falta evidencia necesaria para sostener una determinación factual.

### CONFLICTING_DATA

Cuando existen fuentes o evidencias incompatibles sin resolución autorizada.

### NOT_DETERMINABLE

Cuando la evidencia existe pero no permite una determinación válida bajo la metodología autorizada.

## 10. Frontera de ejecución provenance-safe

La implementación debe seguir el patrón:

```text
inputs autorizados
↓
snapshot / deep copy
↓
validación de contexto + P-ROT-001
↓
derivación de ventana
↓
producción factual
↓
SalesActivityWindowEvidence
↓
revalidación antes de reutilización
```

Un `SalesActivityWindowEvidence` construido manualmente o desprendido no debe aceptarse automáticamente como autoridad suficiente en Rules.

La frontera de reutilización deberá reconstruirlo o revalidar:

- identidad;
- ventana;
- configuración;
- provenance factual;
- estado.

## 11. Separación de responsabilidades

El productor Track A:

- produce evidencia factual;
- no crea `Assessment`;
- no aplica excepciones;
- no decide `NO COMPRAR`;
- no asigna severidad;
- no ejecuta CRC.

El futuro bridge `R-ROT-002` será una unidad separada.

## 12. Relación con C0 Evidence

Los estados Track A no sustituyen:

```text
Evidence.state
EvidenceValidation.status
```

Cuando se utilicen evidencias C0, deberán mantenerse sus invariantes y referencias.

## 13. No alcance técnico

Esta unidad no introduce:

- nuevo parámetro;
- nuevo ID de regla;
- nuevo resultado oficial;
- scoring;
- ranking;
- forecast de demanda;
- consumo;
- stock;
- política de devoluciones/anulaciones;
- fallback temporal;
- decisión humana automatizada.

## 14. Tests obligatorios

La materialización deberá probar al menos:

1. configuración válida `P-ROT-001`;
2. rechazo de otro parameter_id;
3. rechazo de parameters_version distinta;
4. rechazo de unidad distinta de `días`;
5. rechazo de valor cero, negativo, decimal, NaN, Infinity o texto;
6. cálculo correcto de ventana para 1 día;
7. cálculo correcto de ventana para N días;
8. mismatch de article_id;
9. mismatch de decision_id;
10. mismatch de scenario_id;
11. mismatch de evaluation_date;
12. mismatch de window_start/window_end;
13. ausencia de filas no produce `ZERO_VALID_SALES_DEMONSTRATED`;
14. suma neta cero no produce cero ventas;
15. cobertura parcial no produce cero ventas;
16. evidencia completa + ausencia demostrada produce `ZERO_VALID_SALES_DEMONSTRATED`;
17. evento válido demostrado produce `SALES_ACTIVITY_PRESENT`;
18. conflicto produce `CONFLICTING_DATA`;
19. evidencia insuficiente conserva `NOT_EVIDENCED/NOT_DETERMINABLE`;
20. revalidación rechaza carrier forjado/desprendido.

## 15. Gates

```text
ROT002-AW-G01 → carrier físico exacto
ROT002-AW-G02 → P-ROT-001 provenance
ROT002-AW-G03 → contexto/identidad
ROT002-AW-G04 → ventana inclusiva exacta
ROT002-AW-G05 → source semantics
ROT002-AW-G06 → completeness
ROT002-AW-G07 → estados Track A
ROT002-AW-G08 → revalidación provenance-safe
ROT002-AW-G09 → sin Assessment/CRC/excepciones
```

## 16. Criterio de cierre

La unidad solo podrá cerrarse cuando:

1. Audit 1 no detecte ambigüedades de contrato;
2. DEPURAR incorpore correcciones;
3. Audit 2 confirme que no se introducen semánticas de Rules;
4. código y tests respeten exactamente el contrato;
5. CI pre-merge sea satisfactoria;
6. se integre el mismo head;
7. CI post-merge sea satisfactoria.

