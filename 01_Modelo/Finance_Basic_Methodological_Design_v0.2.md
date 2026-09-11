# EIOS — FINANCE BASIC · METHODOLOGICAL DESIGN v0.2

**Estado:** DEPURADO — PENDIENTE DE AUDITORÍA 2  
**Fecha:** 11/09/2026  
**Baseline:** EIOS Vertical MVP  
**Sustituye como diseño de trabajo a:** `Finance_Basic_Methodological_Design_v0.1.md`  
**Audit 1:** `07_Pruebas/Finance_Basic_Methodological_Audit_v0.1.md`  
**Ámbito:** Capa 4 — Finanzas Básica

---

## 1. Propósito y límite

Definir la frontera metodológica mínima de Finance Basic para representar consecuencias financieras de una propuesta de compra con evidencia, temporalidad y trazabilidad suficientes.

Este documento sigue siendo **diseño**, no contrato técnico. No autoriza implementación cuantitativa ni convierte gaps abiertos en reglas.

Finance Basic:

- analiza hechos y consecuencias financieras;
- no produce una decisión empresarial;
- no resuelve CRC;
- no crea reglas ni parámetros;
- no sustituye TCO, Stock, PRICE, QTG o Rules;
- no inventa financiación, cobros, pagos, saldos, vencimientos, FX o valores ausentes.

---

## 2. Autoridades

El diseño se subordina a Gobierno, Matriz de Autoridad, Salvaguarda Vertical MVP, Especificación Funcional, Architecture Blueprint, MED, Catálogo de Parámetros, Matriz Parámetro↔Regla, Matriz de Reglas, Evidence Contract, RDM, Centro de Parametrización y contratos cerrados de capas adyacentes.

Una discrepancia se resuelve por la fuente competente; este documento no crea precedencia propia.

---

## 3. Invariantes transversales

### FIN-P01 — Ausencia ≠ cero

Un hecho financiero ausente, insuficiente o contradictorio no se sustituye silenciosamente por cero.

### FIN-P02 — Evidencia antes de cálculo

Todo importe utilizado cuantitativamente debe ser identificable, trazable y aplicable al snapshot/horizonte correspondiente.

### FIN-P03 — Temporalidad explícita

Todo análisis temporal conserva `as_of_date`. Una proyección exige además un horizonte cuya autoridad sea conocida.

### FIN-P04 — Hecho ≠ configuración

Saldos y flujos son hechos. Umbrales, tolerancias y criterios de suficiencia proceden de parámetros/políticas autorizados.

### FIN-P05 — Análisis ≠ regla

Finance Basic produce hechos/resultados analíticos. `R-FIN-*` y `R-PAG-*` conservan condición, efecto, severidad y resultado.

### FIN-P06 — Análisis ≠ decisión

Una situación financiera desfavorable no equivale por sí misma a `NO COMPRAR`.

### FIN-P07 — No compensación implícita

PRICE, TCO, Stock, margen u otras señales no compensan riesgos financieros dentro de Finance Basic. La consolidación corresponde a CRC.

### FIN-P08 — Reconstruibilidad

Snapshot, fuentes y parámetros consumidos deben relacionarse con las versiones/contexto aplicables.

### FIN-P09 — Comparabilidad monetaria

No se agregan monedas incompatibles. Finance Basic no inventa FX, fecha de conversión ni fuente de tipo de cambio.

### FIN-P10 — Coste económico ≠ flujo de caja

Un valor PRICE/TCO no se convierte automáticamente en pago o desembolso. Cualquier transformación exige autoridad y evidencia propias.

---

# 4. FIN-M01 — Snapshot financiero

El análisis parte de un corte financiero identificable.

Conceptualmente conserva, cuando existan:

```text
company_scope
as_of_date
data_snapshot_id
analysis_currency
source_references
```

El snapshot no implica completitud.

No se fusionan silenciosamente datos de empresas, ámbitos o fechas incompatibles.

---

# 5. FIN-M02 — Tesorería evidenciada

`treasury_current` representa una posición de tesorería utilizable únicamente cuando importe, moneda, fecha, ámbito y fuente están suficientemente demostrados.

Este diseño **no define qué cuentas o instrumentos componen tesorería**. Esa composición permanece `FIN-G02` hasta autoridad suficiente.

Si existen posiciones contradictorias para el mismo contexto:

- se conservan las fuentes;
- no se elige máximo, mínimo, último valor, promedio o valor arbitrario;
- no se presenta una proyección cuantitativa falsamente precisa cuando la contradicción sea material.

---

# 6. FIN-M03 — Liquidez

MED, Especificación Funcional, Architecture Blueprint y la frontera de TCO reconocen `liquidez` como materia financiera.

Finance Basic debe mantener **liquidez separada de tesorería y fondo de maniobra**.

Hasta que exista definición metodológica especializada suficiente:

- puede consumir una magnitud de liquidez ya demostrada por una fuente competente;
- no crea fórmula propia;
- no identifica automáticamente liquidez con tesorería;
- no identifica automáticamente liquidez con fondo de maniobra;
- no crea ratio por conveniencia de implementación.

La definición cuantitativa aplicable al MVP permanece `FIN-G03`.

---

# 7. FIN-M04 — Flujos futuros

Finance Basic puede representar pagos y cobros futuros relevantes para el análisis solo cuando estén suficientemente evidenciados.

Información conceptual mínima:

```text
flow_id
flow_nature = PAYMENT | COLLECTION
amount
currency
due_date
source_ref
evidence/applicability context
```

La nomenclatura no es todavía schema técnico.

Para intervenir cuantitativamente, el flujo debe estar demostrado como aplicable y pendiente respecto de `as_of_date`. Fecha e importe por sí solos no demuestran que siga vigente.

Flujos cancelados, liquidados, sustituidos, duplicados o cuya vigencia no pueda demostrarse no se incorporan silenciosamente como pendientes.

### Parámetros FIN-005/006

La autoridad vigente demuestra:

```text
P-FIN-005 → R-FIN-001 (relación compuesta)
P-FIN-006 → R-FIN-001 (relación compuesta)
```

Este diseño **no los convierte en controles globales de cualquier proyección financiera**. Su uso operativo fuera del contexto demostrado requiere autoridad adicional.

---

# 8. FIN-M05 — Horizonte financiero

`P-FIN-001` existe en el Catálogo como `Horizonte de pagos`, pero permanece pendiente de identificación documental individual en la matriz parámetro↔regla.

Por tanto:

- no se asigna por inferencia a `R-FIN-*`;
- no se utiliza todavía como horizonte universal de Finance Basic;
- ninguna implementación debe fijar un horizonte por default para cerrar este gap.

Una proyección cuantitativa general queda bloqueada hasta que la autoridad del horizonte aplicable esté determinada.

---

# 9. FIN-M06 — Impacto financiero de la propuesta

Finance Basic puede representar flujos atribuibles a la propuesta cuando estén demostrados.

La compra no equivale automáticamente a un pago inmediato ni a `quantity × unit_price` como flujo de caja final.

Cuando exista evidencia, pueden ser relevantes:

- importe exigible;
- calendario/fecha de pago;
- plazo y condiciones de pago;
- descuentos **efectivamente aplicables**;
- otros ajustes previamente autorizados.

No se permite:

- inferir vencimiento;
- aplicar descuentos meramente potenciales;
- asumir financiación;
- transformar TCO en cash outflow;
- usar el valor económico de otra capa como pago sin transformación autorizada.

---

# 10. FIN-M07 — Proyección de tesorería

## 10.1 Composición candidata

La arquitectura exige distinguir situación actual, impacto de la compra y situación proyectada.

La composición candidata es:

```text
projected_treasury
=
current_evidenced_treasury
+ evidenced_inflows_in_scope
- evidenced_non_purchase_outflows_in_scope
- evidenced_purchase_outflows_in_scope
```

Los dos conjuntos de outflows deben ser **disjuntos**. Un mismo `flow_id` no puede computarse dos veces aunque aparezca en varias fuentes.

**Estado:** PROPUESTA METODOLÓGICA, no autoridad cerrada.

## 10.2 Requisitos previos

No puede presentarse cuantitativamente si falta cualquiera de las condiciones necesarias para el alcance declarado, entre ellas:

- tesorería de partida utilizable;
- horizonte autorizado;
- flujos materialmente necesarios y suficientemente evidenciados;
- comparabilidad monetaria;
- ausencia de contradicción crítica no resuelta.

## 10.3 Moneda

Todos los términos agregados deben estar en moneda comparable. Si requieren FX y no existe normalización autorizada, la proyección no se agrega silenciosamente.

---

# 11. FIN-M08 — Fondo de maniobra

El sistema debe considerar fondo de maniobra y existe:

`P-FIN-003 → R-FIN-002` — relación directa confirmada.

No obstante, la documentación vigente revisada no cierra para EIOS:

- fórmula/composición autorizada;
- partidas incluidas;
- corte temporal;
- impacto de la propuesta;
- relación con financiación/vencimientos.

Por tanto, Finance Basic solo puede consumir una magnitud de fondo de maniobra ya demostrada por una fuente/metodología competente hasta resolver `FIN-G04`.

No se crea fórmula contable por inferencia.

---

# 12. FIN-M09 — Margen de seguridad financiera

Existe:

`P-FIN-004 → R-FIN-003` — relación directa confirmada.

Pero no existe todavía definición especializada suficiente de la magnitud que debe compararse contra ese umbral.

No se infiere que sea porcentaje de:

- tesorería;
- liquidez;
- fondo de maniobra;
- capacidad de pago;
- otra magnitud seleccionada por implementación.

La definición cuantitativa permanece `FIN-G05`.

---

# 13. FIN-M10 — Capacidad financiera prevista

La matriz vigente confirma:

```text
P-FIN-002 → R-FIN-001 (compuesta)
P-FIN-005 → R-FIN-001 (compuesta)
P-FIN-006 → R-FIN-001 (compuesta)
```

`R-FIN-001` evalúa riesgo de incapacidad de pago.

La documentación revisada no define todavía una identidad cuantitativa única de `capacidad financiera prevista`.

No se identifica automáticamente con:

- projected_treasury;
- liquidez;
- fondo de maniobra;
- saldo neto de flujos;
- ratio inventado.

Permanece `FIN-G06`.

---

# 14. FIN-M11 — Salida analítica

Finance Basic entrega hechos/resultados analíticos, no resultados oficiales de negocio.

Debe mantener separados, cuando estén autorizados/disponibles:

```text
financial_snapshot
current_treasury
liquidity_reference
future_payments
future_collections
purchase_financial_impact
projected_treasury
working_capital_reference
financial_safety_margin_reference
financial_capacity_reference
unresolved_financial_items
source/evidence references
```

La lista es conceptual y no crea clases/campos físicos.

Una salida no adquiere automáticamente consumidor de regla. Rules solo consume dependencias demostradas.

---

# 15. Frontera con TCO

TCO calcula coste económico atribuible. Finance Basic analiza posición y flujos financieros.

Se preserva:

```text
TCO value ≠ cash payment
TCO timing ≠ payment timing
TCO determinability ≠ financial evaluability
```

Finance Basic no absorbe financiación/coste de capital dentro de TCO Core ni reabre GAP-TCO-01.

---

# 16. Frontera con reglas financieras

### R-FIN-001

Finance Basic no produce `NO COMPRAR`. Proporcionará únicamente hechos/resultados cuya dependencia esté autorizada.

La identidad de `capacidad financiera prevista` sigue abierta.

### R-FIN-002

`P-FIN-003` está confirmado como consumidor directo. Finance Basic no elige entre las ramas `NO COMPRAR` / `COMPRAR CONDICIONADO`.

### R-FIN-003

`P-FIN-004` está confirmado como consumidor directo. Finance Basic no decide escalada `R1→R0` ni resolubilidad de una condición.

Esas ramas pertenecen a Rules/CRC y requieren autoridad propia.

---

# 17. Frontera con pagos/negociación

Finance Basic puede representar el efecto temporal/económico de condiciones de pago demostradas, pero no:

- negocia;
- crea plazo objetivo;
- transforma `P-PAG-*` en `P-FIN-*`;
- genera condición de compra;
- duplica `R-PAG-001/002`.

---

# 18. Dependencias y evaluabilidad

RDM permanece como autoridad transversal de dependencias.

Este diseño no crea por inferencia:

- dependencias `DATA`;
- dependencias `EVIDENCE`;
- dependencias `COMPONENT`;
- `Criticality`;
- `Evaluability_Impact`;
- fallback.

La ausencia de esos elementos puede bloquear el futuro contrato técnico aunque la metodología conceptual quede mejor definida.

---

# 19. Gaps tras depuración

| Gap | Materia | Estado |
|---|---|---|
| FIN-G01 | Autoridad de `P-FIN-001` como horizonte operativo | OPEN |
| FIN-G02 | Composición autorizada de tesorería | OPEN |
| FIN-G03 | Definición cuantitativa de liquidez aplicable al MVP | OPEN |
| FIN-G04 | Fórmula/composición de fondo de maniobra e impacto post-compra | OPEN |
| FIN-G05 | Definición cuantitativa de margen de seguridad financiera | OPEN |
| FIN-G06 | Identidad cuantitativa de capacidad financiera prevista | OPEN |
| FIN-G07 | Autoridad final de la composición `projected_treasury` | OPEN |
| FIN-G08 | Dependencias DATA concretas por regla financiera | OPEN |
| FIN-G09 | Evidencias concretas por regla financiera | OPEN |
| FIN-G10 | Criticality/Evaluability_Impact de dependencias financieras | OPEN |
| FIN-G11 | Selección de ramas/escaladas de R-FIN-002/R-FIN-003 | OPEN — RULES, no Finance Basic |

---

# 20. Correcciones Audit 1

| Hallazgo | Tratamiento v0.2 |
|---|---|
| FIN-A1-01 | Liquidez incorporada como FIN-M03 separada y sin fórmula inferida |
| FIN-A1-02 | Outflows separados en conjuntos disjuntos + identidad/deduplicación |
| FIN-A1-03 | Añadido FIN-P09 y control de comparabilidad/FX |
| FIN-A1-04 | Añadido FIN-P10 y frontera TCO≠cash flow |
| FIN-A1-05 | FIN-005/006 limitados a relación demostrada con R-FIN-001 |
| FIN-A1-06 | P-FIN-001 no se usa como horizonte universal; bloquea proyección general |
| FIN-A1-07 | Exigida evidencia de vigencia/aplicabilidad de flujos |
| FIN-A1-08 | Aplicabilidad de flujos referida a `as_of_date` |
| FIN-A1-09 | Gaps cuantitativos preservados, no ocultados |

---

# 21. Criterio de Audit 2

Audit 2 debe determinar por separado:

1. si la **frontera metodológica** v0.2 está limpia y puede cerrarse como marco;
2. si existe autoridad suficiente para cerrar alguna definición cuantitativa pendiente;
3. cuáles gaps requieren decisión empresarial expresa;
4. si el contrato técnico debe permanecer bloqueado aun cuando el marco metodológico pueda cerrarse.

No se confundirá “diseño metodológico coherente” con “implementación autorizada”.

---

# 22. Estado

**Versión de diseño:** 0.2  
**Estado:** DEPURADO — PENDIENTE DE AUDITORÍA 2  
**Contrato técnico:** NO AUTORIZADO  
**Código Finance Basic:** NO AUTORIZADO  
**Valores empresariales nuevos:** NINGUNO

Siguiente paso obligatorio:

**AUDITAR 2** contra autoridad y fronteras cerradas.