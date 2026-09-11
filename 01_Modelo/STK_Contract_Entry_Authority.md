# EIOS — STK · Autoridad empresarial de entrada a contrato técnico

**Versión:** 1.0
**Estado:** APROBADO — AUTORIDAD EMPRESARIAL CERRADA
**Fecha de decisión:** 11/09/2026
**Autoridad:** decisión humana expresa
**Origen:** aprobación del paquete STK de entrada tras `07_Pruebas/STK_Contract_Entry_Audit_v0.1.md`

---

## 1. Propósito

Cerrar exclusivamente los dos gaps de autoridad empresarial identificados por la auditoría de entrada STK v0.1:

1. semántica canónica de `stock_on_hand`, `stock_committed` y `stock_available`;
2. política de demanda admisible para cobertura y proyección STK.

Esta autoridad no valida los valores iniciales del catálogo, no crea una decisión automática y no modifica las autoridades STK-M01…M10 ya cerradas.

---

## 2. Estado canónico de stock

### 2.1 `stock_on_hand`

`stock_on_hand` representa la **cantidad física evidenciada del artículo existente en inventario en la fecha de evaluación**, expresada en la unidad base normalizada del artículo.

Es stock físico. No equivale por sí mismo a stock disponible.

No incorpora:

- pedidos de compra pendientes;
- compras en tránsito;
- recepciones futuras no materializadas;
- cantidades meramente previstas.

La cantidad debe conservar fuente, fecha de referencia, unidad fuente, conversión aplicada y evidencia.

### 2.2 `stock_committed`

`stock_committed` representa la **parte de `stock_on_hand` reservada o asignada de forma suficientemente evidenciada a obligaciones existentes y que, por esa asignación, no está libre para nuevas necesidades**.

Una expectativa comercial, previsión o pedido de cliente confirmado no convierte automáticamente una cantidad en `stock_committed`. Debe existir evidencia de reserva o asignación sobre el stock físico.

La misma unidad física no puede contabilizarse simultáneamente como comprometida más de una vez para el mismo instante de evaluación.

### 2.3 `stock_available`

La relación empresarial autorizada es:

`stock_available = max(0, stock_on_hand - stock_committed)`

Todas las magnitudes deben referirse al mismo artículo, unidad base, ámbito operativo y fecha de evaluación.

Si `stock_committed > stock_on_hand`, EIOS no produce stock disponible negativo. Conserva:

`availability_deficit = stock_committed - stock_on_hand`

como evidencia explícita de déficit de disponibilidad.

El uso de `max(0, ...)` no elimina ni oculta el déficit.

### 2.4 Ausencia y contradicción

Si falta evidencia suficiente de `stock_on_hand` o de la magnitud comprometida necesaria para el cálculo, el resultado dependiente es `UNKNOWN / NOT_EVIDENCED` conforme a STK-M09.

Si existen fuentes materialmente incompatibles, se aplica STK-M10. EIOS no selecciona silenciosamente una fuente.

---

## 3. Política de demanda STK

### 3.1 Principio

EIOS no equipara automáticamente:

- ventas históricas;
- consumo real;
- demanda histórica;
- demanda prevista.

Cada evaluación STK debe identificar explícitamente **qué método de demanda utiliza, su fuente, versión, ventana temporal y fecha de referencia**.

No se mezclan métodos o fuentes sin una política específica, documentada y autorizada.

### 3.2 Métodos admitidos en el MVP

Se autorizan inicialmente dos vías:

#### A. Previsión externa/autorizada

EIOS puede consumir una previsión de demanda generada externamente al cálculo STK cuando:

- la fuente está identificada;
- la magnitud está definida como demanda;
- la unidad y horizonte son compatibles;
- la versión y fecha de referencia son trazables;
- existe evidencia suficiente para utilizarla.

STK no inventa ni reconstruye internamente dicha previsión.

#### B. Base histórica derivada de `consumption`

Cuando la política aplicable seleccione base histórica, la fuente autorizada es el `consumption` real definido por STK-M01.

La tasa media diaria autorizada es:

`historical_daily_demand = total_evidenced_consumption / evidenced_days_in_window`

Condiciones:

- la ventana debe estar explícitamente configurada y trazable;
- solo se utilizan periodos completos exigidos por la ventana;
- todos los consumos deben estar normalizados a la misma unidad base;
- el denominador contiene únicamente días pertenecientes a periodos cuya información requerida está suficientemente evidenciada;
- si falta un periodo requerido por la ventana, no se reduce silenciosamente la ventana: el resultado es `UNKNOWN / NOT_EVIDENCED`;
- consumo cero solo existe cuando esté explícitamente evidenciado conforme a M01.

`P-STK-006` puede gobernar la longitud de la ventana cuando exista un valor empresarial vigente. El valor inicial de 12 meses del catálogo **no queda validado por esta autoridad**.

### 3.3 Ventas históricas

Las ventas históricas no se convierten automáticamente en `consumption` ni en demanda STK.

`P-PYE-005 — Considerar ventas históricas` no autoriza por sí mismo ninguna transformación ventas → demanda. Su valor inicial `Sí` no produce comportamiento operativo mientras no exista una transformación empresarial específica autorizada y trazable.

### 3.4 Selección del método

La selección entre previsión autorizada y base histórica debe estar declarada por la política/configuración vigente y quedar registrada con la evaluación.

El motor STK no elige silenciosamente el método “más conveniente”, no promedia ambos por defecto y no sustituye uno por otro ante ausencia de datos.

Si el método seleccionado no puede calcularse o demostrarse, el resultado dependiente conserva incertidumbre conforme a M09.

---

## 4. Relación con parámetros existentes

Esta decisión no valida valores numéricos iniciales.

Continúan pendientes de validación empresarial como valores concretos:

- `STK-002 = 15 %`;
- `STK-003 = 30 días`;
- `STK-004 = 90 días`;
- `STK-005 = 10 %`;
- `STK-006 = 12 meses`;
- `PYE-001 = 90 días`;
- `PYE-002…005 = Sí`;
- `PYE-006 = 15 días`.

Un contrato técnico podrá exigir valores configurados y autorizados sin convertir esos valores iniciales en defaults normativos.

---

## 5. Frontera de autoridad

Esta decisión:

- no crea un parámetro nuevo;
- no redefine las condiciones de `R-STK-001…004`;
- no convierte una métrica en una decisión;
- no autoriza reposición automática;
- no autoriza forecasting implícito;
- no modifica C0;
- no permite utilizar ventas como sustituto silencioso de demanda;
- no reabre M01…M10.

La autoridad decisional final permanece en la persona autorizada.

---

## 6. Estado

Los gaps empresariales B1 y B2 de `STK_Contract_Entry_Audit_v0.1.md` quedan **CERRADOS**.

Queda como trabajo documental/contractual el cruce demostrable `P-STK/P-PYE ↔ reglas/dependencias` antes de repetir el gate de entrada.
