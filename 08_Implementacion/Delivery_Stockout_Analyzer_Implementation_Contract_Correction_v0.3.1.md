# EIOS — DELIVERY / STOCKOUT ANALYZER · CONTRACT CORRECTION v0.3.1

**Estado:** CORRECCIÓN PRE-AUDIT 2 FINAL  
**Fecha:** 11/09/2026  
**Base:** `Delivery_Stockout_Analyzer_Implementation_Contract_v0.3.md`

---

## 1. Motivo

La revisión pre-final detecta una ambigüedad residual en la forma:

```text
DeliveryTimingEvidenceState = NOT_DETERMINABLE
+ expected_delivery_date != None
```

Sin una restricción adicional, esa forma podría representar indistintamente:

- aplicabilidad de propuesta no demostrada;
- semántica de fecha no demostrada;
- otra causa no autorizada.

Eso haría insegura la emisión de:

```text
PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

---

## 2. Corrección vinculante

Para la implementación v0.3, `NOT_DETERMINABLE` puede conservar `expected_delivery_date` **solo** cuando:

1. la fecha factual está identificada;
2. `delivery_semantic_ref` está presente;
3. `source_ref` está presente;
4. `captured_at` está presente;
5. existe al menos un `evidence_ref`;
6. la única precondición no demostrada es la aplicabilidad de esa fecha a la propuesta actual;
7. `purchase_applicability_ref = None`.

Por tanto:

```text
NOT_DETERMINABLE + fecha
→ forma técnica específica de PURCHASE APPLICABILITY UNPROVEN
```

No se utiliza esta forma para ambigüedad semántica u otras causas.

Si la semántica de la fecha tampoco está suficientemente determinada, ENT no publica la fecha operativa:

```text
expected_delivery_date = None
state = NOT_DETERMINABLE
```

---

## 3. Regla de fecha pasada corregida

Con la invariante anterior, el engine aplica de forma determinista:

```text
delivery.state = NOT_DETERMINABLE
AND delivery.expected_delivery_date is not None
AND delivery.expected_delivery_date < delivery.evaluation_date
→ NOT_DETERMINABLE
+ PAST_DELIVERY_DATE_APPLICABILITY_UNPROVEN
```

No necesita inferir causalidad desde nombres, textos o refs parciales.

---

## 4. Resto del contrato

Todo el contenido de v0.3 permanece vigente salvo donde esta corrección lo precisa.

No cambia:

- los estados ENT;
- la comparación temporal;
- el horizonte;
- STK;
- Supplier;
- Rules;
- RDM;
- Assessment;
- parámetros;
- persistencia.

---

## 5. Estado

**CORRECCIÓN v0.3.1 MATERIALIZADA.**

Procede Audit 2 final sobre el contrato compuesto:

```text
v0.3 + Correction v0.3.1
```
