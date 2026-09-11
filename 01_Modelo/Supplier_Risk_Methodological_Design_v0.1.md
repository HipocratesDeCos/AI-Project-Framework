# EIOS — SUPPLIER / RISK · METHODOLOGICAL DESIGN v0.1

**Estado:** DISEÑO — PENDIENTE DE AUDIT 1  
**Fecha:** 11/09/2026  
**Baseline:** EIOS Vertical MVP  
**Ámbito:** Capa 5 — Proveedor / Riesgo

---

## 1. Propósito

Definir la frontera metodológica mínima de Capa 5 para representar y comparar hechos relevantes de proveedor sin crear un SRM completo, un score arbitrario ni una autoridad decisional paralela.

La capa debe poder aportar evidencia estructurada sobre:

- proveedor actual;
- proveedores alternativos;
- condiciones comparables;
- comportamiento histórico evidenciado;
- fiabilidad/cumplimiento cuando exista metodología demostrada;
- disponibilidad y entrega cuando estén evidenciadas;
- concentración cuando exista definición autorizada;
- señales críticas trazables.

Este diseño no constituye contrato técnico ni autoriza implementación cuantitativa.

---

## 2. Autoridades

Se subordina a:

- `03_Arquitectura/Architecture_Blueprint.md`;
- `01_Modelo/Especificacion_funcional.md`;
- `05_Motor/Modelo_Empresarial_Decision.md`;
- `04_Reglas/Matriz_Reglas_MVP.md`;
- `04_Reglas/Evidence_Contract.md`;
- `04_Reglas/Rule_Dependency_Matrix.md`;
- `08_Implementacion/Quality_Trust_Implementation_Contract.md`;
- autoridades cerradas de PRICE, TCO, STK y Finance Basic cuando sus resultados sean consumidos.

No se atribuye autoridad normativa a similitudes semánticas entre documentos.

---

## 3. Frontera de responsabilidad

Supplier/Risk puede:

- identificar proveedor actual y alternativas con identidad estable;
- conservar ofertas/condiciones de proveedor evidenciadas;
- consumir resultados comparables ya autorizados de PRICE, pagos, entrega, stock u otras capas;
- conservar historial de incidencias/cumplimientos como hechos;
- exponer dimensiones de comparación separadas;
- señalar ausencia, contradicción o no comparabilidad;
- entregar resultados analíticos a Rules/Viability.

Supplier/Risk no puede:

- inventar un score global de proveedor;
- promediar precio, plazo, fiabilidad y disponibilidad para crear una clasificación única;
- convertir confianza de Quality & Trust en fiabilidad del proveedor;
- decidir que un proveedor es “mejor” sin criterio documentado;
- crear umbrales de mejora significativa;
- crear pesos entre dimensiones;
- declarar una alternativa comparable por mera coincidencia de artículo/proveedor;
- ejecutar cambio de proveedor;
- producir COMPRAR/NEGOCIAR/COMPRAR CONDICIONADO/NO COMPRAR;
- resolver conflictos de reglas.

---

## 4. Principios

### PROV-P01 — Evidencia antes que valoración
Un atributo del proveedor solo participa cuando identidad, periodo/contexto, fuente y significado están suficientemente demostrados.

### PROV-P02 — Ausencia ≠ neutralidad
No disponer de incidencias, disponibilidad, fiabilidad o alternativas no significa automáticamente que el proveedor sea fiable, disponible o único.

### PROV-P03 — Calidad de evidencia ≠ desempeño del proveedor
`Quality & Trust confidence` describe la calidad del conjunto evaluado; no es un supplier reliability score.

### PROV-P04 — Dimensiones separadas
Precio, plazo, condiciones, fiabilidad, disponibilidad, cumplimiento y concentración se conservan separadamente salvo transformación autorizada.

### PROV-P05 — Comparabilidad explícita
Una mejora solo puede afirmarse sobre magnitudes comparables bajo la autoridad especializada correspondiente.

### PROV-P06 — Histórico contextual
Una incidencia histórica no se convierte automáticamente en riesgo actual; debe conservar fecha, alcance y contexto.

### PROV-P07 — Análisis ≠ regla
Supplier/Risk no ejecuta R-PROV-001/002; entrega hechos/resultados para su evaluación posterior.

---

## 5. PROV-M01 — Identidad de proveedor

Cada proveedor relevante debe poder identificarse por un identificador estable dentro de la empresa/tenant y vincularse a sus fuentes.

Conceptualmente:

```text
supplier_id
company_scope
source_refs
```

Nombre comercial no constituye por sí solo identidad suficiente cuando existan homónimos o entidades distintas.

---

## 6. PROV-M02 — Alternativa de proveedor

Una alternativa existe metodológicamente cuando hay evidencia de una fuente/propuesta/oferta atribuible a otro proveedor para el objeto de compra evaluado.

La mera existencia de un proveedor maestro o histórico no demuestra que sea una alternativa **disponible para la operación actual**.

Estados conceptuales mínimos:

```text
EVIDENCED_CANDIDATE
NOT_EVIDENCED
CONFLICTING_DATA
```

La existencia de una alternativa no implica que sea comparable ni mejor.

---

## 7. PROV-M03 — Condiciones de alternativa

Las condiciones se conservan por dimensión, cuando existan:

```text
price / price_result_ref
payment_term
commercial_conditions
delivery_date_or_lead_time
availability
quality_or_reliability_reference
other_evidenced_conditions
```

No se rellenan campos desconocidos con valores del proveedor actual ni con defaults.

Cuando una dimensión ya tenga autoridad especializada, Supplier/Risk consume su resultado o dato autorizado y no recalcula su metodología.

---

## 8. PROV-M04 — Comparabilidad

Supplier/Risk no crea una regla universal de comparabilidad económica.

Para afirmar una mejora por **precio**, deberá consumir comparabilidad/normalización autorizada por PRICE.

Para plazo/entrega/condiciones, la comparabilidad requiere como mínimo que el objeto, alcance y contexto evaluado sean compatibles; los criterios exactos permanecen sujetos a autoridad específica cuando no estén ya documentados.

`same item` no implica automáticamente `comparable offer`.

---

## 9. PROV-M05 — Fiabilidad y cumplimiento

La arquitectura exige fiabilidad y cumplimiento, pero las fuentes revisadas no autorizan todavía una fórmula, score, periodo, denominador o umbral universal.

Por tanto, este diseño distingue:

1. **hechos de cumplimiento/incidencia**: eventos evidenciados;
2. **métrica de fiabilidad**: solo consumible si una fuente/metodología competente la define;
3. **valoración global del proveedor**: no autorizada en v0.1.

No se autoriza:

```text
nº incidencias / nº pedidos
```

ni cualquier otra ratio por inferencia.

---

## 10. PROV-M06 — Disponibilidad y entrega

La disponibilidad debe ser evidencia operacional atribuible al proveedor/oferta y al objeto evaluado.

No se identifica automáticamente con:

- existencia en catálogo;
- histórico de entrega;
- stock interno de la empresa;
- promesa no confirmada.

Cuando exista fecha prevista de entrega o lead time evidenciado, puede conservarse y cruzarse posteriormente con la autoridad de stock/entrega aplicable.

Supplier/Risk no redefine `R-ENT-001`.

---

## 11. PROV-M07 — Comportamiento histórico

Cada hecho histórico debe conservar como mínimo conceptual:

```text
event_type
event_date
scope/object
source_ref
evidence_state
```

Ejemplos posibles solo como categorías de hechos, no como score:

- retraso;
- incumplimiento de cantidad;
- rechazo/calidad;
- cancelación;
- discrepancia documental;
- cumplimiento confirmado.

La taxonomía definitiva y su impacto no se consideran autorizados por estos ejemplos.

---

## 12. PROV-M08 — Concentración

La arquitectura reconoce concentración “cuando sea relevante”, pero no se ha demostrado una metodología autorizada para:

- denominador;
- periodo;
- unidad de concentración;
- umbral;
- tratamiento por artículo/familia/empresa;
- impacto decisional.

Por tanto, Supplier/Risk no calcula concentración en v0.1 hasta que exista autoridad suficiente. Puede consumir una métrica externa ya evidenciada como contexto si mantiene definición, periodo y fuente.

---

## 13. PROV-M09 — Comparación multidimensional

La comparación debe preservar una matriz por dimensión:

| Dimensión | Proveedor actual | Alternativa | Estado comparabilidad | Fuente/resultado |
|---|---|---|---|---|
| Precio | dato/resultado | dato/resultado | comparable/no/unknown | PRICE |
| Plazo pago | dato | dato | comparable/no/unknown | fuente/PAG |
| Entrega | dato | dato | comparable/no/unknown | fuente/ENT/STK |
| Disponibilidad | dato | dato | comparable/no/unknown | fuente |
| Fiabilidad | referencia autorizada | referencia autorizada | comparable/no/unknown | metodología futura |
| Otras condiciones | dato | dato | comparable/no/unknown | fuente |

No se agregan dimensiones en una puntuación única.

---

## 14. PROV-M10 — Relación con R-PROV-001

Regla vigente:

> existe uno o más proveedores alternativos con condiciones potencialmente mejores.

Supplier/Risk puede demostrar:

- existencia evidenciada de candidatos;
- dimensiones disponibles;
- diferencias observables cuando sean comparables.

Permanece gap de autoridad definir qué significa exactamente `potencialmente mejores` si la regla pretende activarse por una o varias dimensiones sin criterio adicional.

Supplier/Risk no activa la regla por inferencia.

---

## 15. PROV-M11 — Relación con R-PROV-002

Regla vigente:

> existe una alternativa comparable que mejora significativamente precio, plazo, condiciones, fiabilidad o disponibilidad.

Supplier/Risk puede entregar la matriz de comparación y referencias autorizadas.

Permanecen gaps:

- definición de `significativamente` por dimensión;
- si basta una dimensión o se requiere combinación;
- tratamiento de empeoramientos simultáneos en otras dimensiones;
- definición autorizada de fiabilidad;
- definición operativa de disponibilidad comparable.

No se crea un umbral o score para cerrar estos gaps.

---

## 16. Salida conceptual

```text
supplier_current
alternative_candidates
alternative_evidence
comparison_dimensions
comparability_states
historical_facts
external_reliability_references
external_concentration_reference
unresolved_items
source_references
```

La salida no contiene recomendación ni resultado de regla.

---

## 17. Gaps de autoridad iniciales

| Gap | Materia | Estado |
|---|---|---|
| PROV-G01 | Criterio exacto de alternativa disponible para operación actual | OPEN |
| PROV-G02 | Definición/metodología de fiabilidad de proveedor | OPEN |
| PROV-G03 | Metodología de cumplimiento | OPEN |
| PROV-G04 | Definición operativa comparable de disponibilidad | OPEN |
| PROV-G05 | Metodología de concentración | OPEN |
| PROV-G06 | Criterio `potencialmente mejores` de R-PROV-001 | OPEN |
| PROV-G07 | Umbral/criterio `mejora significativamente` de R-PROV-002 | OPEN |
| PROV-G08 | Regla de trade-offs entre dimensiones en R-PROV-002 | OPEN |
| PROV-G09 | Taxonomía/impacto de señales críticas | OPEN |

---

## 18. Criterio de Audit 1

Audit 1 deberá distinguir:

1. qué gaps pueden resolverse recuperando autoridad documental ya existente;
2. qué conceptos pueden cerrarse como **representación de hechos** sin política nueva;
3. qué puntos requieren verdadera autorización empresarial antes de Rules o de una implementación cuantitativa.
