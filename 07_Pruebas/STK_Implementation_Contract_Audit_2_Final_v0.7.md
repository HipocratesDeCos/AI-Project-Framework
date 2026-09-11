# EIOS — STK Implementation Contract · Audit 2 Final v0.7

**Estado:** NO SUPERADA — DEPURACIÓN DE COMPOSICIÓN FINAL REQUERIDA  
**Contrato auditado:** `08_Implementacion/STK_Implementation_Contract.md` v0.8  
**Fecha:** 11/09/2026

---

## 1. Dictamen

La v0.8 cierra G1…G2 y conserva resueltos todos los hallazgos anteriores. La auditoría de composición entre demanda, proyección y absorción detecta **2 últimos bloqueos físicos**.

No crean política empresarial. Impiden que una dependencia de Forecast quede semánticamente incoherente y que una misma demanda confirmada reduzca dos veces el mismo exceso.

**DICTAMEN:** NO CERRAR v0.8. Resolver H1…H2 y repetir Audit 2 Final.

---

## 2. H1 — Coherencia de `forecast_version` según método de demanda

**Tipo:** BLOQUEANTE.

v0.8 incorpora correctamente `forecast_version` a `StockResultIdentity`, pero debe cerrar cómo se comporta cuando el método seleccionado es histórico.

Si `StockResultIdentity` deriva `forecast_version` del contexto y a la vez `HISTORICAL_CONSUMPTION` declara no depender de forecast, un contexto con versión no nula podría producir una identidad semánticamente contradictoria.

**Corrección requerida:**

- `AUTHORIZED_FORECAST` exige `context.forecast_version != null` y coincidencia exacta con forecast, `DemandRateResult.forecast_version` e identidad de resultados dependientes;
- `HISTORICAL_CONSUMPTION` exige `context.forecast_version == null`, `DemandRateResult.forecast_version == null` e identidad con `forecast_version == null`;
- no se arrastra una versión de forecast a una evaluación histórica por mera disponibilidad técnica;
- si un escenario empresarial necesita distinguir dos hipótesis de demanda, debe hacerlo mediante el contexto/escenario correspondiente, no mezclando dependencias incompatibles.

---

## 3. H2 — Doble uso de demanda confirmada entre M05 y M08

**Tipo:** BLOQUEANTE.

M05 permite salidas `AUTHORIZED_DEMAND`. M08 permite que demanda comercial confirmada absorba un exceso M07. Si un pedido confirmado ya fue incorporado en la proyección que originó `stock_reference`, volver a contabilizar su cantidad en M08 mitigaría dos veces la misma demanda.

La prohibición M08 de reutilizar una cantidad entre excesos no cubre este caso intermodular M05↔M08.

**Corrección requerida:**

1. `ProjectionMovement` debe poder conservar una identidad de demanda empresarial cuando una salida representa demanda confirmada, equivalente a:

```text
confirmed_demand_id: str | null
```

2. Para `source_kind == AUTHORIZED_DEMAND` procedente de demanda comercial confirmada, `confirmed_demand_id` es obligatorio y trazable.
3. La salida de M05 / referencia proyectada debe conservar el conjunto de IDs de demanda confirmada ya incorporados, sin convertirlo en autoridad de asignación.
4. `StockReferenceValue` de tipo `PROJECTED` conserva `incorporated_confirmed_demand_ids` derivados exclusivamente de movimientos M05 efectivamente contabilizados.
5. M08 excluye de `total_remaining_applicable` cualquier `confirmed_demand_id` cuya cantidad ya esté incorporada en la referencia de stock que produjo el exceso.
6. Para una referencia `CURRENT_AVAILABLE`, el conjunto es vacío salvo evidencia técnica específica de composición autorizada; STK no inventa esa composición.
7. El ledger M08 continúa evitando reutilización entre absorciones; este nuevo control evita reutilización **entre proyección y absorción**.

Si una demanda está solo parcialmente incorporada en M05, una mera lista de IDs sería insuficiente; por tanto, la representación debe conservar **cantidad incorporada por `confirmed_demand_id`**, no únicamente presencia/ausencia.

Representación mínima equivalente:

```text
IncorporatedDemandQuantity
├── confirmed_demand_id: str
├── quantity: Decimal
├── unit: str
└── trace_refs: tuple[str, ...]
```

M08 calcula el saldo absorbible después de descontar tanto la cantidad ya incorporada en M05 como la ya asignada por el ledger M08, sin permitir valores negativos ni doble descuento de la misma cantidad.

---

## 4. Resultado

- A…G: resueltos.
- H1…H2: abiertos en v0.8.

**Siguiente paso:** DEPURAR v0.9 → Audit 2 Final independiente.
