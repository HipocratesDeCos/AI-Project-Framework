# EIOS — FINANCE BASIC · IMPLEMENTATION CONTRACT v0.3.1

**Estado:** DEPURADO FINAL  
**Fecha:** 11/09/2026  
**Supersede:** `Finance_Basic_Implementation_Contract_v0.3.md` únicamente en la representabilidad de moneda de flujos no demostrados.

---

Este contrato conserva íntegramente `Finance_Basic_Implementation_Contract_v0.3.md` salvo la corrección objetiva siguiente, que pasa a ser normativa para implementación.

## CashFlow.currency

Contrato físico autorizado:

```text
CashFlow.currency: str[3] | None
```

Reglas:

1. `DEMONSTRATED` exige `currency`, `amount`, `due_date` y `source_ref`.
2. `NOT_EVIDENCED` puede conservar `currency=None`.
3. `CONFLICTING_DATA` puede conservar `currency=None`.
4. Nunca se hereda silenciosamente `snapshot.currency` cuando la moneda del flujo no está demostrada.
5. Si `due_date` está demostrada y es posterior a `horizon_end`, el flujo queda fuera de ese horizonte aunque otros atributos no estén demostrados.
6. Si un flujo puede afectar al horizonte y su moneda no está demostrada, conserva el estado analítico del propio flujo (`NOT_EVIDENCED` o `CONFLICTING_DATA`).
7. Un flujo DEMONSTRATED con moneda distinta de `snapshot.currency` produce `NOT_EVALUABLE / CURRENCY_INCOMPATIBLE:<flow_id>`; no se aplica FX.

## FinancialSnapshot.currency

Permanece obligatorio como `str` de tres caracteres porque define la moneda base del cálculo.

## Resto del contrato

Todas las secciones, invariantes, tests obligatorios, exclusiones y fronteras de `v0.3` permanecen vigentes sin modificación.
