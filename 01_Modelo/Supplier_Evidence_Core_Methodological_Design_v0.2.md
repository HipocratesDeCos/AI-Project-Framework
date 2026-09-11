# EIOS — SUPPLIER EVIDENCE CORE · METHODOLOGICAL DESIGN v0.2

**Estado:** DEPURADO — PENDIENTE DE AUDIT 2  
**Fecha:** 11/09/2026  
**Baseline:** EIOS Vertical MVP  
**Ámbito:** Capa 5 — Proveedor / Riesgo  
**Sustituye conceptualmente:** `Supplier_Risk_Methodological_Design_v0.1.md` para el alcance cerrable sin nueva política empresarial

---

## 1. Propósito

Definir la frontera metodológica mínima y cerrable de Capa 5 como **Supplier Evidence Core**.

El Supplier Evidence Core representa de forma factual, trazable y reproducible:

- el proveedor actual;
- candidatos alternativos evidenciados;
- condiciones de proveedor conservadas por dimensión;
- hechos históricos atribuibles a proveedor;
- afirmaciones evidenciadas de disponibilidad/entrega;
- referencias externas de fiabilidad, cumplimiento o concentración cuando ya exista una metodología competente;
- diferencias observables entre dimensiones comparables cuando esa comparabilidad venga autorizada por la capa correspondiente;
- gaps y contradicciones sin resolverlos arbitrariamente.

No constituye un SRM completo, un supplier score, un motor de reglas, una clasificación de proveedor ni una recomendación de compra.

---

## 2. Autoridades y precedencia

Esta metodología se subordina a:

- `03_Arquitectura/Architecture_Blueprint.md`;
- `03_Arquitectura/DSS_Functional_Architecture.md`;
- `01_Modelo/Especificacion_funcional.md`;
- `05_Motor/Modelo_Empresarial_Decision.md`;
- `04_Reglas/Matriz_Reglas_MVP.md`;
- `04_Reglas/Evidence_Contract.md`;
- `04_Reglas/Rule_Dependency_Matrix.md`;
- `08_Implementacion/Quality_Trust_Implementation_Contract.md`;
- autoridades cerradas de PRICE, TCO, STK y Finance Basic cuando sus resultados sean consumidos.

La similitud semántica entre documentos no crea autoridad.

El Supplier Evidence Core no modifica ninguna de estas fuentes.

---

## 3. Separación obligatoria de responsabilidades

```text
SUPPLIER EVIDENCE CORE
    ↓
hechos + candidatos + condiciones + referencias + gaps

SUPPLIER RISK METRICS
    ↓
futuro, solo con metodología autorizada

RULES R-PROV-001 / R-PROV-002
    ↓
evaluación de reglas

CRC
    ↓
consolidación decisional

CEO
    ↓
decisión empresarial
```

El Supplier Evidence Core no puede adelantar funciones de ninguna capa posterior.

---

## 4. Invariantes

### SEC-I01 — Evidencia antes que valoración
Un hecho de proveedor solo puede participar cuando su identidad, objeto, alcance, fuente y temporalidad necesaria sean suficientemente trazables.

### SEC-I02 — GAP no equivale a FALSE
La ausencia de evidencia no demuestra ausencia del hecho empresarial.

### SEC-I03 — Q&T no es supplier reliability
La confianza de Quality & Trust describe calidad/confianza del conjunto de evidencia, no desempeño del proveedor.

### SEC-I04 — Dimensiones separadas
Precio, plazo, disponibilidad, entrega, condiciones, hechos de cumplimiento, métricas externas y concentración permanecen separadas.

### SEC-I05 — No scoring
No se ponderan, promedian ni agregan dimensiones en una puntuación única.

### SEC-I06 — No superioridad implícita
Una diferencia observable no autoriza afirmar que un proveedor es globalmente mejor.

### SEC-I07 — Comparabilidad heredada
Cuando una dimensión ya tenga autoridad especializada, el Supplier Evidence Core consume el resultado autorizado y no reconstruye su lógica.

### SEC-I08 — Histórico no es estado actual
Un hecho histórico no se transforma automáticamente en riesgo presente, fiabilidad o disponibilidad actual.

### SEC-I09 — Contradicción preservada
Datos/evidencias incompatibles no se resuelven por último valor, promedio, máximo, mínimo, score o prioridad arbitraria.

### SEC-I10 — No decisión
La salida no contiene COMPRAR, NEGOCIAR, COMPRAR CONDICIONADO, NO COMPRAR ni equivalente.

---

## 5. SEC-M01 — Identidad de proveedor

Cada proveedor relevante se representa mediante identidad empresarial estable y trazable.

Campos conceptuales mínimos:

```text
supplier_id
company_scope
source_refs
```

El nombre comercial puede conservarse como atributo descriptivo, pero no sustituye `supplier_id` cuando exista riesgo de homonimia o entidades distintas.

El proveedor actual y un candidato alternativo no pueden compartir la misma identidad de proveedor dentro del mismo `company_scope`.

---

## 6. SEC-M02 — Objeto de compra evaluado

Toda evidencia de alternativa debe vincularse al objeto de compra al que pretende aplicarse.

Como mínimo conceptual debe poder reconstruirse:

```text
article_or_object_id
company_scope
decision_context_reference
source_ref
captured_at
```

La coincidencia nominal de descripción no sustituye la identidad del objeto cuando exista identificador estable.

Un proveedor existente en el maestro o en históricos no se convierte por ello en candidato para la operación actual.

---

## 7. SEC-M03 — Existencia factual de candidato alternativo

`PROV-G01` se cierra únicamente para la **existencia factual evidenciada**.

Existe un candidato alternativo evidenciado cuando concurren conjuntamente:

1. identidad de proveedor distinta del proveedor actual;
2. vínculo demostrable con el objeto de compra evaluado;
3. evidencia atribuible de oferta, propuesta, disponibilidad/capacidad u otra manifestación concreta aplicable a la operación o contexto evaluado;
4. referencia de fuente reproducible;
5. temporalidad conservada cuando sea necesaria para interpretar vigencia;
6. ausencia de contradicción no resuelta que impida identificar al candidato o su vínculo con el objeto.

Esto permite afirmar exclusivamente:

> existe evidencia suficiente de que este proveedor es un candidato para el objeto/contexto evaluado.

No permite afirmar:

- que sea comparable en todas las dimensiones;
- que esté necesariamente disponible en cantidad/plazo suficiente;
- que sea mejor;
- que deba sustituir al proveedor actual;
- que active por sí solo `R-PROV-001`.

Estados conceptuales de resolución del candidato:

```text
EVIDENCED_CANDIDATE
NOT_EVIDENCED
CONFLICTING_DATA
```

Estos estados son de dominio Supplier Evidence Core y **no sustituyen** los estados físicos `Evidence.state = DEMONSTRATED | GAP` de C0.

---

## 8. SEC-M04 — Condiciones de proveedor por dimensión

Las condiciones se conservan de forma separada y trazable.

Dimensiones posibles, solo cuando existan datos/evidencia:

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

Reglas:

- no completar valores desconocidos con defaults;
- no copiar condiciones del proveedor actual a un candidato;
- no inferir disponibilidad desde existencia en catálogo;
- no inferir cumplimiento histórico desde una promesa actual;
- no inferir fiabilidad desde una condición aislada;
- no convertir ausencia de incidencias en fiabilidad demostrada.

Cada dimensión conserva su propia fuente y contexto.

---

## 9. SEC-M05 — Consumo de resultados especializados

Cuando una dimensión esté gobernada por otra autoridad cerrada, Supplier Evidence Core consume referencias/resultados autorizados.

### Precio

Puede consumir `price_result_ref` o dato fuente trazable.

No redefine:

- comparabilidad PRICE;
- normalización;
- PR;
- PO;
- PMR;
- PPV.

### Stock / entrega

Puede conservar entrega/lead time evidenciado y referencias de resultados STK cuando proceda.

No redefine `R-ENT-001`, rotura de stock ni proyección STK.

### Finanzas / pago

Puede conservar condiciones de pago de la oferta y referencias a resultados financieros autorizados cuando proceda.

No recalcula Finance Basic ni reglas financieras.

### TCO

Puede referenciar resultados TCO cuando una comparación autorizada los necesite posteriormente.

No agrega ni duplica costes.

---

## 10. SEC-M06 — Disponibilidad como hecho

La disponibilidad se representa como una afirmación operacional atribuible a proveedor/oferta/objeto/contexto.

Como mínimo debe conservar, cuando exista:

```text
supplier_id
object_id
availability_value_or_statement
quantity_scope
validity_or_capture_date
source_ref
```

La disponibilidad puede ser:

- cuantitativa, si existe cantidad demostrada;
- cualitativa, si la fuente únicamente demuestra una declaración identificable.

Supplier Evidence Core no convierte una declaración cualitativa en cantidad.

La presencia de disponibilidad evidenciada no implica automáticamente mejor disponibilidad frente a otro proveedor.

`PROV-G04` queda **cerrado solo para representación factual**; su valoración comparativa permanece OPEN.

---

## 11. SEC-M07 — Hechos históricos de proveedor

El núcleo puede conservar hechos históricos demostrados sin convertirlos en métrica agregada.

Campos conceptuales mínimos:

```text
supplier_id
event_id
event_type
event_date
scope_or_object
source_ref
evidence_ref
```

Pueden representarse categorías descriptivas ya presentes en la evidencia empresarial, por ejemplo:

- retraso;
- entrega conforme;
- discrepancia de cantidad;
- rechazo/calidad;
- cancelación;
- discrepancia documental;
- cumplimiento confirmado.

La lista no constituye taxonomía normativa cerrada ni asigna severidad.

No se autoriza derivar por defecto:

```text
reliability_score
compliance_rate
incident_rate
risk_score
```

`PROV-G02` y `PROV-G03` permanecen OPEN para cualquier métrica agregada.

---

## 12. SEC-M08 — Referencias externas de métricas

Puede preservarse una métrica externa ya calculada por una fuente competente siempre que se conserve, como mínimo:

```text
metric_name
metric_value
unit
scope
period
methodology_ref
source_ref
captured_at
```

El Supplier Evidence Core no valida ni reconstruye una metodología no documentada.

Una métrica sin `methodology_ref` suficiente se conserva, como máximo, como dato contextual no autorizado para valoración.

Esto aplica a:

- fiabilidad;
- cumplimiento;
- concentración;
- otras métricas de proveedor.

---

## 13. SEC-M09 — Concentración

`PROV-G05` permanece OPEN para cálculo nativo.

No se define:

- denominador;
- numerador;
- periodo;
- alcance artículo/familia/empresa;
- umbral;
- efecto decisional.

Supplier Evidence Core solo puede conservar una referencia externa de concentración si incluye definición, unidad, periodo, alcance, metodología y fuente.

No calcula concentración por inferencia.

---

## 14. SEC-M10 — Comparación dimensional

La comparación se representa como matriz de dimensiones independientes.

| Dimensión | Proveedor actual | Candidato | Estado de comparabilidad | Autoridad/fuente |
|---|---|---|---|---|
| Precio | dato/resultado | dato/resultado | comparable / no comparable / unknown | PRICE |
| Pago | dato | dato | comparable / no comparable / unknown | fuente / PAG |
| Entrega | dato | dato | comparable / no comparable / unknown | fuente / ENT/STK |
| Disponibilidad | dato | dato | comparable / no comparable / unknown | fuente |
| Fiabilidad | referencia autorizada | referencia autorizada | comparable / no comparable / unknown | metodología externa competente |
| Otras condiciones | dato | dato | comparable / no comparable / unknown | fuente |

`unknown` no equivale a `no comparable`.

La matriz puede conservar diferencias observables cuando las magnitudes son comparables, pero no las transforma en una preferencia global.

---

## 15. SEC-M11 — Comparabilidad

No existe una comparabilidad universal de proveedor.

La comparabilidad es **por dimensión**.

Para precio, se hereda de PRICE.

Para otras dimensiones, solo puede declararse comparable cuando:

- la semántica de ambos valores coincide;
- unidad/escala son compatibles cuando aplique;
- objeto y alcance son compatibles;
- referencia temporal es compatible para el uso pretendido;
- no existe contradicción material no resuelta.

Estas condiciones permiten decidir si dos representaciones son comparables como datos; **no definen qué diferencia es buena, mala o significativa**.

---

## 16. SEC-M12 — Contradicciones y gaps

Cuando faltan datos/evidencia:

```text
GAP / ausencia
    ↓
se preserva la insuficiencia
```

No se convierte en:

```text
FALSE
0
neutral
cumplimiento
fiabilidad
disponibilidad
```

Cuando existen datos materialmente incompatibles para la misma identidad/dimensión/contexto:

```text
CONFLICTING_DATA
```

Supplier Evidence Core conserva las referencias incompatibles y no selecciona una de forma implícita.

---

## 17. SEC-M13 — Relación con R-PROV-001

La regla vigente menciona proveedores alternativos con condiciones `potencialmente mejores`.

Supplier Evidence Core puede entregar:

- candidatos evidenciados;
- condiciones disponibles por dimensión;
- estados de comparabilidad;
- diferencias observables trazables.

No define `potencialmente mejores`.

`PROV-G06` permanece OPEN bajo autoridad de Rules.

Por tanto, Supplier Evidence Core **no activa R-PROV-001**.

---

## 18. SEC-M14 — Relación con R-PROV-002

La regla vigente exige una alternativa comparable que mejore significativamente precio, plazo, condiciones, fiabilidad o disponibilidad.

Supplier Evidence Core puede aportar la matriz factual necesaria.

No define:

- `significativamente`;
- si una dimensión basta;
- cómo tratar un empeoramiento simultáneo en otra dimensión;
- un score multidimensional;
- una regla de compensación.

`PROV-G07` y `PROV-G08` permanecen OPEN bajo Rules/CRC.

Por tanto, Supplier Evidence Core **no activa R-PROV-002**.

---

## 19. SEC-M15 — Señales críticas

Se puede conservar una señal/incidencia como hecho tipado y trazable:

```text
signal_id
supplier_id
signal_type
observed_at
scope
source_ref
evidence_ref
```

Supplier Evidence Core no asigna por sí mismo:

- criticidad;
- severidad;
- probabilidad;
- efecto R0/R1/R2/R3;
- recomendación.

`PROV-G09` queda cerrable para representación genérica; su taxonomía normativa e impacto permanecen OPEN.

---

## 20. Salida conceptual autorizada

```text
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

La salida es analítica/factual.

No contiene:

```text
supplier_score
supplier_rank
preferred_supplier
supplier_risk_level
recommendation
assessment
effect
severity
crc_result
purchase_decision
```

salvo que una futura autoridad específica lo autorice expresamente.

---

## 21. Estado de gaps tras depuración

| Gap | Estado v0.2 | Tratamiento |
|---|---|---|
| PROV-G01 alternativa actual | CLOSED-FACTUAL | Existencia factual evidenciada mediante SEC-M03 |
| PROV-G02 fiabilidad | OPEN-METRIC | Hechos/referencias sí; métrica nativa no |
| PROV-G03 cumplimiento | OPEN-METRIC | Hechos/referencias sí; métrica nativa no |
| PROV-G04 disponibilidad | CLOSED-FACTUAL / OPEN-VALUATION | Representación sí; superioridad no |
| PROV-G05 concentración | OPEN-METRIC | Solo referencia externa trazable |
| PROV-G06 potencialmente mejores | OPEN-RULES | No se infiere |
| PROV-G07 mejora significativamente | OPEN-RULES | No se infiere |
| PROV-G08 trade-offs | OPEN-RULES/CRC | No se compensa |
| PROV-G09 señales críticas | CLOSED-FACTUAL / OPEN-IMPACT | Señal sí; criticidad/efecto no |

---

## 22. Frontera de implementación potencial

Si Audit 2 valida esta metodología, un contrato técnico podrá materializar **solo** representación factual y trazable del Supplier Evidence Core.

Queda explícitamente fuera de ese contrato futuro:

- supplier score;
- reliability score;
- compliance score;
- concentration calculation;
- supplier ranking;
- supplier preference;
- activación de R-PROV-001/002;
- compensaciones multidimensionales;
- decisión o recomendación.

---

## 23. Criterios de Audit 2

Audit 2 deberá comprobar como mínimo:

1. que SEC-M03 no convierte mera existencia histórica en alternativa actual;
2. que ningún estado de dominio sustituye `Evidence.state` de C0;
3. que precio/comparabilidad PRICE no se recalculan;
4. que disponibilidad no se infiere desde catálogo o histórico;
5. que hechos históricos no se convierten en fiabilidad/riesgo;
6. que métricas externas conservan metodología y fuente;
7. que concentración no se calcula por inferencia;
8. que comparación dimensional no crea ranking ni score;
9. que R-PROV-001/002 permanecen fuera de autoridad del Supplier Evidence Core;
10. que gaps y contradicciones no se convierten en valores favorables/desfavorables;
11. que la salida no contiene campos decisionales;
12. que la metodología puede trasladarse a contrato técnico sin nueva política empresarial.
