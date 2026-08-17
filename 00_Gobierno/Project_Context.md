# EIOS — Project Context

> **Documento de recuperación y continuidad del proyecto**
>
> **Versión:** 0.1  
> **Estado:** ACTIVO  
> **Última actualización:** 09/08/2026  
> **Proyecto:** EIOS — Enterprise Intelligent Operations System

---

## 1. PROPÓSITO DE ESTE DOCUMENTO

Este archivo contiene el contexto esencial y estable de EIOS.

Su función principal es permitir recuperar rápidamente el contexto del proyecto si se pierde continuidad en una conversación, se inicia un nuevo chat o se incorpora una nueva IA al proyecto.

Este documento NO sustituye al resto de documentación del proyecto.

Debe utilizarse como mapa de navegación hacia los documentos específicos.

---

# 2. IDENTIDAD DEL PROYECTO

EIOS es un sistema de apoyo a la decisión empresarial basado en datos.

Su objetivo inicial es ayudar al CEO y al responsable de compras a tomar mejores decisiones de adquisición mediante el análisis conjunto de:

- histórico de compras;
- proveedores;
- precios;
- condiciones de compra;
- stock;
- rotación;
- pedidos pendientes;
- márgenes;
- tesorería;
- fondo de maniobra;
- situación financiera;
- y otros factores relevantes.

EIOS no pretende sustituir al ERP ni los procesos contables.

---

# 3. OBJETIVO PRINCIPAL

EIOS debe ayudar a determinar si una compra propuesta:

- debe realizarse;
- debe negociarse;
- puede realizarse condicionadamente;
- o no debe realizarse.

La decisión debe considerar tanto la operación individual como su impacto sobre la situación económica, financiera y operativa de la empresa.

---

# 4. ALCANCE ACTUAL

## Prioridad actual

### DECISIÓN DE COMPRAS

Es el núcleo inicial del proyecto.

La funcionalidad relacionada con ventas para comerciales queda actualmente:

**EN STANDBY**

Podrá incorporarse posteriormente.

---

# 5. PRINCIPIOS FUNDAMENTALES

EIOS debe ser:

- intuitivo;
- rápido;
- fiable;
- escalable;
- visualmente atractivo;
- comprensible para usuarios no financieros;
- configurable;
- adaptable a diferentes empresas;
- parametrizable sin necesidad de modificar el código;
- orientado a la toma de decisiones.

### Principio de simplicidad

EIOS no debe saturar al CEO con información.

Debe mostrar primero la información necesaria para tomar una decisión y permitir profundizar cuando sea necesario.

---

# 6. LÍMITES DEL SISTEMA

EIOS:

- NO sustituye al ERP.
- NO genera facturas.
- NO sustituye la contabilidad.
- NO debe presentar información como actual si los datos tienen una antigüedad superior al límite establecido por la configuración.
- NO debe ocultar incertidumbres o referencias de baja calidad.
- NO debe convertir automáticamente una hipótesis debatida en una regla definitiva.

---

# 7. ORIGEN Y RUTA DE LOS DATOS

La ruta inicialmente considerada es:

ERP → Excel → Power BI → SQL Server

Actualmente se trabaja habitualmente con SAGE, pero la arquitectura NO debe quedar limitada exclusivamente a SAGE.

La conexión automática con ERP queda contemplada como evolución futura.

---

# 8. MODELO GENERAL DE DECISIÓN

La lógica conceptual actual es:

COMPRA PROPUESTA  
↓  
SIMULACIÓN  
↓  
MOTOR DE REGLAS  
↓  
EVALUACIÓN DE CONFLICTOS  
↓  
DECISIÓN  
↓  
PLAN DE ACCIÓN

Las posibles respuestas principales son:

- 🟢 COMPRAR
- 🟡 NEGOCIAR
- 🔵 COMPRAR CONDICIONADO
- 🔴 NO COMPRAR

---

# 9. VARIABLES PRINCIPALES DE LA DECISIÓN DE COMPRA

Entre las variables inicialmente consideradas están:

## Compra

- artículo;
- proveedor;
- cantidad;
- precio;
- importe;
- fecha de propuesta;
- fecha prevista de entrega;
- plazo de pago;
- condiciones de pago;
- descuentos;
- rappels;
- incidencias.

## Histórico

- últimas compras;
- fechas de compra;
- precios;
- cantidades;
- proveedor;
- condiciones;
- operaciones comparables.

## Stock

- stock actual;
- stock comprometido;
- stock en tránsito;
- pedidos pendientes;
- rotación;
- demanda;
- cobertura;
- stock proyectado.

## Rentabilidad

- precio de venta;
- margen;
- margen porcentual;
- margen mínimo objetivo.

## Finanzas

- tesorería;
- fondo de maniobra;
- liquidez;
- pagos previstos;
- impacto financiero de la compra.

## Proveedores

- proveedor actual;
- proveedores alternativos;
- histórico;
- precios;
- condiciones;
- incidencias.

---

# 10. SIMULACIÓN TEMPORAL

La fecha de propuesta de compra es un elemento fundamental.

EIOS no debe limitarse a analizar el estado actual.

Debe poder proyectar la evolución futura teniendo en cuenta, cuando existan datos suficientes:

- stock actual;
- ventas históricas;
- demanda prevista;
- pedidos pendientes;
- compras en tránsito;
- fecha prevista de entrega;
- plazo de entrega;
- cantidad comprada.

Conceptualmente:

Stock proyectado =
Stock actual
+ entradas previstas
- salidas previstas

Una aplicación importante es detectar posibles roturas de stock antes de que ocurran.

---

# 11. CRITERIOS DE REFERENCIA Y CÁLCULO

Se ha identificado como área pendiente de diseño el:

**Reference & Calculation Framework (RCF)**

Su función será definir cómo EIOS transforma datos en información válida para la decisión.

Para cada cálculo deberá poder determinarse, cuando corresponda:

- periodo de referencia;
- fecha;
- antigüedad;
- operaciones comparables;
- método de cálculo;
- ponderación;
- límites;
- excepciones;
- calidad o fiabilidad de la referencia.

No debe utilizarse automáticamente un precio medio histórico de muchos años si puede resultar poco representativo por inflación, evolución del mercado u otros factores.

---

# 12. REFERENCIAS TEMPORALES

Los criterios deberán poder utilizar ventanas temporales configurables.

Ejemplos:

- últimos 3 meses;
- últimos 6 meses;
- últimos 12 meses;
- últimos 24 meses.

La antigüedad de una referencia debe tenerse en cuenta.

Ejemplo:

Una última compra realizada hace 20 días puede ser una referencia relevante.

Una última compra realizada hace 4 años puede no serlo.

---

# 13. INFORMACIÓN EXPLICABLE

EIOS no debe mostrar únicamente:

> "Precio superior al histórico."

Debe explicar la referencia utilizada.

Ejemplo conceptual:

Precio ofertado: 18,50 €

+7,6 % respecto a la última compra:
17,20 € — realizada hace 25 días.

+3,4 % respecto al precio medio ponderado:
últimos 3 meses.

+6,6 % respecto al precio medio ponderado:
últimos 12 meses.

La información detallada debe estar disponible sin saturar la pantalla principal.

---

# 14. FIABILIDAD DE LAS REFERENCIAS

Cuando sea relevante, EIOS deberá poder valorar la calidad de la referencia.

Ejemplo:

🟢 Alta  
Existen varias operaciones recientes y comparables.

🟠 Media  
Existen pocas operaciones o presentan diferencias relevantes.

🔴 Baja  
Los datos son escasos, antiguos o poco comparables.

EIOS debe evitar transmitir una falsa sensación de precisión.

---

# 15. MOTOR DE REGLAS

El sistema debe disponer de un motor de reglas configurable.

Las reglas deben poder adaptarse a:

- empresa;
- momento;
- política empresarial;
- condiciones económicas;
- criterios de riesgo;
- estrategia de compras.

No deben quedar rígidamente codificadas.

---

# 16. TIPOS DE REGLAS

Se han identificado inicialmente tres categorías:

### Reglas de bloqueo

Pueden impedir una recomendación de compra.

Ejemplo:

Liquidez insuficiente para atender pagos.

### Reglas de recomendación

Modifican o condicionan la decisión.

Ejemplo:

Precio superior al objetivo → recomendar negociación.

### Reglas de excepción

Pueden modificar el efecto de otra regla.

Ejemplo:

Stock elevado + pedido de cliente confirmado → reducir riesgo de sobrestock.

---

# 17. PRIORIDAD Y CONFLICTO ENTRE REGLAS

Este apartado está actualmente:

**PENDIENTE DE DEFINICIÓN**

Se ha establecido como principio que no debe utilizarse una simple suma de reglas verdes y rojas.

Una regla financiera crítica, por ejemplo, no debe quedar anulada simplemente porque existan varias condiciones favorables.

Debe diseñarse una jerarquía de reglas.

También debe contemplarse la posibilidad de reglas superiores, excepciones y condiciones.

---

# 18. COMPRA CONDICIONADA

Se ha incorporado una cuarta posibilidad de decisión:

### COMPRAR CONDICIONADO

Ejemplos:

- comprar si se consigue un plazo de pago de 90 días;
- comprar si se reduce el precio;
- comprar si se reduce la cantidad;
- comprar si existe un pedido confirmado;
- comprar si se consigue determinada condición comercial.

EIOS no debe limitarse a diagnosticar un problema.

Cuando sea posible, debe ayudar a identificar condiciones que hagan viable la operación.

---

# 19. PLAN DE ACCIÓN FINANCIERO

Cuando una compra comprometa la situación financiera, EIOS debe poder mostrar alternativas que permitan estudiar la viabilidad.

Ejemplos considerados:

- ampliación de capital;
- venta de inmovilizado no utilizado;
- promoción de productos de baja rotación;
- reducción del periodo de cobro de clientes;
- negociación de plazos con proveedores;
- reducción de la cantidad comprada.

Estas alternativas no deben ejecutarse automáticamente.

EIOS debe presentarlas como posibles vías de actuación para valoración humana.

---

# 20. CONFIGURATION CENTER

Se ha identificado una nueva pieza transversal:

## EIOS Configuration Center

Será el centro de parametrización del sistema.

Debe permitir configurar, entre otros:

- valores de referencia;
- periodos;
- fechas;
- límites;
- tolerancias;
- criterios;
- reglas;
- prioridades;
- excepciones;
- políticas de empresa.

Debe partir de valores estándar editables.

---

# 21. EXPLICACIÓN DE LOS PARÁMETROS

Cada parámetro configurable debería incluir una explicación breve y comprensible.

Ejemplo:

**Antigüedad máxima de referencia: 12 meses**

ⓘ Determina hasta qué antigüedad EIOS considera válida una compra histórica para comparar el precio actual. Reducir este valor prioriza referencias más recientes, pero puede reducir el número de operaciones comparables.

El usuario debe comprender qué efecto produce modificar un parámetro.

---

# 22. CONFIGURACIÓN POR EMPRESA

La configuración debe poder adaptarse a diferentes empresas.

El motor puede ser común, mientras que cada empresa puede tener:

- diferentes límites;
- diferentes políticas;
- diferentes márgenes;
- diferentes criterios de stock;
- diferentes criterios financieros;
- diferentes prioridades;
- diferentes reglas.

---

# 23. VERSIONADO DE CONFIGURACIÓN

Los cambios importantes deben conservar historial.

Ejemplo:

Margen mínimo:

01/01/2026 → 20 %

01/07/2026 → 22 %

01/01/2027 → 25 %

EIOS debe poder conocer qué configuración estaba vigente cuando se produjo una determinada decisión.

---

# 24. SIMULACIÓN DE CAMBIOS

Se considera interesante que el Configuration Center pueda permitir:

**Simular una modificación antes de aplicarla.**

Ejemplo:

Margen mínimo actual: 20 %

Nuevo margen mínimo: 25 %

EIOS podría mostrar:

"Con este cambio, 14 operaciones históricas que anteriormente eran aceptables pasarían a clasificarse como negociar."

Esta funcionalidad queda como propuesta de evolución.

---

# 25. PRINCIPIO DE TRAZABILIDAD

Las decisiones importantes deben poder explicar:

- qué datos se utilizaron;
- qué referencias se utilizaron;
- qué parámetros estaban vigentes;
- qué reglas se activaron;
- qué excepciones se aplicaron;
- qué resultado produjo el motor.

El objetivo es que EIOS pueda explicar:

> "He llegado a esta recomendación por estas razones."

---

# 26. ESTADO ACTUAL DEL PROYECTO

## 🟢 Definido

- Objetivo general.
- Alcance inicial.
- Decisión de compras como núcleo.
- Usuarios iniciales.
- Ruta inicial de datos.
- Principios de diseño.
- Variables principales.
- Simulación temporal.
- Stock proyectado como concepto.
- Cuatro tipos de resultado.
- Necesidad de motor de reglas.
- Necesidad de parametrización.
- Configuration Center como componente transversal.

## 🟡 En desarrollo

- Reference & Calculation Framework.
- Criterios temporales.
- Métodos de comparación de precios.
- Fiabilidad de referencias.
- Motor de prioridades.
- Resolución de conflictos entre reglas.
- Sistema de excepciones.
- Parámetros iniciales.

## ⚪ Pendiente

- Arquitectura técnica definitiva.
- Modelo de datos definitivo.
- Integración automática con ERP.
- Implementación del motor de reglas.
- Interfaz del Configuration Center.
- Desarrollo del MVP.

---

# 27. REGLA DE TRABAJO DEL PROYECTO

EIOS se desarrollará mediante:

DEFINIR
↓
CUESTIONAR
↓
CONTRASTAR
↓
MEJORAR
↓
SIMPLIFICAR
↓
VALIDAR
↓
DOCUMENTAR
↓
IMPLEMENTAR

No se debe programar una pieza importante antes de haber definido suficientemente su lógica de negocio.

---

# 28. ESTADO DE LA CONVERSACIÓN ACTUAL

### Nodo principal

EOM / Enterprise Decision Model

### Subnodo

Decisión de Compra

### Punto actual

Prioridad y conflicto entre reglas.

### Nuevo componente identificado

EIOS Configuration Center.

### Nuevo framework identificado

Reference & Calculation Framework (RCF).

---

# 29. PRÓXIMO PASO

Continuar trabajando sobre:

## PRIORIDAD Y CONFLICTO ENTRE REGLAS

Definir mediante casos reales:

- qué reglas tienen prioridad;
- qué reglas pueden bloquear;
- qué reglas pueden ser anuladas;
- qué excepciones existen;
- cuándo una compra pasa a "Negociar";
- cuándo pasa a "Comprar condicionado";
- cuándo debe producirse un "No comprar".

Posteriormente formalizar estas decisiones en el motor de reglas.

---

# 30. PRINCIPIO FUNDAMENTAL

> EIOS no debe limitarse a decir qué está ocurriendo.
>
> Debe ayudar a comprender por qué ocurre, qué riesgo implica y qué alternativas existen para tomar una mejor decisión.
