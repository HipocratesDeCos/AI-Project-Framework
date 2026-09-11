# EIOS — ROTACIÓN · METHODOLOGICAL AUDIT 2 v0.2

**Estado:** AUDIT 2 — HALLAZGO CORRECTIVO  
**Fecha:** 11/09/2026  
**Objeto auditado:** `Rotation_Methodological_Design_v0.2.md`

---

## 1. Resultado general

La separación `TRACK-A / TRACK-B` es correcta y evita introducir una fórmula de rotación no autorizada.

Sin embargo, Audit 2 identifica **un hallazgo bloqueante de precisión semántica** antes del cierre parcial de Track A.

---

## 2. ROT-A2-01 — “cantidad agregada = 0” no equivale necesariamente a “no existen ventas”

El diseño v0.2 admite conceptualmente:

```text
sales_records / aggregated_sales_quantity
```

como entrada.

Esto puede permitir una implementación errónea:

```text
sum(sales_quantity) == 0
→ ZERO_SALES_DEMONSTRATED
```

La transformación no está autorizada.

Casos que podrían producir un neto cero sin demostrar ausencia de ventas:

- venta y devolución compensadas;
- venta anulada posteriormente;
- cantidades positivas y negativas;
- registros de ajuste;
- eventos comerciales con cantidad cero;
- fuentes con semántica documental heterogénea.

La condición oficial de `R-ROT-002` es:

> no existen ventas durante el periodo configurado.

Por tanto, el análisis debe demostrar **ausencia de eventos de venta válidos según una semántica de fuente autorizada**, no solo un agregado numérico igual a cero.

---

## 3. Corrección obligatoria

Track A deberá reemplazar cualquier posible regla implícita de suma por un objeto/evidencia conceptual equivalente a:

```text
SalesActivityWindowEvidence
├── article_id
├── window_start
├── window_end
├── source_ref
├── source_semantics_ref
├── completeness_ref
├── valid_sales_activity_state
├── evidence_refs
└── trace_refs
```

con estados conceptuales:

```text
SALES_ACTIVITY_PRESENT
ZERO_VALID_SALES_DEMONSTRATED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

`source_semantics_ref` debe demostrar qué registros constituyen una venta válida para esa fuente.

ROT no redefine facturación, devoluciones, anulaciones ni contabilidad comercial.

---

## 4. Resto de Audit 2

### Separación STK

LIMPIA.

No existe conversión:

```text
consumption/demand/coverage → rotation
```

### Parámetros

LIMPIO COMO GAP.

No se inventan `P-ROT-*` ni se reutilizan STK/DAT.

### RDM

LIMPIO COMO GAP.

No se registran dependencias canónicas no demostradas.

### Excepciones

LIMPIO.

Track A no aplica excepciones y no crea una dependencia automática con STK-M08.

### Track B

CORRECTAMENTE BLOQUEADO.

No aparece fórmula, unidad, ventana o umbral implícitos.

### Decisión/CRC

LIMPIO.

ROT no decide ni consolida resultados.

---

## 5. Dictamen

**AUDIT 2 v0.2: NO SUPERADA — 1 HALLAZGO CORRECTIVO.**

Hallazgo único:

`ROT-A2-01 — evitar que net sales quantity = 0 se interprete como ausencia de ventas.`

Debe emitirse diseño v0.3 y repetir Audit 2 final.
