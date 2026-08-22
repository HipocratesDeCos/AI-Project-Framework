# MATRIZ DE REGLAS MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 2.1  
**Estado:** APROBADO — Baseline EIOS Vertical MVP  
**Última actualización:** 22/08/2026

---

# 1. PROPÓSITO

La Matriz de Reglas MVP define las condiciones mediante las cuales EIOS transforma los datos y parámetros disponibles en una recomendación empresarial sobre una propuesta de compra.

Constituye el puente entre:

- los datos;
- los parámetros;
- el análisis;
- las reglas;
- las excepciones;
- y la decisión final.

**Autoridad de resolución:** La Matriz define las reglas y sus resultados individuales. La resolución de conflictos entre reglas corresponde a `04_Reglas/Capa_resolucion_conflictos.md` (CRC v2.0). Esta matriz no constituye un segundo motor de resolución.

---

# 2. OBJETIVO

Determinar, para cada propuesta de compra, si la operación debe clasificarse inicialmente como:

- COMPRAR
- NEGOCIAR
- COMPRAR CONDICIONADO
- NO COMPRAR
- INFORMACIÓN INSUFICIENTE

La quinta categoría se incorpora para evitar que EIOS emita una recomendación cuando la calidad de los datos no permita una conclusión suficientemente fiable.

---

# 3. PRINCIPIO FUNDAMENTAL

EIOS no debe tomar una decisión basándose en un único indicador cuando la operación requiere una evaluación conjunta.

La recomendación deberá considerar, cuando estén disponibles:

1. precio;
2. histórico;
3. proveedores alternativos;
4. stock;
5. rotación;
6. demanda;
7. pedidos pendientes;
8. plazo de entrega;
9. condiciones de pago;
10. margen;
11. tesorería;
12. fondo de maniobra;
13. riesgo financiero;
14. calidad y antigüedad de los datos.

---

# 4. CLASIFICACIÓN DE LAS REGLAS

La versión 2.0 separa dos conceptos que en la versión anterior estaban mezclados:

- **Efecto de la regla:** qué capacidad tiene el resultado para intervenir en la decisión.
- **Severidad:** importancia o gravedad del resultado.

## 4.1 Efecto de la regla

| Código | Efecto | Descripción |
|---|---|---|
| R0 | BLOQUEO | Puede impedir la compra |
| R1 | CONDICIONANTE | Puede generar una compra condicionada |
| R2 | NEGOCIACIÓN | Recomienda mejorar una condición |
| R3 | INFORMATIVA | Aporta contexto sin modificar necesariamente la decisión |

## 4.2 Severidad

| Severidad | Significado |
|---|---|
| CRÍTICA | Puede comprometer la viabilidad de la operación |
| ALTA | Puede generar un perjuicio importante |
| MEDIA | Requiere atención |
| BAJA | Desviación menor |
| INFORMATIVA | Contexto sin impacto directo |

La severidad no sustituye al efecto y el efecto no sustituye a la severidad.

La CRC utiliza ambos conceptos junto con las salvaguardas, condiciones y excepciones aplicables.

---

# 5. REGLAS FINANCIERAS

## R-FIN-001 — Riesgo de incapacidad de pago

### Condición

Si la compra provoca que la capacidad prevista de atender pagos quede por debajo del nivel mínimo establecido.

### Resultado

**NO COMPRAR**

### Efecto / severidad

**R0 — BLOQUEO / CRÍTICA**

### Bloqueo

Sí.

### Explicación

La compra no debe realizarse si compromete la capacidad de la empresa para hacer frente a sus obligaciones de pago.

---

## R-FIN-002 — Fondo de maniobra insuficiente

### Condición

Si después de considerar la operación el fondo de maniobra queda por debajo del límite configurado.

### Resultado

**NO COMPRAR** o **COMPRAR CONDICIONADO**, según la severidad configurada.

### Efecto / severidad

**R0 — BLOQUEO / CRÍTICA**

### Bloqueo

Configurable.

---

## R-FIN-003 — Riesgo financiero elevado

### Condición

La operación reduce significativamente el margen de seguridad financiera de la empresa.

### Resultado

**COMPRAR CONDICIONADO** o **NO COMPRAR**

### Efecto / severidad

**R1 — CONDICIONANTE / ALTA**, pudiendo escalar a **R0 — BLOQUEO / CRÍTICA** cuando la condición financiera no sea resoluble.

### Posibles condiciones

- mejorar plazo de pago;
- reducir cantidad;
- reducir precio;
- conseguir financiación;
- mejorar cobros;
- adoptar otra medida financiera previamente definida.

---

# 6. REGLAS DE MARGEN

## R-MGE-001 — Margen inferior al mínimo

### Condición

El margen previsto después de la compra es inferior al margen mínimo configurado.

### Resultado

**NO COMPRAR**

o

**NEGOCIAR**

cuando exista posibilidad razonable de modificar las condiciones.

### Efecto / severidad

**R1 — CONDICIONANTE / ALTA**; podrá escalar a R0 cuando el margen negativo o el límite empresarial aplicable constituya un bloqueo no resoluble.

---

## R-MGE-002 — Margen dentro de tolerancia

### Condición

El margen se encuentra ligeramente por debajo del objetivo, pero dentro de la tolerancia configurada.

### Resultado

**NEGOCIAR** o **COMPRAR CONDICIONADO**

### Efecto / severidad

**R2 — NEGOCIACIÓN / MEDIA**

---

## R-MGE-003 — Margen objetivo alcanzado

### Condición

El margen cumple o supera el objetivo.

### Resultado

No genera una decisión por sí mismo.

### Función

Actúa como condición favorable.

### Efecto / severidad

**R3 — INFORMATIVA / INFORMATIVA**

---

# 7. REGLAS DE PRECIO

## R-PRE-001 — Precio superior a compra comparable reciente

### Condición

El precio propuesto supera el precio de una operación comparable reciente en el porcentaje configurado.

### Resultado

**NEGOCIAR**

### Efecto / severidad

**R2 — NEGOCIACIÓN / ALTA**

### Evidencia

La referencia deberá proceder de una operación comparable y suficientemente reciente conforme a los parámetros configurados.

---

## R-PRE-002 — Precio superior al límite crítico

### Condición

El precio supera el umbral crítico configurado.

### Resultado

**NEGOCIAR** o **NO COMPRAR**

### Efecto / severidad

**R1 — CONDICIONANTE / ALTA**, pudiendo escalar a R0 si el límite es no negociable.

### Observación

La decisión definitiva dependerá de:

- margen;
- proveedores alternativos;
- stock;
- demanda;
- condiciones de pago;
- situación financiera.

---

## R-PRE-003 — Precio inferior o igual al objetivo

### Condición

El precio propuesto es igual o inferior al precio máximo recomendado.

### Resultado

No genera bloqueo.

Puede contribuir favorablemente a la decisión.

### Efecto / severidad

**R3 — INFORMATIVA / INFORMATIVA**

---

# 8. REGLAS DE ANTIGÜEDAD DEL HISTÓRICO

## R-HIS-001 — Referencia demasiado antigua

### Condición

La compra utilizada como referencia supera la antigüedad máxima configurada.

### Resultado

No utilizar automáticamente como referencia principal.

### Acción

Buscar referencias más recientes.

### Efecto / severidad

**R3 — INFORMATIVA / MEDIA**

---

## R-HIS-002 — Histórico insuficiente

### Condición

No existe el número mínimo de operaciones comparables establecido.

### Resultado

**INFORMACIÓN INSUFICIENTE**
o análisis con advertencia.

### Efecto / severidad

**R3 — INFORMATIVA / INFORMATIVA**, salvo que la política de evidencia determine que la ausencia de histórico constituye un bloqueo de fiabilidad.

---

# 9. REGLAS DE COMPARABILIDAD

## R-HIS-003 — Operación no comparable

### Condición

La operación histórica presenta diferencias relevantes en:

- cantidad;
- proveedor;
- condiciones;
- descuentos;
- rappels;
- plazo de pago;
- características del artículo.

### Resultado

Reducir el nivel de fiabilidad de la referencia.

### No debe

Considerarse automáticamente equivalente a una operación comparable.

### Efecto / severidad

**R3 — INFORMATIVA / MEDIA**

---

# 10. REGLAS DE STOCK

## R-STK-001 — Riesgo de rotura de stock

### Condición

La proyección indica que el stock puede agotarse antes de que llegue una nueva compra.

### Resultado

**COMPRAR** o **COMPRAR CONDICIONADO**

### Efecto / severidad

**R1 — CONDICIONANTE / ALTA**

### Observación

La compra puede estar justificada aunque el precio sea ligeramente superior, siempre que no se incumplan reglas financieras o de margen críticas.

---

## R-STK-002 — Compra innecesaria por stock suficiente

### Condición

La cobertura prevista supera ampliamente el nivel configurado y no existen necesidades justificadas.

### Resultado

**NO COMPRAR**
o
**NEGOCIAR CANTIDAD**

### Efecto / severidad

**R2 — NEGOCIACIÓN / ALTA**; podrá escalar a R0 si existe un bloqueo empresarial explícito contra la compra.

---

## R-STK-003 — Exceso de stock

### Condición

El stock después de la compra supera el nivel máximo configurado.

### Resultado

**NEGOCIAR**
o
**NO COMPRAR**

### Efecto / severidad

**R2 — NEGOCIACIÓN / ALTA**, pudiendo escalar según la severidad configurada.

---

# 11. EXCEPCIÓN DE STOCK POR PEDIDO CONFIRMADO

## R-STK-004

### Condición

Existe exceso de stock o cobertura elevada.

### Excepción

Existe un pedido confirmado de cliente que absorberá total o parcialmente el stock.

### Resultado

La regla de exceso de stock queda mitigada.

### Resultado final posible

**COMPRAR**
o
**COMPRAR CONDICIONADO**

según el resto de reglas.

### Efecto / severidad

**R1 — CONDICIONANTE / ALTA**

### Tipo

EXCEPCIÓN

---

# 12. REGLAS DE ROTACIÓN

## R-ROT-001 — Producto de baja rotación

### Condición

La rotación se encuentra por debajo del umbral establecido.

### Resultado

**NEGOCIAR**
o
**NO COMPRAR**

### Efecto / severidad

**R2 — NEGOCIACIÓN / ALTA**

---

## R-ROT-002 — Producto sin rotación

### Condición

No existen ventas durante el periodo configurado.

### Resultado

**NO COMPRAR**

salvo excepción.

### Efecto / severidad

**R1 — CONDICIONANTE / ALTA**, pudiendo escalar a R0 cuando la política aplicable establezca bloqueo.

### Excepciones posibles

- pedido confirmado;
- campaña prevista;
- operación estratégica;
- decisión empresarial explícita.

---

# 13. REGLAS DE PLAZO DE ENTREGA

## R-ENT-001 — Entrega posterior al riesgo de rotura

### Condición

La fecha prevista de entrega es posterior a la fecha estimada de agotamiento del stock.

### Resultado

**NEGOCIAR**

### Efecto / severidad

**R2 — NEGOCIACIÓN / ALTA**

### Posibles recomendaciones

- solicitar entrega anticipada;
- dividir entrega;
- reducir plazo;
- buscar proveedor alternativo.

---

# 14. REGLAS DE PAGO

## R-PAG-001 — Plazo de pago inferior al objetivo

### Condición

El proveedor ofrece un plazo inferior al establecido como objetivo.

### Parámetros utilizados

- `P-PAG-002` — Plazo objetivo.
- `P-PAG-003` — Tolerancia de plazo, aplicada para modular la desviación respecto del objetivo.
- `P-PAG-004` — Considerar plazo, como control de activación de la evaluación ordinaria.
- `P-PAG-005` — Descuento pronto pago, cuando exista y deba incorporarse al cálculo económico de la condición de pago.

### Resultado

**NEGOCIAR**

### Efecto / severidad

**R2 — NEGOCIACIÓN / ALTA**

### Trazabilidad funcional

`P-PAG-002 → R-PAG-001` — directa.  
`P-PAG-003 → R-PAG-001` — derivada.  
`P-PAG-004 → R-PAG-001` — control funcional.  
`P-PAG-005 → R-PAG-001` — indirecta, mediante cálculo económico cuando corresponda.

La relación y su naturaleza están formalizadas en `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md`.

---

## R-PAG-002 — Plazo de pago insuficiente ante riesgo financiero

### Condición

La operación puede ser viable únicamente si se amplía el plazo de pago.

### Parámetros utilizados

- `P-PAG-001` — Plazo mínimo deseado, como mínimo aceptable para la condición de compra.
- `P-PAG-004` — Considerar plazo, como control de activación de la evaluación del plazo.
- `P-PAG-005` — Descuento pronto pago, cuando deba incorporarse al análisis económico de la condición financiera.

### Resultado

**COMPRAR CONDICIONADO**

### Condición de compra

La operación únicamente será recomendable si se consigue el plazo de pago mínimo establecido.

### Efecto / severidad

**R1 — CONDICIONANTE / ALTA**

### Trazabilidad funcional

`P-PAG-001 → R-PAG-002` — directa.  
`P-PAG-004 → R-PAG-002` — control funcional.  
`P-PAG-005 → R-PAG-002` — indirecta, mediante cálculo económico cuando corresponda.

La relación y su naturaleza están formalizadas en `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md`.

---

# 15. REGLAS DE PROVEEDORES

## R-PROV-001 — Existencia de proveedor alternativo

### Condición

Existe uno o más proveedores alternativos con condiciones potencialmente mejores.

### Resultado

**NEGOCIAR**

### Efecto / severidad

**R2 — NEGOCIACIÓN / MEDIA**

---

## R-PROV-002 — Proveedor actual con condiciones claramente desfavorables

### Condición

Existe una alternativa comparable que mejora significativamente:

- precio;
- plazo;
- condiciones;
- fiabilidad;
- disponibilidad.

### Resultado

**NEGOCIAR**

La evaluación de un proveedor alternativo se documenta como **acción secundaria**, no como resultado oficial adicional.

### Efecto / severidad

**R2 — NEGOCIACIÓN / ALTA**

---

# 16. DESCUENTOS Y RAPPELS

## R-COM-001 — Descuento disponible

### Condición

Existe posibilidad de obtener un descuento.

### Resultado

Incluir en la negociación.

### No debe

Modificar automáticamente la recomendación si no se conoce su aplicación real.

### Efecto / severidad

**R2 — NEGOCIACIÓN / MEDIA**

---

## R-COM-002 — Rappel disponible

### Condición

La operación puede mejorar el coste efectivo mediante rappel.

### Resultado

Calcular, cuando sea posible, el coste efectivo.

### Efecto / severidad

**R3 — INFORMATIVA / MEDIA**

---

# 17. REGLAS DE CALIDAD DE DATOS

## R-DAT-001 — Datos actualizados

### Condición

Los datos se encuentran dentro del periodo máximo permitido.

### Resultado

Continuar análisis normalmente.

### Efecto / severidad

**R3 — INFORMATIVA / INFORMATIVA**

---

## R-DAT-002 — Datos antiguos

### Condición

La fecha de actualización supera el periodo establecido.

### Resultado

Mostrar advertencia.

### Resultado de decisión

Puede continuar si la política lo permite.

### Efecto / severidad

**R3 — INFORMATIVA / MEDIA**

---

## R-DAT-003 — Datos insuficientes

### Condición

No existe información suficiente para realizar una evaluación fiable.

### Resultado

**INFORMACIÓN INSUFICIENTE**

### Efecto / severidad

**R0 — BLOQUEO / CRÍTICA respecto a la fiabilidad**

### Principio

EIOS no debe inventar una recomendación cuando los datos no permiten sostenerla.

---

# 18. REGLAS DE INTERACCIÓN Y CONFLICTO

Las reglas `CON-*` conservan los casos de conflicto definidos en la v1.0. En v2.0 documentan **situaciones de interacción y resultados esperados**; no constituyen un segundo sistema de resolución.

Cuando varias reglas se activan simultáneamente:

```text
REGLAS INDIVIDUALES
       ↓
EVALUACIÓN
       ↓
CRC
       ↓
RESULTADO CONSOLIDADO
```

La CRC aplica la jerarquía oficial, salvaguardas, excepciones y condiciones.

---

# 19. REGLA DE CONFLICTO FINANCIERO

## R-CON-001

### Situación

La compra:

- tiene buen precio;
- tiene buen margen;
- evita una posible rotura de stock;

pero compromete la capacidad financiera de la empresa.

### Resultado

**NO COMPRAR**

### Efecto / severidad

**R0 — BLOQUEO / CRÍTICA**

### Principio

La solvencia y capacidad de pago prevalecen sobre ventajas operativas o comerciales de menor autoridad.

---

## R-CON-002 — Conflicto stock / precio

### Situación

Existe riesgo de rotura, pero el precio es superior al objetivo.

### Resultado

**NEGOCIAR**

### Posibles recomendaciones

- mantener precio si se adelanta entrega;
- negociar precio;
- reducir cantidad;
- buscar proveedor alternativo.

### Efecto / severidad

**R2 — NEGOCIACIÓN / ALTA**

---

## R-CON-003 — Conflicto stock / finanzas

### Situación

Existe riesgo de rotura, pero la compra compromete la situación financiera.

### Resultado

**NO COMPRAR**

salvo que se encuentre una condición que elimine el riesgo financiero.

### Posibles alternativas

- ampliar plazo de pago;
- reducir cantidad;
- negociar precio;
- financiación;
- solución financiera previamente aprobada.

### Efecto / severidad

**R0 — BLOQUEO / CRÍTICA**, salvo que la condición alternativa elimine el bloqueo y la CRC determine un resultado condicionable.

---

## R-CON-004 — Conflicto stock / pedido confirmado

### Situación

Existe exceso de stock, pero existe un pedido confirmado que justifica la compra.

### Resultado

La regla de exceso de stock queda mitigada.

### Resultado final

Dependerá de:

- margen;
- precio;
- situación financiera;
- plazo de entrega.

### Efecto / severidad

**R1 — CONDICIONANTE / ALTA**

---

## R-CON-005 — Conflicto precio / margen

### Situación

El precio de compra es elevado pero el margen final continúa dentro de los parámetros aceptables.

### Resultado

**NEGOCIAR**

o

**COMPRAR**

según el resto de reglas.

### Efecto / severidad

**R2 — NEGOCIACIÓN / MEDIA**

---

## R-CON-006 — Conflicto histórico / mercado

### Situación

El precio histórico es inferior al precio actual, pero el mercado ha experimentado un incremento de costes.

### Resultado

No utilizar automáticamente el histórico como bloqueo.

### Acción

Comparar con:

- referencias recientes;
- proveedores alternativos;
- evolución del mercado;
- costes actuales.

### Efecto / severidad

**R3 — INFORMATIVA / MEDIA**

---

# 25. RESULTADOS OFICIALES

Los resultados oficiales de EIOS son únicamente:

| Resultado | Significado |
|---|---|
| COMPRAR | Operación viable conforme a las reglas aplicables |
| NEGOCIAR | Existe margen para mejorar condiciones |
| COMPRAR CONDICIONADO | La compra puede ser viable si se cumple una condición |
| NO COMPRAR | Existe un bloqueo o la operación no resulta viable |
| INFORMACIÓN INSUFICIENTE | La evidencia disponible no permite una recomendación fiable |

Expresiones como **NEGOCIAR CANTIDAD** o **EVALUAR PROVEEDOR ALTERNATIVO** son acciones secundarias, no resultados oficiales.

---

# 26. ESTRUCTURA OBLIGATORIA DE UNA REGLA

Cada regla deberá poder documentarse mediante:

```text
Rule_ID
Dominio
Nombre
Condición
Efecto (R0-R3)
Severidad
Resultado
Parámetros
Evidencia
Excepciones
Explicación
```

Opcionalmente:

```text
Dependencias
Reglas relacionadas
Escenarios
Observaciones
```

---

# 27. PARÁMETROS

Las reglas no deberán fijar valores rígidos cuando estos deban ser configurables.

Ejemplos:

- margen mínimo;
- stock mínimo;
- stock máximo;
- antigüedad máxima de datos;
- plazo mínimo de pago;
- límite de precio;
- umbral de impacto financiero;
- número mínimo de comparables.

Los valores deberán proceder del catálogo de parámetros correspondiente.

---

# 28. EVIDENCIA

Toda regla que influya en una recomendación deberá poder identificar la evidencia utilizada.

La evidencia deberá respetar el contrato de evidencia definido para EIOS.

Cuando la evidencia requerida sea insuficiente, la regla no deberá producir una recomendación que exceda la fiabilidad permitida.

---

# 29. EXCEPCIONES

Las excepciones deberán estar explícitamente definidas.

Una excepción debe indicar:

```text
Exception_ID
Rule_ID
Condición de aplicación
Autoridad
Resultado permitido
Trazabilidad
```

No se permitirán excepciones implícitas.

Las salvaguardas clasificadas como no anulables no podrán ser neutralizadas por una excepción ordinaria.

---

# 30. NO COMPENSACIÓN AUTOMÁTICA

Una regla favorable no debe compensar automáticamente una regla crítica desfavorable.

Ejemplo:

```text
Precio        → favorable
Margen        → favorable
Proveedor     → favorable
Tesorería     → CRÍTICA
```

El resultado no se determina mediante suma de puntos.

La CRC resolverá el conflicto según la autoridad correspondiente.

---

# 31. RELACIÓN CON VIABILITY FRONTIER

Las reglas pueden aportar restricciones o condiciones a la determinación de viabilidad.

La **Viability Frontier** determina si una alternativa se encuentra dentro o fuera de la frontera de viabilidad definida.

La matriz de reglas no debe duplicar esa metodología.

---

# 32. RELACIÓN CON ESCENARIOS

Cuando una regla pueda resolverse mediante una modificación de:

- precio;
- cantidad;
- plazo;
- proveedor;
- condiciones comerciales;

podrá generar una condición o alternativa para evaluación mediante escenarios.

El escenario determinará si la modificación propuesta permite recuperar la viabilidad.

---

# 33. RELACIÓN CON NEGOCIACIÓN

Las reglas R2 pueden producir una recomendación de negociación.

Ejemplo:

```text
R-PRE-001
→ NEGOCIAR

Acción secundaria:
Solicitar reducción del precio.
```

La negociación concreta será desarrollada por los componentes especializados correspondientes.

---

# 34. REGLA DE INFORMACIÓN INSUFICIENTE

Cuando una regla crítica no pueda evaluarse por falta de evidencia:

```text
Resultado:
INFORMACIÓN INSUFICIENTE
```

Esto evita confundir:

```text
"No sabemos"
```

con:

```text
"No es viable"
```

---

# 35. ESTRUCTURA MÍNIMA DE TRAZABILIDAD DE REGLA

Cada regla deberá poder identificar, como mínimo:

```text
Rule_ID
Dominio
Nombre
Condición
Efecto (R0-R3)
Severidad
Resultado
Parámetros utilizados
Evidencia requerida
Excepciones aplicables
Explicación
```

Cuando el sistema lo soporte, deberá añadir:

```text
Decision_ID
Scenario_ID
Data_Snapshot_ID
Parameter_Version
Rules_Version
EIOS_Version
```

---

# 36. TRAZABILIDAD

Toda recomendación deberá poder reconstruirse a partir de:

```text
Datos
↓
Parámetros
↓
Reglas activadas
↓
Efecto / severidad
↓
Evidencia
↓
CRC
↓
Recomendación
```

La explicación deberá permitir identificar por qué se activó una regla y qué evidencia sustentó su resultado.

---

# 37. EXPLICABILIDAD

Cada regla deberá poder traducirse a una explicación ejecutiva.

Ejemplo:

```text
Regla:
R-PRE-001

Resultado:
NEGOCIAR

Explicación:
El precio propuesto está por encima de la referencia
configurada para operaciones comparables.
```

La explicación no deberá introducir información que no proceda de la evidencia disponible.

---

# 38. CONTROL HUMANO

Las reglas proporcionan evaluaciones.

La CRC consolida resultados.

EIOS genera una recomendación.

El decisor autorizado toma la decisión empresarial final.

```text
REGLAS
   ↓
EVALUACIÓN
   ↓
CRC
   ↓
RECOMENDACIÓN
   ↓
DECISOR
```

---

# 39. PRINCIPIOS RECTORES

La Matriz de Reglas MVP deberá respetar:

1. **Trazabilidad**
2. **Explicabilidad**
3. **No compensación automática**
4. **Separación entre efecto y severidad**
5. **Separación entre regla y resolución de conflictos**
6. **Configurabilidad**
7. **Evidencia suficiente**
8. **Control humano**
9. **No automatización silenciosa**
10. **Coherencia con la arquitectura EIOS**

---

# 40. REGLAS PENDIENTES DE PARAMETRIZACIÓN O VALIDACIÓN EMPRESARIAL

Quedan pendientes de parametrización o validación empresarial:

- umbrales definitivos de margen;
- límites de precio;
- metodología de comparables;
- umbrales de stock;
- horizonte financiero;
- umbrales de tesorería;
- niveles definitivos de riesgo de proveedor;
- catálogo definitivo de excepciones;
- salvaguardas no anulables;
- reglas específicas por familia de producto.

No deben fijarse valores definitivos sin validación empresarial.

---

# 41. ESTADO DEL DOCUMENTO

**Versión:** 2.1  
**Estado:** APROBADO — Baseline EIOS Vertical MVP  
**Baseline:** EIOS Vertical MVP  
**Autoridad:** Definición de reglas de negocio MVP  
**Resolución de conflictos:** `04_Reglas/Capa_resolucion_conflictos.md`  
**Control:** Sujeto a `Matriz_Autoridad_Documental.md` y Salvaguarda Oficial EIOS Vertical MVP

---

# 42. RELACIÓN DOCUMENTAL

La matriz deberá mantenerse coherente con:

- `Matriz_Autoridad_Documental.md` — autoridad documental.
- `04_Reglas/Capa_resolucion_conflictos.md` — resolución de conflictos.
- contrato de evidencia EIOS — requisitos de evidencia.
- `Rule_Dependency_Matrix.md` — dependencias entre reglas.
- catálogo de parámetros MVP — parámetros configurables.
- `05_Motor/Viability_Frontier.md` — viabilidad.
- `05_Motor/Scenario_Engine.md` — escenarios.

Ninguna regla de este documento debe establecer silenciosamente una jerarquía de resolución que contradiga la CRC o la autoridad documental superior.
