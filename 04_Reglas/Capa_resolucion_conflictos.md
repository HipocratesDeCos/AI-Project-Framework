# CAPA DE RESOLUCIÓN DE CONFLICTOS — MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 2.0  
**Estado:** v2.0 — preparada para aprobación y posterior sustitución en GitHub  
**Ubicación:** `04_Reglas/Capa_resolucion_conflictos.md`

---

# 1. Propósito

La Capa de Resolución de Conflictos (CRC) es el componente de EIOS encargado de **consolidar los resultados de múltiples reglas y evaluaciones** cuando producen recomendaciones distintas o contradictorias.

La CRC no sustituye al motor de reglas ni a los motores especializados.

El motor de reglas determina qué condiciones se cumplen.

La CRC determina cómo deben resolverse los resultados incompatibles dentro de la jerarquía definida y consolida los resultados procedentes de las capas y motores especializados.

La CRC **no constituye un segundo motor de decisión ni sustituye al decisor humano**.

---

# 2. Objetivo empresarial

EIOS no debe limitarse a detectar problemas.

Debe ayudar a encontrar la alternativa económicamente más viable para realizar una operación cuando sea posible.

Principio fundamental:

> **EIOS no pretende impedir comprar. Pretende evitar comprar mal.**

Por tanto, ante una situación desfavorable, el sistema debe intentar determinar si existe una condición que permita realizar la operación sin comprometer la situación económico-financiera de la empresa.

La existencia de viabilidad no implica automáticamente una orden de compra.

---

# 3. Posición dentro de la arquitectura

La CRC se sitúa después de la evaluación de reglas y de la determinación de viabilidad, antes de la recomendación consolidada al decisor.

```text
DATOS
  ↓
EVIDENCIA
  ↓
REGLAS
  ↓
EVALUACIÓN
  ↓
VIABILITY FRONTIER
  ↓
ESCENARIOS / DECISION TWIN
  ↓
NEGOCIACIÓN
  ↓
CRC
  ↓
RECOMENDACIÓN
  ↓
DECISOR
```

Assurance actúa transversalmente sobre todo el flujo.

La decisión empresarial final permanece bajo control humano.

---

# 4. Responsabilidades

La CRC debe:

- recibir los resultados de las reglas;
- comprobar la fiabilidad de los datos utilizados;
- identificar reglas críticas;
- identificar bloqueos;
- evaluar excepciones;
- determinar si una situación desfavorable puede resolverse mediante una condición;
- resolver conflictos entre reglas y evaluaciones;
- comparar escenarios cuando sea necesario;
- consolidar el resultado de la evaluación;
- identificar el motivo dominante;
- identificar los factores relevantes;
- generar una explicación comprensible;
- mantener trazabilidad hacia reglas, parámetros, datos, escenarios y versiones;
- evitar la saturación de información al usuario.

La CRC no debe:

- redefinir silenciosamente una regla;
- sustituir al motor de reglas;
- convertir una condición viable en una orden automática de compra;
- ejecutar decisiones empresariales externas.

---

# 5. Principio de no compensación automática

EIOS no debe utilizar un sistema simple de puntuación en el que factores positivos compensen automáticamente factores negativos.

Ejemplo:

```text
Precio       FAVORABLE
Proveedor    FAVORABLE
Margen       FAVORABLE
Stock        DESFAVORABLE
Tesorería    CRÍTICA
```

La existencia de tres factores favorables no permite compensar automáticamente una situación financiera crítica.

Las reglas críticas deben prevalecer según la jerarquía establecida.

Una puntuación agregada nunca debe neutralizar silenciosamente una salvaguarda o bloqueo crítico.

---

# 6. Niveles de efecto de una regla

Cada regla deberá clasificarse según el efecto que puede producir.

| Nivel | Tipo | Efecto |
|---|---|---|
| R0 | BLOQUEO | Puede impedir la compra |
| R1 | CONDICIONANTE | Puede convertir la operación en COMPRAR CONDICIONADO |
| R2 | NEGOCIACIÓN | Recomienda negociar |
| R3 | INFORMATIVA | Aporta contexto sin modificar necesariamente la decisión |

La clasificación de una regla pertenece a la documentación oficial de reglas.

---

# 7. Severidad

Cada resultado de una regla deberá incorporar un nivel de severidad.

| Severidad | Significado |
|---|---|
| CRÍTICA | Puede comprometer la viabilidad de la operación |
| ALTA | Puede generar un perjuicio importante |
| MEDIA | Situación desfavorable que requiere atención |
| BAJA | Desviación menor |
| INFORMATIVA | Información contextual |

La severidad y el efecto de la regla son conceptos diferentes.

Ejemplo:

Una regla puede ser de tipo **NEGOCIACIÓN** y tener severidad **ALTA**.

---

# 8. Jerarquía de resolución

La CRC utilizará una jerarquía conceptual:

```text
SALVAGUARDAS CRÍTICAS
        ↓
BLOQUEOS
        ↓
CONDICIONES SOLUCIONABLES
        ↓
REGLAS DE NEGOCIACIÓN
        ↓
REGLAS INFORMATIVAS
```

Esta jerarquía no sustituye a los parámetros configurables.

Determina cómo debe resolverse un conflicto cuando varias reglas o evaluaciones actúan simultáneamente.

Las salvaguardas definidas como obligatorias no pueden ser compensadas mediante señales favorables.

---

# 9. Decisiones oficiales

EIOS tendrá cinco resultados posibles:

### 🟢 COMPRAR

La operación cumple los criterios establecidos y no existe una condición crítica que impida realizarla.

### 🟡 NEGOCIAR

La operación puede ser viable, pero existen condiciones comerciales que justifican intentar mejorar la operación.

### 🔵 COMPRAR CONDICIONADO

La operación presenta una o varias condiciones desfavorables, pero existe una modificación concreta que permitiría hacerla viable.

### 🔴 NO COMPRAR

La operación no resulta viable o compromete una condición crítica que no puede solucionarse mediante las alternativas disponibles.

### ⚪ INFORMACIÓN INSUFICIENTE

La información disponible no permite realizar una recomendación fiable.

La decisión final corresponde al decisor autorizado.

---

# 10. Motivo dominante

Toda recomendación deberá tener un único motivo dominante.

El motivo dominante es el factor que ha tenido mayor influencia en el resultado consolidado.

Ejemplo:

```text
NO COMPRAR

Motivo dominante:
La operación compromete la capacidad prevista de atender
los pagos dentro del horizonte configurado.
```

El motivo dominante debe ser breve, concreto y comprensible para un usuario no financiero.

---

# 11. Factores relevantes

El motivo dominante no debe ocultar información complementaria de valor.

Los factores relevantes son circunstancias adicionales que ayudan al CEO o responsable de compras a comprender la situación y disponer de argumentos para negociar.

Ejemplo:

```text
NEGOCIAR

Motivo dominante:
Precio superior a la referencia configurable.

Factores relevantes:
Precio propuesto: 18,20 €.
Precio de referencia: 17,10 €.
Diferencia: +6,43 %.
Última compra comparable: 17,40 € hace 2 meses.
Stock actual: 420 unidades.
Cobertura estimada: 74 días.
Existe proveedor alternativo.
Plazo de pago propuesto: 30 días.
```

Los factores relevantes no deben modificar por sí mismos el resultado salvo que una regla específica así lo determine.

Su función principal es proporcionar:

- contexto;
- argumentos;
- transparencia;
- capacidad de negociación;
- comprensión de la decisión.

---

# 12. Principio de información útil

EIOS debe diferenciar entre:

**Información necesaria para decidir**

y
**Información útil para actuar.**

El CEO no debe recibir toda la información disponible.

Debe recibir primero:

1. Decisión.
2. Motivo dominante.
3. Factores relevantes.
4. Recomendación o condición, si existe.
5. Acceso al detalle cuando sea necesario.

---

# 13. Excepciones

Las excepciones permiten que una circunstancia desfavorable no produzca automáticamente una decisión negativa cuando existe una justificación empresarial válida.

Ejemplo:

```text
Regla:
Exceso de stock

Excepción:
Existe pedido confirmado de cliente

Resultado:
La regla de exceso de stock no bloquea la operación.
```

Las excepciones deberán estar definidas y parametrizadas.

No se permitirá que una excepción se aplique de forma implícita o arbitraria.

---

# 14. Salvaguardas no anulables

No todas las reglas deben poder ser anuladas mediante una excepción.

Las salvaguardas destinadas a proteger la estabilidad financiera y la integridad de la decisión deberán tener un nivel de protección superior.

Ejemplos potenciales:

- imposibilidad de atender obligaciones financieras;
- ausencia de información crítica;
- datos incompatibles o inválidos;
- errores graves en los datos de entrada.

La lista definitiva de salvaguardas no anulables deberá aprobarse antes de la implementación.

---

# 15. Compra condicionada

**COMPRAR CONDICIONADO** debe utilizarse cuando exista una condición concreta capaz de transformar una operación desfavorable en una operación viable.

Ejemplos:

### Caso 1 — Precio

Precio propuesto: 18,50 €

Precio máximo recomendado: 17,80 €

Condición:

Comprar únicamente si el proveedor acepta ≤17,80 €.

### Caso 2 — Plazo de pago

Situación:

El pago a 30 días genera tensión financiera.

Condición:

Ampliar el plazo a 90 días.

### Caso 3 — Cantidad

Situación:

La cantidad propuesta genera exceso de stock.

Condición:

Reducir la compra de 1.000 a 400 unidades.

La condición debe quedar explícita y ser trazable.

---

# 16. Principio de mínima intervención

Cuando una operación presenta un problema, EIOS debe buscar la solución menos restrictiva que mantenga la seguridad económica de la empresa.

Orden conceptual:

```text
INFORMAR
   ↓
NEGOCIAR
   ↓
CONDICIONAR
   ↓
NO COMPRAR
```

No se debe recomendar **NO COMPRAR** cuando existe una alternativa razonable que permite resolver el problema.

Sin embargo, las salvaguardas críticas prevalecen sobre este principio.

---

# 17. Riesgo financiero

El riesgo financiero tendrá especial prioridad.

Si una compra compromete la capacidad de la empresa para atender sus pagos, EIOS deberá considerar la operación no viable salvo que exista una condición concreta que permita resolver el riesgo.

Posibles alternativas a evaluar:

- ampliación del plazo de pago;
- reducción de la cantidad comprada;
- reducción del precio;
- utilización de stock existente;
- recuperación de liquidez mediante productos de baja rotación;
- reducción del periodo de cobro;
- otras medidas empresariales configuradas.

EIOS podrá proponer alternativas, pero no ejecutará automáticamente decisiones financieras o empresariales.

---

# 18. Stock: escenario con y sin compra

La CRC podrá evaluar dos escenarios:

### ESCENARIO A — No realizar la compra

```text
Stock actual
+ entradas previstas
- salidas previstas
= stock proyectado
```

### ESCENARIO B — Realizar la compra

```text
Stock actual
+ compra propuesta
+ entradas previstas
- salidas previstas
= stock proyectado con compra
```

La comparación permitirá detectar, entre otras situaciones:

- posible rotura de stock;
- exceso de stock;
- compra innecesaria;
- mejora de cobertura;
- impacto de la cantidad propuesta.

---

# 19. Fecha de referencia

La fecha de propuesta de compra será la fecha principal de referencia para el análisis.

EIOS deberá evitar utilizar información posterior a dicha fecha cuando se realice una evaluación histórica o una simulación de decisión.

Ejemplo:

```text
Fecha de propuesta:
09/08/2026

Datos operativos:
referidos a la fecha de propuesta

Histórico:
información disponible hasta la fecha de propuesta

Proyección:
desde la fecha de propuesta

Fecha prevista de entrega:
25/08/2026
```

Este principio será especialmente importante para las pruebas retrospectivas.

---

# 20. Calidad y fiabilidad de los datos

La CRC deberá considerar la calidad de la información antes de emitir una recomendación.

Niveles:

```text
ALTA
MEDIA
BAJA
INSUFICIENTE
```

La antigüedad de los datos no debe interpretarse de forma uniforme.

Debe distinguirse entre:

- actualidad de datos operativos;
- antigüedad de referencias históricas;
- antigüedad de precios comparables;
- calidad de los registros.

La calidad y suficiencia de la evidencia deberá respetar el `Evidence_Contract.md`.

---

# 21. Histórico insuficiente

Como criterio inicial:

| Compras comparables | Resultado |
|---:|---|
| 0 | Información insuficiente |
| 1 | Fiabilidad baja |
| 2 o más | Puede utilizarse como referencia |

Estos valores serán configurables y deberán validarse con datos reales.

---

# 22. Precio y referencia histórica

EIOS no deberá considerar automáticamente que un precio histórico antiguo representa un precio actual fiable.

La comparación deberá considerar:

- antigüedad;
- número de operaciones;
- fechas;
- condiciones de compra;
- proveedor;
- cantidad;
- descuentos;
- rappels;
- condiciones de pago;
- otros factores relevantes disponibles.

El precio máximo recomendado será objeto de una metodología específica que deberá definirse antes de su implementación.

---

# 23. Resolución mediante escenarios

Cuando exista una situación conflictiva, EIOS podrá comparar escenarios.

Ejemplo:

| Factor | No comprar | Comprar | Condicionado |
|---|---|---|---|
| Tesorería | 🟢 | 🔴 | 🟢 |
| Stock | 🟢 | 🔴 | 🟡 |
| Margen | — | 🟢 | 🟢 |
| Plazo de pago | — | 🔴 | 🟢 |

Resultado:

**COMPRAR CONDICIONADO**

Condición:

Obtener un plazo de pago mínimo de 90 días.

Los escenarios deberán utilizarse únicamente cuando aporten valor a la decisión y deberán respetar el `Scenario_Engine.md` y el `Decision_Twin.md`.

---

# 24. Trazabilidad

Toda recomendación deberá poder rastrearse hasta:

```text
DECISIÓN
   ↓
MOTIVO DOMINANTE
   ↓
RESULTADO CONSOLIDADO
   ↓
REGLA / EVALUACIÓN
   ↓
PARÁMETRO
   ↓
INDICADOR
   ↓
DATO / EVIDENCIA DE ORIGEN
```

Ejemplo:

```text
NO COMPRAR
   ↓
Riesgo financiero crítico
   ↓
FIN-001
   ↓
Tesorería mínima
   ↓
Tesorería proyectada
   ↓
Datos financieros del ERP
```

La trazabilidad deberá incorporar, cuando corresponda, los identificadores de versionado definidos por EIOS.

---

# 25. Explicabilidad

La explicación para el usuario deberá responder:

- ¿Qué recomienda EIOS?
- ¿Por qué?
- ¿Qué factores ha considerado?
- ¿Existe alguna alternativa?
- ¿Qué condición permitiría modificar la recomendación?
- ¿Qué nivel de fiabilidad tienen los datos?

La explicación deberá ser coherente con la evidencia disponible y no ocultar incertidumbres relevantes.

---

# 26. Ejemplo de salida para el CEO

### 🟡 NEGOCIAR

**Motivo principal**

Precio superior a la referencia configurable.

**Factores relevantes**

- Precio propuesto: 18,20 €.
- Precio de referencia: 17,10 €.
- Diferencia: +6,43 %.
- Última compra comparable: 17,40 €.
- Última compra: hace 2 meses.
- Stock actual: 420 unidades.
- Cobertura estimada: 74 días.
- Proveedor alternativo disponible.
- Plazo de pago actual: 30 días.

**Recomendación de negociación**

Precio máximo recomendado: 17,80 €.

**Objetivo**

Reducir el precio manteniendo un margen operativo adecuado y evitando incrementar innecesariamente el stock.

---

# 27. Principio de comunicación ejecutiva

La pantalla principal deberá ser breve.

El sistema no debe mostrar automáticamente todos los cálculos disponibles.

Orden recomendado:

```text
DECISIÓN
   ↓
MOTIVO DOMINANTE
   ↓
FACTORES RELEVANTES
   ↓
RECOMENDACIÓN / CONDICIÓN
   ↓
DETALLE
```

El detalle completo deberá estar disponible bajo demanda.

---

# 28. Registro interno de resolución

Aunque el usuario vea una respuesta resumida, EIOS deberá conservar internamente:

- reglas activadas;
- reglas no activadas;
- parámetros utilizados;
- valores utilizados;
- severidad;
- prioridad;
- excepciones;
- condiciones evaluadas;
- escenarios;
- calidad de datos;
- motivo dominante;
- factores relevantes;
- resultado consolidado;
- decisión final;
- identificadores de trazabilidad y versionado cuando proceda.

Esto permitirá auditoría, pruebas y mejora futura.

---

# 29. Principio de no automatización de decisiones empresariales externas

EIOS puede:

- analizar;
- calcular;
- recomendar;
- comparar;
- alertar;
- proponer condiciones de negociación.

EIOS no debe ejecutar automáticamente:

- ampliaciones de capital;
- ventas de inmovilizado;
- cambios de política de cobro;
- ofertas comerciales;
- compras;
- negociaciones con proveedores;

salvo que una futura versión incorpore explícitamente esas capacidades y exista autorización empresarial.

---

# 30. Relación con otros documentos

La CRC depende conceptualmente de:

### `01_Modelo/Modelo_Empresarial_Decision.md`

Define qué debe decidir EIOS.

### `02_Parametros/Catalogo_Parametros_MVP.md`

Define los parámetros configurables.

### `02_Parametros/Centro_Parametrizacion.md`

Define cómo se administran los parámetros.

### `04_Reglas/Matriz_Reglas_MVP.md`

Define las reglas que generan resultados.

### `04_Reglas/Evidence_Contract.md`

Define la evidencia necesaria y los criterios de suficiencia.

### `04_Reglas/Rule_Dependency_Matrix.md`

Define dependencias entre reglas, datos y evidencias.

### `05_Motor/Viability_Frontier.md`

Define la frontera de viabilidad.

### `05_Motor/Scenario_Engine.md`

Define la generación, comparación y versionado de escenarios.

### `05_Motor/Decision_Twin.md`

Define la representación estructurada de alternativas.

### `05_Motor/Negotiation_Intelligence.md`

Define el análisis de negociación.

### `05_Motor/Negotiation_Ladder.md`

Define la secuencia de negociación.

La CRC consolida los resultados que recibe de estos componentes según su autoridad especializada.

---

# 31. Regla de coherencia documental

Ninguno de los documentos anteriores deberá definir una jerarquía de decisión contradictoria con esta capa.

Cuando exista una modificación en:

- prioridades;
- severidades;
- bloqueos;
- excepciones;
- resultados;
- condiciones;

deberá revisarse la coherencia entre todos los documentos relacionados.

La CRC no modifica silenciosamente las reglas que originaron el conflicto.

Cuando exista una contradicción con una autoridad documental superior, deberá aplicarse la `Matriz_Autoridad_Documental.md`.

---

# 32. Estado MVP

La siguiente definición queda establecida como base conceptual del MVP:

### Resultados

```text
COMPRAR
NEGOCIAR
COMPRAR CONDICIONADO
NO COMPRAR
INFORMACIÓN INSUFICIENTE
```

### Componentes de resolución

- efecto de la regla;
- severidad;
- prioridad;
- bloqueos;
- excepciones;
- condiciones;
- calidad de datos;
- escenarios;
- motivo dominante;
- factores relevantes;
- trazabilidad;
- resultado consolidado.

### Principios

- no compensación automática;
- salvaguarda financiera;
- mínima intervención;
- no saturación informativa;
- explicabilidad;
- trazabilidad;
- configuración humana;
- adaptabilidad empresarial;
- control humano de la decisión.

---

# 33. Elementos pendientes de definición

Quedan deliberadamente pendientes:

- fórmula definitiva del precio máximo recomendado;
- jerarquía numérica definitiva de prioridades;
- lista definitiva de salvaguardas no anulables;
- catálogo definitivo de excepciones;
- metodología de cálculo de fiabilidad;
- fórmula definitiva de proyección de stock;
- método definitivo para calcular el impacto financiero de una compra;
- reglas específicas por familia o artículo;
- diseño visual definitivo del Centro de Parametrización;
- implementación técnica de la CRC.

Estos elementos no deben inventarse prematuramente.

Deberán definirse mediante casos reales y validación empresarial.

---

# 34. Principio rector

EIOS no debe limitarse a responder:

> **¿Compro o no compro?**

Debe ayudar a responder:

> **¿Qué tendría que cambiar para que esta compra fuese económicamente segura y razonable para la empresa?**

Y cuando no exista una solución viable:

> **No comprar.**

La CRC consolida la evaluación; **EIOS recomienda y el decisor decide**.

---

# 35. Estado documental

**Versión:** 2.0  
**Estado:** v2.0 — preparada para aprobación y posterior sustitución en GitHub  
**Baseline:** EIOS Vertical MVP  
**Autoridad:** Resolución de conflictos entre reglas y evaluaciones  
**Control:** Sujeto a Matriz de Autoridad Documental y Salvaguarda Oficial EIOS Vertical MVP
