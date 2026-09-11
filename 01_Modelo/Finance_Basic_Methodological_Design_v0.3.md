# EIOS — FINANCE BASIC · METHODOLOGICAL DESIGN v0.3

**Estado:** DEPURADO FINAL — AUTORIDAD INCORPORADA  
**Fecha:** 11/09/2026  
**Baseline:** EIOS Vertical MVP  
**Autoridad específica:** `Finance_Basic_Authority_v0.1.md`

---

## 1. Propósito

Definir la metodología cerrable de Capa 4 — Finanzas Básica para representar y calcular consecuencias financieras mínimas de una propuesta de compra, con trazabilidad, temporalidad explícita y sin asumir autoridad decisional.

Finance Basic produce hechos y magnitudes analíticas. Rules interpreta condiciones de regla; CRC consolida resultados; el decisor humano conserva la decisión final.

---

## 2. Frontera

Finance Basic puede:

- representar un snapshot financiero por empresa y fecha;
- representar tesorería disponible demostrada;
- representar pagos y cobros futuros demostrados;
- incorporar pagos de la propuesta como flujos identificados, sin doble cómputo;
- proyectar tesorería cronológicamente;
- obtener la capacidad financiera prevista como mínimo de tesorería proyectada del horizonte;
- calcular el margen de seguridad financiera autorizado;
- calcular fondo de maniobra a partir de activo y pasivo corriente ya clasificados por fuente autorizada;
- conservar liquidez externa como contexto cuando esté evidenciada;
- exponer insuficiencias y contradicciones sin convertirlas en cero.

Finance Basic no puede:

- decidir COMPRAR/NEGOCIAR/COMPRAR CONDICIONADO/NO COMPRAR;
- aplicar efectos o severidades de reglas;
- resolver conflictos;
- inventar financiación, FX, flujos o saldos;
- reclasificar cuentas contables;
- convertir TCO en flujo de caja;
- estimar información ausente;
- ejecutar pagos, cobros o compras.

---

## 3. Principios

### FIN-P01 — Ausencia ≠ cero
Un hecho financiero necesario y desconocido no se reemplaza por cero.

### FIN-P02 — Evidencia antes que cálculo
Todo importe cuantitativo debe conservar identidad, fecha/periodo, moneda, fuente y ámbito.

### FIN-P03 — Temporalidad
Toda evaluación usa `as_of_date` y un horizonte identificable.

### FIN-P04 — Moneda
No se agregan importes de monedas incompatibles sin normalización FX autorizada.

### FIN-P05 — Identidad de flujo
Cada flujo tiene identidad estable y se computa como máximo una vez.

### FIN-P06 — Hecho ≠ política
Los umbrales pertenecen a parámetros/versiones autorizadas; Finance Basic no los fija.

### FIN-P07 — Análisis ≠ regla
Las magnitudes FIN no son Assessment ni resultado CRC.

### FIN-P08 — Reconstruibilidad
El resultado conserva snapshot, fuentes y parámetros/metodología aplicables.

---

## 4. FIN-M01 — Snapshot financiero

Información mínima conceptual:

```text
company_scope
as_of_date
data_snapshot_id
base_currency
source_references
```

No se fusionan silenciosamente empresas, cortes o monedas incompatibles.

---

## 5. FIN-M02 — Tesorería disponible

Definición autorizada:

> saldos monetarios efectivamente disponibles para atender pagos en `as_of_date`, demostrados por fuente válida.

Excluye saldos restringidos, financiación posible no confirmada, líneas no dispuestas, cobros futuros y activos no monetarios.

---

## 6. FIN-M03 — Flujos futuros

Cada flujo conserva:

```text
flow_id
flow_type = PAYMENT | COLLECTION
amount
currency
due_date
source_ref
evidence_state
```

Solo flujos demostrados pueden participar en el cálculo. `P-FIN-005/006` conservan su función autorizada ligada a R-FIN-001 y no se generalizan por inferencia.

`P-FIN-001` gobierna el horizonte metodológico de Finance Basic, sin convertirse en parámetro directo de R-FIN-001.

---

## 7. FIN-M04 — Impacto monetario de la propuesta

Un pago atribuible a la propuesta se representa como flujo `PAYMENT` con identidad propia y vencimiento evidenciado.

No se asume pago inmediato por defecto. No se descuenta dos veces. Un descuento solo modifica el flujo si su aplicación efectiva está demostrada.

TCO y flujo de caja permanecen separados.

---

## 8. FIN-M05 — Proyección cronológica de tesorería

Relación autorizada:

```text
treasury(t)
=
opening_available_treasury
+ confirmed_collections(due <= t)
- confirmed_payments(due <= t)
```

para:

```text
as_of_date < t <= horizon_end
```

El cálculo puede representarse por eventos ordenados por vencimiento. Flujos posteriores al horizonte no participan.

Si falta un flujo que la fuente/alcance declara necesario para la proyección, el resultado no debe presentarse como completo.

---

## 9. FIN-M06 — Capacidad financiera prevista

```text
financial_capacity_forecast
=
minimum_projected_treasury_within_authorized_horizon
```

El mínimo incluye la posición de apertura como punto de comparación y los saldos resultantes tras cada fecha de eventos dentro del horizonte.

Finance Basic devuelve la magnitud. La comparación decisional con `P-FIN-002` pertenece a R-FIN-001.

---

## 10. FIN-M07 — Fondo de maniobra

```text
working_capital = current_assets - current_liabilities
```

Ambos valores deben pertenecer al mismo `company_scope`, fecha y moneda comparable. Finance Basic no reclasifica partidas.

Un `working_capital_projected` solo puede consumirse si viene evidenciado o si existe una transformación contable posterior expresamente autorizada. Esta metodología no inventa esa transformación.

---

## 11. FIN-M08 — Margen de seguridad financiera

```text
financial_safety_margin_pct
=
(financial_capacity_forecast - treasury_minimum)
/ treasury_minimum
× 100
```

`treasury_minimum = P-FIN-002`.

Si `treasury_minimum <= 0`, el indicador es no evaluable. No se sustituye denominador.

Finance Basic calcula la magnitud; R-FIN-003 conserva la condición de regla y cualquier escalada R1→R0.

---

## 12. FIN-M09 — Liquidez

El MVP no crea un ratio propio de liquidez.

Puede conservar una magnitud de liquidez externa demostrada como contexto, sin identificarla con tesorería y sin usarla para activar reglas mientras RDM no demuestre dependencia específica.

---

## 13. Estados metodológicos

Para resultados analíticos se requiere distinguir como mínimo:

```text
DETERMINED
NOT_EVIDENCED
NOT_EVALUABLE
CONFLICTING_DATA
```

Estos estados no sustituyen `Assessment.status` de C0. Son estados del dato/cálculo financiero.

---

## 14. Relación con reglas

- R-FIN-001 consume posteriormente `financial_capacity_forecast` y `P-FIN-002` conforme a Rules/RDM.
- R-FIN-002 consume un fondo de maniobra post-operación válido y `P-FIN-003`; esta metodología no fabrica el valor post-operación.
- R-FIN-003 puede consumir `financial_safety_margin_pct` y `P-FIN-004`; la selección de resultado/efecto permanece fuera de Finance Basic.

La metodología no resuelve las ramas configurables de R-FIN-002 ni la escalada de R-FIN-003.

---

## 15. Salida conceptual

```text
financial_snapshot
opening_available_treasury
cash_flows_in_scope
projection_points
financial_capacity_forecast
working_capital
external_liquidity_reference
financial_safety_margin_pct
unresolved_items
source_references
```

Los nombres físicos se fijarán en contrato técnico.

---

## 16. Exclusiones

Fuera de alcance MVP inicial:

- FX engine;
- crédito disponible como tesorería por defecto;
- forecast probabilístico;
- optimización financiera;
- coste de capital;
- ratios financieros no autorizados;
- simulación contable de working capital post-operación;
- ejecución financiera;
- reglas/CRC.

---

## 17. Criterio de cierre

La metodología puede cerrarse cuando Audit 2 confirme:

1. alineación con FIN-AUTH-v0.1;
2. ausencia de doble cómputo;
3. ausencia de FX implícito;
4. separación TCO/cash;
5. separación Finance/Rules/CRC;
6. estados de insuficiencia explícitos;
7. temporalidad reconstruible;
8. no modificación de C0.
