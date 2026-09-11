# EIOS — FINANCE BASIC · AUTHORITY PROPOSAL v0.1

**Estado:** PROPUESTA — NO AUTORIZADA  
**Fecha:** 11/09/2026  
**Origen:** `Finance_Basic_Methodological_Audit_2_v0.2.md`  
**Objeto:** Resolver FIN-G01…FIN-G07 mediante una política MVP conservadora

> Este documento **NO tiene autoridad normativa** mientras el decisor del proyecto no lo apruebe expresamente.

---

## 1. Criterio de diseño

La propuesta busca el mínimo financiero útil para el Vertical MVP sin convertir EIOS en un ERP, sistema contable, treasury management system o motor financiero avanzado.

Principios:

- cálculo determinista y explicable;
- datos demostrados, nunca estimaciones silenciosas;
- sin FX implícito;
- sin crédito/financiación presumidos;
- sin inventar ratios no necesarios;
- máxima separación entre análisis financiero y Rules/CRC;
- suficiente para hacer evaluable `R-FIN-001` cuando existan datos;
- `R-FIN-002` utiliza una magnitud de fondo de maniobra demostrada, no un motor contable nuevo.

---

# 2. FIN-AUTH-01 — Horizonte financiero

## Propuesta

Autorizar `P-FIN-001 — Horizonte de pagos` como **horizonte metodológico de la proyección financiera de Finance Basic**.

No se redefine como parámetro directo de `R-FIN-001`.

Relación propuesta:

```text
P-FIN-001
   ↓
Finance Basic projection horizon
   ↓
financial_capacity_forecast
   ↓
R-FIN-001
```

Por tanto, su eventual vínculo con la regla es **indirecto/derivado mediante el componente Finance Basic**, no un consumidor directo inventado.

El valor empresarial vigente continúa gobernado por Centro de Parametrización; este documento no valida el valor inicial de 30 días.

---

# 3. FIN-AUTH-02 — Tesorería disponible

## Propuesta

Para el MVP:

> **Tesorería disponible = saldos monetarios efectivamente disponibles para atender pagos en `as_of_date`, demostrados por fuente válida.**

Incluye únicamente saldos cuya disponibilidad esté acreditada.

Excluye por defecto:

- saldos restringidos/no utilizables;
- líneas de crédito no dispuestas;
- financiación meramente posible;
- cobros futuros todavía no realizados;
- activos no monetarios.

Una línea de crédito o financiación solo podrá intervenir cuando exista una capacidad financiera específica que la represente de forma evidenciada y autorizada; no se incorpora silenciosamente a tesorería.

No se impone en esta fase un catálogo universal de cuentas contables.

---

# 4. FIN-AUTH-03 — Liquidez

## Propuesta

**No crear un nuevo ratio de liquidez calculado por EIOS en el MVP inicial.**

Tratamiento:

- Finance Basic puede consumir una magnitud de liquidez ya demostrada por una fuente competente;
- se conserva como contexto analítico/trazable;
- no se identifica con tesorería;
- no se utiliza para activar una regla mientras RDM no demuestre una dependencia específica;
- un futuro ratio de liquidez requerirá metodología/versionado propio.

Motivo: evita introducir Current Ratio, Quick Ratio u otra convención sin autoridad y sin consumidor de regla demostrado.

---

# 5. FIN-AUTH-04 — Fondo de maniobra

## Propuesta

Adoptar para el MVP la definición empresarial estándar:

```text
working_capital
=
current_assets
-
current_liabilities
```

con estas restricciones:

1. ambas magnitudes deben pertenecer al mismo `company_scope` y corte temporal;
2. no se mezclan balances de fechas distintas;
3. la composición de activo/pasivo corriente procede del sistema contable/fuente autorizada, no de Finance Basic;
4. Finance Basic no reclasifica cuentas;
5. para `R-FIN-002`, el valor **post-operación** debe ser suministrado/evidenciado o derivado por una transformación contable posterior expresamente autorizada;
6. el MVP **no inventa** el efecto contable de la compra para fabricar `working_capital_projected`.

Así, EIOS puede validar/comparar una magnitud de fondo de maniobra sin convertirse en motor contable.

---

# 6. FIN-AUTH-05 — Proyección de tesorería

## Propuesta

Autorizar una proyección cronológica basada en eventos monetarios demostrados:

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

Reglas:

- el/los pago(s) de la compra propuesta se incorporan como `confirmed_payments` de la propia proyección;
- no existe una segunda resta separada del pago de compra;
- cada flujo posee identidad y solo se computa una vez;
- un cobro/pago no demostrado no se convierte en cero ni se estima;
- moneda incompatible bloquea agregación salvo normalización FX autorizada;
- `P-FIN-005/006` intervienen únicamente conforme a su política autorizada para R-FIN-001; no se generalizan a otras finalidades.

---

# 7. FIN-AUTH-06 — Capacidad financiera prevista

## Propuesta

Definir para el MVP:

```text
financial_capacity_forecast
=
minimum_projected_treasury_within_authorized_horizon
```

Es decir, el punto de tesorería proyectada más bajo dentro del horizonte autorizado.

Relación con `R-FIN-001`:

```text
financial_capacity_forecast
<
P-FIN-002 (tesorería mínima)

→ condición R-FIN-001 activada
```

La regla, no Finance Basic, conserva efecto/severidad/resultado.

Motivo: evalúa la capacidad real de atravesar el horizonte de pagos sin confundirla con saldo final, liquidez o fondo de maniobra.

---

# 8. FIN-AUTH-07 — Margen de seguridad financiera

## Propuesta

Definir el margen de seguridad respecto del mínimo de tesorería como:

```text
financial_safety_margin_pct
=
(
  financial_capacity_forecast
  - treasury_minimum
)
/
treasury_minimum
× 100
```

con:

```text
treasury_minimum = P-FIN-002
```

Interpretación:

- `0 %` → el mínimo se alcanza exactamente;
- valor positivo → existe colchón por encima del mínimo;
- valor negativo → se cae por debajo del mínimo;
- `P-FIN-004` expresa el colchón porcentual mínimo deseado.

Condición ordinaria candidata para `R-FIN-003`:

```text
financial_safety_margin_pct < P-FIN-004
```

La eventual escalada R1→R0 sigue siendo autoridad de Rules/CRC y **no queda autorizada por esta propuesta**.

### Caso treasury_minimum <= 0

La fórmula porcentual no se considera evaluable bajo esta metodología. No se inventa denominador alternativo. La configuración deberá proporcionar un mínimo positivo para utilizar este indicador porcentual.

---

# 9. Efecto sobre dependencias

Si FIN-AUTH-01…07 fueran aprobadas, la siguiente fase documental podrá demostrar, sin inferencia:

- datos necesarios para proyección de tesorería;
- evidencia requerida;
- dependencia del componente Finance Basic;
- criticidad/evaluability de las entradas de `R-FIN-001`;
- transformación `P-FIN-001 → horizonte Finance Basic → capacity forecast`;
- relación cuantitativa entre `P-FIN-002`, capacidad prevista y margen de seguridad;
- uso de `P-FIN-003` con working capital demostrado;
- uso de `P-FIN-004` con safety margin definido.

No se actualizará RDM antes de la autorización.

---

# 10. Elementos que siguen fuera de alcance

La aprobación de este paquete no autorizaría:

- límites empresariales concretos distintos de los configurados;
- financiación automática;
- líneas de crédito como tesorería;
- FX;
- forecasting de cobros/pagos no evidenciados;
- scoring financiero;
- optimización;
- ejecución de pagos/cobros;
- decisión automática;
- rama R1/R0 de `R-FIN-002/003`;
- reglas nuevas;
- implementación técnica inmediata.

Tras aprobación seguirá siendo obligatorio:

`DEPURACIÓN FINAL → AUDIT 2 DE CIERRE → CERRAR METODOLOGÍA → AUDITORÍA DE ENTRADA A CONTRATO → CONTRATO TÉCNICO`.

---

# 11. Decisión requerida

El decisor del proyecto puede:

```text
APROBAR FIN-AUTH-v0.1
```

aprobar con modificaciones explícitas, o rechazar puntos concretos.

Hasta entonces:

**ESTADO: PROPUESTA — NO AUTORIZADA.**