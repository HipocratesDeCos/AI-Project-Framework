# EIOS — FINANCE BASIC · ENTRY TO TECHNICAL CONTRACT AUDIT v0.1

**Estado:** SUPERADA — APTO PARA DISEÑAR CONTRATO TÉCNICO  
**Fecha:** 11/09/2026  
**Metodología:** `01_Modelo/Finance_Basic_Methodological_Design_v0.3.md`  
**Cierre:** `01_Modelo/Finance_Basic_Methodological_Closure_v0.3.md`

---

## 1. Objetivo

Verificar que existe autoridad suficiente para diseñar un contrato técnico ejecutable de Finance Basic sin inventar política, modificar C0 ni invadir Rules/CRC.

---

## 2. Resultado por gate

| Gate | Resultado | Observación |
|---|---|---|
| Metodología cerrada | PASS | v0.3 cerrada tras Audit 2 |
| Autoridad financiera | PASS | FIN-AUTH-v0.1 aprobada |
| Entradas identificables | PASS | snapshot, tesorería, flujos, parámetros financieros |
| Temporalidad definida | PASS | as_of_date + horizonte + due_date |
| Moneda definida | PASS | sin FX implícito |
| Doble cómputo resuelto | PASS | flow_id único y pago de compra como flujo normal |
| Capacidad prevista definida | PASS | mínimo de tesorería proyectada |
| Working capital definido | PASS | current_assets - current_liabilities |
| Safety margin definido | PASS | fórmula autorizada |
| Liquidez acotada | PASS | referencia externa, sin ratio propio |
| No data ≠ zero | PASS | invariante cerrada |
| C0 estable | PASS | no requiere nuevos campos en PurchaseOperation |
| Rules/CRC separados | PASS | contrato analítico, no decisional |
| TCO separado | PASS | coste económico ≠ flujo monetario |
| Patrón físico disponible | PASS | dominios existentes usan models/engine/tests |

---

## 3. Frontera física recomendada

Nuevo dominio:

```text
eios/finance/
    __init__.py
    models.py
    engine.py
```

Tests:

```text
tests/test_finance_basic.py
```

Documentación:

```text
08_Implementacion/Finance_Basic_Implementation_Contract.md
```

No se modifican por este gate:

- `eios/core/models.py`;
- `eios/rules/*`;
- `eios/tco/*`;
- `eios/stock/*`;
- CRC;
- SQL.

---

## 4. Decisiones físicas permitidas

El contrato técnico puede definir modelos propios para:

- `FinancialSnapshot`;
- `CashFlow`;
- `FinanceBasicInput`;
- `ProjectionPoint`;
- `FinanceBasicResult`;
- estado analítico financiero propio.

Puede usar `Decimal`, `date`, tuples y Pydantic v2 conforme al repositorio.

Puede imponer validaciones estructurales necesarias para hacer ejecutables invariantes ya cerradas, por ejemplo:

- importes finitos/no negativos donde corresponda;
- identidad única de flujo;
- fechas de flujo posteriores a `as_of_date` para proyección futura;
- horizonte positivo;
- compatibilidad monetaria;
- coherencia de company_scope y snapshot;
- no mutación.

Estas validaciones implementan metodología existente y no crean política empresarial nueva.

---

## 5. Límites técnicos obligatorios

El contrato no puede:

- evaluar `R-FIN-*`;
- devolver resultados oficiales del MED;
- introducir financiación presunta;
- crear FX;
- usar `float` para dinero;
- usar defaults empresariales para FIN-001…006;
- convertir ausencia en 0;
- inferir working capital post-operación;
- reusar TCO como cash outflow sin flujo explícito.

---

## 6. Riesgos a resolver dentro del contrato

1. definir la semántica exacta de completitud de la proyección;
2. distinguir flujo fuera de horizonte de flujo no evidenciado;
3. ordenar varios flujos del mismo día determinísticamente sin que el orden artificial cambie el mínimo intradía;
4. definir si el mínimo se evalúa por evento o por fecha agregada;
5. representar `treasury_minimum <= 0` sin excepción accidental;
6. evitar que `working_capital` parcial se presente como determinado;
7. asegurar IDs duplicados rechazados antes del cálculo.

Estos riesgos son cerrables técnicamente sin nueva política si el contrato adopta agregación por fecha para evitar dependencia del orden intradía.

---

## 7. Dictamen

**GO — DISEÑAR CONTRATO TÉCNICO FINANCE BASIC v0.1.**

No existe autorización para saltar directamente a implementación antes de AUDITAR → DEPURAR → AUDITAR 2 → CERRAR el contrato.
