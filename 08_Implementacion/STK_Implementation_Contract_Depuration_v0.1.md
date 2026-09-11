# EIOS — STK Implementation Contract · Depuración v0.1

**Estado:** COMPLETADA  
**Fecha:** 11/09/2026  
**Origen:** `07_Pruebas/STK_Implementation_Contract_Audit_v0.1.md`  
**Contrato resultante:** `08_Implementacion/STK_Implementation_Contract.md` v0.2

---

## 1. Propósito

Materializar las correcciones de Audit 1 sin ampliar autoridad empresarial ni cambiar M01…M10.

---

## 2. Correcciones

| Hallazgo | Corrección materializada | Estado |
|---|---|---|
| A1 Orden intradía arbitrario | Eliminado desempate económico por `movement_id`; movimientos agregados por fecha antes del cierre diario. No se infiere secuencia intradía. | RESUELTO |
| A2 Colección vacía ≠ ausencia | Introducido `CollectionEnvelope` con estado explícito. Solo `KNOWN + items=()` significa conjunto vacío evidenciado. | RESUELTO |
| A3 Identidad M06 | Añadido `supply_identity` separado de `movement_id`; obligatorio para pendiente/tránsito. | RESUELTO |
| A4 `expected_window_days` | Eliminado. Se introduce `HistoricalDemandPolicy.required_period_count` y `ConsumptionPeriod.evidenced_days`; el denominador suma días evidenciados de periodos completos. | RESUELTO |
| A5 `KNOWN` sin traza | `KNOWN` exige `source_ref` o `trace_ref`; valor huérfano no puede ser `KNOWN`. | RESUELTO |
| A6 UNBOUNDED ambiguo | Cobertura cero confirmada se representa con `status=UNBOUNDED`, `coverage_days=null`, `reason=CONFIRMED_ZERO_DEMAND`. | RESUELTO |
| A7 Puntos tras incertidumbre | Cada `ProjectionPoint` tiene estado; desde primera fecha no determinada, los puntos dependientes posteriores no recuperan `KNOWN` automáticamente. | RESUELTO |
| A8 Forecast fuera de horizonte | `evaluation_date` debe estar dentro del horizonte del forecast para cobertura. | RESUELTO |
| A9 Fecha M06 vencida | Prohibido roll-forward automático; fecha anterior a `evaluation_date` no se incorpora como entrada futura determinada. | RESUELTO |

---

## 3. Salvaguardas preservadas

La depuración no cambia:

- C0;
- las fórmulas empresariales autorizadas;
- las reglas `R-STK-001…004`;
- los valores pendientes del catálogo;
- la autoridad de Quality & Trust, Evidence, Motor de Reglas, CRC o MED;
- la decisión humana final.

No se añade forecasting ni transformación ventas → demanda.

---

## 4. Estado

**Audit 1:** 7 bloqueantes + 2 precisiones.  
**Depuración:** 9/9 incorporados.  
**Siguiente paso:** Audit 2 independiente sobre contrato v0.2.
