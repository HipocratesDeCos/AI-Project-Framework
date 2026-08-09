# MATRIZ DE REGLAS MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.1  
**Estado:** En desarrollo  
**Última actualización:** 09/08/2026

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

# 4. JERARQUÍA DE DECISIÓN

Las reglas se organizan inicialmente por niveles de prioridad.

## NIVEL 1 — CRÍTICO

Puede impedir la compra.

Principalmente:

- riesgo financiero grave;
- incapacidad prevista para atender pagos;
- incumplimiento de condiciones financieras mínimas.

## NIVEL 2 — MUY ALTO

Puede impedir la compra o exigir condiciones.

Principalmente:

- margen insuficiente;
- exceso de stock grave;
- compra incompatible con la situación operativa.

## NIVEL 3 — ALTO

Normalmente genera negociación o compra condicionada.

Principalmente:

- precio elevado;
- condiciones de pago desfavorables;
- riesgo relevante de stock.

## NIVEL 4 — MEDIO

Puede modificar la recomendación.

Principalmente:

- diferencias históricas;
- proveedor alternativo;
- rotación;
- descuentos;
- rappels.

## NIVEL 5 — INFORMATIVO

Aporta contexto sin modificar por sí mismo la decisión.

---

# 5. REGLAS FINANCIERAS

## FIN-001 — Riesgo de incapacidad de pago

### Condición

Si la compra provoca que la capacidad prevista de atender pagos quede por debajo del nivel mínimo establecido.

### Resultado

**NO COMPRAR**

### Prioridad

1 — CRÍTICA

### Bloqueo

Sí.

### Explicación

La compra no debe realizarse si compromete la capacidad de la empresa para hacer frente a sus obligaciones de pago.

---

## FIN-002 — Fondo de maniobra insuficiente

### Condición

Si después de considerar la operación el fondo de maniobra queda por debajo del límite configurado.

### Resultado

**NO COMPRAR** o **COMPRAR CONDICIONADO**, según la severidad configurada.

### Prioridad

1 — CRÍTICA

### Bloqueo

Configurable.

---

## FIN-003 — Riesgo financiero elevado

### Condición

La operación reduce significativamente el margen de seguridad financiera de la empresa.

### Resultado

**COMPRAR CONDICIONADO** o **NO COMPRAR**

### Prioridad

1 — CRÍTICA

### Posibles condiciones

- mejorar plazo de pago;
- reducir cantidad;
- reducir precio;
- conseguir financiación;
- mejorar cobros;
- adoptar otra medida financiera previamente definida.

---

# 6. REGLAS DE MARGEN

## MAR-001 — Margen inferior al mínimo

### Condición

El margen previsto después de la compra es inferior al margen mínimo configurado.

### Resultado

**NO COMPRAR**

o

**NEGOCIAR**

cuando exista posibilidad razonable de modificar las condiciones.

### Prioridad

2 — MUY ALTA

---

## MAR-002 — Margen dentro de tolerancia

### Condición

El margen se encuentra ligeramente por debajo del objetivo, pero dentro de la tolerancia configurada.

### Resultado

**NEGOCIAR** o **COMPRAR CONDICIONADO**

### Prioridad

2 — MUY ALTA

---

## MAR-003 — Margen objetivo alcanzado

### Condición

El margen cumple o supera el objetivo.

### Resultado

No genera una decisión por sí mismo.

### Función

Actúa como condición favorable.

---

# 7. REGLAS DE PRECIO

## PRE-001 — Precio superior a compra comparable reciente

### Condición

El precio propuesto supera el precio de una operación comparable reciente en el porcentaje configurado.

Ejemplo:

Precio anterior:

17,20 €

Precio propuesto:

18,50 €

Diferencia:

+7,56 %

### Resultado

**NEGOCIAR**

### Prioridad

3 — ALTA

---

## PRE-002 — Precio superior al límite crítico

### Condición

El precio supera el umbral crítico configurado.

### Resultado

**NEGOCIAR** o **NO COMPRAR**

### Prioridad

2 — MUY ALTA

### Observación

La decisión definitiva dependerá de:

- margen;
- proveedores alternativos;
- stock;
- demanda;
- condiciones de pago;
- situación financiera.

---

## PRE-003 — Precio inferior o igual al objetivo

### Condición

El precio propuesto es igual o inferior al precio máximo recomendado.

### Resultado

No genera bloqueo.

Puede contribuir favorablemente a la decisión.

---

# 8. REGLAS DE ANTIGÜEDAD DEL HISTÓRICO

## HIS-001 — Referencia demasiado antigua

### Condición

La compra utilizada como referencia supera la antigüedad máxima configurada.

### Resultado

No utilizar automáticamente como referencia principal.

### Acción

Buscar referencias más recientes.

---

## HIS-002 — Histórico insuficiente

### Condición

No existe el número mínimo de operaciones comparables establecido.

### Resultado

**INFORMACIÓN INSUFICIENTE**

o análisis con advertencia.

### Prioridad

5 — INFORMATIVA

---

# 9. REGLAS DE COMPARABILIDAD

## HIS-003 — Operación no comparable

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

---

# 10. REGLAS DE STOCK

## STK-001 — Riesgo de rotura de stock

### Condición

La proyección indica que el stock puede agotarse antes de que llegue una nueva compra.

### Resultado

**COMPRAR** o **COMPRAR CONDICIONADO**

### Prioridad

3 — ALTA

### Observación

La compra puede estar justificada aunque el precio sea ligeramente superior, siempre que no se incumplan reglas financieras o de margen críticas.

---

## STK-002 — Compra innecesaria por stock suficiente

### Condición

La cobertura prevista supera ampliamente el nivel configurado y no existen necesidades justificadas.

### Resultado

**NO COMPRAR**

o

**NEGOCIAR CANTIDAD**

### Prioridad

2 — MUY ALTA

---

## STK-003 — Exceso de stock

### Condición

El stock después de la compra supera el nivel máximo configurado.

### Resultado

**NEGOCIAR**

o

**NO COMPRAR**

### Prioridad

2 — MUY ALTA

---

# 11. EXCEPCIÓN DE STOCK POR PEDIDO CONFIRMADO

## STK-004

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

### Prioridad

2 — MUY ALTA

### Tipo

EXCEPCIÓN

---

# 12. REGLAS DE ROTACIÓN

## ROT-001 — Producto de baja rotación

### Condición

La rotación se encuentra por debajo del umbral establecido.

### Resultado

**NEGOCIAR CANTIDAD**

o

**NO COMPRAR**

### Prioridad

3 — ALTA

---

## ROT-002 — Producto sin rotación

### Condición

No existen ventas durante el periodo configurado.

### Resultado

**NO COMPRAR**

salvo excepción.

### Excepciones posibles

- pedido confirmado;
- campaña prevista;
- operación estratégica;
- decisión empresarial explícita.

---

# 13. REGLAS DE PLAZO DE ENTREGA

## ENT-001 — Entrega posterior al riesgo de rotura

### Condición

La fecha prevista de entrega es posterior a la fecha estimada de agotamiento del stock.

### Resultado

**NEGOCIAR**

### Prioridad

3 — ALTA

### Posibles recomendaciones

- solicitar entrega anticipada;
- dividir entrega;
- reducir plazo;
- buscar proveedor alternativo.

---

# 14. REGLAS DE PAGO

## PAG-001 — Plazo de pago inferior al objetivo

### Condición

El proveedor ofrece un plazo inferior al establecido como objetivo.

### Resultado

**NEGOCIAR**

### Prioridad

3 — ALTA

---

## PAG-002 — Plazo de pago insuficiente ante riesgo financiero

### Condición

La operación puede ser viable únicamente si se amplía el plazo de pago.

### Resultado

**COMPRAR CONDICIONADO**

### Condición de compra

La operación únicamente será recomendable si se consigue el plazo de pago mínimo establecido.

---

# 15. REGLAS DE PROVEEDORES

## PROV-001 — Existencia de proveedor alternativo

### Condición

Existe uno o más proveedores alternativos con condiciones potencialmente mejores.

### Resultado

**NEGOCIAR**

### Prioridad

4 — MEDIA

---

## PROV-002 — Proveedor actual con condiciones claramente desfavorables

### Condición

Existe una alternativa comparable que mejora significativamente:

- precio;
- plazo;
- condiciones;
- fiabilidad;
- disponibilidad.

### Resultado

**NEGOCIAR**

o

**EVALUAR PROVEEDOR ALTERNATIVO**

---

# 16. DESCUENTOS Y RAPPELS

## COM-001 — Descuento disponible

### Condición

Existe posibilidad de obtener un descuento.

### Resultado

Incluir en la negociación.

### No debe

Modificar automáticamente la recomendación si no se conoce su aplicación real.

---

## COM-002 — Rappel disponible

### Condición

La operación puede mejorar el coste efectivo mediante rappel.

### Resultado

Calcular, cuando sea posible, el coste efectivo.

### Prioridad

4 — MEDIA

---

# 17. REGLAS DE CALIDAD DE DATOS

## DAT-001 — Datos actualizados

### Condición

Los datos se encuentran dentro del periodo máximo permitido.

### Resultado

Continuar análisis normalmente.

---

## DAT-002 — Datos antiguos

### Condición

La fecha de actualización supera el periodo establecido.

### Resultado

Mostrar advertencia.

### Resultado de decisión

Puede continuar si la política lo permite.

---

## DAT-003 — Datos insuficientes

### Condición

No existe información suficiente para realizar una evaluación fiable.

### Resultado

**INFORMACIÓN INSUFICIENTE**

### Prioridad

1 — CRÍTICA respecto a la fiabilidad.

### Principio

EIOS no debe inventar una recomendación cuando los datos no permiten sostenerla.

---

# 18. REGLA DE CONFLICTO FINANCIERO

## CON-001

### Situación

La compra:

- tiene buen precio;
- tiene buen margen;
- evita una posible rotura de stock;

pero compromete la capacidad financiera de la empresa.

### Resultado

**NO COMPRAR**

### Prioridad

1 — CRÍTICA

### Principio

La solvencia y capacidad de pago prevalecen sobre ventajas operativas o comerciales de menor prioridad.

---

# 19. REGLA DE CONFLICTO STOCK / PRECIO

## CON-002

### Situación

Existe riesgo de rotura, pero el precio es superior al objetivo.

### Resultado

**NEGOCIAR**

### Posibles recomendaciones

- mantener precio si se adelanta entrega;
- negociar precio;
- reducir cantidad;
- buscar proveedor alternativo.

---

# 20. REGLA DE CONFLICTO STOCK / FINANZAS

## CON-003

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

---

# 21. REGLA DE CONFLICTO STOCK / PEDIDO CONFIRMADO

## CON-004

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

---

# 22. REGLA DE CONFLICTO PRECIO / MARGEN

## CON-005

### Situación

El precio de compra es elevado respecto al histórico, pero el precio de venta permite mantener el margen mínimo.

### Resultado

**NEGOCIAR**

No necesariamente:

**NO COMPRAR**

### Motivo

Un precio superior al histórico no implica automáticamente que la operación sea inviable.

---

# 23. REGLA DE CONFLICTO PRECIO / PROVEEDOR ALTERNATIVO

## CON-006

### Situación

El proveedor actual presenta un precio superior y existe alternativa comparable.

### Resultado

**NEGOCIAR**

### Información mostrada

- precio actual;
- precio alternativo;
- diferencia;
- condiciones;
- plazo;
- posibles ventajas e inconvenientes.

---

# 24. REGLA DE CONFLICTO PRECIO / PLAZO DE PAGO

## CON-007

### Situación

El precio es superior al objetivo, pero el proveedor ofrece mejores condiciones de pago.

### Resultado

Calcular impacto económico-financiero antes de decidir.

### Posible resultado

**COMPRAR CONDICIONADO**

si las mejores condiciones de pago compensan suficientemente la diferencia de precio según los criterios configurados.

---

# 25. REGLA DE COMPRA CONDICIONADA

## CON-008

Una compra podrá clasificarse como:

**COMPRAR CONDICIONADO**

cuando la operación sea potencialmente viable pero dependa de una condición concreta.

Ejemplos:

- precio máximo;
- plazo mínimo;
- cantidad máxima;
- descuento;
- rappel;
- entrega anticipada;
- confirmación de pedido;
- solución financiera.

La condición deberá mostrarse explícitamente.

---

# 26. REGLA DE NO COMPRA

## CON-009

Una operación deberá clasificarse como:

**NO COMPRAR**

cuando:

- existe riesgo financiero crítico;
- el margen es inaceptable;
- existe exceso de stock injustificado;
- la operación es claramente inviable;
- o se incumple una regla crítica de bloqueo.

La explicación deberá indicar el motivo principal.

---

# 27. REGLA DE COMPRA

## CON-010

Una operación podrá clasificarse como:

**COMPRAR**

cuando:

- no existen bloqueos críticos;
- el margen cumple;
- la situación financiera es viable;
- el stock está justificado;
- el precio se encuentra dentro de los límites;
- las condiciones son aceptables;
- la calidad de datos es suficiente.

---

# 28. REGLA DE INFORMACIÓN INSUFICIENTE

## CON-011

Cuando la información disponible no permita realizar una evaluación fiable:

### Resultado

**INFORMACIÓN INSUFICIENTE**

### EIOS deberá indicar:

- qué dato falta;
- por qué es importante;
- qué decisión queda afectada;
- qué información debería obtenerse.

Ejemplo:

> No existe histórico suficiente del artículo para evaluar el precio propuesto.

---

# 29. ORDEN DE EVALUACIÓN

El flujo inicial será:

1. Validación de datos.
2. Calidad y antigüedad.
3. Situación financiera.
4. Margen.
5. Stock y demanda.
6. Plazo de entrega.
7. Precio.
8. Condiciones de pago.
9. Proveedores alternativos.
10. Descuentos y rappels.
11. Excepciones.
12. Resolución de conflictos.
13. Decisión final.

Este orden podrá evolucionar durante las pruebas.

---

# 30. REGLA DE BLOQUEO

Una regla crítica de bloqueo no podrá ser anulada por una regla favorable de menor prioridad.

Ejemplo:

### Precio excelente

🟢

### Margen excelente

🟢

### Stock necesario

🟢

### Tesorería insuficiente

🔴 CRÍTICO

### Resultado

**NO COMPRAR**

---

# 31. REGLA DE COMPENSACIÓN

Las condiciones favorables no deberán compensar automáticamente una condición crítica.

Sin embargo, una condición problemática podrá solucionarse mediante una condición negociada.

Ejemplo:

Precio:

🔴 superior al objetivo

Plazo de pago:

🟢 90 días

Tesorería:

🟢 suficiente

Resultado posible:

**COMPRAR CONDICIONADO**

---

# 32. REGLA DE EXCEPCIÓN

Toda excepción deberá cumplir:

1. estar previamente definida;
2. tener una condición concreta;
3. estar autorizada;
4. quedar registrada;
5. poder explicarse posteriormente.

No deberán existir excepciones "ocultas".

---

# 33. EXPLICACIÓN DE LA DECISIÓN

EIOS deberá poder generar una explicación breve.

Ejemplo:

## 🟡 NEGOCIAR

**Motivo principal:**

El precio ofertado es un 7,6 % superior a la última compra comparable realizada hace 25 días.

**Situación:**

- Stock: 420 uds.
- Cobertura: 23 días.
- Entrega prevista: 15 días.
- Margen previsto: 27 %.
- Tesorería: suficiente.

**Recomendación:**

Intentar reducir el precio hasta 17,80 €.

---

# 34. RESUMEN EJECUTIVO PARA EL CEO

La pantalla principal no deberá mostrar todas las reglas activadas.

Deberá mostrar:

### DECISIÓN

COMPRAR / NEGOCIAR / COMPRAR CONDICIONADO / NO COMPRAR

### MOTIVO PRINCIPAL

Una explicación breve.

### RIESGOS

Los principales riesgos detectados.

### NEGOCIACIÓN

Qué debería intentarse conseguir.

### FIABILIDAD

Nivel de fiabilidad del análisis.

La información secundaria estará disponible bajo demanda.

---

# 35. TRAZABILIDAD

Cada decisión deberá conservar:

- reglas evaluadas;
- reglas activadas;
- parámetros utilizados;
- excepciones;
- datos de origen;
- fecha de actualización;
- configuración vigente;
- decisión final.

Esto permitirá reconstruir posteriormente por qué EIOS recomendó una determinada acción.

---

# 36. MATRIZ INICIAL DE DECISIÓN

| Situación principal | Resultado inicial |
|---|---|
| Riesgo financiero crítico | NO COMPRAR |
| Margen por debajo del mínimo | NO COMPRAR |
| Precio elevado pero negociable | NEGOCIAR |
| Stock excesivo | NEGOCIAR / NO COMPRAR |
| Riesgo de rotura | COMPRAR / CONDICIONADO |
| Producto sin rotación | NO COMPRAR |
| Plazo insuficiente | NEGOCIAR |
| Buen precio y condiciones | COMPRAR |
| Datos insuficientes | INFORMACIÓN INSUFICIENTE |
| Exceso de stock + pedido confirmado | Evaluar excepción |
| Precio alto + buen plazo de pago | Evaluar compensación |
| Precio alto + proveedor alternativo | NEGOCIAR |
| Riesgo financiero + cualquier ventaja comercial | NO COMPRAR |

---

# 37. PRINCIPIO DE NO AUTOMATIZACIÓN ABSOLUTA

Las reglas no deben convertir EIOS en un sistema que tome decisiones empresariales irreversibles sin intervención humana.

EIOS proporciona:

- análisis;
- recomendación;
- explicación;
- alternativas;
- riesgos.

La decisión final corresponde al usuario autorizado.

---

# 38. ESTADO DEL DOCUMENTO

Este documento constituye una primera versión de la Matriz de Reglas MVP.

No debe considerarse definitivo.

Las reglas deberán validarse mediante casos reales y pruebas antes de convertirse en lógica de producción.

---

# 39. PRÓXIMO TRABAJO

Los siguientes trabajos previstos son:

1. Validar cada regla.
2. Definir valores concretos.
3. Definir prioridad.
4. Definir bloqueos.
5. Definir excepciones.
6. Definir conflictos.
7. Crear casos de prueba.
8. Convertir las reglas validadas en lógica técnica.
