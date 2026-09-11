# EIOS — STOCK & DEMAND METHODOLOGICAL MATRIX

**Versión:** 0.10
**Estado:** DISEÑO PARCIAL — STK-M01…M09 CERRADOS; STK-M10 PENDIENTE
**Baseline:** EIOS Vertical MVP  
**Fecha:** 11/09/2026

---

## 1. Propósito

Esta matriz formaliza el perímetro metodológico de Stock & Demand Intelligence sin introducir fórmulas o criterios cuantitativos no demostrados por la documentación vigente.

Su finalidad es preparar la posterior implementación técnica de STK mediante la secuencia:

`metodología → regla → parámetro → contrato → implementación → tests`

La matriz no crea reglas, parámetros, excepciones ni valores empresariales nuevos.

---

## 2. Autoridad utilizada

Fuentes actualmente demostradas:

- `01_Modelo/Especificacion_funcional.md` — alcance funcional de stock y demanda.
- `04_Reglas/Matriz_Reglas_MVP.md` v2.1 — reglas `R-STK-001…004`, reglas de rotación y `R-ENT-001`.
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` — parámetros `STK-001…006` y `PYE-001…006`.
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md` — estado de los parámetros y relaciones parámetro-regla.
- `04_Reglas/Rule_Dependency_Matrix.md` v1.3 — gobierno de dependencias.

Ninguna de estas fuentes autoriza por sí sola una fórmula cuantitativa completa para STK.

---

## 3. Perímetro funcional demostrado

EIOS puede considerar, cuando exista información suficiente:

- stock actual;
- stock comprometido;
- pedidos pendientes;
- compras en tránsito;
- consumo/demanda histórica;
- demanda prevista;
- plazo de entrega;
- fecha prevista de recepción;
- cantidad propuesta.

El análisis puede identificar:

- riesgo de rotura;
- exceso de stock;
- compra potencialmente innecesaria;
- compra necesaria para atender demanda prevista.

---

## 4. Reglas STK demostradas

| Rule_ID | Regla | Condición documental | Resultado | Estado metodológico |
|---|---|---|---|---|
| `R-STK-001` | Riesgo de rotura | La proyección indica agotamiento antes de nueva recepción | COMPRAR / COMPRAR CONDICIONADO | Fórmula de proyección pendiente |
| `R-STK-002` | Compra innecesaria por stock suficiente | Cobertura supera ampliamente nivel configurado sin necesidad justificada | NO COMPRAR / NEGOCIAR CANTIDAD | Definición cuantitativa de cobertura pendiente |
| `R-STK-003` | Exceso de stock | Stock posterior a compra supera máximo configurado | NEGOCIAR / NO COMPRAR | Fórmula y horizonte temporal pendientes |
| `R-STK-004` | Excepción por pedido confirmado | Pedido confirmado absorbe total/parcialmente el exceso | COMPRAR / COMPRAR CONDICIONADO | Mecánica de absorción pendiente |

---

## 5. Parámetros STK demostrados

El catálogo vigente define:

| ID | Definición vigente | Estado |
|---|---|---|
| `STK-001` | Stock mínimo | Pendiente de datos |
| `STK-002` | Stock de seguridad | 15 % del consumo; pendiente de validación |
| `STK-003` | Cobertura mínima | 30 días; pendiente de validación |
| `STK-004` | Cobertura máxima | 90 días; pendiente de validación |
| `STK-005` | Tolerancia de exceso | 10 %; pendiente de validación |
| `STK-006` | Periodo para calcular consumo | 12 meses; pendiente de validación |

Estos valores son valores iniciales de trabajo, no autoridad cuantitativa definitiva.

---

## 6. Parámetros de proyección relacionados

| ID | Definición vigente | Estado |
|---|---|---|
| `PYE-001` | Horizonte de proyección | Pendiente de validación |
| `PYE-002` | Considerar pedidos pendientes | Pendiente de validación |
| `PYE-003` | Considerar compras en tránsito | Pendiente de validación |
| `PYE-004` | Considerar plazo de entrega | Pendiente de validación |
| `PYE-005` | Considerar ventas históricas | Pendiente de validación |
| `PYE-006` | Umbral de riesgo de rotura | Pendiente de validación |

La existencia de estos parámetros no demuestra todavía qué regla los consume ni qué transformación aplica.

---

## 7. Variables canónicas requeridas

Antes de implementar STK deben quedar definidas, con unidad y fecha de referencia inequívocas:

1. `stock_on_hand` — stock físico disponible en la fecha de evaluación.
2. `stock_committed` — stock comprometido cuya semántica debe ser confirmada.
3. `pending_orders` — pedidos pendientes relevantes.
4. `in_transit` — compras en tránsito relevantes.
5. `consumption` — cantidad real consumida del artículo por la organización o unidad operativa correspondiente, agregada por periodo mensual en la unidad base normalizada del artículo; autoridad cerrada en `STK_M01_Consumption_Authority.md`.
6. `demand` — demanda utilizada para proyección.
7. `lead_time` — plazo de entrega aplicable.
8. `expected_receipt_date` — fecha prevista de recepción.
9. `proposed_quantity` — cantidad de la propuesta.
10. `evaluation_date` — fecha canónica de evaluación.

La lista anterior define variables de entrada necesarias para el diseño; no define todavía sus fórmulas de agregación.

---

## 8. Puntos metodológicos que deben resolverse antes del código

### STK-M01 — Consumo — CERRADO

`consumption` representa exclusivamente la cantidad real consumida de un artículo por la organización o unidad operativa correspondiente. Se mide en la unidad base normalizada del artículo y se agrega mediante suma de los consumos registrados dentro de cada periodo mensual correspondiente.

Ventas y demanda prevista permanecen como magnitudes distintas. Un periodo sin datos es `UNKNOWN`, nunca cero salvo evidencia explícita de consumo cero. Una conversión no demostrada a la unidad base también impide producir un valor cuantitativo y conserva `UNKNOWN`.

La política entra en vigor con la puesta en producción de EIOS y se aplica retrospectivamente a los datos históricos incorporados, preservando fuente, periodo, unidad y transformación. Autoridad completa: `01_Modelo/STK_M01_Consumption_Authority.md`.

### STK-M02 — Stock mínimo — CERRADO

`stock_minimum` representa la cantidad mínima de existencias que debe mantenerse disponible para proteger la continuidad operativa de un artículo antes de que la reposición resulte necesaria. Se expresa en la unidad base normalizada del artículo.

Su valor vigente debe proceder de una política o cálculo explícito, trazable y autorizado basado en demanda esperada, `lead_time`, su variabilidad y el nivel de protección requerido. Esta decisión no autoriza una fórmula concreta ni un valor por defecto.

`Safety_stock` puede formar parte de `stock_minimum` como reserva frente a incertidumbre, pero no es equivalente. La cobertura expresa, combinando `stock_minimum` y demanda esperada, los días o periodos protegidos antes de alcanzar el umbral. La demanda justifica y dimensiona el umbral, pero no modifica automáticamente su valor vigente sin recálculo o autorización de la política correspondiente.

La ausencia del valor o de evidencia de procedencia produce `UNKNOWN / NOT_EVIDENCED`, nunca cero ni una estimación implícita, y no puede fundamentar una decisión automática de reposición. Autoridad completa: `01_Modelo/STK_M02_Minimum_Stock_Authority.md`.

### STK-M03 — Stock de seguridad — CERRADO

`safety_stock` representa la cantidad adicional de existencias mantenida como reserva frente a variaciones no previstas, en la unidad base normalizada del artículo.

Su valor procede de política explícita, documentada, trazable y autorizada, con datos y previsiones válidos y evidenciados de demanda y suministro. Puede formar parte de `stock_minimum`, pero no es equivalente. Ausencia de valor o evidencia produce `UNKNOWN / NOT_EVIDENCED`, nunca cero o inferencia.

No se valida el 15 % del catálogo ni fórmula, base única, horizonte, estadístico, nivel de servicio o reposición automática. Autoridad completa: `01_Modelo/STK_M03_Safety_Stock_Authority.md`.

### STK-M04 — Cobertura — CERRADO

`coverage` representa el tiempo estimado durante el cual el stock disponible puede cubrir la demanda o consumo esperado. La relación autorizada divide stock disponible válido y normalizado en `as_of_date` entre demanda o consumo medio autorizado por unidad de tiempo, con compatibilidad de unidad base.

La unidad estándar es días, salvo parametrización autorizada. Cero confirmado del denominador produce `UNBOUNDED / NOT_APPLICABLE`; ausencia o evidencia insuficiente produce `UNKNOWN / NOT_EVIDENCED`, nunca cero. Fuentes distintas no se mezclan sin regla documentada.

Los umbrales son parámetros versionados y autorizados; los 30/90 días del catálogo siguen pendientes. La composición del stock disponible y la ventana de promedio no se infieren. Autoridad completa: `01_Modelo/STK_M04_Coverage_Authority.md`.

### STK-M05 — Proyección — CERRADO

`stock_projection` representa la evolución proyectada desde `as_of_date`: stock disponible actual más entradas previstas menos salidas previstas, en la unidad base normalizada y sobre horizonte explícito.

Solo participan entradas cuya existencia, cantidad y fecha estén evidenciadas. `lead_time` puede fechar una reposición evidenciada, pero nunca convierte una compra no confirmada en entrada. Las salidas proceden de demanda, consumo, reservas u otras necesidades reconocidas por fuente autorizada.

Los elementos sin datos o evidencia son `UNKNOWN / NOT_EVIDENCED`, nunca cero ni omisión silenciosa. La salida es evidencia proyectiva, no decisión de compra o reposición. `PYE-001…006` siguen pendientes. Autoridad completa: `01_Modelo/STK_M05_Projection_Authority.md`.

### STK-M06 — Pedidos pendientes y tránsito — CERRADO

STK-M06 representa cantidades compradas formalmente reconocidas aún no incorporadas al stock disponible. Distingue pedido pendiente y tránsito como estados mutuamente excluyentes, en unidad base y con evidencia de existencia, cantidad y estado.

Cada entrada conserva origen documental, proveedor, estado, fecha prevista y evidencia. Solo puede incorporarse una vez como entrada futura en la fecha evidenciada; una recepción confirmada retira la cantidad correspondiente y conserva toda la transición.

Ausencia produce `UNKNOWN / NOT_EVIDENCED`, nunca cero o recepción confirmada. La evidencia logística no autoriza compra ni reposición y no valida la inclusión incondicional de `PYE-002/003`. Autoridad completa: `01_Modelo/STK_M06_Logistics_Authority.md`.

### STK-M07 — Exceso — CERRADO

STK-M07 cuantifica el stock por encima de `stock_maximum + excess_tolerance`, tras normalizar ambas magnitudes. Distingue `NO_EXCESS`, `WITHIN_TOLERANCE` y `EXCESS`, cuantificando solo lo situado sobre el umbral tolerado.

La referencia futura consume M05 y no vuelve a sumar M06. La tolerancia porcentual se convierte respecto al máximo mediante política explícita; 90 días y 10 % siguen pendientes. Ausencia produce `UNKNOWN / NOT_EVIDENCED`, nunca `NO_EXCESS`.

El resultado no autoriza cancelaciones, devoluciones, liquidaciones, transferencias o reducciones. Autoridad completa: `01_Modelo/STK_M07_Excess_Authority.md`.

### STK-M08 — Pedido confirmado — CERRADO

STK-M08 representa demanda comercial firme y evidenciada que absorbe total o parcialmente exceso M07. Un pedido exige identidad, cliente, artículo, cantidad, fechas, estado y fuente verificables; un booleano aislado no basta.

La absorción es el mínimo entre exceso y cantidad confirmada aplicable pendiente de servir; se conservan exceso original, absorción y residual, sin reutilizar cantidades. Estados: `NO_EXISTE`, `NO_APLICABLE`, `APLICABLE_Y_VALIDADA`, `NO_VERIFICABLE`.

La mitigación no reescribe M07 ni autoriza decisiones. Autoridad completa: `01_Modelo/STK_M08_Confirmed_Demand_Authority.md`.

### STK-M09 — Ausencia de datos — CERRADO

STK-M09 representa la imposibilidad de determinar de forma suficientemente evidenciada datos necesarios para evaluar el stock. La ausencia no equivale a cero, inexistencia, normalidad ni ausencia de riesgo.

Estados mínimos: `UNKNOWN`, `NOT_EVIDENCED`, `NOT_APPLICABLE` y `CONFLICTING_DATA`. No se sustituyen datos por cero, medias, valores anteriores, estimaciones o valores por defecto sin política empresarial específica, autorizada, versionada y trazable.

La incertidumbre se propaga a las conclusiones dependientes de M01–M08; se registran dato, fuente esperada, fecha, causa y módulos afectados, y toda reevaluación conserva versiones. M09 no inventa criticidades pendientes ni autoriza decisiones. Autoridad completa: `01_Modelo/STK_M09_Missing_Data_Authority.md`.

### STK-M10 — Contradicciones

Debe definirse el tratamiento de datos de stock/demanda temporalmente incompatibles o contradictorios, sin resolverlos mediante heurística no autorizada.

---

## 9. Regla de no invención

Hasta que `STK-M10` esté resuelto documentalmente:

- no se implementan fórmulas cuantitativas de STK;
- no se asignan consumidores definitivos a `P-STK-*` o `PYE-*` por inferencia nominal;
- no se crean parámetros adicionales;
- no se crean reglas adicionales;
- no se convierten valores iniciales del catálogo en política empresarial definitiva.

---

## 10. Criterio de entrada a implementación

STK podrá pasar a contrato técnico cuando exista evidencia suficiente para determinar, como mínimo:

- entradas canónicas;
- unidad de cada magnitud;
- fecha de referencia;
- fórmula de consumo/demanda;
- fórmula de cobertura;
- regla de proyección;
- tratamiento de recepción futura;
- tratamiento de ausencia;
- tratamiento de contradicción;
- relación demostrada regla ↔ parámetro.

**Estado actual:** NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA.

---

## 11. Estado

**STK Methodological Matrix v0.10**
**Estado:** DISEÑO PARCIAL — STK-M01…M09 CERRADOS; STK-M10 PENDIENTE
**No constituye contrato de implementación.**
