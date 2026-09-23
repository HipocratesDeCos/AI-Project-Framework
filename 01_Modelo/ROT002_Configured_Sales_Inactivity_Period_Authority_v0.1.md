# EIOS — ROT002 Configured Sales-Inactivity Period Authority v0.1

**Baseline de autorización:** `main @ 8109c7d45629c271ed0bd7733ae1f5273820ec3a`  
**Fecha:** 23/09/2026  
**Estado:** AUTORIZADO  
**Regla afectada:** `R-ROT-002 — Producto sin rotación`  
**Gate:** `ROT-G01`

## 1. Autoridad humana

Se autoriza expresamente `P-ROT-001` y la semántica propuesta en `ROT002_Configured_Sales_Inactivity_Period_Authority_Proposal_v0.1.md`.

La autorización cubre exclusivamente el periodo configurado requerido por la condición documental de `R-ROT-002`:

> No existen ventas durante el periodo configurado.

No autoriza todavía el bridge completo de la regla, sus excepciones, escalada R0 ni una política empresarial concreta de duración.

## 2. Identificador canónico

Se establece:

```text
P-ROT-001
```

Nombre canónico:

```text
Periodo de inactividad de ventas
```

Función exclusiva inicial:

> Definir la longitud temporal de la ventana utilizada para evaluar la condición factual de `R-ROT-002`.

`P-ROT-001` no gobierna `R-ROT-001` y no define una métrica general de rotación.

## 3. Unidad y tipo

Unidad:

```text
días
```

Tipo:

```text
INTEGER positivo
```

Restricción:

```text
period_days >= 1
```

No se autorizan:

- cero;
- negativos;
- decimales;
- alias textuales;
- conversión implícita desde meses o años.

## 4. Política empresarial

No se establece valor empresarial por defecto.

El valor debe proceder de configuración empresarial vigente.

Si no existe configuración válida y evidenciada:

```text
R-ROT-002 → NOT_EVALUABLE
```

No se permite fallback silencioso.

## 5. Fecha de evaluación

Se autoriza:

```text
evaluation_date = PurchaseOperation.operation_date
```

No debe sustituirse por:

- reloj del sistema;
- `Evidence.captured_at`;
- `effective_at` de parámetros;
- fecha inferida desde `data_snapshot_id`.

## 6. Ventana temporal

Con `period_days` resuelto:

```text
window_end = evaluation_date
window_start = evaluation_date - (period_days - 1 días)
```

La ventana es inclusiva:

```text
window_start <= sale_event_date <= window_end
```

La autoridad no redefine qué constituye una venta válida. Esa semántica permanece en Track A y en sus referencias de fuente.

## 7. Configuración y provenance

La futura materialización debe consumir:

```text
ResolvedConfiguration(P-ROT-001)
+
Evidence de configuración
```

y comprobar coherencia con:

- `DecisionContext.parameters_version`;
- empresa/scope autorizado;
- vigencia aplicable;
- operación y contexto evaluados.

Un entero desprendido no constituye autoridad suficiente.

## 8. Binding con SalesActivityWindowEvidence

La evaluación deberá comprobar correspondencia exacta entre la ventana autorizada y el carrier factual:

```text
article_id = PurchaseOperation.article_id
evaluation_date = PurchaseOperation.operation_date
window_end = PurchaseOperation.operation_date
window_start = ventana derivada de P-ROT-001
```

Debe conservarse además la provenance propia de `SalesActivityWindowEvidence`.

## 9. Mapeo factual autorizado

Sin aplicar todavía excepciones:

```text
ZERO_VALID_SALES_DEMONSTRATED
→ condición factual satisfecha

SALES_ACTIVITY_PRESENT
→ condición factual no satisfecha

NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
→ NOT_EVALUABLE
```

La ausencia de evidencia no puede convertirse en FALSE.

## 10. Dependencia canónica

Queda autorizada la relación:

```text
P-ROT-001 → R-ROT-002
```

como dependencia `PARAMETER` directa de la condición temporal de la regla.

También quedan autorizados como dependencias de binding:

```text
PurchaseOperation.article_id
PurchaseOperation.operation_date
ResolvedConfiguration(P-ROT-001)
Evidence de configuración
SalesActivityWindowEvidence
```

No se autoriza reutilizar `P-STK-006`, `P-PYE-001` ni otro parámetro temporal de distinto dominio.

## 11. No alcance

Esta autoridad no resuelve:

- `R-ROT-001`;
- fórmula o métrica general de rotación;
- umbral de baja rotación;
- excepciones de `R-ROT-002`;
- escalada R1 → R0;
- `active_result` técnico de CRC;
- campaña prevista;
- operación estratégica;
- decisión empresarial explícita;
- productor universal de ventas.

## 12. Gate

```text
ROT-G01 → CLOSED
```

El cierre de `ROT-G01` no equivale al cierre completo de `R-ROT-002`.

## 13. Estado

**P-ROT-001 / ROT-G01 — AUTORIZADO Y CERRADO EN SU ALCANCE.**
