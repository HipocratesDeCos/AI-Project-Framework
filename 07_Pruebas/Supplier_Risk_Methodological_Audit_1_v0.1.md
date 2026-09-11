# EIOS — SUPPLIER / RISK · METHODOLOGICAL AUDIT 1 v0.1

**Estado:** COMPLETADA — DEPURACIÓN REQUERIDA  
**Fecha:** 11/09/2026  
**Objeto:** `01_Modelo/Supplier_Risk_Methodological_Design_v0.1.md`

---

## 1. Dictamen

La autoridad vigente permite cerrar una capa de **representación de evidencia y alternativas de proveedor**, pero no permite todavía cerrar un motor cuantitativo de riesgo/fiabilidad ni activar determinísticamente `R-PROV-001/002`.

La arquitectura funcional confirma además que no existe scoring decisional autorizado y que los bloqueos/criterios deben permanecer en sus autoridades específicas.

---

## 2. Hallazgos

### PROV-A1-01 — “Proveedor/Riesgo” es demasiado amplio para el alcance autorizado

La arquitectura enumera fiabilidad, cumplimiento, riesgo, alternativas, concentración, histórico y señales, pero no define fórmulas ni umbrales.

**Depuración:** separar:

```text
Supplier Evidence Core
    → hechos / candidatos / referencias
Supplier Risk Metrics
    → futuro, cuando exista metodología autorizada
Rules R-PROV
    → evaluación posterior
```

---

### PROV-A1-02 — Quality & Trust no puede reutilizarse como supplier reliability

Q&T evalúa calidad/confianza de evidencia y entrada, no desempeño del proveedor.

**Resultado:** separación confirmada; mantener PROV-P03 como invariante.

---

### PROV-A1-03 — Alternativa actual puede definirse como hecho, no como valoración

Puede cerrarse metodológicamente que un `alternative_candidate` requiere evidencia de una oferta/propuesta/capacidad atribuible a un proveedor diferente para el objeto evaluado.

No puede cerrarse que sea “mejor”.

**PROV-G01:** RESOLUBLE como criterio de existencia factual.

---

### PROV-A1-04 — Precio debe consumirse, no recalcularse

PRICE ya gobierna comparabilidad/normalización de precio. Supplier Evidence Core debe conservar `price_result_ref` o valor fuente, pero no redefinir PR/PO/PMR/comparabilidad.

---

### PROV-A1-05 — Plazo/entrega no equivalen a fiabilidad

Una fecha prometida o lead time evidenciado es una condición de oferta. El histórico de cumplimiento de fechas es otro hecho distinto.

No debe inferirse fiabilidad desde una única promesa ni disponibilidad desde histórico.

---

### PROV-A1-06 — Fiabilidad/cumplimiento solo pueden cerrarse como hechos elementales

No existe autoridad para score, ratio, ventana temporal, peso o umbral.

**PROV-G02/G03:** permanecen OPEN para métrica; se pueden representar eventos sin valoración agregada.

---

### PROV-A1-07 — Disponibilidad: representación posible, valoración no

Puede representarse una afirmación evidenciada de disponibilidad ligada a artículo/oferta/fecha/fuente.

No existe criterio universal para traducirla a “mejor disponibilidad”.

**PROV-G04:** parcialmente resoluble como hecho; valoración permanece OPEN.

---

### PROV-A1-08 — Concentración no tiene metodología suficiente

No se ha demostrado denominador, periodo, alcance ni umbral.

**PROV-G05:** OPEN. Solo referencia externa contextual si está definida y trazable.

---

### PROV-A1-09 — R-PROV-001/002 siguen sin criterio ejecutable completo

`potencialmente mejores` y `mejora significativamente` no disponen de criterio cerrado por dimensión ni trade-off.

**PROV-G06/G07/G08:** OPEN y bloquean implementación de las reglas, pero no bloquean Supplier Evidence Core.

---

### PROV-A1-10 — Señales críticas deben ser hechos tipados, no efecto automático

Puede conservarse una señal/incidencia evidenciada con tipo, fecha, alcance y fuente. La taxonomía definitiva y su criticidad no deben inventarse.

**PROV-G09:** representación genérica posible; impacto permanece OPEN.

---

## 3. Resultado por gap

| Gap | Resultado Audit 1 |
|---|---|
| PROV-G01 alternativa actual | CERRABLE como existencia evidenciada |
| PROV-G02 fiabilidad | HECHOS sí / MÉTRICA no |
| PROV-G03 cumplimiento | HECHOS sí / MÉTRICA no |
| PROV-G04 disponibilidad | HECHO sí / valoración comparativa no |
| PROV-G05 concentración | OPEN; referencia externa únicamente |
| PROV-G06 “potencialmente mejores” | OPEN Rules |
| PROV-G07 “mejora significativamente” | OPEN Rules |
| PROV-G08 trade-offs | OPEN Rules/CRC |
| PROV-G09 señales críticas | HECHOS sí / impacto no |

---

## 4. Decisión de depuración

Depurar el diseño a v0.2 con alcance:

> **Supplier Evidence Core — representación factual y trazable de proveedor y alternativas, sin scoring ni decisión.**

Este alcance puede auditarse y potencialmente cerrarse sin introducir política empresarial nueva.
