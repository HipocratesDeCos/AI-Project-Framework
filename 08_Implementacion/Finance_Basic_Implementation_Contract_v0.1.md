# EIOS — FINANCE BASIC · IMPLEMENTATION CONTRACT v0.1

**Estado:** DISEÑADO — PENDIENTE DE AUDIT 1  
**Fecha:** 11/09/2026  
**Dominio:** Capa 4 — Finanzas Básica  
**Metodología:** Finance Basic v0.3 🔒

---

## 1. Propósito

Definir el núcleo físico determinista mínimo para materializar Finance Basic sin modificar C0 ni evaluar reglas de negocio.

El núcleo calcula consecuencias financieras. No produce Assessment, resultado MED ni resolución CRC.

---

## 2. Paquete físico

```text
eios/finance/
    __init__.py
    models.py
    engine.py

tests/test_finance_basic.py
```

No se modifica `eios/core/models.py`.

---

## 3. Tipos controlados

```text
FlowType = PAYMENT | COLLECTION
FinancialEvidenceState = DEMONSTRATED | NOT_EVIDENCED | CONFLICTING_DATA
CalculationStatus = DETERMINED | NOT_EVIDENCED | NOT_EVALUABLE | CONFLICTING_DATA
```

Estos estados pertenecen a Finance Basic y no redefinen `AssessmentStatus`.

---

## 4. FinancialSnapshot

Contrato conceptual físico:

```text
FinancialSnapshot
- company_scope: str
- as_of_date: date
- data_snapshot_id: str
- currency: Currency
- available_treasury: Decimal | None
- treasury_evidence_ref: str | None
- external_liquidity_reference: Decimal | None
- liquidity_evidence_ref: str | None
```

Invariantes:

- `available_treasury` presente exige `treasury_evidence_ref`;
- referencia de liquidez presente exige evidencia;
- ausencia no se transforma en 0;
- decimales deben ser finitos.

---

## 5. CashFlow

```text
CashFlow
- flow_id: str
- flow_type: FlowType
- amount: Decimal | None
- currency: Currency
- due_date: date | None
- source_ref: str | None
- evidence_state: FinancialEvidenceState
```

Para `DEMONSTRATED` se requieren `amount`, `due_date` y `source_ref`.

Para `NOT_EVIDENCED` o `CONFLICTING_DATA` se permite conservar campos parciales, pero no pueden contribuir cuantitativamente.

`amount` representa magnitud positiva; el signo deriva de `flow_type`.

---

## 6. WorkingCapitalInput

```text
WorkingCapitalInput
- company_scope: str
- as_of_date: date
- currency: Currency
- current_assets: Decimal | None
- current_liabilities: Decimal | None
- assets_source_ref: str | None
- liabilities_source_ref: str | None
```

Si ambas magnitudes están demostradas y son comparables:

```text
working_capital = current_assets - current_liabilities
```

Finance Basic no reclasifica cuentas.

---

## 7. FinanceBasicInput

```text
FinanceBasicInput
- context: DecisionContext
- snapshot: FinancialSnapshot
- cash_flows: tuple[CashFlow, ...]
- horizon_days: int > 0
- treasury_minimum: Decimal | None
- working_capital_input: WorkingCapitalInput | None
```

Coherencias:

- `snapshot.data_snapshot_id == context.data_snapshot_id`;
- `flow_id` no puede repetirse;
- todos los cálculos monetarios del núcleo operan en `snapshot.currency`;
- `horizon_days` es valor ya resuelto de `P-FIN-001`; Finance Basic no aporta default;
- `treasury_minimum`, cuando exista, es valor ya resuelto de `P-FIN-002`; Finance Basic no aporta default.

La trazabilidad de versión de parámetros se conserva mediante `context.parameters_version`.

---

## 8. ProjectionPoint

```text
ProjectionPoint
- date: date
- collections: Decimal
- payments: Decimal
- treasury_after: Decimal
```

Los flujos demostrados se agregan por `due_date` antes de modificar tesorería. Así, varios flujos del mismo día no generan un mínimo artificial dependiente del orden de iteración.

---

## 9. ProjectionResult

```text
ProjectionResult
- status: CalculationStatus
- horizon_end: date
- opening_treasury: Decimal | None
- points: tuple[ProjectionPoint, ...]
- financial_capacity_forecast: Decimal | None
- unresolved_flow_ids: tuple[str, ...]
- limitations: tuple[str, ...]
```

### DETERMINED

Requiere tesorería de apertura demostrada y ausencia de flujos no resolubles que puedan afectar al horizonte.

### NOT_EVIDENCED

Se usa cuando falta tesorería de apertura o existe un flujo potencialmente aplicable cuya evidencia cuantitativa/temporal sea insuficiente.

### CONFLICTING_DATA

Se usa cuando un flujo relevante se marca como `CONFLICTING_DATA` o existe contradicción material de entrada que impide cálculo único.

### NOT_EVALUABLE

Se usa para una limitación conocida que impide cálculo autorizado, por ejemplo moneda incompatible sin FX.

---

## 10. WorkingCapitalResult

```text
WorkingCapitalResult
- status: CalculationStatus
- value: Decimal | None
- limitations: tuple[str, ...]
```

`DETERMINED` solo cuando activo y pasivo corriente están demostrados, pertenecen a mismo company_scope/fecha y moneda compatible.

---

## 11. SafetyMarginResult

```text
SafetyMarginResult
- status: CalculationStatus
- value_pct: Decimal | None
- limitations: tuple[str, ...]
```

Si proyección es DETERMINED y `treasury_minimum > 0`:

```text
(capacity - treasury_minimum) / treasury_minimum * 100
```

Si `treasury_minimum` falta → `NOT_EVIDENCED`.

Si `treasury_minimum <= 0` → `NOT_EVALUABLE`.

No se compara aquí con `P-FIN-004`; esa comparación pertenece a Rules.

---

## 12. FinanceBasicResult

```text
FinanceBasicResult
- decision_id
- scenario_id
- data_snapshot_id
- parameters_version
- currency
- projection: ProjectionResult
- working_capital: WorkingCapitalResult
- safety_margin: SafetyMarginResult
- external_liquidity_reference: Decimal | None
```

No existe campo `recommendation`, `assessment`, `effect`, `severity` o resultado CRC.

---

## 13. Algoritmo de proyección

1. determinar `horizon_end = as_of_date + horizon_days`;
2. validar tesorería de apertura;
3. clasificar flujos respecto del horizonte;
4. cualquier flujo con `due_date` desconocida y evidencia insuficiente mantiene incompleta la proyección porque no puede demostrarse si cae dentro o fuera del horizonte;
5. flujos demostrados con `due_date <= as_of_date` no se reinterpretan automáticamente como futuros;
6. flujos demostrados con `as_of_date < due_date <= horizon_end` participan;
7. flujos demostrados posteriores a `horizon_end` no participan y no son un gap del horizonte;
8. moneda incompatible en flujo participante → `NOT_EVALUABLE`;
9. agregar por fecha;
10. actualizar tesorería diaria:

```text
closing = prior + collections - payments
```

11. `financial_capacity_forecast = min(opening_treasury, treasury_after de cada point)`;
12. si existe gap/contradicción relevante no se publica una capacidad parcial como determinada.

---

## 14. No mutación

El motor no modifica `DecisionContext`, snapshot, flujos ni working capital input.

Los modelos de datos/resultados se configurarán `extra='forbid'`; resultados serán frozen. Los modelos de entrada propios también serán frozen cuando no exista razón contractual para mutabilidad.

---

## 15. Errores estructurales vs insuficiencia

Se rechaza estructuralmente mediante validación Pydantic:

- `flow_id` vacío;
- ID duplicado dentro de `FinanceBasicInput`;
- importes no finitos;
- `amount < 0`;
- `horizon_days <= 0`;
- snapshot/context con `data_snapshot_id` distintos;
- estado DEMONSTRATED sin campos mínimos.

No se lanza error solo porque falte un dato legítimamente no evidenciado; ese caso debe sobrevivir como estado analítico.

---

## 16. Exclusiones técnicas

El motor no implementa:

- Rules R-FIN-*;
- CRC;
- FX;
- financiación;
- TCO financiero;
- forecast probabilístico;
- persistencia/SQL;
- integración ERP;
- API/UI;
- working capital proyectado por simulación contable.

---

## 17. Tests mínimos obligatorios

1. proyección determinista simple;
2. mínimo de tesorería correcto;
3. agregación de flujos del mismo día independiente del orden;
4. IDs duplicados rechazados;
5. flujo fuera de horizonte ignorado sin gap;
6. flujo sin due_date no evidenciado vuelve proyección incompleta;
7. flujo contradictorio bloquea determinación;
8. moneda incompatible bloquea agregación;
9. opening treasury ausente ≠ 0;
10. working capital correcto;
11. working capital parcial no determinado;
12. safety margin correcto;
13. treasury_minimum ausente/<=0 tratado explícitamente;
14. input no mutado;
15. no existe salida decisional.

---

## 18. Criterio de cierre

El contrato solo puede cerrarse tras Audit 1 → depuración → Audit 2 sin bloqueadores.
