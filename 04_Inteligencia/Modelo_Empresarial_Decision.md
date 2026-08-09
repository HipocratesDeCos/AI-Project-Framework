# MODELO EMPRESARIAL DE DECISIÓN

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.2  
**Estado:** En desarrollo  
**Última actualización:** 09/08/2026

---

# 1. PROPÓSITO

El Modelo Empresarial de Decisión (MED) define cómo EIOS analiza una propuesta de compra, combina información histórica, operativa y financiera, aplica los criterios y reglas establecidos por la empresa y genera una recomendación comprensible para el usuario.

El MED constituye el núcleo lógico de decisión de EIOS.

No ejecuta automáticamente la compra.

Su función es proporcionar información, análisis, riesgos, alternativas y una recomendación que facilite la decisión humana.

---

# 2. OBJETIVO

Determinar si una compra propuesta:

- debe realizarse;
- debe negociarse;
- puede realizarse condicionadamente;
- o no debe realizarse.

La decisión debe considerar tanto la operación concreta como su impacto sobre la situación económica, financiera y operativa de la empresa.

---

# 3. PRINCIPIO FUNDAMENTAL

EIOS no debe limitarse a responder:

> ¿Podemos comprar?

Debe intentar responder:

> ¿Tiene sentido realizar esta compra en estas condiciones y qué deberíamos negociar para mejorarla o hacerla viable?

---

# 4. ENTRADA DEL MODELO

La entrada principal es una:

## PROPUESTA DE COMPRA

Cuando estén disponibles, deberá incorporar:

- artículo;
- proveedor;
- cantidad;
- precio unitario;
- importe total;
- fecha de propuesta;
- fecha prevista de entrega;
- plazo de entrega;
- plazo de pago;
- condiciones de pago;
- descuentos;
- rappels;
- incidencias;
- otras condiciones relevantes.

La **fecha de propuesta de compra** es especialmente importante porque permite realizar análisis temporales y proyectar el impacto de la operación.

---

# 5. INFORMACIÓN UTILIZADA

El modelo puede utilizar información procedente de diferentes áreas.

## 5.1 Compras

- últimas compras;
- fechas;
- precios;
- cantidades;
- proveedores;
- condiciones;
- descuentos;
- rappels;
- incidencias.

## 5.2 Proveedores

- proveedor actual;
- proveedores alternativos;
- histórico;
- precios;
- condiciones;
- incidencias.

## 5.3 Stock

- stock actual;
- stock comprometido;
- pedidos pendientes;
- compras en tránsito;
- rotación;
- cobertura;
- demanda histórica;
- demanda prevista.

## 5.4 Rentabilidad

- precio de venta;
- margen en euros;
- margen porcentual;
- margen mínimo establecido;
- impacto de descuentos;
- impacto de rappels.

## 5.5 Situación financiera

- tesorería;
- pagos previstos;
- liquidez;
- fondo de maniobra;
- necesidades financieras;
- impacto de la compra sobre la capacidad de pago.

---

# 6. ANÁLISIS TEMPORAL

El MED debe analizar la compra teniendo en cuenta el tiempo.

No debe limitarse al estado actual de la empresa.

Cuando existan datos suficientes podrá considerar:

- stock actual;
- ventas históricas;
- demanda;
- pedidos pendientes;
- compras en tránsito;
- fecha prevista de recepción;
- plazo de entrega;
- cantidad propuesta.

El análisis temporal permitirá estudiar la evolución prevista de la situación después de realizar la compra.

---

# 7. PROYECCIÓN DE STOCK

EIOS debe poder estimar la evolución futura del stock.

Conceptualmente:

Stock proyectado =
Stock actual
+ entradas previstas
- salidas previstas

La proyección podrá utilizar:

- ventas históricas;
- demanda prevista;
- pedidos pendientes;
- compras en tránsito;
- fecha de recepción;
- plazo de entrega.

Una de sus aplicaciones principales será anticipar:

- posibles roturas de stock;
- exceso de stock;
- compras innecesarias;
- compras de productos de baja rotación.

---

# 8. ROTURA DE STOCK

El MED debe poder evaluar si una compra puede:

- evitar una futura rotura de stock;
- llegar demasiado tarde para evitarla;
- generar exceso de stock;
- ser innecesaria.

La evaluación deberá tener en cuenta especialmente:

- stock actual;
- consumo histórico;
- demanda;
- pedidos pendientes;
- plazo de entrega;
- fecha prevista de recepción;
- cantidad propuesta.

No debe limitarse a mostrar el stock actual.

---

# 9. REFERENCIAS TEMPORALES DEL PRECIO

El precio de compra propuesto no debe compararse automáticamente con un único valor histórico.

El modelo deberá poder trabajar con diferentes ventanas temporales, configurables por la empresa.

Ejemplos:

- últimos 3 meses;
- últimos 6 meses;
- últimos 12 meses;
- últimos 24 meses.

La elección del periodo deberá responder a criterios empresariales y podrá variar según artículo, sector o política de la empresa.

---

# 10. ANTIGÜEDAD DE LAS REFERENCIAS

La antigüedad de un dato debe formar parte de la evaluación.

Ejemplo:

Última compra:

17,20 €

Fecha:

14/07/2026

Antigüedad:

25 días.

Esta referencia puede ser relevante.

En cambio, una compra realizada hace cuatro años puede no representar adecuadamente el precio actual.

Por tanto, el modelo deberá considerar:

- fecha;
- antigüedad;
- número de operaciones;
- comparabilidad;
- condiciones de compra.

---

# 11. COMPARABILIDAD DE LAS COMPRAS

No todos los precios históricos deben considerarse automáticamente comparables.

Cuando los datos estén disponibles, deberán considerarse:

- artículo;
- proveedor;
- cantidad;
- fecha;
- descuentos;
- rappels;
- condiciones de pago;
- otras condiciones comerciales.

Una compra de 10 unidades no necesariamente constituye una referencia adecuada para una compra de 1.000 unidades.

---

# 12. PRECIO MEDIO HISTÓRICO

El precio medio histórico no deberá considerarse automáticamente una referencia válida.

Cuando el histórico abarque muchos años pueden existir factores que reduzcan su utilidad:

- inflación;
- evolución del mercado;
- cambios de proveedor;
- cambios en las cantidades;
- descuentos;
- rappels;
- cambios de condiciones;
- cambios en la política de compras.

Por ello, el MED deberá priorizar referencias que sean suficientemente recientes y comparables.

---

# 13. PRECIO MÁXIMO RECOMENDADO

El MED podrá generar un:

## PRECIO MÁXIMO RECOMENDADO

Este valor no debe ser arbitrario.

Su metodología deberá definirse mediante criterios configurables.

Podrá considerar:

- compras recientes;
- histórico de compras;
- precio ponderado;
- operaciones comparables;
- proveedor;
- proveedores alternativos;
- margen mínimo;
- precio de venta;
- condiciones de pago;
- descuentos;
- rappels;
- estrategia empresarial.

La metodología definitiva queda pendiente de definición.

---

# 14. EXPLICACIÓN DEL PRECIO

EIOS deberá evitar mensajes genéricos.

### No deseable:

> Precio superior al histórico reciente.

### Preferible:

> Precio ofertado: 18,50 €

> +7,6 % respecto a la última compra de 17,20 €, realizada hace 25 días.

> +3,4 % respecto al precio medio ponderado de los últimos 3 meses.

> +6,6 % respecto al precio medio ponderado de los últimos 12 meses.

La información detallada deberá estar disponible sin saturar la pantalla principal.

---

# 15. FIABILIDAD DE LAS REFERENCIAS

Cuando sea posible, EIOS deberá valorar la calidad de la referencia.

### Alta

Datos recientes, suficientes y comparables.

### Media

Datos limitados o con diferencias relevantes.

### Baja

Datos antiguos, escasos o poco comparables.

EIOS no debe transmitir una falsa sensación de precisión cuando los datos disponibles sean insuficientes.

---

# 16. MOTOR DE REGLAS

El MED utilizará un motor de reglas configurable.

Las reglas podrán adaptarse a:

- empresa;
- sector;
- política empresarial;
- situación económica;
- estrategia de compras;
- estrategia financiera;
- nivel de riesgo aceptado.

Las reglas no deben quedar rígidamente codificadas.

---

# 17. TIPOS DE REGLAS

## 17.1 Reglas de bloqueo

Pueden impedir que una operación sea recomendada como compra directa.

Ejemplo:

> La operación compromete la capacidad de atender pagos.

Resultado:

**NO COMPRAR**

o, cuando exista una solución viable:

**COMPRAR CONDICIONADO**

---

## 17.2 Reglas de recomendación

Modifican la recomendación.

Ejemplo:

> Precio superior al objetivo.

Resultado:

**NEGOCIAR**

---

## 17.3 Reglas de excepción

Pueden modificar el efecto de otra regla cuando se cumplen determinadas condiciones.

Ejemplo:

> Stock elevado + pedido confirmado de cliente.

La existencia del pedido puede reducir el riesgo asociado al exceso de stock.

---

# 18. PRIORIDAD DE LAS REGLAS

No se utilizará una simple suma de reglas favorables y desfavorables.

Una regla financiera crítica no debe quedar anulada porque existan varias condiciones favorables de menor importancia.

Las reglas deberán disponer, como mínimo conceptualmente, de:

- prioridad;
- severidad;
- tipo;
- capacidad de bloqueo;
- posibilidad de excepción.

La jerarquía definitiva queda pendiente de definición.

---

# 19. CONFLICTO ENTRE REGLAS

El MED deberá gestionar situaciones en las que diferentes reglas produzcan resultados distintos.

Ejemplo:

Precio:

🟢 favorable

Margen:

🟢 favorable

Stock:

🔴 elevado

Pedido confirmado:

🟢 existente

Tesorería:

🟢 suficiente

El sistema deberá determinar cómo interactúan estas condiciones antes de producir una recomendación.

---

# 20. EXCEPCIONES

Las excepciones deberán estar expresamente definidas y no producirse de forma arbitraria.

Ejemplo:

Regla:

> No comprar si existe exceso de stock.

Excepción:

> Existe un pedido confirmado que absorberá el stock.

Resultado:

> La regla de exceso de stock queda mitigada.

Las excepciones deberán quedar registradas y ser trazables.

---

# 21. RESULTADOS DE LA DECISIÓN

El MED tendrá inicialmente cuatro resultados principales.

## 🟢 COMPRAR

La operación cumple los criterios establecidos y no presenta riesgos relevantes.

## 🟡 NEGOCIAR

La operación puede ser viable, pero existen condiciones que deberían mejorarse.

## 🔵 COMPRAR CONDICIONADO

La operación puede ser viable si se cumplen determinadas condiciones.

## 🔴 NO COMPRAR

La operación presenta un riesgo o incumplimiento que desaconseja realizarla.

---

# 22. NEGOCIACIÓN

Cuando una operación pueda mejorar mediante negociación, EIOS deberá identificar, cuando sea posible:

- precio objetivo;
- precio máximo recomendado;
- plazo de pago objetivo;
- cantidad recomendada;
- descuento necesario;
- rappel necesario;
- condiciones necesarias.

Ejemplo:

> NEGOCIAR

> Precio ofertado: 18,50 €

> Precio máximo recomendado: 17,80 €

> Alternativa:

> Mantener 18,50 € si el plazo de pago aumenta de 30 a 90 días.

---

# 23. COMPRA CONDICIONADA

Esta categoría permite transformar determinadas situaciones problemáticas en condiciones concretas.

Ejemplos:

- comprar si se obtiene un plazo de pago determinado;
- comprar si se reduce el precio;
- comprar si se reduce la cantidad;
- comprar si existe un pedido confirmado;
- comprar si se mantiene un margen mínimo.

---

# 24. SITUACIÓN FINANCIERA

La compra no debe evaluarse únicamente desde la perspectiva de compras.

Debe analizarse su impacto sobre:

- tesorería;
- pagos próximos;
- liquidez;
- fondo de maniobra;
- capacidad de atender obligaciones;
- rentabilidad.

Una compra que comprometa la capacidad de hacer frente a los pagos puede ser desaconsejada aunque el precio de compra sea excelente.

---

# 25. ALTERNATIVAS ANTE RIESGO FINANCIERO

Cuando una compra comprometa la situación financiera, EIOS podrá mostrar alternativas para valoración humana.

Ejemplos:

- solicitar ampliación de capital;
- vender inmovilizado no utilizado;
- promocionar productos de baja rotación;
- acelerar cobros de clientes;
- negociar condiciones de pago;
- reducir la cantidad comprada.

EIOS no ejecutará estas acciones automáticamente.

---

# 26. EXCESO DE STOCK

No se recomendará automáticamente una compra cuando exista un nivel elevado de stock.

Sin embargo, deberán contemplarse excepciones.

Ejemplo:

Stock elevado:

🔴 Riesgo

Pedido confirmado:

🟢 Excepción

El MED deberá analizar conjuntamente ambas circunstancias.

---

# 27. PARAMETRIZACIÓN

Los criterios utilizados por el MED deberán poder configurarse mediante un Centro de Parametrización de EIOS.

Entre otros, podrán configurarse:

- periodos de referencia;
- antigüedad máxima;
- límites;
- tolerancias;
- niveles de stock;
- márgenes;
- prioridades;
- reglas;
- excepciones;
- criterios financieros.

La configuración será adaptable a diferentes empresas y a cambios en la política empresarial.

---

# 28. VALORES ESTÁNDAR

EIOS deberá partir de valores estándar editables.

Estos valores servirán como configuración inicial.

La empresa podrá modificarlos según:

- actividad;
- tamaño;
- política;
- situación financiera;
- estrategia;
- nivel de riesgo aceptado.

---

# 29. EXPLICACIÓN DE LOS PARÁMETROS

Cada parámetro configurable deberá incluir una explicación breve y comprensible sobre su función y sobre el efecto que produce modificarlo.

Ejemplo:

### Antigüedad máxima de referencia: 12 meses

> Determina hasta qué antigüedad EIOS considera válida una compra histórica para comparar el precio actual.

La explicación deberá estar orientada a usuarios empresariales y no técnicos.

---

# 30. VIGENCIA DE LOS PARÁMETROS

Las modificaciones importantes deberán conservar:

- valor;
- fecha de inicio;
- fecha de finalización, cuando corresponda;
- usuario que realizó el cambio;
- motivo del cambio.

EIOS debe poder determinar qué configuración estaba vigente cuando se tomó una decisión.

---

# 31. HISTORIAL DE CONFIGURACIÓN

Ejemplo:

Margen mínimo:

01/01/2026 → 20 %

01/07/2026 → 22 %

01/01/2027 → 25 %

No se deberá sobrescribir una configuración anterior sin conservar su historial.

---

# 32. SIMULACIÓN DE CAMBIOS

Como evolución del sistema, el Centro de Parametrización podrá permitir simular el efecto de modificar un parámetro antes de aplicarlo.

Ejemplo:

Margen mínimo actual:

20 %

Nuevo valor:

25 %

EIOS podría mostrar:

> 14 operaciones históricas que anteriormente eran aceptables pasarían a clasificarse como "NEGOCIAR".

Esta funcionalidad queda pendiente de validación y diseño.

---

# 33. TRAZABILIDAD

Cada decisión importante deberá poder reconstruirse.

EIOS deberá poder identificar:

- datos utilizados;
- fecha de los datos;
- referencias utilizadas;
- parámetros vigentes;
- reglas activadas;
- excepciones aplicadas;
- resultado final.

El sistema debe poder explicar:

> POR QUÉ HA LLEGADO A ESTA RECOMENDACIÓN.

---

# 34. FLUJO GENERAL

PROPUESTA DE COMPRA
↓
VALIDACIÓN DE DATOS
↓
ANÁLISIS HISTÓRICO
↓
ANÁLISIS DE STOCK
↓
PROYECCIÓN TEMPORAL
↓
ANÁLISIS DE RENTABILIDAD
↓
ANÁLISIS FINANCIERO
↓
COMPARACIÓN CON REFERENCIAS
↓
APLICACIÓN DE REGLAS
↓
RESOLUCIÓN DE CONFLICTOS
↓
APLICACIÓN DE EXCEPCIONES
↓
DECISIÓN
↓
CONDICIONES DE NEGOCIACIÓN
↓
EXPLICACIÓN DE LA DECISIÓN

---

# 35. PRINCIPIO DE SIMPLICIDAD

La complejidad debe permanecer principalmente en el motor interno.

La interfaz destinada al CEO deberá mostrar inicialmente:

1. decisión;
2. principales motivos;
3. riesgos;
4. condiciones de negociación;
5. fiabilidad de los datos cuando sea relevante.

La información detallada deberá estar disponible bajo demanda.

El sistema debe evitar la saturación de información.

---

# 36. ÁREAS PENDIENTES DE DEFINICIÓN

Queda pendiente definir:

- jerarquía definitiva de reglas;
- prioridad entre reglas;
- sistema de excepciones;
- metodología exacta para calcular el precio máximo recomendado;
- ponderación temporal;
- definición de operaciones comparables;
- cálculo de rotación;
- cálculo de cobertura;
- proyección de stock;
- impacto financiero proyectado;
- niveles de fiabilidad;
- parámetros iniciales;
- diseño definitivo del Centro de Parametrización.

---

# 37. PRINCIPIO DE EVOLUCIÓN

El Modelo Empresarial de Decisión no se considera cerrado.

Debe evolucionar a medida que se validen:

- nuevos casos reales;
- nuevas reglas;
- nuevos datos;
- nuevas necesidades empresariales;
- nuevas pruebas del sistema.

Toda modificación estructural deberá quedar documentada.

---

# 38. ESTADO ACTUAL

**Nodo de trabajo actual:**

Prioridad y conflicto entre reglas.

**Nuevos conceptos identificados:**

- Referencias temporales.
- Antigüedad de datos.
- Comparabilidad.
- Fiabilidad de referencias.
- Precio máximo recomendado.
- Reglas de bloqueo.
- Reglas de recomendación.
- Reglas de excepción.
- Compra condicionada.
- Centro de Parametrización.
- Vigencia de parámetros.
- Historial de configuración.
- Simulación de cambios.

**Siguiente trabajo previsto:**

Definir mediante casos reales la prioridad, interacción, conflicto y excepciones entre reglas.
