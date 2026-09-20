# EIOS — Profitability Core Technical Contract v0.1

**Baseline:** `main @ 3f4cad32b544d78f721d6179876f24fbaebfc067`  
**Autoridad:** `MGE-AUTH v0.1`  
**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA — LISTO PARA MATERIALIZACIÓN

## 1. Propósito

Definir el contrato físico mínimo de un `Profitability Core` determinista que calcule margen únicamente sobre bases económicas previamente autorizadas.

El core:

- calcula;
- valida compatibilidad;
- conserva trazabilidad;
- falla cerrado.

El core no:

- selecciona fuentes;
- decide qué precio de venta usar;
- decide qué coste usar;
- convierte TCO en base de margen;
- aplica descuentos o rappels;
- hace FX;
- consume parámetros MGE;
- ejecuta Rules;
- produce Assessment, CRC, recomendación o decisión.

## 2. Posición arquitectónica

Profitability Core es una capacidad analítica especializada del Vertical. No crea una nueva capa decisional.

```text
upstream authorized economic bases
        ↓
Profitability Core
        ↓
analytical profitability result
        ↓
future Rules binding (separate authority)
```

No altera C0, PRICE, TCO, Finance Basic, CRC o MED.

## 3. Entrada física

```text
ProfitabilityInput
├── context: DecisionContext
├── purchase_operation: PurchaseOperation
├── company_scope: str
├── evaluation_date: date
├── sale_basis: AuthorizedSaleBasis
├── cost_basis: AuthorizedCostBasis
└── methodology_version: str
```

### 3.1 Identidad

`purchase_operation.decision_id/scenario_id` deben coincidir con `DecisionContext`.

Cada base autorizada conserva:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
evaluation_date
```

y debe coincidir exactamente con:

- `DecisionContext`;
- `ProfitabilityInput.company_scope`;
- `PurchaseOperation.article_id`;
- `ProfitabilityInput.evaluation_date`.

Una discrepancia de identidad es entrada estructuralmente inválida. No se corrige ni se convierte en fallback.

## 4. Estados de base

Tipo cerrado:

```text
KNOWN
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Tanto `AuthorizedSaleBasis` como `AuthorizedCostBasis` son tipos físicos distintos.

Campos:

```text
state
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
evaluation_date
value
currency
economic_basis_ref
authority_ref
source_ref
transformation_ref
trace_refs
```

### 4.1 Reglas físicas

Si `state = KNOWN`:

- `value` es obligatorio;
- `value >= 0`;
- valor finito;
- `currency` obligatoria;
- `economic_basis_ref` obligatoria;
- `authority_ref` obligatoria;
- `source_ref` obligatoria;
- al menos un `trace_ref`.

Si `state != KNOWN`:

- `value = null`;
- no puede publicarse una magnitud determinada.

La restricción v0.1 `value >= 0` es conservadora: MGE-AUTH no define semántica para bases económicas negativas. Una futura extensión requerirá autoridad propia.

## 5. Compatibilidad obligatoria

Solo se calcula margen cuando ambas bases están `KNOWN` y:

```text
sale.currency == cost.currency
sale.economic_basis_ref == cost.economic_basis_ref
```

Además, sus identidades deben coincidir con la entrada según §3.1.

No existe:

- FX implícito;
- normalización de unidad/basis implícita;
- tolerancia de moneda;
- reconciliación por redondeo;
- selección de una base alternativa.

## 6. Precedencia fail-closed de estados

Si una o ambas bases no son `KNOWN`, el resultado no calcula importes.

Precedencia de salida:

```text
CONFLICTING_DATA
> NOT_EVIDENCED
> NOT_DETERMINABLE
```

Si alguna base está `CONFLICTING_DATA` → resultado `CONFLICTING_DATA`.

En ausencia de conflicto, si alguna está `NOT_EVIDENCED` → `NOT_EVIDENCED`.

En ausencia de los anteriores, si alguna está `NOT_DETERMINABLE` → `NOT_DETERMINABLE`.

No existe estado favorable por defecto.

## 7. Cálculo

Cuando ambas bases son `KNOWN` y compatibles:

```text
margin_amount = sale.value - cost.value
```

No se clampa a cero.

Puede ser:

- positivo;
- cero;
- negativo.

### 7.1 Margen porcentual

Si:

```text
sale.value > 0
```

entonces:

```text
margin_percentage = margin_amount / sale.value × 100
```

No es markup.

### 7.2 Base de venta cero

Si:

```text
sale.value = 0
```

entonces:

```text
margin_amount = 0 - cost.value
margin_percentage = null
calculation_state = NOT_DETERMINABLE
limitation = SALE_BASIS_ZERO
```

Este es el único caso v0.1 en que `calculation_state != DETERMINED` puede conservar un `margin_amount` determinado.

## 8. Incompatibilidad

Si moneda o `economic_basis_ref` no coinciden:

```text
margin_amount = null
margin_percentage = null
calculation_state = NOT_DETERMINABLE
```

Limitaciones cerradas:

- `CURRENCY_INCOMPATIBLE`;
- `ECONOMIC_BASIS_INCOMPATIBLE`.

No se intenta conversión.

## 9. Salida física

```text
ProfitabilityResult
├── decision_id
├── scenario_id
├── data_snapshot_id
├── parameters_version
├── company_scope
├── article_id
├── evaluation_date
├── methodology_version
├── sale_basis
├── cost_basis
├── calculation_state
├── currency
├── economic_basis_ref
├── margin_amount
├── margin_percentage
├── limitations
└── trace_refs
```

La salida conserva las bases autorizadas completas para no desprender el cálculo de su provenance.

### 9.1 Estado de cálculo

Tipo cerrado:

```text
DETERMINED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

### 9.2 Reglas de publicación

`DETERMINED`:

- `margin_amount != null`;
- `margin_percentage != null`;
- `currency != null`;
- `economic_basis_ref != null`.

`NOT_EVIDENCED` o `CONFLICTING_DATA`:

- `margin_amount = null`;
- `margin_percentage = null`.

`NOT_DETERMINABLE`:

- normalmente ambos valores son null;
- excepción exclusiva: `SALE_BASIS_ZERO` puede conservar `margin_amount` y obliga `margin_percentage = null`.

## 10. Trazabilidad

`trace_refs` de resultado es la unión ordenada y deduplicada de:

- `sale_basis.trace_refs`;
- `cost_basis.trace_refs`.

No crea `Trace` paralelo.

`authority_ref`, `source_ref` y `transformation_ref` permanecen dentro de cada base.

## 11. Parámetros y Rules

Profitability Core v0.1 no consume:

- `P-MGE-001`;
- `P-MGE-002`;
- `P-MGE-003`;
- `P-MGE-004`;
- `P-MGE-005`;
- `P-MGE-006`.

Las relaciones existentes:

```text
P-MGE-001 → R-MGE-001
P-MGE-002 → R-MGE-003
P-MGE-003 → R-MGE-002
```

permanecen fuera del core.

Un futuro binding MGE → Rules requerirá contrato provenance-safe independiente.

## 12. TCO / PRICE

`TCOResult` no es `AuthorizedCostBasis`.

`PriceIntelligenceResult` no es `AuthorizedSaleBasis` ni `AuthorizedCostBasis`.

Cualquier adaptación upstream debe:

- disponer de autoridad propia;
- conservar identidad;
- conservar provenance;
- ser explícita.

Profitability Core no contiene adapters PRICE/TCO.

## 13. Descuentos y rappels

No existen campos especiales de descuento/rappel en el engine.

Su efecto solo puede estar ya incorporado en una base autorizada mediante `transformation_ref` trazable.

No se consulta `P-MGE-005/006`.

## 14. Redondeo y precisión

El core usa `Decimal`.

No redondea para cambiar clasificación ni para reconciliar incompatibilidades.

La serialización puede conservar la precisión resultante de Decimal; cualquier política contable de redondeo futura requiere autoridad específica.

## 15. Mutabilidad

Los contratos físicos serán `frozen=True` y `extra="forbid"`.

El engine no modifica inputs.

## 16. API prevista

```python
calculate_profitability(payload: ProfitabilityInput) -> ProfitabilityResult
```

No hay I/O, filesystem, red, SQL, clock implícito o estado global.

`evaluation_date` llega como input; no se usa `date.today()`.

## 17. Errores estructurales vs estados analíticos

Error estructural (`ValueError` / validación):

- identity mismatch;
- `KNOWN` sin value/source/authority/trace;
- valor negativo v0.1;
- value publicado con estado no `KNOWN`.

Estado analítico fail-closed:

- base no evidenciada;
- base contradictoria;
- base no determinable;
- moneda incompatible;
- basis incompatible;
- venta cero para porcentaje.

No se mezclan ambos niveles.

## 18. Invariantes

1. cálculo ≠ regla.
2. cálculo ≠ decisión.
3. evidence/base ≠ source selection.
4. PRICE ≠ sale basis.
5. TCO ≠ cost basis.
6. sale basis y cost basis son tipos distintos.
7. identidad completa debe coincidir.
8. ausencia ≠ cero.
9. contradicción ≠ elección arbitraria.
10. sin FX implícito.
11. sin conversión implícita.
12. sin descuento/rappel implícito.
13. sin parámetros MGE en core.
14. margin percentage usa venta como denominador.
15. sale=0 nunca divide por cero.
16. margin amount puede ser negativo.
17. no fallback.
18. no I/O.
19. no clock implícito.
20. resultado conserva las bases autorizadas.

## 19. Fuera de alcance

- construcción/selección de `AuthorizedSaleBasis`;
- construcción/selección de `AuthorizedCostBasis`;
- adapters desde PRICE/TCO;
- parámetros empresariales MGE;
- Rules R-MGE;
- CRC;
- negociación;
- forecast de venta;
- FX;
- descuentos/rappels calculados;
- persistencia.

## 20. Criterio de materialización

Puede escribirse código solo si Audit 2 confirma:

- conformidad exacta con MGE-AUTH v0.1;
- ninguna autoridad nueva;
- separación PRICE/TCO;
- no consumo de Rules/params;
- fail-closed completo;
- provenance retenida;
- pruebas de casos límite definidas.

