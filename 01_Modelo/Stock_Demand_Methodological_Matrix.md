# EIOS — STOCK & DEMAND METHODOLOGICAL MATRIX

**Versión:** 1.1
**Estado:** METODOLOGÍA STK-M01…M10 CERRADA — ENTRADA A CONTRATO TÉCNICO AUTORIZADA
**Baseline:** EIOS Vertical MVP  
**Fecha:** 11/09/2026

---

## 1. Propósito

Esta matriz formaliza el perímetro metodológico de Stock & Demand Intelligence sin introducir fórmulas o criterios cuantitativos no demostrados por la documentación vigente.

Su finalidad es preparar la implementación técnica de STK mediante la secuencia:

`metodología → regla → parámetro → contrato → implementación → tests`

La matriz no crea reglas, parámetros, excepciones ni valores empresariales nuevos.

---

## 2. Autoridad utilizada

Fuentes demostradas:

- `01_Modelo/Especificacion_funcional.md` — alcance funcional de stock y demanda.
- `01_Modelo/STK_M01_Consumption_Authority.md` … `STK_M10_Contradictions_Authority.md` — metodología M01…M10.
- `01_Modelo/STK_Contract_Entry_Authority.md` — estado canónico de stock y política de demanda aprobados.
- `04_Reglas/Matriz_Reglas_MVP.md` v2.1 — reglas `R-STK-001…004`, reglas de rotación y `R-ENT-001`.
- `04_Reglas/Especificacion_Reglas_STK_Parametros_MVP.md` v1.0 — cruce STK/PYE ↔ reglas.
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` — parámetros `STK-001…006` y `PYE-001…006`.
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md` v0.9 — vista especializada de relaciones parámetro-regla.
- `04_Reglas/Rule_Dependency_Matrix.md` v1.4 — dependencias canónicas.
- `07_Pruebas/STK_Contract_Entry_Audit_v0.1.md` y v0.2 — gates de entrada.

Los valores iniciales del catálogo continúan sin constituir autoridad cuantitativa definitiva.

---

## 3. Perímetro funcional demostrado

EIOS puede considerar, cuando exista información suficiente:

- stock físico (`stock_on_hand`);
- stock comprometido (`stock_committed`);
- stock disponible (`stock_available`);
- pedidos pendientes;
- compras en tránsito;
- consumo real;
- demanda autorizada;
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
| `R-STK-001` | Riesgo de rotura | La proyección indica agotamiento antes de nueva recepción | COMPRAR / COMPRAR CONDICIONADO | Proyección M05 y temporalidad M06 cerradas |
| `R-STK-002` | Compra innecesaria por stock suficiente | Cobertura supera ampliamente nivel configurado sin necesidad justificada | NO COMPRAR / NEGOCIAR CANTIDAD | Cobertura M04 cerrada; `P-STK-004` consumidor directo confirmado |
| `R-STK-003` | Exceso de stock | Stock posterior a compra supera máximo configurado | NEGOCIAR / NO COMPRAR | Exceso M07 cerrado; `P-STK-004/005` derivados confirmados |
| `R-STK-004` | Excepción por pedido confirmado | Pedido confirmado absorbe total/parcialmente el exceso | COMPRAR / COMPRAR CONDICIONADO | Absorción M08 cerrada; sin parámetro directo demostrado |

---

## 5. Parámetros STK demostrados

El catálogo vigente define:

| ID | Definición vigente | Estado |
|---|---|---|
| `STK-001` | Stock mínimo | Valor pendiente de datos/validación; función M02 cerrada |
| `STK-002` | Stock de seguridad | 15 % inicial pendiente de validación; función M03 cerrada |
| `STK-003` | Cobertura mínima | 30 días iniciales pendientes de validación; función M04 cerrada |
| `STK-004` | Cobertura máxima | 90 días iniciales pendientes de validación; relación con `R-STK-002/003` cerrada |
| `STK-005` | Tolerancia de exceso | 10 % inicial pendiente de validación; relación derivada con `R-STK-003` cerrada |
| `STK-006` | Periodo para calcular consumo | 12 meses iniciales pendientes de validación; gobierna ventana histórica autorizada |

Estos valores son valores iniciales de trabajo, no autoridad cuantitativa definitiva.

---

## 6. Parámetros de proyección relacionados

| ID | Definición vigente | Estado de cruce |
|---|---|---|
| `PYE-001` | Horizonte de proyección | Función metodológica M05; sin consumidor directo de regla demostrado |
| `PYE-002` | Considerar pedidos pendientes | Control metodológico M05/M06; `Sí` no implica inclusión incondicional |
| `PYE-003` | Considerar compras en tránsito | Control metodológico M05/M06; `Sí` no implica inclusión incondicional |
| `PYE-004` | Considerar plazo de entrega | Control metodológico temporal; sin consumidor directo demostrado |
| `PYE-005` | Considerar ventas históricas | No operativo como transformación ventas → demanda sin política posterior específica |
| `PYE-006` | Umbral de riesgo de rotura | Sin consumidor directo demostrado en `R-STK-001` vigente |

El cruce individual `P-STK/P-PYE ↔ R-STK` queda cerrado por `04_Reglas/Especificacion_Reglas_STK_Parametros_MVP.md`. La ausencia de consumidor directo demostrado no elimina la función metodológica autorizada del parámetro.

---

## 7. Variables canónicas requeridas

Las variables canónicas quedan determinadas de la siguiente forma:

1. `stock_on_hand` — cantidad física evidenciada existente en inventario en `evaluation_date`, en unidad base normalizada. No incluye tránsito, pedidos pendientes ni recepciones futuras.
2. `stock_committed` — parte evidenciada de `stock_on_hand` reservada o asignada a obligaciones existentes y no libre para nuevas necesidades.
3. `stock_available` — `max(0, stock_on_hand - stock_committed)`. Si el comprometido excede al físico, se conserva además `availability_deficit = stock_committed - stock_on_hand`.
4. `pending_orders` — cantidades formalmente compradas en estado `PENDING_ORDER` conforme a M06.
5. `in_transit` — cantidades formalmente compradas en estado `IN_TRANSIT` conforme a M06.
6. `consumption` — cantidad real consumida, agregada mensualmente en unidad base normalizada conforme a M01.
7. `demand` — magnitud seleccionada por política explícita y versionada: previsión externa/autorizada o base histórica derivada de `consumption` real.
8. `lead_time` — plazo de entrega aplicable y evidenciado cuando se utilice temporalmente.
9. `expected_receipt_date` — fecha prevista de recepción evidenciada; no equivale a recepción confirmada.
10. `proposed_quantity` — cantidad de la propuesta de compra en unidad compatible.
11. `evaluation_date` — fecha empresarial canónica de referencia; el contrato técnico deberá mapear `as_of_date` a esta identidad sin crear una segunda fecha ambigua.

### Política histórica de demanda

Cuando se seleccione base histórica:

`historical_daily_demand = total_evidenced_consumption / evidenced_days_in_window`

La ventana debe estar completa y evidenciada. Un periodo requerido ausente produce `UNKNOWN / NOT_EVIDENCED`; no se reduce silenciosamente la ventana.

Las ventas históricas no sustituyen consumo o demanda por defecto.

---

## 8. Puntos metodológicos cerrados

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

Los umbrales son parámetros versionados y autorizados; los 30/90 días del catálogo siguen pendientes. La composición del stock disponible queda cerrada por `STK_Contract_Entry_Authority.md`. Autoridad completa: `01_Modelo/STK_M04_Coverage_Authority.md`.

### STK-M05 — Proyección — CERRADO

`stock_projection` representa la evolución proyectada desde `as_of_date`: stock disponible actual más entradas previstas menos salidas previstas, en la unidad base normalizada y sobre horizonte explícito.

Solo participan entradas cuya existencia, cantidad y fecha estén evidenciadas. `lead_time` puede fechar una reposición evidenciada, pero nunca convierte una compra no confirmada en entrada. Las salidas proceden de demanda, consumo, reservas u otras necesidades reconocidas por fuente autorizada.

Los elementos sin datos o evidencia son `UNKNOWN / NOT_EVIDENCED`, nunca cero ni omisión silenciosa. La salida es evidencia proyectiva, no decisión de compra o reposición. Los valores iniciales `PYE-001…006` siguen pendientes de validación, aunque su función metodológica queda clasificada. Autoridad completa: `01_Modelo/STK_M05_Projection_Authority.md`.

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

### STK-M10 — Contradicciones — CERRADO

STK-M10 identifica datos o evidencias suficientemente identificados que representan el mismo artículo, variable, ámbito y momento comparable, pero no pueden ser simultáneamente ciertos. Una diferencia no es contradicción hasta comprobar unidad, normalización, tiempo, ámbito, versión y contexto.

Toda contradicción conserva fuentes y valores, usa `CONFLICTING_DATA / UNRESOLVED_CONTRADICTION`, se propaga a conclusiones dependientes y no se resuelve por recencia, magnitud, promedio, score ni otra heurística. Solo una política de autoridad previamente autorizada permite resolverla trazablemente.

`contradiction ≠ missing_data`. M10 gobierna datos STK; los conflictos entre resultados permanecen en CRC y las contradicciones documentales en la Matriz de Autoridad Documental. Autoridad completa: `01_Modelo/STK_M10_Contradictions_Authority.md`.

---

## 9. Regla de no invención

La entrada a contrato técnico no autoriza a ampliar alcance. Durante contrato e implementación:

- no se asignan consumidores adicionales a `P-STK-*` o `P-PYE-*` por inferencia nominal;
- no se crean parámetros o reglas adicionales sin autoridad;
- no se convierten valores iniciales del catálogo en política empresarial definitiva;
- no se transforma ventas históricas en demanda sin política específica posterior;
- no se sustituyen datos ausentes por defaults;
- no se amplía C0 silenciosamente;
- no se convierte una evaluación STK en decisión final.

---

## 10. Criterio de entrada a contrato técnico

| Gate | Estado |
|---|---|
| Entradas canónicas | PASS |
| Unidad de cada magnitud | PASS |
| Fecha de referencia | PASS — mapping `as_of_date ↔ evaluation_date` reservado al contrato |
| Fórmula/política de consumo y demanda | PASS |
| Fórmula de cobertura | PASS |
| Regla de proyección | PASS |
| Recepción futura | PASS |
| Ausencia | PASS |
| Contradicción | PASS |
| Relación demostrada regla ↔ parámetro | PASS |

**Estado actual:** APTO PARA DISEÑO DE CONTRATO TÉCNICO STK.

La aptitud autoriza el contrato técnico, no la implementación directa. El contrato deberá superar su propia secuencia `DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR` antes de materializar código.

---

## 11. Estado

**STK Methodological Matrix v1.1**  
**Estado:** METODOLOGÍA CERRADA — GATE DE ENTRADA A CONTRATO TÉCNICO SUPERADO  
**No constituye por sí misma implementación ejecutable.**
