# EIOS — PAG-READINESS-02 — Reauditoría de condiciones de pago v0.2

**Baseline:** `main @ 04274e0fbfa297832b3c10b91d7481965cc08cc5`  
**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA — CIERRE DE DIAGNÓSTICO

## 1. DISEÑAR

Reevaluar el frente PAG después de la materialización posterior de:

- Supplier Evidence Core v0.3.3;
- `DocumentaryPaymentCapture`;
- `RequiredInstallmentCalendar`;
- `RequiredInstallmentCoverage`;
- cadena `PROJECTION_ONLY` de pagos/cuotas.

Objetivo: determinar si estos artefactos eliminan el antiguo gap “plazo ofrecido sin carrier provenance-safe” y permiten implementar `R-PAG-001` o `R-PAG-002` sin inventar semántica.

No se autoriza crear un segundo Payment Evidence Core. PR #88 quedó cerrada sin merge precisamente por duplicar Supplier Evidence Core.

## 2. FUENTES CONTRASTADAS

- `04_Reglas/Matriz_Reglas_MVP.md`;
- `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md`;
- `04_Reglas/Rule_Dependency_Matrix.md`;
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md`;
- Supplier Evidence Core metodología/contrato/código;
- `eios/supplier/models.py`;
- `eios/supplier/engine.py`;
- `eios/core/documentary_payment_capture.py`;
- `eios/core/required_installment_coverage.py`;
- trazabilidad de PR #88, cerrada sin merge.

## 3. AUDITAR

### A1 — El carrier factual ya no está totalmente ausente

Supplier Evidence Core puede preservar una observación del proveedor actual con:

- `dimension=PAYMENT_TERM`;
- `candidate_id=None`;
- identidad de proveedor y artículo coherentes con la compra;
- estado `KNOWN / NOT_EVIDENCED / CONFLICTING_DATA`;
- valor tipado;
- unidad;
- `semantic_ref`;
- fuente, evidencia y fecha de captura.

Por tanto, la formulación histórica “no existe carrier factual del plazo” es ya demasiado amplia.

**Corrección:** existe carrier factual genérico de condición de pago, pero no un binding de regla autorizado que convierta cualquier `PAYMENT_TERM` en el escalar canónico “plazo ofrecido” consumible por `R-PAG-001`.

### A2 — Supplier Evidence Core no autoriza comparabilidad de regla

Su contrato establece expresamente:

`STRUCTURALLY_COMPARABLE ≠ RULE_COMPARABLE`.

Además, Supplier Evidence Core no ejecuta Rules y no crea autoridad downstream.

La RDM contiene dependencias `PARAMETER/DERIVED/CONTROL` para `R-PAG-001/002`, pero **no contiene una dependencia EVIDENCE/DATA confirmada** que identifique a `SupplierObservation(PAYMENT_TERM)` como entrada canónica de la regla.

**Conclusión:** no puede conectarse por coincidencia nominal.

### A3 — El calendario documental tampoco define “plazo ofrecido”

`RequiredInstallmentCalendar` conserva:

- cuotas;
- importes;
- vencimientos;
- secuencia;
- total;
- localizadores documentales.

No define:

- fecha base jurídica/económica desde la que se computa el plazo;
- regla para múltiples cuotas;
- vencimiento medio ponderado;
- mínimo/máximo;
- days-after-invoice;
- days-after-delivery;
- days-after-order.

`PurchaseOperation.operation_date` no está autorizada como sustituto automático de fecha de factura, recepción u otra fecha contractual.

**Conclusión:** no puede derivarse `offered_payment_term_days` mediante `due_date - operation_date` ni mediante agregación de cuotas sin nueva autoridad.

### A4 — PR #88 confirma la dirección, no concede autoridad

La implementación exploratoria no integrada creó un campo `offered_payment_term_days`, pero fue cerrada sin merge al detectar duplicación objetiva con Supplier Evidence Core.

Su existencia histórica demuestra un intento descartado; **no es fuente normativa ni código reutilizable**.

La lección vigente es: reutilizar Supplier Evidence Core como fuente factual y cerrar por separado la semántica PAG.

### A5 — P-PAG-003 sigue sin transformación ejecutable exacta

La autoridad vigente dice:

- `P-PAG-003` = tolerancia de plazo;
- unidad = días;
- modula la desviación respecto de `P-PAG-002`;
- no sustituye `P-PAG-001`.

No define mecánicamente una condición equivalente a:

- `offered < target - tolerance`;
- `abs(offered-target) > tolerance`;
- banda unilateral/bilateral;
- otra transformación.

**Conclusión:** implementar cualquiera de estas fórmulas sería inventar política.

### A6 — P-PAG-005 conserva una contradicción objetiva de semántica

Catálogo:

`P-PAG-005 = Considerar descuento por pronto pago`  
valor inicial: `Sí`  
unidad: `Sí/No`.

Especificación especializada:

`P-PAG-005 representa el factor económico asociado al descuento por pronto pago`.

También indica que alimenta un cálculo de coste/beneficio.

Un booleano de activación no contiene el porcentaje/importe/curva económica del descuento.

**Conclusión:** no existe todavía una semántica física única suficiente para cálculo económico.

### A7 — P-PAG-004 está definido como control, no como valor de plazo

La relación de control está documentada. Esto no resuelve A1–A6.

### A8 — R-PAG-002 conserva un bloqueo independiente

La condición exige saber que:

> la operación puede ser viable únicamente si se amplía el plazo de pago.

Eso requiere un análisis contrafactual autorizado de viabilidad financiera bajo un plazo alternativo.

Ni Supplier Evidence Core ni la cadena documental de cuotas producen esa afirmación.

Finance Basic actual tampoco debe reinterpretarse por inferencia como motor contrafactual PAG.

**Conclusión:** R-PAG-002 permanece bloqueada aunque se resolviera el carrier de plazo.

## 4. DEPURAR

Se descartan expresamente:

- crear `eios/payment` como segundo sistema factual;
- usar el código abandonado de PR #88 como autoridad;
- convertir cualquier `PAYMENT_TERM` INTEGER en días sin semántica canónica;
- derivar plazo desde `operation_date`;
- inventar vencimiento medio o ponderación de cuotas;
- fijar la fórmula de tolerancia de `P-PAG-003`;
- reinterpretar `P-PAG-005` booleano como descuento económico;
- usar Finance Basic como contrafactual de plazo sin contrato;
- implementar `R-PAG-001/002` con defaults o branches favorables.

## 5. AUDITAR 2

### Estado depurado de gaps

| Gap | Estado después de reauditoría |
|---|---|
| Carrier factual genérico de condición de pago | **CERRADO PARCIALMENTE** — Supplier Evidence Core y material documental existen |
| Binding EVIDENCE/DATA canónico hacia R-PAG-001 | **ABIERTO** |
| Semántica escalar canónica “plazo ofrecido en días” | **ABIERTA** |
| Regla multi-cuota → plazo | **ABIERTA** |
| Transformación exacta P-PAG-003 | **ABIERTA** |
| Semántica económica P-PAG-005 | **CONTRADICTORIA / ABIERTA** |
| Control P-PAG-004 | **DOCUMENTADO** |
| Contrafactual de viabilidad R-PAG-002 | **ABIERTO** |
| Implementación R-PAG-001 | **BLOQUEADA** |
| Implementación R-PAG-002 | **BLOQUEADA** |

### Dictamen

No existe base suficiente para escribir código de Rules PAG sin crear autoridad empresarial o semántica temporal nueva.

Sí existe base suficiente para **corregir el diagnóstico de continuidad**: ya no debe afirmarse que no existe carrier factual de condiciones de pago. El bloqueo real está en su normalización/binding hacia Rules y en las políticas derivadas pendientes.

**AUDITAR 2: SUPERADA — 0 bloqueadores para cerrar este diagnóstico; implementación positiva NO autorizada.**

## 6. CERRAR

Se cierra `PAG-READINESS-02` como diagnóstico vigente:

```text
Supplier Evidence / Documentary Payment Material
        ↓
hechos de pago preservables
        ↓
[ GAP: semántica PAG canónica + dependency binding ]
        ↓
R-PAG-001

Finance / condición alternativa
        ↓
[ GAP: productor contrafactual autorizado ]
        ↓
R-PAG-002
```

La siguiente implementación PAG solo podrá abrirse cuando exista autoridad explícita para el significado canónico de “plazo ofrecido” y para el uso de `P-PAG-003/P-PAG-005`, o cuando una fuente especializada cierre esos puntos.

## 7. MATERIALIZAR → CI

Esta unidad materializa:

- este diagnóstico;
- reconciliación descriptiva de `Project_Context.md`.

No modifica:

- código Python;
- RDM;
- Matriz de Reglas;
- catálogo/parámetros;
- Supplier Evidence Core;
- material documental de pagos;
- Finance;
- CRC;
- QTG.

CI valida no regresión técnica; no resuelve los gaps de autoridad identificados.
