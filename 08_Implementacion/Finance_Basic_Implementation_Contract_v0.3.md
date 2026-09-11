# EIOS — FINANCE BASIC · IMPLEMENTATION CONTRACT v0.3

**Estado:** DEPURADO FINAL — PENDIENTE DE AUDIT 2 FINAL  
**Fecha:** 11/09/2026  
**Dominio:** Capa 4 — Finanzas Básica  
**Metodología:** Finance Basic v0.3 🔒

---

## 1. Paquete físico

```text
eios/finance/
    __init__.py
    models.py
    engine.py

tests/test_finance_basic.py
```

No se modifica C0.

---

## 2. Tipos controlados

```text
FlowType = PAYMENT | COLLECTION
FinancialEvidenceState = DEMONSTRATED | NOT_EVIDENCED | CONFLICTING_DATA
CalculationStatus = DETERMINED | NOT_EVIDENCED | NOT_EVALUABLE | CONFLICTING_DATA
```

Precedencia representacional:

```text
CONFLICTING_DATA > NOT_EVIDENCED > NOT_EVALUABLE > DETERMINED
```

Todas las limitaciones se conservan.

---

## 3. Currency propia del dominio financiero

Finance Basic usa códigos monetarios como `str` de 3 caracteres en sus modelos propios.

No reutiliza `eios.core.models.Currency` porque C0 restringe ese tipo a `EUR` y Finance Basic debe poder conservar una moneda incompatible para devolver `NOT_EVALUABLE` sin inventar FX.

No se valida catálogo ISO ni se convierte moneda; solo se exige forma de 3 caracteres y se normaliza a mayúsculas.

---

## 4. FinancialSnapshot

```text
FinancialSnapshot
- company_scope: str
- as_of_date: date
- data_snapshot_id: str
- currency: str[3]
- available_treasury: Decimal | None >= 0
- treasury_evidence_ref: str | None
- external_liquidity: ExternalLiquidityReference | None
```

`available_treasury` presente exige `treasury_evidence_ref`.

La proyección posterior sí puede producir saldos negativos.

---

## 5. ExternalLiquidityReference

```text
ExternalLiquidityReference
- value: Decimal
- unit: str
- source_ref: str
```

Es solo contexto trazable. No participa en cálculos ni reglas del core v0.1.

---

## 6. CashFlow

```text
CashFlow
- flow_id: str
- flow_type: PAYMENT | COLLECTION
- amount: Decimal | None >= 0
- currency: str[3]
- due_date: date | None
- source_ref: str | None
- evidence_state: FinancialEvidenceState
```

`DEMONSTRATED` exige `amount`, `due_date`, `source_ref`.

Estados no demostrados pueden conservar campos parciales pero nunca contribuyen cuantitativamente.

---

## 7. WorkingCapitalInput

```text
WorkingCapitalInput
- company_scope: str
- as_of_date: date
- currency: str[3]
- current_assets: Decimal | None
- current_liabilities: Decimal | None
- assets_source_ref: str | None
- liabilities_source_ref: str | None
```

Cada magnitud presente exige su fuente. Finance Basic no reclasifica cuentas.

---

## 8. FinanceBasicInput

```text
FinanceBasicInput
- context: DecisionContext
- snapshot: FinancialSnapshot
- cash_flows: tuple[CashFlow, ...]
- horizon_days: int > 0
- treasury_minimum: Decimal | None
- working_capital_input: WorkingCapitalInput | None
```

Validaciones:

- `snapshot.data_snapshot_id == context.data_snapshot_id`;
- `flow_id` únicos;
- `horizon_days > 0`;
- `treasury_minimum`, si existe, finito;
- no existen defaults empresariales;
- `context.parameters_version` conserva versión de parámetros.

---

## 9. Temporalidad de flujos

`horizon_end = as_of_date + horizon_days`.

### DEMONSTRATED

- `due_date <= as_of_date` → `NOT_EVALUABLE`, `NON_FUTURE_FLOW:<id>`;
- `as_of_date < due_date <= horizon_end` → participa si moneda compatible;
- `due_date > horizon_end` → excluido sin gap.

### NOT_EVIDENCED

- fecha desconocida → `NOT_EVIDENCED`;
- fecha dentro del horizonte y faltan datos → `NOT_EVIDENCED`;
- fecha demostrada posterior al horizonte → excluido del horizonte sin contaminarlo.

### CONFLICTING_DATA

- si puede afectar al horizonte o la temporalidad no es resoluble → `CONFLICTING_DATA`;
- si existe fecha demostrada posterior al horizonte, la contradicción no contamina esa proyección concreta.

---

## 10. ProjectionPoint

```text
ProjectionPoint
- date
- collections
- payments
- treasury_after
```

Los flujos participantes se agregan por fecha antes de actualizar tesorería.

---

## 11. ProjectionResult

```text
ProjectionResult
- status
- horizon_end
- opening_treasury
- points
- financial_capacity_forecast
- unresolved_flow_ids
- limitations
```

`DETERMINED` exige apertura demostrada y ausencia de incidencia relevante.

Cálculo:

```text
closing(day) = prior + collections(day) - payments(day)
financial_capacity_forecast = min(opening_treasury, closing(day_1), ..., closing(day_n))
```

Si el status global no es `DETERMINED`, `financial_capacity_forecast = None` y `points = ()` en el MVP v0.1 para evitar interpretación parcial.

---

## 12. WorkingCapitalResult

```text
WorkingCapitalResult
- status
- value
- limitations
```

- ambos valores presentes + mismo scope/fecha/moneda que snapshot → `DETERMINED`;
- falta alguno → `NOT_EVIDENCED`;
- incompatibilidad de scope/fecha/moneda → `NOT_EVALUABLE`;
- no invalida la proyección de tesorería.

Fórmula:

```text
current_assets - current_liabilities
```

---

## 13. SafetyMarginResult

```text
SafetyMarginResult
- status
- value_pct
- limitations
```

- projection DETERMINED + `treasury_minimum > 0` → DETERMINED;
- minimum ausente → NOT_EVIDENCED;
- minimum <= 0 → NOT_EVALUABLE;
- projection no determinada → propaga su status.

Fórmula:

```text
(capacity - treasury_minimum) / treasury_minimum * 100
```

No se cuantiza ni se compara con `P-FIN-004`.

---

## 14. FinanceBasicResult

```text
FinanceBasicResult
- decision_id
- scenario_id
- data_snapshot_id
- parameters_version
- currency
- projection
- working_capital
- safety_margin
- external_liquidity
```

No contiene recomendación, Assessment, efecto, severidad ni CRC.

---

## 15. No mutación y validación estructural

Todos los modelos propios usan `extra='forbid'`; entradas y resultados son frozen.

Se rechazan estructuralmente:

- IDs vacíos;
- flow IDs duplicados;
- amount negativo/no finito;
- available_treasury negativo/no finito;
- horizon <= 0;
- snapshot/context con snapshot IDs distintos;
- DEMONSTRATED incompleto;
- códigos de moneda con longitud distinta de 3.

La ausencia legítima de evidencia se conserva como estado analítico, no como excepción estructural.

---

## 16. Tests obligatorios

1. proyección simple;
2. capacidad mínima correcta;
3. agregación por fecha independiente del orden;
4. IDs duplicados rechazados;
5. moneda incompatible produce NOT_EVALUABLE;
6. flujo fuera del horizonte no contamina;
7. fecha desconocida no evidenciada produce NOT_EVIDENCED;
8. contradicción relevante produce CONFLICTING_DATA;
9. flujo no futuro produce NOT_EVALUABLE;
10. apertura ausente ≠ 0;
11. apertura negativa rechazada;
12. working capital determinado;
13. working capital parcial/incompatible explícito;
14. safety margin determinado;
15. minimum ausente/<=0 explícito;
16. precedencia de status independiente del orden;
17. external liquidity preserva valor/unidad/fuente pero no afecta cálculo;
18. inputs no mutados;
19. no existen campos decisionales.

---

## 17. Exclusiones

Sin Rules, CRC, FX, financiación, TCO financiero, forecasting probabilístico, optimización, SQL, ERP, API/UI ni simulación contable de working capital proyectado.
