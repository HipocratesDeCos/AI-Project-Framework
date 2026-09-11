# EIOS — FINANCE BASIC · AUTHORITY v0.1

**Estado:** APROBADO  
**Fecha:** 11/09/2026  
**Baseline:** EIOS Vertical MVP  
**Origen:** `Finance_Basic_Authority_Proposal_v0.1.md`  
**Autorización:** instrucción explícita del decisor del proyecto en la conversación EIOS: `Continúa sin detenerte.`

---

## 1. Alcance de la autorización

Se aprueba íntegramente, sin modificaciones de contenido, el paquete metodológico conservador `FIN-AUTH-v0.1` presentado previamente.

Esta autorización resuelve los gaps metodológicos FIN-G01…FIN-G07 únicamente dentro del alcance MVP definido en la propuesta. No autoriza todavía implementación técnica ni modifica la autoridad de Rules, CRC, MED, TCO, STK o Centro de Parametrización.

---

## 2. FIN-AUTH-01 — Horizonte financiero

`P-FIN-001 — Horizonte de pagos` queda autorizado como horizonte metodológico de la proyección financiera de Finance Basic.

No se redefine como parámetro directo de `R-FIN-001`.

Cadena autorizada:

```text
P-FIN-001
   ↓
Finance Basic projection horizon
   ↓
financial_capacity_forecast
   ↓
R-FIN-001
```

El valor empresarial vigente sigue gobernado por Centro de Parametrización. Esta autoridad no valida por sí sola el valor inicial de 30 días.

---

## 3. FIN-AUTH-02 — Tesorería disponible

Para el MVP:

> **Tesorería disponible = saldos monetarios efectivamente disponibles para atender pagos en `as_of_date`, demostrados por fuente válida.**

Se excluyen por defecto saldos restringidos/no utilizables, líneas de crédito no dispuestas, financiación posible no confirmada, cobros futuros todavía no realizados y activos no monetarios.

No se impone un catálogo universal de cuentas contables.

---

## 4. FIN-AUTH-03 — Liquidez

No se crea un ratio de liquidez propio de EIOS en el MVP inicial.

Finance Basic puede consumir una magnitud de liquidez ya demostrada por una fuente competente, conservarla como contexto analítico/trazable y mantenerla separada de tesorería.

No activa reglas mientras RDM no demuestre una dependencia específica.

---

## 5. FIN-AUTH-04 — Fondo de maniobra

Se autoriza para el MVP:

```text
working_capital = current_assets - current_liabilities
```

Restricciones:

1. activo y pasivo corriente deben pertenecer al mismo `company_scope` y corte temporal;
2. no se mezclan balances de fechas distintas;
3. la clasificación contable procede de una fuente autorizada;
4. Finance Basic no reclasifica cuentas;
5. un valor post-operación debe estar suministrado/evidenciado o derivarse mediante transformación contable expresamente autorizada;
6. Finance Basic no inventa el efecto contable de una compra para fabricar `working_capital_projected`.

---

## 6. FIN-AUTH-05 — Proyección de tesorería

Se autoriza la proyección cronológica:

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

Reglas obligatorias:

- los pagos de la compra se incorporan como `confirmed_payments` de la propia proyección;
- no existe una segunda resta separada del pago de compra;
- cada flujo se computa una sola vez;
- cobros/pagos no demostrados no se sustituyen por cero ni se estiman;
- monedas incompatibles bloquean agregación salvo normalización FX autorizada;
- `P-FIN-005/006` se consumen conforme a su relación autorizada con `R-FIN-001`, sin generalización implícita.

---

## 7. FIN-AUTH-06 — Capacidad financiera prevista

Para el MVP:

```text
financial_capacity_forecast
=
minimum_projected_treasury_within_authorized_horizon
```

Relación autorizada con `R-FIN-001`:

```text
financial_capacity_forecast < P-FIN-002
→ condición R-FIN-001 activada
```

Finance Basic produce la magnitud analítica; Rules conserva la autoridad sobre efecto, severidad y resultado.

---

## 8. FIN-AUTH-07 — Margen de seguridad financiera

Se autoriza:

```text
financial_safety_margin_pct
=
(financial_capacity_forecast - treasury_minimum)
/ treasury_minimum
× 100
```

con:

```text
treasury_minimum = P-FIN-002
```

`P-FIN-004` representa el colchón porcentual mínimo deseado.

Condición cuantitativa ordinaria autorizada para evaluación posterior por `R-FIN-003`:

```text
financial_safety_margin_pct < P-FIN-004
```

La eventual escalada R1→R0 no queda autorizada por este documento.

Si `treasury_minimum <= 0`, el indicador porcentual queda `NOT_EVALUABLE`; no se crea un denominador alternativo.

---

## 9. Límites

Esta autorización no habilita:

- financiación automática;
- uso de líneas de crédito como tesorería disponible por defecto;
- FX implícito;
- forecasting de flujos no evidenciados;
- scoring financiero;
- optimización financiera;
- ejecución de pagos/cobros/compras;
- decisión automática;
- nuevas reglas;
- implementación técnica inmediata.

TCO permanece separado del flujo de caja. Finance Basic no sustituye Rules, CRC, MED ni el sistema contable.

---

## 10. Siguiente gate obligatorio

Tras esta autoridad:

```text
DEPURACIÓN FINAL
→ AUDIT 2 DE CIERRE
→ CIERRE METODOLÓGICO
→ AUDITORÍA DE ENTRADA A CONTRATO TÉCNICO
→ CONTRATO TÉCNICO
```

No se autoriza saltar directamente a código.
