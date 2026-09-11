# EIOS — SUPPLIER EVIDENCE CORE · METHODOLOGICAL AUDIT 2 v0.2

**Estado:** COMPLETADA — DEPURACIÓN FINAL REQUERIDA  
**Fecha:** 11/09/2026  
**Objeto:** `01_Modelo/Supplier_Evidence_Core_Methodological_Design_v0.2.md`

---

## 1. Dictamen

El diseño v0.2 corrige el exceso de alcance detectado en Audit 1 y mantiene la frontera factual de Capa 5.

No introduce score, ranking, umbrales, fórmulas de fiabilidad, cálculo de concentración ni activación de `R-PROV-001/002`.

Sin embargo, Audit 2 detecta **cuatro ambigüedades contractuales** que deben cerrarse antes de declarar la metodología lista para contrato técnico.

Ninguna requiere nueva política empresarial; son restricciones de autoridad, trazabilidad y representabilidad.

---

## 2. Hallazgos

### PROV-A2-01 — Comparabilidad estructural ≠ comparabilidad de R-PROV-002

SEC-M10/M11 utiliza estados `comparable / no comparable / unknown`.

Aunque el texto posterior impide activar `R-PROV-002`, la palabra `comparable` puede inducir a un futuro consumidor a interpretar que la capa ha satisfecho el requisito normativo de “alternativa comparable”.

**Riesgo:** ampliación implícita de autoridad desde una compatibilidad de datos hacia una condición de regla.

**Depuración obligatoria:** distinguir expresamente:

```text
STRUCTURALLY_COMPARABLE
NOT_STRUCTURALLY_COMPARABLE
UNKNOWN
```

La comparabilidad estructural únicamente indica que dos representaciones pueden ponerse lado a lado sin incompatibilidad semántica/técnica conocida.

Debe quedar explícito:

```text
STRUCTURALLY_COMPARABLE
    ≠
RULE_COMPARABLE para R-PROV-002
```

`RULE_COMPARABLE` permanece sin definición cerrada salvo por autoridades especializadas concretas, como PRICE para su propia dimensión.

---

### PROV-A2-02 — Candidato actual requiere aplicabilidad temporal/contextual demostrable

SEC-M03 permite evidencia atribuible aplicable “a la operación o contexto evaluado” y conserva temporalidad cuando sea necesaria.

La formulación todavía permite que una oferta histórica sin vigencia demostrada sea tratada como `EVIDENCED_CANDIDATE` actual.

**Depuración obligatoria:** para declarar `EVIDENCED_CANDIDATE` respecto de la operación actual debe poder demostrarse que la evidencia pertenece al contexto evaluado y que no existe una incompatibilidad temporal conocida.

Si la evidencia solo demuestra capacidad histórica o una oferta expirada/no vigente, se conserva como referencia histórica pero **no** como candidato actual evidenciado.

La ausencia de prueba de vigencia cuando sea material se trata como `NOT_EVIDENCED` respecto de la candidatura actual, no como `FALSE` sobre la capacidad general del proveedor.

---

### PROV-A2-03 — Métrica externa documentada ≠ métrica autorizada para comparación

SEC-M08 exige `methodology_ref`, pero una mera referencia metodológica no demuestra que esa metodología tenga autoridad dentro de EIOS ni que sea comparable con otra métrica.

**Riesgo:** incorporar un score externo opaco a la matriz dimensional y convertirlo de facto en valoración autorizada.

**Depuración obligatoria:** distinguir dos usos:

```text
AUTHORIZED_EXTERNAL_METRIC
CONTEXT_ONLY_METRIC
```

Una métrica solo puede participar en comparación analítica autorizada si la metodología, alcance, unidad y autoridad de uso son suficientes y trazables.

En otro caso se conserva únicamente como contexto, sin compararla ni derivar preferencia.

Esto no crea una lista universal de proveedores de métricas ni una autoridad externa nueva.

---

### PROV-A2-04 — Falta identidad contextual explícita en la salida conceptual

La metodología exige trazabilidad y menciona `decision_context_reference` en el objeto de compra, pero la salida conceptual no hace obligatoria la identidad del contexto evaluado.

**Riesgo:** resultado factual correcto pero no inequívocamente vinculable a `Decision_ID / Scenario_ID / Data_Snapshot_ID`.

**Depuración obligatoria:** la salida debe conservar explícitamente la identidad contextual disponible del procesamiento, alineada con Decision Versioning y sin redefinir C0.

Como mínimo conceptual:

```text
decision_id
scenario_id
data_snapshot_id
```

cuando el Supplier Evidence Core opere dentro de un `DecisionContext` EIOS.

---

## 3. Comprobaciones superadas

Audit 2 confirma que v0.2 preserva correctamente:

1. Q&T confidence ≠ supplier reliability;
2. GAP/ausencia ≠ FALSE/neutralidad;
3. PRICE se consume y no se recalcula;
4. TCO, STK y Finance no se duplican;
5. disponibilidad ≠ catálogo ≠ histórico;
6. promesa de entrega ≠ historial de cumplimiento;
7. hechos históricos ≠ reliability/risk score;
8. concentración no se calcula;
9. R-PROV-001/002 no se ejecutan;
10. no existe supplier score/ranking;
11. no se resuelven contradicciones arbitrariamente;
12. no se emite recomendación o decisión.

---

## 4. Estado de gaps tras Audit 2

| Gap | Estado |
|---|---|
| PROV-G01 | Cerrable factual tras precisión temporal/contextual A2-02 |
| PROV-G02 | OPEN-METRIC |
| PROV-G03 | OPEN-METRIC |
| PROV-G04 | CLOSED-FACTUAL / OPEN-VALUATION |
| PROV-G05 | OPEN-METRIC |
| PROV-G06 | OPEN-RULES |
| PROV-G07 | OPEN-RULES |
| PROV-G08 | OPEN-RULES/CRC |
| PROV-G09 | CLOSED-FACTUAL / OPEN-IMPACT |

---

## 5. Decisión

**AUDIT 2 v0.2: NO CERRABLE TODAVÍA.**

Requiere una depuración final v0.3 limitada a:

1. `STRUCTURALLY_COMPARABLE` ≠ `RULE_COMPARABLE`;
2. aplicabilidad temporal/contextual de candidato actual;
3. `AUTHORIZED_EXTERNAL_METRIC` vs `CONTEXT_ONLY_METRIC`;
4. identidad contextual explícita del resultado.

Tras esas cuatro correcciones deberá ejecutarse Audit 2 final. No se autoriza todavía contrato técnico ni implementación.
