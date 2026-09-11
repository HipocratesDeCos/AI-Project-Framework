# EIOS — FINANCE BASIC · AUDIT 2 OBJECTIVE CORRECTION v0.3.1

**Estado:** CORRECCIÓN OBJETIVA PRE-IMPLEMENTACIÓN  
**Fecha:** 11/09/2026

## Hallazgo

El contrato v0.3 declaraba `CashFlow.currency` obligatoria incluso para estados `NOT_EVIDENCED` y `CONFLICTING_DATA`.

Esto impediría representar correctamente un flujo cuya moneda sea precisamente parte de la evidencia ausente/contradictoria, transformando un caso analítico legítimo en error estructural.

## Corrección

En la materialización física:

```text
CashFlow.currency: str[3] | None
```

Reglas:

- `DEMONSTRATED` exige currency, amount, due_date y source_ref;
- `NOT_EVIDENCED` puede tener currency desconocida;
- `CONFLICTING_DATA` puede tener currency desconocida o no resoluble;
- si un flujo no demostrado tiene `due_date` demostrada posterior al horizonte, puede excluirse del horizonte aunque otros atributos sean desconocidos;
- si puede afectar al horizonte y currency es desconocida, conserva el status no demostrado correspondiente;
- no se inventa moneda por defecto a partir de snapshot.

`FinancialSnapshot.currency` permanece obligatoria porque define la moneda base del cálculo.

## Dictamen

La corrección no altera FIN-AUTH-v0.1 ni la metodología Finance Basic v0.3. Cierra una contradicción de representabilidad del contrato técnico antes de código.
