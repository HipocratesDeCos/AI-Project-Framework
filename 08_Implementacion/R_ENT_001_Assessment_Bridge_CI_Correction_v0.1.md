# EIOS — R-ENT-001 · Assessment Bridge CI Correction v0.1

**Estado:** CORRECCIÓN DE TEST AUTORIZADA  
**Fecha:** 11/09/2026  
**CI afectado:** EIOS Tests #599  
**PR:** #77

---

## 1. Hallazgo ejecutable

CI #599 ejecutó la suite Python y obtuvo:

```text
1 failed, 584 passed
```

Único fallo:

```text
test_not_evidenced_ent_maps_to_not_evaluable
```

La excepción fue:

```text
ValueError:
delivery_evidence.demonstration_ref no pertenece a la provenance delivery
```

---

## 2. Causa

El fixture upstream `PurchaseSpecificDeliveryTimingEvidence(state="NOT_EVIDENCED")` conserva como provenance válida:

```text
source_ref = "source:delivery"
trace_refs = ("trace:delivery",)
```

pero no publica `evidence_refs=("evidence:delivery",)` porque dicho ref solo existe en el fixture `KNOWN`.

El test utilizaba por defecto un objeto C0:

```text
Evidence(
    state="DEMONSTRATED",
    demonstration_ref="evidence:delivery",
)
```

Por tanto el bridge rechazó correctamente un `demonstration_ref` que no pertenecía a la provenance role-specific del input `NOT_EVIDENCED`.

---

## 3. Corrección

No se modifica código productivo.

El test utilizará:

```text
demonstration_ref = "trace:delivery"
```

que sí pertenece explícitamente a la provenance del fixture upstream `NOT_EVIDENCED`.

El estado ENT seguirá siendo:

```text
NOT_EVIDENCED
```

y el resultado esperado seguirá siendo:

```text
Assessment.status = NOT_EVALUABLE
Assessment.outcome = None
```

---

## 4. Autoridad preservada

La corrección no cambia:

- la condición de `R-ENT-001`;
- el mapeo ENT → Assessment;
- el binding role-specific de evidencia;
- `Evidence Contract`;
- C0;
- ENT;
- STK;
- Supplier;
- RDM;
- parámetros;
- SQL.

No se debilita la validación para hacer pasar el test.

---

## 5. Resultado

**CI #599: fallo atribuible exclusivamente al fixture del test.**  
**Corrección autorizada:** actualizar el test y repetir CI sobre un nuevo HEAD.
