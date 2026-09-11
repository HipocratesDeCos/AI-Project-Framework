# EIOS — FINANCE BASIC · IMPLEMENTATION CONTRACT AUDIT 1 v0.1

**Estado:** COMPLETADA — 6 HALLAZGOS DEPURABLES  
**Fecha:** 11/09/2026  
**Objeto:** `Finance_Basic_Implementation_Contract_v0.1.md`

---

## Hallazgos

### FIN-IC-A1-01 — Flujo demostrado no futuro

El contrato dice que `due_date <= as_of_date` no se reinterpreta, pero no fija resultado.

**Riesgo:** implementación divergente: ignorar, incluir o lanzar error.

**Corrección:** un flujo DEMONSTRATED con vencimiento no posterior a `as_of_date` queda fuera de la semántica de “flujo futuro” y hace la proyección `NOT_EVALUABLE` con limitación explícita `NON_FUTURE_FLOW:<id>`. No se descuenta automáticamente.

---

### FIN-IC-A1-02 — Precedencia de estados múltiples

Una proyección puede contener simultáneamente contradicción, ausencia y moneda incompatible.

**Riesgo:** status dependiente del orden de iteración.

**Corrección:** fijar precedencia representacional, sin autoridad decisional:

```text
CONFLICTING_DATA
> NOT_EVIDENCED
> NOT_EVALUABLE
> DETERMINED
```

Todas las limitaciones se conservan aunque un único status represente el resultado global.

---

### FIN-IC-A1-03 — Evidencia de working capital

El contrato no obliga a asociar cada magnitud disponible con su fuente.

**Corrección:** `current_assets` exige `assets_source_ref`; `current_liabilities` exige `liabilities_source_ref`. Si faltan magnitudes legítimamente, el resultado será `NOT_EVIDENCED`, no error estructural.

---

### FIN-IC-A1-04 — Coherencia working capital vs snapshot

No está cerrado si una fecha/empresa/moneda incompatible invalida todo el input.

**Corrección:** no abortar la proyección de tesorería. `WorkingCapitalResult` queda `NOT_EVALUABLE` con limitaciones específicas si `company_scope`, `as_of_date` o `currency` no coinciden con snapshot. Se preserva independencia de subcálculos.

---

### FIN-IC-A1-05 — Precisión del porcentaje

No debe imponerse redondeo empresarial no autorizado.

**Corrección:** `financial_safety_margin_pct` se mantiene como `Decimal` con la precisión del contexto Decimal de Python; el core no cuantiza ni redondea a una cifra empresarial. Presentación/UI podrá formatear posteriormente sin alterar el valor analítico.

---

### FIN-IC-A1-06 — Fuera de horizonte vs temporalidad desconocida

Un flujo demostrado posterior al horizonte es irrelevante para ese horizonte; un flujo no evidenciado sin fecha no permite saber si es irrelevante.

**Corrección:** distinguir explícitamente:

- `DEMONSTRATED` y `due_date > horizon_end` → excluido de cálculo, sin gap;
- `NOT_EVIDENCED` con `due_date > horizon_end` demostrada → fuera de horizonte respecto de fecha, pero si `amount` no está demostrado no afecta al horizonte porque la fecha ya prueba exclusión;
- due_date desconocida en flujo no resuelto → `NOT_EVIDENCED`, porque no puede demostrarse exclusión;
- `CONFLICTING_DATA` con temporalidad potencialmente dentro del horizonte o no resoluble → `CONFLICTING_DATA`.

---

## Dictamen

No hay contradicción con metodología cerrada ni autoridad adicional requerida.

**Resultado:** DEPURAR contrato a v0.2 y repetir Audit 2.
