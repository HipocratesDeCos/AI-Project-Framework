# EIOS — Project Context

> **Documento de recuperación y continuidad del proyecto**
>
> **Versión:** 2.1
> **Estado:** APROBADO
> **Última actualización:** 29/08/2026
> **Proyecto:** EIOS — Enterprise Intelligent Operations System

---

## 1. PROPÓSITO DE ESTE DOCUMENTO

Este archivo contiene el contexto esencial y estable de EIOS.

Su función principal es permitir recuperar rápidamente el contexto del proyecto si se pierde continuidad en una conversación, se inicia un nuevo chat o se incorpora una nueva IA al proyecto.

Este documento NO sustituye al resto de documentación del proyecto.

Debe utilizarse como mapa de navegación hacia los documentos específicos.

La autoridad sobre identidad, propósito, visión, alcance y límites corresponde al:

`00_Gobierno/Project_Charter.md`

La autoridad sobre precedencia documental corresponde a:

`00_Gobierno/Matriz_Autoridad_Documental.md`

El marco congelado del EIOS Vertical MVP está definido por:

`00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

---

# 2. IDENTIDAD DEL PROYECTO

EIOS — Enterprise Intelligent Operations System es un sistema inteligente de apoyo a la decisión empresarial basado en datos.

El proyecto se estructura mediante una arquitectura conceptual:

**CORE + VERTICAL**

El **EIOS Vertical MVP** se centra actualmente en:

**Intelligent Procurement Decision & Negotiation**

Su objetivo es ayudar al CEO y al Responsable de Compras a evaluar, simular, negociar y tomar mejores decisiones de adquisición mediante el análisis conjunto de información financiera, operativa, comercial e histórica.

EIOS no sustituye al ERP ni los procesos contables.

EIOS tampoco sustituye al decisor.

EIOS:

- analiza;
- evalúa;
- simula;
- explica;
- recomienda.

La decisión empresarial final corresponde al usuario autorizado.

---

# 3. OBJETIVO PRINCIPAL

EIOS debe ayudar a determinar si una compra propuesta:

- debe realizarse;
- debe negociarse;
- puede realizarse condicionadamente;
- o no debe realizarse.

La decisión debe considerar tanto la operación individual como su impacto sobre la situación económica, financiera y operativa de la empresa.

Cuando una operación inicialmente desfavorable pueda convertirse en viable mediante modificación de sus condiciones, negociación o aplicación de una alternativa, EIOS debe poder identificar y explicar dichas posibilidades.

---

# 4. ALCANCE ACTUAL

## Prioridad actual

### EIOS VERTICAL — DECISIÓN DE COMPRAS Y NEGOCIACIÓN

Es el núcleo actual del proyecto.

La funcionalidad relacionada con ventas para comerciales queda actualmente:

**EN STANDBY**

Podrá incorporarse posteriormente como otro Vertical o como ampliación futura.

El alcance actual comprende:

- decisión de compras;
- evaluación financiera;
- evaluación operativa;
- evaluación de proveedores;
- reglas;
- evidencia;
- viabilidad;
- escenarios;
- Decision Twin;
- negociación;
- Negotiation Ladder;
- resolución de conflictos;
- recomendación explicable;
- trazabilidad de decisiones.

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
- orientado a la toma de decisiones;
- explicable;
- trazable;
- gobernado.

### Principio de simplicidad

EIOS no debe saturar al CEO con información.

Debe mostrar primero la información necesaria para tomar una decisión y permitir profundizar cuando sea necesario.

---

# 6. LÍMITES DEL SISTEMA

EIOS:

- NO sustituye al ERP.
- NO genera facturas.
- NO sustituye la contabilidad.
- NO sustituye la decisión empresarial.
- NO debe ejecutar unilateralmente una compra como consecuencia de una recomendación.
- NO debe presentar información como actual si los datos superan el límite de antigüedad establecido por la configuración.
- NO debe ocultar incertidumbres o referencias de baja calidad.
- NO debe convertir automáticamente una hipótesis debatida en una regla definitiva.
- NO debe presentar como certeza aquello que sea una estimación o escenario.

---

# 7. ORIGEN Y RUTA DE LOS DATOS

La ruta:

`ERP → Excel → Power BI → SQL Server`

corresponde a una **ruta inicial de trabajo y origen de datos**, no a la arquitectura conceptual oficial de EIOS.

Actualmente se trabaja habitualmente con SAGE, pero EIOS NO debe quedar limitado exclusivamente a SAGE.

La conexión automática con ERP queda contemplada como evolución futura.

Las decisiones sobre arquitectura técnica corresponden a la documentación de Arquitectura y no a este Project Context.

---

# 8. MODELO GENERAL DE DECISIÓN

La lógica conceptual actual es:

```text
DATOS
  ↓
EVIDENCIA
  ↓
REGLAS
  ↓
EVALUACIÓN
  ↓
VIABILIDAD
  ↓
ESCENARIOS
  ↓
DECISION TWIN
  ↓
NEGOCIACIÓN
  ↓
RESOLUCIÓN DE CONFLICTOS
  ↓
RECOMENDACIÓN
  ↓
DECISOR
```

Las posibles respuestas principales son:

- 🟢 COMPRAR
- 🟡 NEGOCIAR
- 🔵 COMPRAR CONDICIONADO
- 🔴 NO COMPRAR

La recomendación de EIOS no constituye automáticamente una orden de compra.

---

# 9. VARIABLES PRINCIPALES DE LA DECISIÓN DE COMPRA

Entre las variables consideradas están:

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

```text
Stock proyectado =
Stock actual
+ entradas previstas
- salidas previstas
```

Una aplicación importante es detectar posibles roturas de stock antes de que ocurran.

---

# 11. REFERENCE & CALCULATION FRAMEWORK

Se ha identificado como área de diseño el:

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

```text
Precio ofertado: 18,50 €

+7,6 % respecto a la última compra:
17,20 € — realizada hace 25 días.

+3,4 % respecto al precio medio ponderado:
últimos 3 meses.

+6,6 % respecto al precio medio ponderado:
últimos 12 meses.
```

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

La suficiencia y calidad de la evidencia deberán alinearse con el `Evidence_Contract.md`.

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

La definición oficial de las reglas corresponde a:

`04_Reglas/Matriz_Reglas_MVP.md`

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

Pueden modificar el efecto de otra regla cuando las condiciones definidas lo permitan.

Ejemplo:

Stock elevado + pedido de cliente confirmado → reducir riesgo de sobrestock.

La clasificación definitiva y su comportamiento corresponden a la documentación oficial del motor de reglas.

---

# 17. PRIORIDAD Y CONFLICTO ENTRE REGLAS

La prioridad y resolución de conflictos entre reglas constituye un área formal del diseño de EIOS.

No debe utilizarse una simple suma de reglas verdes y rojas.

Una regla financiera crítica, por ejemplo, no debe quedar anulada simplemente porque existan varias condiciones favorables.

Debe existir una jerarquía formal que contemple:

- prioridad;
- severidad;
- bloqueos;
- excepciones;
- dependencias;
- condiciones;
- conflictos;
- resultado consolidado.

La resolución formal de conflictos corresponde a:

`04_Reglas/Capa_resolucion_conflictos.md`

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

La condición debe quedar explícita y ser trazable.

---

# 19. PLAN DE ACCIÓN FINANCIERO

Cuando una compra comprometa la situación financiera, EIOS puede mostrar alternativas que permitan estudiar la viabilidad.

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

El:

**EIOS Configuration Center**

es un componente transversal del sistema.

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

La definición de qué parámetros existen corresponde al:

`02_Parametros/Catalogo_Parametros_MVP_v0.3.md`

La configuración y gobierno de sus valores corresponde al:

`02_Parametros/Centro_Parametrizacion.md`

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

```text
Margen mínimo:

01/01/2026 → 20 %

01/07/2026 → 22 %

01/01/2027 → 25 %
```

EIOS debe poder conocer qué configuración estaba vigente cuando se produjo una determinada decisión.

La trazabilidad temporal de las decisiones deberá alinearse con:

`05_Motor/Decision_Versioning.md`

---

# 24. SIMULACIÓN DE CAMBIOS

Se considera interesante que el Configuration Center pueda permitir:

**Simular una modificación antes de aplicarla.**

Ejemplo:

```text
Margen mínimo actual: 20 %

Nuevo margen mínimo: 25 %

Resultado simulado:

14 operaciones históricas que anteriormente eran aceptables
pasarían a clasificarse como negociar.
```

Esta funcionalidad queda como propuesta de evolución hasta su formalización.

---

# 25. PRINCIPIO DE TRAZABILIDAD

Las decisiones importantes deben poder explicar:

- qué datos se utilizaron;
- qué evidencias se utilizaron;
- qué referencias se utilizaron;
- qué parámetros estaban vigentes;
- qué reglas se activaron;
- qué excepciones se aplicaron;
- qué escenarios se evaluaron;
- qué resultado produjo el motor;
- qué recomendación se generó.

El objetivo es que EIOS pueda explicar:

> "He llegado a esta recomendación por estas razones."

---

# 26. ASSURANCE Y SALVAGUARDAS

Assurance actúa transversalmente sobre EIOS.

Las decisiones deberán respetar:

- evidencia suficiente;
- trazabilidad;
- explicabilidad;
- integridad;
- coherencia;
- auditabilidad;
- control de regresiones.

La autoridad sobre Assurance corresponde a:

`00_Gobierno/EIOS_Assurance_Framework.md`

El marco congelado del EIOS Vertical MVP corresponde a:

`00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`

Ningún componente especializado puede contradecir una restricción expresamente congelada por la Salvaguarda.

---

# 27. ESTADO ACTUAL DEL PROYECTO

## 🟢 Definido

- Identidad EIOS.
- Propósito general.
- Alcance del Vertical MVP.
- Decisión de compras como núcleo.
- Negociación como parte del Vertical.
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
- Arquitectura conceptual Core + Vertical.
- Salvaguarda del Vertical MVP.
- Autoridad documental.

## 🟡 En desarrollo / formalización

- Reference & Calculation Framework.
- Criterios temporales.
- Métodos de comparación de precios.
- Fiabilidad de referencias.
- Motor de prioridades.
- Resolución de conflictos entre reglas.
- Sistema de excepciones.
- Parámetros iniciales.
- Componentes especializados del Motor.

## ⚪ Pendiente

- Arquitectura técnica definitiva.
- Modelo de datos definitivo.
- Integración automática con ERP.
- Implementación completa del motor de reglas.
- Interfaz definitiva del Configuration Center.
- Desarrollo completo del MVP.

El estado detallado de cada componente debe determinarse mediante su documentación oficial y no mediante este documento cuando exista discrepancia.

---

# 28. AUTORIDAD Y NAVEGACIÓN DOCUMENTAL

Este documento es un documento de contexto y continuidad.

No redefine conceptos cuya autoridad corresponda a documentos especializados.

Cuando exista una discrepancia documental, debe consultarse:

```text
Matriz_Autoridad_Documental.md
          ↓
determina la fuente oficial
          ↓
documento especializado
          ↓
implementación
```

Documentos fundamentales de referencia:

```text
00_Gobierno/
├── Project_Charter.md
├── Project_Context.md
├── Project_Governance.md
├── Matriz_Autoridad_Documental.md
├── EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md
└── EIOS_Assurance_Framework.md
```

---

# 29. REGLA DE TRABAJO DEL PROYECTO

EIOS se desarrollará mediante:

```text
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
```

No se debe programar una pieza importante antes de haber definido suficientemente su lógica de negocio.

Las decisiones congeladas por la Salvaguarda no deben modificarse silenciosamente.

---

# 30. PRINCIPIO FUNDAMENTAL

> EIOS no debe limitarse a decir qué está ocurriendo.
>
> Debe ayudar a comprender por qué ocurre, qué riesgo implica y qué alternativas existen para tomar una mejor decisión.

Y debe hacerlo manteniendo siempre una premisa fundamental:

> **EIOS analiza, evalúa, simula, explica y recomienda. El decisor decide.**
