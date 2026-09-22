# EIOS — PAG002 Counterfactual Due-Date Proposal Audit v0.1

**Baseline:** `main @ 2776cb85f5fc6e2c112d131e39ed4e4855c1bd69`  
**Fecha:** 22/09/2026  
**Estado:** AUDIT 2 DE PROPUESTA — APTA PARA AUTORIZACIÓN HUMANA

## A1 — Ancla temporal

La propuesta no usa operation/invoice/receipt date.

Usa exclusivamente la baseline due_date evidenciada y aplica un delta de plazo.

Esto evita inventar la fecha de inicio contractual.

## A2 — Multicuota

Queda explícitamente fuera de v0.1.

No se promedian ni desplazan múltiples vencimientos.

## A3 — Evidencia vs hipótesis

La due_date simulada no se etiqueta como hecho.

Se conserva en un envelope SCENARIO_ONLY y se materializa mediante AuthorizedScenarioChange.

## A4 — Finance Basic

No se cambia su fórmula ni su horizonte.

El wrapper contrafactual debe reconstruir y recalcular internamente, preservando todas las entradas salvo la due_date autorizada.

## A5 — Cambio único

Se exige identidad material completa entre baseline y counterfactual.

Esto cierra el riesgo de atribuir a un plazo de pago una mejora producida por otro cambio.

## A6 — Días fraccionarios

Se rechazan para date arithmetic; no se redondean.

## A7 — Documentary Payment

La cadena existente puede demostrar asociación installment_ref ↔ flow_id ↔ operación, pero no autoriza por sí misma la fecha contrafactual. Esta propuesta cubre únicamente esa transformación futura si es aprobada.

## Dictamen

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ✅
AUDITAR 2     ✅
CERRAR        ⛔ autorización humana
MATERIALIZAR  ⛔
```

**0 bloqueadores documentales para someter PAG002 Counterfactual Due-Date Authority v0.1 a autorización humana.**
