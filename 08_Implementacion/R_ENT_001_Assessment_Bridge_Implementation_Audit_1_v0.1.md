# EIOS — R-ENT-001 · Assessment Bridge Implementation Audit 1 v0.1

**Estado:** NO SUPERADA — 2 BLOQUEADORES  
**Fecha:** 11/09/2026  
**Objeto:** `eios/rules/delivery.py` + tests

---

## 1. Dictamen

La implementación respeta el mapeo, Evidence Contract y frontera Rules/ENT, pero faltan dos invariantes defensivos antes de autorizar cierre técnico.

---

## 2. ENT-IMPL-A1-B01 — identidad interna de analysis_input incompleta

La función valida la identidad exterior de `analysis_input`, pero no comprueba explícitamente que sus dos dependencias internas pertenezcan al mismo contexto objetivo.

Debe exigir adicionalmente:

```text
baseline.decision_id == analysis_input.decision_id
baseline.article_id == analysis_input.article_id
baseline.evaluation_date == analysis_input.evaluation_date
baseline.evaluated_purchase_ref == analysis_input.evaluated_purchase_ref

delivery.decision_id == analysis_input.decision_id
delivery.article_id == analysis_input.article_id
delivery.evaluation_date == analysis_input.evaluation_date
delivery.evaluated_purchase_ref == analysis_input.evaluated_purchase_ref
```

Aunque el analyzer normal detecta estos mismatches, el bridge recibe objetos ya materializados y no debe asumir que `analysis_input` fue necesariamente ejecutado por el engine en la misma llamada.

---

## 3. ENT-IMPL-A1-B02 — resultado concluyente sin precondiciones upstream

La copy-integrity temporal impide alterar fechas, pero no impide construir manualmente un resultado concluyente incompatible con los estados upstream.

Ejemplos que deben rechazarse:

```text
delivery.state = NOT_EVIDENCED
analysis.state = LATE_DELIVERY_DEMONSTRATED
```

```text
baseline.state = NOT_DETERMINABLE
analysis.state = NOT_LATE_DEMONSTRATED
```

```text
depletion.state = KNOWN
analysis.state = NOT_LATE_WITHIN_EVIDENCED_HORIZON
```

### Corrección requerida

Para estados concluyentes:

```text
baseline.state == KNOWN
delivery.state == KNOWN
```

Además:

```text
LATE_DELIVERY_DEMONSTRATED
NOT_LATE_DEMONSTRATED
→ depletion.state == KNOWN

NOT_LATE_WITHIN_EVIDENCED_HORIZON
→ depletion.state == NOT_APPLICABLE
→ horizon.state == KNOWN
```

Esto no recalcula ENT; verifica compatibilidad estructural entre el resultado presentado y sus dependencias.

---

## 4. Puntos superados

- `R-ENT-001` fija rule_id exacto;
- versions/snapshot STK se verifican;
- `scenario_id` no se usa como prueba de baseline;
- GAP/INVALID nunca se convierte a FALSE;
- evidence_ids son IDs C0 reales;
- binding baseline/delivery está separado;
- Rules no invoca `analyze_delivery_stockout()`;
- Assessment no gana campos decisionales;
- no cambios en C0/ENT/STK/Supplier/RDM.

---

## 5. Resultado

**AUDIT 1 IMPLEMENTACIÓN: NO SUPERADA.**  
Procede DEPURAR `delivery.py` + tests y repetir Audit 2.
