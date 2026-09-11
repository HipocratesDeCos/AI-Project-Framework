# EIOS — FINANCE BASIC · IMPLEMENTATION AUDIT 1 v0.1

**Estado:** COMPLETADA — 2 HALLAZGOS DEPURABLES  
**Fecha:** 11/09/2026  
**Contrato:** Finance Basic Implementation Contract v0.3.1 🔒

---

## FIN-IMPL-A1-01 — Evidencia parcial de due_date no representada

### Hallazgo

El contrato permite excluir un flujo `NOT_EVIDENCED` o `CONFLICTING_DATA` cuando su `due_date` está **demostrada** como posterior al horizonte. La implementación inicial usaba simplemente `due_date is not None` como equivalente a “fecha demostrada”.

Eso no es suficiente: un objeto puede estar en `CONFLICTING_DATA` precisamente porque la fecha esté en conflicto.

### Corrección

Añadir a `CashFlow`:

```text
due_date_evidenced: bool = False
```

Semántica:

- `DEMONSTRATED` ya implica evidencia integral y no depende del flag;
- en `NOT_EVIDENCED` / `CONFLICTING_DATA`, una fecha solo permite exclusión temporal si `due_date_evidenced=True`;
- `due_date_evidenced=True` exige `due_date` no nula;
- una fecha presente sin ese flag no se utiliza para declarar el flujo fuera de horizonte.

Este campo no crea política: materializa la condición “due_date demostrada” ya contenida en el contrato v0.3.1.

---

## FIN-IMPL-A1-02 — Desbordamiento técnico de horizonte

### Hallazgo

`horizon_days > 0` no garantiza que `as_of_date + timedelta(days=horizon_days)` sea representable por Python. Un valor extremadamente grande podría provocar `OverflowError` dentro del engine.

### Corrección

`FinanceBasicInput` debe validar estructuralmente que el horizonte pueda materializarse respecto de `snapshot.as_of_date`.

No se fija máximo empresarial. Solo se rechaza un valor técnicamente irrepresentable.

---

## Verificaciones sin hallazgo

- status precedence correcta;
- same-day aggregation correcta;
- ausencia de opening treasury no se convierte en cero;
- moneda incompatible no usa FX;
- working capital independiente;
- safety margin no cuantizado;
- inputs frozen y motor no muta;
- no existen campos decisionales;
- C0 permanece intacto.

## Dictamen

**DEPURAR → repetir Audit 2 de implementación.**
