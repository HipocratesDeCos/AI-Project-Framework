# EIOS — ROT002 Sales Activity Window Provenance Contract v0.1

**Baseline:** `main @ d0e94c47eb8d1622c2fbb3125c7e1da63756e4fc`  
**Fecha:** 23/09/2026  
**Estado:** CERRADO CONTRACTUALMENTE — APTO PARA MATERIALIZACIÓN  
**Autoridad:** `01_Modelo/ROT002_Configured_Sales_Inactivity_Period_Authority_v0.1.md`  
**Metodología:** `01_Modelo/Rotation_Track_A_Methodological_Closure_v0.1.md`  
**Aggregate de entrada:** `DecisionInputPackage`  
**Regla relacionada:** `R-ROT-002`

## 1. Propósito

Materializar la frontera técnica mínima y provenance-safe que une:

```text
DecisionInputPackage
├── company_id
├── effective_at
├── purchase
├── context
├── configurations
├── missing_parameter_ids
└── evidence
+
fuente factual autorizada de ventas
↓
validación P-ROT-001
↓
ventana temporal exacta
↓
SalesActivityWindowEvidence
```

Esta unidad no materializa todavía el bridge decisional completo de `R-ROT-002`, no aplica excepciones y no modifica CRC.

## 2. Razón de usar DecisionInputPackage

`PurchaseOperation` no contiene `company_id`. Aceptar por separado `PurchaseOperation + DecisionContext + ResolvedConfiguration` permitiría ensamblar identidades desprendidas o requerir un argumento empresarial paralelo.

`DecisionInputPackage` ya captura canónicamente:

```text
company_id
effective_at
purchase
context
requested_parameter_ids
configurations
missing_parameter_ids
evidence
```

y valida:

```text
purchase.decision_id == context.decision_id
purchase.scenario_id == context.scenario_id
configuration.company_id == DIP.company_id
resolved.parameters_version == context.parameters_version
resolved.effective_at == DIP.effective_at
```

Por tanto, la frontera ROT no crea una segunda identidad ni un segundo sistema de resolución.

## 3. Alcance autorizado

La unidad implementable cubre exclusivamente:

1. lectura/revalidación del `DecisionInputPackage`;
2. localización de `P-ROT-001` dentro del aggregate;
3. validación de configuración y evidencia;
4. derivación determinista de la ventana;
5. binding exacto a `purchase.article_id` y `purchase.operation_date`;
6. construcción/revalidación de `SalesActivityWindowEvidence`;
7. conservación de provenance factual;
8. estados Track A autorizados.

No cubre:

- `R-ROT-001`;
- métrica general de rotación;
- excepciones de `R-ROT-002`;
- escalada R1 → R0;
- resultado CRC;
- `Assessment`;
- recomendación empresarial.

## 4. Carrier físico autorizado

El carrier físico se denomina exactamente:

```text
SalesActivityWindowEvidence
```

Debe ser inmutable y conservar, como mínimo, los campos autorizados:

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
activity_state
```

No se añaden campos decisionales.

## 5. Estados

`activity_state` solo puede utilizar:

```text
SALES_ACTIVITY_PRESENT
ZERO_VALID_SALES_DEMONSTRATED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

No se autoriza dentro del carrier:

```text
TRUE
FALSE
COMPRAR
NEGOCIAR
NO_COMPRAR
```

## 6. Selección de P-ROT-001 desde DIP

La frontera pública no acepta un `ResolvedConfiguration` separado.

Debe verificar:

```text
"P-ROT-001" ∈ DIP.requested_parameter_ids
"P-ROT-001" ∉ DIP.missing_parameter_ids
```

y localizar exactamente una configuración con:

```text
resolution.parameter_id == "P-ROT-001"
```

Debe además revalidar:

```text
resolution.company_id == DIP.company_id
resolution.parameters_version == DIP.context.parameters_version
resolution.effective_at == DIP.effective_at
```

y la vigencia del `Configuration` contenido.

Cualquier ausencia, duplicidad o mismatch falla cerrado.

## 7. Tipo y unidad de P-ROT-001

Debe cumplirse:

```text
unit == "días"
value = entero finito y positivo
value >= 1
```

No se autorizan:

- cero;
- negativos;
- decimales;
- NaN;
- Infinity;
- texto no numérico;
- conversión implícita desde meses/años.

No existe fallback.

## 8. Derivación de ventana

La única derivación autorizada es:

```text
evaluation_date = DIP.purchase.operation_date
period_days = resolved P-ROT-001
window_end = evaluation_date
window_start = evaluation_date - (period_days - 1 días)
```

La ventana es inclusiva:

```text
window_start <= sale_event_date <= window_end
```

No puede derivarse desde:

- reloj del sistema;
- `Evidence.captured_at`;
- `DIP.effective_at`;
- `data_snapshot_id`;
- otro parámetro temporal.

## 9. Evidencia de configuración

`ResolvedConfiguration.configuration_ref` es una referencia técnica estable, no una prueba empresarial por sí sola.

La autoridad especializada `01_Modelo/ROT002_Parameter_Configuration_Evidence_Binding_Authority_v0.1.md` cierra el binding específico:

```text
Evidence.source_ref
==
ResolvedConfiguration(P-ROT-001).configuration_ref
```

La suficiencia mínima exige al menos una Evidence vinculada con:

```text
state == "DEMONSTRATED"
demonstration_ref is not None
```

No se exige un `source_type` nuevo ni `captured_at == effective_at`.

`configuration_ref` sigue siendo referencia técnica; la demostración requiere Evidence.

## 10. window_authority_ref

Cuando P-ROT-001 haya sido validado:

```text
window_authority_ref = resolution.configuration_ref
```

Esta referencia permite reproducibilidad técnica.

No reemplaza:

- Evidence;
- autoridad documental;
- source semantics.

## 11. Binding de identidad

Debe cumplirse:

```text
SalesActivityWindowEvidence.article_id
=
DIP.purchase.article_id

SalesActivityWindowEvidence.evaluation_date
=
DIP.purchase.operation_date

SalesActivityWindowEvidence.window_end
=
DIP.purchase.operation_date

SalesActivityWindowEvidence.window_start
=
derived_window_start(P-ROT-001)
```

La identidad decisional ya viene ligada por DIP y debe revalidarse antes de producción/reutilización.

Cualquier mismatch falla cerrado.

## 12. Provenance factual

El carrier debe conservar:

```text
window_authority_ref
source_ref
source_semantics_ref
completeness_ref
evidence_refs
trace_refs
```

`source_semantics_ref` identifica la autoridad upstream que determina qué constituye una venta válida.

`completeness_ref` demuestra la cobertura factual de toda la ventana.

Un literal de referencia no constituye autoridad por sí solo.

## 13. Semántica de estados

### SALES_ACTIVITY_PRESENT

Solo cuando existe al menos un evento de venta válido demostrado dentro de la ventana exacta y scope aplicable.

### ZERO_VALID_SALES_DEMONSTRATED

Solo cuando una fuente autorizada, con semántica identificada y cobertura suficiente de toda la ventana, demuestra ausencia de eventos de venta válidos.

Nunca se deriva de:

- cero filas;
- GAP;
- suma neta cero;
- ventana parcial.

### NOT_EVIDENCED

Cuando falta evidencia necesaria para sostener una determinación factual.

### CONFLICTING_DATA

Cuando existen evidencias incompatibles sin resolución autorizada.

### NOT_DETERMINABLE

Cuando la evidencia existe pero no permite una determinación válida bajo la metodología autorizada.

## 14. Frontera provenance-safe

La implementación debe seguir:

```text
DecisionInputPackage
+
input factual autorizado de ventas
↓
snapshot / deep copy
↓
validación DIP
↓
selección y revalidación P-ROT-001
↓
validación Evidence
↓
derivación de ventana
↓
producción factual
↓
SalesActivityWindowEvidence
↓
revalidación antes de reutilización
```

Un carrier construido manualmente o desprendido no se acepta automáticamente en Rules.

La frontera de reutilización debe reconstruirlo o revalidar:

- aggregate de origen;
- identidad;
- ventana;
- configuración;
- evidencia;
- provenance factual;
- activity_state.

## 15. Separación de responsabilidades

Track A:

- produce soporte factual;
- no crea `Assessment`;
- no aplica excepciones;
- no decide `NO COMPRAR`;
- no asigna severidad;
- no ejecuta CRC.

El futuro bridge `R-ROT-002` será una unidad separada.

## 16. Relación con C0 Evidence

Los estados Track A no sustituyen:

```text
Evidence.state
EvidenceValidation.status
```

La implementación debe reutilizar los contratos C0 existentes y no crear un segundo sistema de evidence status.

## 17. No alcance técnico

No se introduce:

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
- identidad empresarial paralela;
- decisión humana automatizada.

## 18. Tests obligatorios

La materialización deberá probar al menos:

1. DIP válido con P-ROT-001;
2. P-ROT-001 no solicitado;
3. P-ROT-001 declarado missing;
4. ausencia de resolución;
5. resolución duplicada/ambigua;
6. parameter_id incorrecto;
7. company_id distinto del DIP;
8. parameters_version distinta;
9. effective_at distinto;
10. configuración fuera de vigencia;
11. unidad distinta de `días`;
12. valor cero, negativo, decimal, NaN, Infinity o texto;
13. cálculo correcto de ventana para 1 día;
14. cálculo correcto para N días;
15. ausencia de Evidence suficiente para configuración;
16. mismatch de article_id;
17. mismatch de evaluation_date;
18. mismatch de window_start/window_end;
19. cero filas no produce ZERO_VALID_SALES_DEMONSTRATED;
20. net quantity cero no produce ZERO_VALID_SALES_DEMONSTRATED;
21. cobertura parcial no produce ZERO_VALID_SALES_DEMONSTRATED;
22. evidencia completa + ausencia demostrada produce ZERO_VALID_SALES_DEMONSTRATED;
23. evento válido produce SALES_ACTIVITY_PRESENT;
24. conflicto produce CONFLICTING_DATA;
25. insuficiencia conserva NOT_EVIDENCED/NOT_DETERMINABLE;
26. revalidación rechaza carrier forjado/desprendido.

## 19. Gates

```text
ROT002-AW-G01 → DecisionInputPackage como raíz
ROT002-AW-G02 → selección P-ROT-001 dentro del DIP
ROT002-AW-G03 → company/context/effective_at
ROT002-AW-G04 → CLOSED — binding Evidence.source_ref == configuration_ref autorizado
ROT002-AW-G05 → ventana inclusiva exacta
ROT002-AW-G06 → source semantics
ROT002-AW-G07 → completeness
ROT002-AW-G08 → estados Track A
ROT002-AW-G09 → revalidación provenance-safe
ROT002-AW-G10 → sin Assessment/CRC/excepciones
```

## 20. Criterio de cierre

La unidad contractual queda cerrada y autoriza materialización cuando:

1. la implementación use `DecisionInputPackage` como raíz;
2. seleccione `P-ROT-001` exclusivamente dentro del DIP;
3. aplique el binding Evidence autorizado;
4. preserve los estados Track A y la separación respecto a Rules/CRC;
5. los tests cubran los invariantes y fallos cerrados;
6. CI pre-merge sea satisfactoria;
7. se integre el mismo head;
8. CI post-merge sea satisfactoria.
