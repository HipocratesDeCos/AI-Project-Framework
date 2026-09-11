# EIOS — FINANCE BASIC · IMPLEMENTATION CONTRACT AUDIT 2 FINDINGS v0.2

**Estado:** NO CERRABLE AÚN — 3 BLOQUEOS TÉCNICOS  
**Fecha:** 11/09/2026  
**Objeto:** `Finance_Basic_Implementation_Contract_v0.2.md`

---

## FIN-IC-A2-01 — Currency de C0 haría imposible la incompatibilidad monetaria

`eios.core.models.Currency` está restringido a `Literal["EUR"]`.

Si Finance Basic reutiliza ese tipo para todos sus flujos, una entrada USD sería rechazada estructuralmente por Pydantic y nunca podría conservarse como `NOT_EVALUABLE / CURRENCY_INCOMPATIBLE`, contradiciendo la metodología.

**Corrección:** Finance Basic define `currency: str` normalizado a código de 3 caracteres en sus modelos propios. No crea FX. La compatibilidad se decide por igualdad con `snapshot.currency`.

---

## FIN-IC-A2-02 — Liquidez externa sin unidad

`external_liquidity_reference: Decimal` no permite saber si la fuente expresa un ratio, porcentaje o importe monetario.

**Corrección:** sustituir por un objeto contextual:

```text
ExternalLiquidityReference
- value: Decimal
- unit: str
- source_ref: str
```

No interviene en reglas ni cálculos del core v0.1.

---

## FIN-IC-A2-03 — Tesorería disponible negativa

FIN-AUTH-02 define tesorería disponible como saldo monetario efectivamente disponible para atender pagos. Un valor de apertura negativo no representa disponibilidad monetaria bajo esa definición y podría encubrir financiación/descubierto no autorizados.

**Corrección:** `FinancialSnapshot.available_treasury`, cuando exista, debe ser `>= 0`. La proyección sí puede producir saldos negativos después de pagos.

---

## Dictamen

Los tres hallazgos son técnicos y se derivan directamente de autoridad ya cerrada.

**Acción:** depurar a contrato v0.3 y repetir Audit 2 final.
