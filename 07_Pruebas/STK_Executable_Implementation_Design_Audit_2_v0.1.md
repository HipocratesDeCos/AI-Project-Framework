# EIOS — STK Executable Implementation Design · Audit 2 v0.1

**Estado:** NO SUPERADA — DEPURACIÓN B1…B4 REQUERIDA  
**Diseño auditado:** `STK_Executable_Implementation_Design_v0.2`  
**Contrato:** STK Implementation Contract v0.17  
**Fecha:** 11/09/2026

---

## 1. Dictamen

A1…A8 quedan resueltos, pero el cruce literal final con §§23–25 y 30–35 del contrato v0.17 detecta **4 discrepancias de implementación**.

No requieren autoridad empresarial nueva.

**DICTAMEN:** NO CERRAR v0.2. Depurar B1…B4 y repetir Audit 2 final.

---

## 2. B1 — Schedule debe incluir demanda genérica Y confirmada

**BLOQUEANTE.**

El diseño v0.2 exige igualdad del schedule únicamente con movimientos `AUTHORIZED_DEMAND` y afirma que `CONFIRMED_DEMAND` no puede satisfacer el conjunto.

El contrato v0.17 es explícito:

> el conjunto exacto de movimientos `AUTHORIZED_DEMAND | CONFIRMED_DEMAND` coincide con `DemandProjectionSchedule.demand_movement_ids`.

**Corrección:** el set exacto del schedule es la unión de ambos source kinds. La reconciliación autorizada del schedule es precisamente la que evita duplicar demanda genérica, confirmada y reservas/obligaciones.

---

## 3. B2 — `demand_schedule` pertenece al payload contractual

**BLOQUEANTE.**

El diseño propone:

```text
calculate_stock_projection(payload, demand_schedule=None)
```

pero el contrato define `StockProjectionInput` con `demand_schedule: DemandProjectionSchedule` como miembro del input.

Hacerlo opcional y externo permite construir dos APIs distintas y debilita la reproducibilidad del payload.

**Corrección:**

```text
calculate_stock_projection(payload: StockProjectionInput)
```

El schedule siempre está materializado en el input. Puede tener estado no determinado cuando falte transformación/evidencia; en ese caso la proyección dependiente no es `KNOWN`. No se sustituye por `None` fuera del modelo.

---

## 4. B3 — M08 necesita evaluación por ramas de dependencia

**BLOQUEANTE.**

La depuración A7 podría interpretarse como exigencia incondicional de ledger/orders `KNOWN` antes de cualquier resultado M08.

Eso convertiría en `NO_VERIFICABLE` casos donde `NO_APLICABLE` ya está demostrado de forma independiente, por ejemplo `ExcessResult = NO_EXCESS / WITHIN_TOLERANCE`.

**Corrección:** orden técnico de evaluación:

1. exceso no determinado → M08 no verificable/estado dependiente;
2. exceso determinado distinto de `EXCESS` → `NO_APLICABLE`, absorción 0/residual según contrato, sin exigir ledger para demostrar una asignación inexistente;
3. `EXCESS` + colección de pedidos `KNOWN` vacía → `NO_EXISTE`; no se exige plan;
4. solo cuando existe `EXCESS` y pedidos potencialmente aplicables se exige ledger/saldos/aplicabilidad para calcular absorción;
5. falta de evidencia que impida demostrar aplicabilidad/exclusión → `NO_VERIFICABLE`.

Esto no omite ledger cuando materialmente afecta a reutilización de cantidades.

---

## 5. B4 — Igualdad del schedule se evalúa sobre la colección contractual

**BLOQUEANTE.**

El diseño habla de movimientos “que participan”. El contrato exige igualdad con los movement IDs `AUTHORIZED_DEMAND | CONFIRMED_DEMAND` **presentes en la colección** de la proyección.

Filtrar primero por conveniencia podría ocultar un movimiento de demanda adicional no reconciliado.

**Corrección:** antes del cálculo diario:

```text
schedule_ids == ids únicos de todos los movimientos
                source_kind in {AUTHORIZED_DEMAND, CONFIRMED_DEMAND}
                presentes en payload.movements.items
```

si la colección es `KNOWN`. Después se aplica el gate temporal de cada movimiento. Un registro explícitamente `NOT_APPLICABLE` sigue formando parte de la evidencia de entrada, y su tratamiento debe ser coherente con la transformación/reconciliación suministrada; no se borra para conseguir artificialmente igualdad.

---

## 6. Sin nuevos bloqueos

Se confirman limpios:

- A1 propagación determinista;
- A2 state↔payload;
- A4 exclusividad M06;
- A5 composición confirmada;
- A6 normalización M07;
- A8 mínimo/depletion;
- C0 y autoridad humana;
- ausencia de defaults;
- fronteras Rules/CRC/MED.

---

## 7. Resultado

**B1…B4: ABIERTOS.**

Siguiente paso: **DEPURAR diseño v0.3 → AUDIT 2 FINAL**.
