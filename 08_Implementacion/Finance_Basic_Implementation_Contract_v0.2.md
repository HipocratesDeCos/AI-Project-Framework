# EIOS — FINANCE BASIC · IMPLEMENTATION CONTRACT v0.2

**Estado:** DEPURADO — PENDIENTE DE AUDIT 2  
**Fecha:** 11/09/2026  
**Dominio:** Capa 4 — Finanzas Básica  
**Metodología:** Finance Basic v0.3 🔒

---

## 1. Propósito y frontera

Materializar un core financiero determinista que calcule consecuencias financieras mínimas y trazables sin modificar C0 ni ejecutar Rules/CRC.

Paquete:

```text
eios/finance/
    __init__.py
    models.py
    engine.py

tests/test_finance_basic.py
```

No se modifica `eios/core/models.py`.

---

## 2. Tipos controlados

```text
FlowType = PAYMENT | COLLECTION
FinancialEvidenceState = DEMONSTRATED | NOT_EVIDENCED | CONFLICTING_DATA
CalculationStatus = DETERMINED | NOT_EVIDENCED | NOT_EVALUABLE | CONFLICTING_DATA
```

Precedencia representacional cuando coexisten incidencias:

```text
CONFLICTING_DATA
> NOT_EVIDENCED
> NOT_EVALUABLE
> DETERMINED
```

La precedencia solo elige el status global; todas las limitaciones se conservan.

---

## 3. FinancialSnapshot

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

Reglas:

- `available_treasury` presente exige `treasury_evidence_ref`;
- referencia de liquidez presente exige `liquidity_evidence_ref`;
- evidencia sin valor puede conservarse solo si se representa fuera de estos campos; este modelo no fabrica valor;
- `Decimal` no finito se rechaza;
- ausencia permanece ausencia.

---

## 4. CashFlow

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

Reglas:

- `amount`, cuando exista, debe ser finito y `>= 0`;
- el signo deriva de `flow_type`;
- `DEMONSTRATED` exige `amount`, `due_date`, `source_ref`;
- `NOT_EVIDENCED` y `CONFLICTING_DATA` pueden conservar campos parciales;
- ningún estado no demostrado contribuye cuantitativamente.

---

## 5. WorkingCapitalInput

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

Reglas:

- `current_assets` presente exige `assets_source_ref`;
- `current_liabilities` presente exige `liabilities_source_ref`;
- importes presentes deben ser finitos;
- ausencia legítima no lanza error: se representará como `NOT_EVIDENCED`;
- Finance Basic no clasifica partidas contables.

---

## 6. FinanceBasicInput

```text
FinanceBasicInput
- context: DecisionContext
- snapshot: FinancialSnapshot
- cash_flows: tuple[CashFlow, ...]
- horizon_days: int > 0
- treasury_minimum: Decimal | None
- working_capital_input: WorkingCapitalInput | None
```

Validaciones estructurales:

- `snapshot.data_snapshot_id == context.data_snapshot_id`;
- `flow_id` únicos;
- `horizon_days > 0`;
- `treasury_minimum`, si existe, Decimal finito;
- no hay default para FIN-001/FIN-002;
- `context.parameters_version` preserva versión de parametrización.

---

## 7. ProjectionPoint

```text
ProjectionPoint
- date: date
- collections: Decimal
- payments: Decimal
- treasury_after: Decimal
```

Los flujos se agregan por fecha antes de actualizar tesorería. El mínimo no depende del orden arbitrario de eventos del mismo día.

---

## 8. Clasificación temporal de flujos

Sea:

```text
horizon_end = snapshot.as_of_date + timedelta(days=horizon_days)
```

### 8.1 DEMONSTRATED

- `due_date <= as_of_date` → no se reinterpreta como futuro; proyección `NOT_EVALUABLE`, limitación `NON_FUTURE_FLOW:<flow_id>`;
- `as_of_date < due_date <= horizon_end` → participa si moneda compatible;
- `due_date > horizon_end` → excluido del cálculo, sin gap.

### 8.2 NOT_EVIDENCED

- `due_date is None` → `NOT_EVIDENCED`; no puede demostrarse exclusión del horizonte;
- `due_date <= horizon_end` y falta información necesaria → `NOT_EVIDENCED`;
- `due_date > horizon_end` conocida → excluido del cálculo por temporalidad; no hace incompleto el horizonte aunque el amount sea desconocido.

### 8.3 CONFLICTING_DATA

- si la temporalidad es desconocida o puede afectar al horizonte → `CONFLICTING_DATA`;
- si una fecha demostrablemente posterior al horizonte excluye el flujo del horizonte, la contradicción no contamina la proyección de ese horizonte, pero puede conservarse como limitación contextual si el objeto se entrega al motor.

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

Solo cuando:

- tesorería de apertura está demostrada;
- no hay incidencia relevante dentro/potencialmente dentro del horizonte;
- todos los flujos participantes son monetariamente compatibles.

Cálculo:

```text
closing(day) = prior + collections(day) - payments(day)
financial_capacity_forecast = min(opening_treasury, closing(day_1), ..., closing(day_n))
```

Si el status no es `DETERMINED`, `financial_capacity_forecast = None` para impedir falsa precisión, aunque puedan conservarse puntos parciales únicamente si el motor puede producirlos sin inventar datos. La implementación MVP puede optar por devolver `points=()` en resultados no determinados para evitar interpretación parcial.

---

## 10. WorkingCapitalResult

```text
WorkingCapitalResult
- status: CalculationStatus
- value: Decimal | None
- limitations: tuple[str, ...]
```

- ambos valores presentes, misma empresa/fecha/moneda que snapshot → `DETERMINED`, `assets - liabilities`;
- falta uno o ambos → `NOT_EVIDENCED`;
- empresa/fecha/moneda incompatibles → `NOT_EVALUABLE`;
- esta incidencia no invalida por sí misma ProjectionResult.

---

## 11. SafetyMarginResult

```text
SafetyMarginResult
- status: CalculationStatus
- value_pct: Decimal | None
- limitations: tuple[str, ...]
```

- projection `DETERMINED` + `treasury_minimum > 0` → `DETERMINED`;
- `treasury_minimum is None` → `NOT_EVIDENCED`;
- `treasury_minimum <= 0` → `NOT_EVALUABLE`;
- projection no determinada → propaga su status de cálculo cuando sea aplicable.

Fórmula:

```text
(capacity - treasury_minimum) / treasury_minimum * 100
```

`value_pct` es Decimal sin cuantización empresarial en el core.

No se compara con `P-FIN-004`.

---

## 12. FinanceBasicResult

```text
FinanceBasicResult
- decision_id: str
- scenario_id: str
- data_snapshot_id: str
- parameters_version: str
- currency: Currency
- projection: ProjectionResult
- working_capital: WorkingCapitalResult
- safety_margin: SafetyMarginResult
- external_liquidity_reference: Decimal | None
```

No contiene recomendación, Assessment, efecto, severidad ni resultado CRC.

---

## 13. Algoritmo

1. validar estructura del payload;
2. calcular `horizon_end`;
3. evaluar tesorería de apertura;
4. clasificar flujos por evidencia/temporalidad/moneda;
5. acumular todas las limitaciones e IDs irresueltos;
6. seleccionar status mediante precedencia fija;
7. solo si status = DETERMINED, agrupar flujos participantes por fecha y construir puntos;
8. obtener mínimo de tesorería proyectada;
9. calcular working capital de forma independiente;
10. calcular safety margin a partir de ProjectionResult y `treasury_minimum`;
11. devolver resultado frozen y trazable.

---

## 14. No mutación y determinismo

Modelos propios con `extra='forbid'`, `str_strip_whitespace=True` cuando corresponda y `frozen=True` salvo necesidad explícita inexistente en v0.1.

El motor no modifica ningún objeto recibido.

Mismo payload válido → mismo resultado analítico, salvo que no existe timestamp generado por el motor.

---

## 15. Errores estructurales

Pydantic debe rechazar:

- IDs vacíos;
- `flow_id` duplicados;
- amount negativo/no finito;
- horizon <= 0;
- snapshot/context con `data_snapshot_id` distintos;
- DEMONSTRATED incompleto;
- Decimal no finito en campos financieros presentes.

La ausencia legítima de evidencia no es error estructural.

---

## 16. Exclusiones

Sin Rules, CRC, FX, financiación, TCO financiero, optimización, forecast probabilístico, SQL, ERP, API, UI ni simulación contable de working capital proyectado.

---

## 17. Tests obligatorios

1. proyección simple DETERMINED;
2. mínimo de tesorería correcto;
3. same-day aggregation independiente del orden;
4. flow IDs duplicados rechazados;
5. DEMONSTRATED fuera de horizonte ignorado;
6. NOT_EVIDENCED fuera de horizonte por fecha demostrada no contamina horizonte;
7. fecha desconocida no evidenciada → NOT_EVIDENCED;
8. contradicción relevante → CONFLICTING_DATA;
9. moneda incompatible relevante → NOT_EVALUABLE;
10. flujo no futuro → NOT_EVALUABLE;
11. opening treasury ausente ≠ 0;
12. working capital determinado;
13. working capital parcial → NOT_EVIDENCED;
14. working capital scope/date/currency incompatible → NOT_EVALUABLE sin romper proyección;
15. safety margin determinado;
16. minimum ausente/<=0 explícito;
17. precedencia de status independiente del orden;
18. inputs no mutados;
19. ausencia de campos decisionales.

---

## 18. Criterio de cierre

Audit 2 debe verificar todos los invariantes anteriores y ausencia de contradicción con Finance Basic v0.3, C0, TCO y autoridad Rules/CRC.
