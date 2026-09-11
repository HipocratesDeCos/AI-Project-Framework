# EIOS — SUPPLIER EVIDENCE CORE · METHODOLOGICAL DESIGN v0.3

**Estado:** DEPURADO — PENDIENTE DE AUDIT 2 FINAL  
**Fecha:** 11/09/2026  
**Baseline:** EIOS Vertical MVP  
**Ámbito:** Capa 5 — Proveedor / Riesgo  
**Sustituye:** `Supplier_Evidence_Core_Methodological_Design_v0.2.md`

---

## 1. Propósito

Definir la frontera metodológica cerrable de Capa 5 como **Supplier Evidence Core**: representación factual, trazable y reproducible de proveedor, candidatos, condiciones, hechos históricos, referencias externas y diferencias estructuralmente comparables, sin crear valoración agregada ni decisión.

El núcleo no constituye:

- SRM completo;
- supplier score;
- reliability score;
- compliance score;
- risk score;
- supplier ranking;
- motor de reglas;
- autoridad de comparabilidad normativa de `R-PROV-001/002`;
- recomendación o decisión.

---

## 2. Autoridades

Se subordina a:

- `03_Arquitectura/Architecture_Blueprint.md`;
- `03_Arquitectura/DSS_Functional_Architecture.md`;
- `01_Modelo/Especificacion_funcional.md`;
- `05_Motor/Modelo_Empresarial_Decision.md`;
- `04_Reglas/Matriz_Reglas_MVP.md`;
- `04_Reglas/Evidence_Contract.md`;
- `04_Reglas/Rule_Dependency_Matrix.md`;
- `08_Implementacion/Quality_Trust_Implementation_Contract.md`;
- autoridades cerradas de PRICE, TCO, STK y Finance Basic cuando sus resultados sean consumidos.

No modifica C0, Rules, CRC, parámetros ni contratos especializados.

---

## 3. Cadena de responsabilidad

```text
Supplier Evidence Core
    ↓
hechos / candidatos / condiciones / referencias / gaps

Supplier Risk Metrics
    ↓
futuro, solo si existe metodología autorizada

R-PROV-001 / R-PROV-002
    ↓
evaluación de reglas

CRC
    ↓
consolidación

CEO
    ↓
decisión
```

---

## 4. Invariantes

1. Evidencia antes que valoración.
2. Ausencia/GAP no equivale a FALSE, neutralidad ni cumplimiento.
3. `Quality & Trust confidence` no equivale a fiabilidad del proveedor.
4. Las dimensiones de proveedor permanecen separadas.
5. No se crea scoring, ranking ni ponderación.
6. Diferencia observable no equivale a superioridad.
7. La lógica especializada se consume; no se recalcula.
8. Histórico no equivale a estado actual.
9. Contradicciones se preservan.
10. El núcleo no emite resultados decisionales.
11. Comparabilidad estructural no equivale a comparabilidad normativa de regla.
12. Una métrica externa no adquiere autoridad por existir.

---

## 5. SEC-M01 — Identidad contextual del análisis

Todo resultado Supplier Evidence Core ejecutado dentro de EIOS debe permanecer ligado al contexto identificable del procesamiento.

Como mínimo conceptual, cuando exista `DecisionContext`:

```text
decision_id
scenario_id
data_snapshot_id
parameters_version
```

La metodología no redefine `DecisionContext`; conserva sus identificadores para trazabilidad.

---

## 6. SEC-M02 — Identidad de proveedor

Cada proveedor relevante se identifica de forma estable dentro de `company_scope`.

```text
supplier_id
company_scope
source_refs
```

El nombre comercial es descriptivo y no sustituye una identidad estable cuando puedan existir homónimos o entidades diferentes.

Proveedor actual y candidato alternativo deben tener `supplier_id` distintos dentro del mismo `company_scope`.

---

## 7. SEC-M03 — Objeto y contexto de compra

Toda evidencia de candidato o condición debe vincularse al objeto evaluado.

Como mínimo conceptual:

```text
article_or_object_id
company_scope
decision_context_reference
source_ref
captured_at
```

Un registro maestro o histórico no demuestra candidatura actual.

---

## 8. SEC-M04 — Candidato alternativo actual evidenciado

`PROV-G01` se cierra únicamente para **existencia factual de candidato actual evidenciado**.

Un proveedor puede clasificarse como `EVIDENCED_CANDIDATE` respecto de la operación actual solo cuando:

1. tiene identidad distinta del proveedor actual;
2. existe vínculo demostrable con el objeto evaluado;
3. existe una oferta, propuesta, declaración de capacidad/disponibilidad u otra manifestación concreta atribuible al proveedor;
4. la manifestación es aplicable al contexto evaluado;
5. la temporalidad necesaria para interpretar su vigencia está conservada;
6. no existe incompatibilidad temporal conocida que invalide su aplicabilidad actual;
7. existe referencia de fuente reproducible;
8. no existe contradicción no resuelta que impida identificar al candidato o su vínculo con el objeto.

Estados de resolución de candidatura:

```text
EVIDENCED_CANDIDATE
NOT_EVIDENCED
CONFLICTING_DATA
```

Son estados de dominio y no sustituyen `Evidence.state = DEMONSTRATED | GAP`.

### Evidencia histórica o expirada

Una evidencia que solo demuestra capacidad histórica, una oferta expirada o una relación pasada puede conservarse como referencia histórica, pero no demuestra candidatura actual.

Cuando la vigencia sea material y no pueda demostrarse, la candidatura actual se mantiene `NOT_EVIDENCED`.

Esto no equivale a afirmar que el proveedor sea incapaz de suministrar en general.

---

## 9. SEC-M05 — Condiciones por dimensión

Las condiciones se conservan separadamente:

```text
price_reference
payment_term
commercial_conditions
delivery_date
lead_time
availability_statement
quality_reference
reliability_reference
other_evidenced_condition
```

Cada dimensión conserva su fuente, semántica, unidad cuando aplique, alcance y referencia temporal relevante.

No se completan valores desconocidos con defaults ni con datos de otro proveedor.

---

## 10. SEC-M06 — Consumo de autoridades especializadas

### PRICE

Supplier Evidence Core puede consumir `price_result_ref` o valores fuente autorizados.

No redefine comparabilidad PRICE, normalización, PR, PO, PMR o PPV.

### TCO

Puede conservar referencia a resultados TCO.

No recompone ni duplica costes.

### STK / entrega

Puede conservar entrega/lead time evidenciado y referencias STK cuando proceda.

No redefine proyección, cobertura, rotura o `R-ENT-001`.

### Finance / pagos

Puede conservar condiciones de pago y referencias financieras autorizadas.

No ejecuta Finance Basic ni reglas financieras.

---

## 11. SEC-M07 — Disponibilidad factual

La disponibilidad es una afirmación operacional atribuible a proveedor, objeto y contexto.

Debe conservar, cuando exista:

```text
supplier_id
object_id
availability_value_or_statement
quantity_scope
validity_or_capture_date
source_ref
```

Puede ser cuantitativa si existe cantidad demostrada o cualitativa si la fuente solo demuestra una declaración identificable.

Nunca se transforma una declaración cualitativa en cantidad.

No se infiere disponibilidad desde:

- existencia en catálogo;
- relación histórica;
- stock interno de la empresa;
- cumplimiento histórico;
- ausencia de incidencias.

`PROV-G04` queda cerrado para representación factual y permanece OPEN para valoración comparativa.

---

## 12. SEC-M08 — Hechos históricos

Se conservan eventos históricos demostrados sin agregarlos en métricas no autorizadas.

```text
supplier_id
event_id
event_type
event_date
scope_or_object
source_ref
evidence_ref
```

Los tipos pueden describir hechos empresariales presentes en la fuente, por ejemplo retraso, entrega conforme, discrepancia de cantidad, rechazo/calidad, cancelación o discrepancia documental.

Estos ejemplos no constituyen una taxonomía normativa cerrada ni asignan criticidad.

No se derivan automáticamente:

```text
reliability_score
compliance_rate
incident_rate
risk_score
```

`PROV-G02` y `PROV-G03` permanecen OPEN para métricas agregadas.

---

## 13. SEC-M09 — Métricas externas

Supplier Evidence Core puede conservar métricas externas ya calculadas, pero distingue autoridad de uso.

Campos conceptuales mínimos:

```text
metric_name
metric_value
unit
scope
period
methodology_ref
source_ref
captured_at
usage_authority_state
```

Estados conceptuales de uso:

```text
AUTHORIZED_EXTERNAL_METRIC
CONTEXT_ONLY_METRIC
```

### AUTHORIZED_EXTERNAL_METRIC

Solo procede cuando existen trazabilidad suficiente de metodología, alcance, unidad y autoridad para utilizar esa métrica en el contexto EIOS correspondiente.

### CONTEXT_ONLY_METRIC

Se utiliza cuando la métrica existe y es trazable como dato, pero su metodología, autoridad o comparabilidad no son suficientes para utilizarla como valoración analítica autorizada.

Una `CONTEXT_ONLY_METRIC`:

- puede mostrarse como contexto;
- no participa en una comparación valorativa;
- no activa Rules;
- no genera preferencia.

La existencia de `methodology_ref` por sí sola no convierte una métrica en autorizada.

---

## 14. SEC-M10 — Concentración

`PROV-G05` permanece OPEN para cálculo nativo.

El núcleo no define numerador, denominador, periodo, alcance, umbral ni efecto.

Solo puede conservar una métrica externa de concentración bajo SEC-M09.

No calcula concentración por inferencia.

---

## 15. SEC-M11 — Comparabilidad estructural

Supplier Evidence Core solo puede determinar **comparabilidad estructural de representaciones**, no comparabilidad normativa de `R-PROV-002`.

Estados:

```text
STRUCTURALLY_COMPARABLE
NOT_STRUCTURALLY_COMPARABLE
UNKNOWN
```

Dos valores pueden ser `STRUCTURALLY_COMPARABLE` cuando, para la dimensión concreta:

- su semántica coincide;
- unidad/escala son compatibles cuando aplique;
- objeto y alcance son compatibles;
- referencia temporal es compatible para el uso analítico pretendido;
- no existe contradicción material no resuelta que invalide la comparación.

`UNKNOWN` se utiliza cuando la evidencia disponible no permite demostrar compatibilidad estructural ni incompatibilidad.

Invariante:

```text
STRUCTURALLY_COMPARABLE
    ≠
RULE_COMPARABLE
```

La comparabilidad exigida por `R-PROV-002` permanece bajo autoridad de Rules y de las autoridades especializadas que correspondan.

PRICE conserva autoridad exclusiva sobre comparabilidad de precio dentro de su dominio.

---

## 16. SEC-M12 — Matriz dimensional

La salida comparativa conserva dimensiones separadas:

| Dimensión | Proveedor actual | Candidato | Estado estructural | Autoridad/fuente |
|---|---|---|---|---|
| Precio | dato/resultado | dato/resultado | estructural + referencia PRICE | PRICE |
| Pago | dato | dato | estado estructural | fuente/PAG |
| Entrega | dato | dato | estado estructural | fuente/ENT/STK |
| Disponibilidad | dato | dato | estado estructural | fuente |
| Fiabilidad | métrica autorizada o contexto | equivalente | estado estructural si procede | metodología autorizada |
| Otras condiciones | dato | dato | estado estructural | fuente |

La matriz puede mostrar diferencias aritméticas o descriptivas únicamente cuando estén definidas por la dimensión y sean reproducibles.

No transforma diferencias en:

- mejor/peor global;
- ranking;
- score;
- preferencia;
- efecto de regla.

---

## 17. SEC-M13 — Gaps y contradicciones

Ausencia o GAP se preserva como insuficiencia.

No se convierte en:

```text
0
FALSE
neutral
cumplimiento
fiabilidad
disponibilidad
no riesgo
```

Datos incompatibles para misma identidad/dimensión/contexto se conservan como `CONFLICTING_DATA` de dominio, junto con las referencias incompatibles.

El núcleo no decide qué fuente prevalece salvo autoridad documental previa y explícita.

---

## 18. SEC-M14 — Relación con R-PROV-001

Supplier Evidence Core puede proporcionar:

- candidatos actuales evidenciados;
- condiciones por dimensión;
- estados estructurales;
- diferencias observables trazables.

No define `potencialmente mejores`.

`PROV-G06` permanece `OPEN-RULES`.

El núcleo no activa `R-PROV-001`.

---

## 19. SEC-M15 — Relación con R-PROV-002

Supplier Evidence Core puede proporcionar la matriz factual y estructural necesaria para una futura evaluación.

No define:

- `RULE_COMPARABLE` global;
- `significativamente`;
- número de dimensiones necesarias;
- compensación entre mejoras y empeoramientos;
- score multidimensional;
- preferencia de proveedor.

`PROV-G07` permanece `OPEN-RULES`.

`PROV-G08` permanece `OPEN-RULES/CRC`.

El núcleo no activa `R-PROV-002`.

---

## 20. SEC-M16 — Señales de proveedor

Puede conservar hechos/señales trazables:

```text
signal_id
supplier_id
signal_type
observed_at
scope
source_ref
evidence_ref
```

La etiqueta `signal_type` describe el hecho fuente; no asigna automáticamente criticidad.

El núcleo no produce:

- criticality;
- severity;
- probability;
- efecto R0/R1/R2/R3;
- recomendación.

`PROV-G09` queda cerrado para representación factual y permanece OPEN para taxonomía normativa/impacto.

---

## 21. Salida conceptual autorizada

```text
decision_id
scenario_id
data_snapshot_id
parameters_version
current_supplier_ref
candidate_supplier_refs
candidate_resolution_states
supplier_condition_sets
dimension_comparisons
historical_facts
external_metric_references
supplier_signals
unresolved_items
conflicting_items
source_references
```

Campos expresamente fuera de alcance:

```text
supplier_score
supplier_rank
preferred_supplier
supplier_risk_level
reliability_score
compliance_score
recommendation
assessment
effect
severity
crc_result
purchase_decision
```

---

## 22. Estado de gaps v0.3

| Gap | Estado | Tratamiento |
|---|---|---|
| PROV-G01 | CLOSED-FACTUAL | Candidato actual evidenciado SEC-M04 |
| PROV-G02 | OPEN-METRIC | Hechos/referencias sí; métrica nativa no |
| PROV-G03 | OPEN-METRIC | Hechos/referencias sí; métrica nativa no |
| PROV-G04 | CLOSED-FACTUAL / OPEN-VALUATION | Disponibilidad factual sí; superioridad no |
| PROV-G05 | OPEN-METRIC | Solo métrica externa bajo SEC-M09 |
| PROV-G06 | OPEN-RULES | `potencialmente mejores` no definido |
| PROV-G07 | OPEN-RULES | `mejora significativamente` no definido |
| PROV-G08 | OPEN-RULES/CRC | Trade-offs no definidos |
| PROV-G09 | CLOSED-FACTUAL / OPEN-IMPACT | Señal factual sí; criticidad/efecto no |

---

## 23. Frontera de contrato técnico potencial

Si Audit 2 final resulta limpio, el contrato técnico podrá autorizar exclusivamente:

- modelos inmutables de referencia de proveedor;
- candidatura factual evidenciada;
- condiciones por dimensión;
- disponibilidad factual;
- hechos históricos;
- referencias de métricas externas con autoridad de uso explícita;
- comparabilidad estructural;
- matriz dimensional;
- gaps/contradicciones;
- identidad contextual y trazabilidad.

Quedará fuera:

- métricas nativas de riesgo/fiabilidad/cumplimiento/concentración;
- scoring/ranking;
- preferencia de proveedor;
- reglas R-PROV;
- CRC;
- decisión.

---

## 24. Criterio de cierre metodológico

La metodología será cerrable si Audit 2 final confirma que:

1. no existe política empresarial nueva implícita;
2. candidatura actual exige aplicabilidad contextual/temporal suficiente;
3. estados de dominio no sustituyen C0 Evidence;
4. comparabilidad estructural no satisface por sí sola R-PROV-002;
5. métricas externas sin autoridad permanecen `CONTEXT_ONLY_METRIC`;
6. ninguna dimensión se agrega en score/ranking;
7. PRICE/TCO/STK/Finance no se duplican;
8. Q&T no se convierte en supplier reliability;
9. gaps y contradicciones permanecen explícitos;
10. salida conserva Decision Context y no contiene decisión.
