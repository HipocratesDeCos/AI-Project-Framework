# ESPECIFICACIÓN FUNCIONAL

## EIOS — Enterprise Intelligent Operations System

**Versión:** 2.0  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP  
**Última actualización:** 19/08/2026

---

# 1. PROPÓSITO

La Especificación Funcional define qué capacidades y comportamientos debe ofrecer EIOS desde el punto de vista funcional y empresarial.

EIOS tiene como finalidad evaluar una propuesta de compra antes de comprometer recursos de la empresa, utilizando información disponible de compras, stock, ventas, rentabilidad, proveedores y situación financiera.

El sistema debe generar una recomendación explicable y trazable para facilitar la decisión humana.

EIOS no sustituye al decisor autorizado ni ejecuta automáticamente la compra.

---

# 2. ALCANCE

La especificación comprende las capacidades funcionales necesarias para:

- registrar o recibir una propuesta de compra;
- validar la información disponible;
- determinar si existe evidencia suficiente;
- analizar la operación;
- evaluar las condiciones empresariales relevantes;
- aplicar las reglas vigentes;
- considerar excepciones autorizadas;
- consolidar los resultados mediante el mecanismo de resolución de conflictos;
- generar una recomendación;
- explicar los principales motivos;
- conservar la trazabilidad de la evaluación;
- permitir la decisión final por parte del usuario autorizado.

La especificación no define la implementación técnica de estas capacidades.

---

# 3. PRINCIPIO DE SEPARACIÓN FUNCIONAL

Este documento define:

> **QUÉ DEBE HACER EIOS.**

No define:

> **CÓMO DEBE IMPLEMENTARSE.**

Quedan fuera de esta especificación:

- código;
- estructura SQL;
- diseño físico de bases de datos;
- algoritmos técnicos de implementación;
- arquitectura de infraestructura;
- diseño visual detallado;
- catálogo de reglas;
- catálogo de parámetros;
- metodología detallada de cálculo de cada indicador.

Estos elementos deberán mantenerse en sus documentos y capas correspondientes.

---

# 4. ACTORES

## 4.1 Decisor autorizado

Persona responsable de tomar la decisión empresarial final.

EIOS proporciona una recomendación, pero la decisión final corresponde al usuario autorizado.

## 4.2 Responsable de Compras

Usuario que puede introducir, consultar o analizar propuestas de compra y sus condiciones.

## 4.3 Administrador / configurador

Cuando la configuración del sistema lo contemple, podrá gestionar parámetros y configuraciones autorizadas.

La gestión concreta de parámetros queda fuera del alcance de esta especificación y corresponde al sistema de parametrización.

---

# 5. PROPUESTA DE COMPRA

EIOS deberá poder evaluar una propuesta de compra.

Cuando la información esté disponible, podrá incluir:

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
- otras condiciones comerciales relevantes.

La ausencia de información crítica deberá poder ser detectada antes de emitir una recomendación.

---

# 6. INFORMACIÓN EMPRESARIAL UTILIZADA

Para evaluar una propuesta, EIOS podrá utilizar información procedente de:

## Compras

- compras históricas;
- precios;
- cantidades;
- proveedores;
- condiciones;
- descuentos;
- rappels;
- incidencias.

## Stock

- stock actual;
- stock comprometido;
- pedidos pendientes;
- compras en tránsito;
- rotación;
- cobertura;
- demanda histórica;
- demanda prevista.

## Ventas y rentabilidad

- ventas;
- precio de venta;
- margen;
- margen porcentual;
- rentabilidad;
- evolución de la demanda.

## Proveedores

- proveedor actual;
- proveedores alternativos;
- histórico;
- condiciones;
- incidencias.

## Situación financiera

- tesorería;
- pagos previstos;
- liquidez;
- fondo de maniobra;
- capacidad de pago;
- necesidades financieras;
- impacto económico de la operación.

La utilización concreta de cada fuente dependerá de la evaluación y de la información disponible.

---

# 7. VALIDACIÓN Y SUFICIENCIA DE LA INFORMACIÓN

Antes de generar una recomendación, EIOS deberá determinar si dispone de información suficiente para realizar la evaluación.

La evaluación podrá considerar:

- completitud;
- actualidad;
- consistencia;
- comparabilidad;
- cantidad de referencias disponibles;
- calidad de la evidencia.

Cuando la información crítica sea insuficiente, EIOS no deberá fabricar una conclusión.

El resultado funcional podrá ser:

**INFORMACIÓN INSUFICIENTE**

---

# 8. ANÁLISIS FUNCIONAL

EIOS deberá poder evaluar, cuando existan datos suficientes, diferentes dimensiones de la propuesta:

- precio;
- histórico de compras;
- condiciones comerciales;
- stock;
- demanda;
- rentabilidad;
- proveedores;
- situación financiera;
- impacto temporal de la operación.

No todas las dimensiones estarán necesariamente disponibles para todas las propuestas.

---

# 9. ANÁLISIS HISTÓRICO

EIOS deberá poder comparar la propuesta con referencias históricas disponibles.

La evaluación podrá considerar:

- compras recientes;
- compras históricas;
- cantidades;
- proveedor;
- fecha;
- condiciones;
- descuentos;
- rappels;
- comparabilidad.

La información histórica deberá utilizarse de forma contextualizada.

Un dato antiguo o poco comparable no deberá presentarse como una referencia equivalente a una operación reciente y comparable.

---

# 10. ANÁLISIS TEMPORAL Y STOCK

EIOS deberá poder evaluar el efecto previsto de la compra sobre el stock.

Cuando existan datos suficientes, podrá considerar:

- stock actual;
- consumo;
- demanda;
- pedidos pendientes;
- compras en tránsito;
- plazo de entrega;
- fecha prevista de recepción;
- cantidad propuesta.

El sistema deberá poder identificar situaciones como:

- riesgo de rotura de stock;
- exceso de stock;
- compra potencialmente innecesaria;
- compra necesaria para atender una demanda prevista.

---

# 11. RENTABILIDAD

EIOS deberá poder considerar el impacto de la propuesta sobre la rentabilidad.

Cuando los datos estén disponibles podrá evaluar:

- precio de compra;
- precio de venta;
- margen;
- margen porcentual;
- margen mínimo configurado;
- descuentos;
- rappels.

La metodología concreta de cálculo deberá mantenerse fuera de esta especificación y documentarse en la capa correspondiente.

---

# 12. SITUACIÓN FINANCIERA

EIOS deberá poder considerar el impacto de una compra sobre la situación financiera de la empresa.

Podrá evaluar, cuando exista información suficiente:

- tesorería;
- pagos previstos;
- liquidez;
- fondo de maniobra;
- capacidad de pago;
- necesidades financieras.

Una operación económicamente atractiva no deberá considerarse automáticamente conveniente si genera un riesgo financiero relevante identificado por las reglas vigentes.

---

# 13. REGLAS DE NEGOCIO

EIOS deberá evaluar la propuesta conforme a las reglas empresariales vigentes.

Las reglas podrán analizar diferentes aspectos de la operación y generar resultados individuales.

La especificación funcional no define el catálogo ni la lógica interna de las reglas.

La autoridad documental de las reglas corresponde a la documentación específica de reglas de EIOS.

---

# 14. EFECTO DE LAS REGLAS

Las reglas podrán producir diferentes tipos de intervención:

- bloqueo;
- condicionamiento;
- negociación;
- información.

La interpretación detallada de estos efectos corresponde a la Matriz de Reglas vigente.

EIOS deberá conservar la relación entre el resultado producido y la regla que lo generó.

---

# 15. EXCEPCIONES

EIOS deberá poder considerar excepciones autorizadas cuando una regla contemple dicha posibilidad.

Una excepción deberá ser:

- identificable;
- justificable;
- trazable;
- compatible con las salvaguardas aplicables.

Las excepciones no podrán utilizarse para anular restricciones que hayan sido definidas como no anulables.

El catálogo y la lógica concreta de las excepciones quedan fuera de esta especificación.

---

# 16. RESOLUCIÓN DE CONFLICTOS

Cuando varias reglas produzcan resultados que entren en conflicto, EIOS deberá utilizar el mecanismo de resolución de conflictos definido para el sistema.

La Capa de Resolución de Conflictos (CRC) deberá consolidar los resultados conforme a la autoridad y metodología establecidas.

La Especificación Funcional no define la jerarquía interna de resolución de la CRC.

---

# 17. RESULTADOS FUNCIONALES OFICIALES

EIOS deberá utilizar los siguientes resultados oficiales:

## COMPRAR

La operación puede realizarse conforme a los criterios y reglas aplicables.

## NEGOCIAR

La operación puede resultar viable, pero deben mejorarse determinadas condiciones.

## COMPRAR CONDICIONADO

La operación puede realizarse siempre que se cumplan unas condiciones explícitas.

## NO COMPRAR

La operación no debe realizarse conforme a los criterios y reglas aplicables.

## INFORMACIÓN INSUFICIENTE

La información disponible no permite realizar una evaluación suficientemente fiable.

Estos cinco resultados constituyen la clasificación funcional oficial de la recomendación.

---

# 18. RECOMENDACIÓN

EIOS deberá generar una recomendación a partir de:

- información disponible;
- análisis realizado;
- reglas activadas;
- excepciones aplicadas;
- resolución consolidada;
- condiciones relevantes.

La recomendación deberá ser comprensible para el usuario.

EIOS no deberá presentar como hecho una conclusión que no esté sustentada por la evidencia disponible.

---

# 19. CONDICIONES DE NEGOCIACIÓN

Cuando el resultado sea **NEGOCIAR** o **COMPRAR CONDICIONADO**, EIOS deberá poder mostrar las condiciones relevantes identificadas por el análisis.

Cuando sea posible, podrá mostrar:

- precio objetivo;
- precio máximo recomendado;
- plazo de pago objetivo;
- cantidad recomendada;
- descuento requerido;
- otras condiciones necesarias.

Estas condiciones constituyen recomendaciones para valoración humana y no órdenes de ejecución.

---

# 20. EXPLICACIÓN DE LA RECOMENDACIÓN

EIOS deberá poder explicar los principales motivos de su recomendación.

La explicación deberá permitir identificar, cuando corresponda:

- resultado;
- principales factores;
- reglas activadas;
- evidencia relevante;
- excepciones;
- condiciones;
- riesgos.

La explicación detallada deberá estar disponible sin obligar al usuario a visualizar toda la complejidad interna del sistema.

---

# 21. TRAZABILIDAD FUNCIONAL

EIOS deberá conservar la información necesaria para reconstruir el contexto de una recomendación.

Cuando el sistema lo soporte, deberá poder relacionar:

- propuesta;
- datos utilizados;
- fecha de los datos;
- parámetros vigentes;
- reglas aplicadas;
- resultados individuales;
- excepciones;
- resolución consolidada;
- recomendación;
- versión de los componentes relevantes.

La especificación funcional no define el modelo físico de almacenamiento.

---

# 22. PARAMETRIZACIÓN

EIOS deberá utilizar los parámetros vigentes definidos en el sistema de parametrización.

Entre los elementos potencialmente configurables se encuentran:

- periodos de referencia;
- límites;
- tolerancias;
- niveles de stock;
- márgenes;
- criterios financieros;
- reglas;
- excepciones.

La gestión, versionado y administración de parámetros corresponde a la capa de parametrización.

---

# 23. VIGENCIA DE LA CONFIGURACIÓN

Cuando una recomendación dependa de parámetros configurables, EIOS deberá poder identificar qué configuración estaba vigente en el momento de la evaluación.

Esto permite mantener la reproducibilidad de las recomendaciones.

La definición técnica del versionado de parámetros queda fuera del alcance de esta especificación.

---

# 24. SIMULACIÓN

EIOS podrá ofrecer capacidades de simulación para evaluar escenarios hipotéticos.

La simulación deberá distinguirse de la evaluación de una propuesta real.

Un escenario simulado no deberá modificar por sí mismo:

- la configuración vigente;
- los datos históricos;
- una decisión real;
- una compra.

Los cambios simulados deberán identificarse como tales.

---

# 25. PRESENTACIÓN DE LA INFORMACIÓN

La interfaz deberá presentar inicialmente la información necesaria para comprender la recomendación.

Como mínimo, deberá poder mostrar:

1. resultado;
2. principales motivos;
3. riesgos relevantes;
4. condiciones de negociación o compra condicionada;
5. evidencia relevante cuando sea necesaria.

El detalle adicional deberá estar disponible bajo demanda.

Esta especificación no define colores, posiciones, componentes visuales ni tecnología de interfaz.

---

# 26. CONTROL HUMANO

EIOS deberá mantener una separación clara entre:

- evaluación del sistema;
- recomendación;
- decisión empresarial.

El flujo funcional será:

```text
DATOS
  ↓
ANÁLISIS
  ↓
REGLAS
  ↓
RESOLUCIÓN
  ↓
RECOMENDACIÓN
  ↓
DECISOR HUMANO
  ↓
DECISIÓN EMPRESARIAL
```

EIOS no deberá ejecutar automáticamente una compra como consecuencia de una recomendación, salvo que dicha capacidad sea posteriormente definida, autorizada y documentada mediante una modificación específica de la arquitectura y del modelo de gobierno.

---

# 27. COMPORTAMIENTO ANTE INFORMACIÓN INSUFICIENTE

Cuando falte información crítica para una evaluación fiable, EIOS deberá:

- identificar la insuficiencia;
- indicar, cuando sea posible, qué información falta;
- evitar una recomendación basada en evidencia insuficiente;
- utilizar el resultado **INFORMACIÓN INSUFICIENTE** cuando corresponda.

La ausencia de evidencia no deberá convertirse automáticamente en una evaluación favorable o desfavorable.

---

# 28. COMPORTAMIENTO ANTE RESULTADOS CONFLICTIVOS

Cuando diferentes evaluaciones produzcan resultados incompatibles, EIOS deberá:

1. conservar los resultados individuales;
2. identificar las reglas que los generaron;
3. considerar las excepciones válidas;
4. trasladar la resolución a la CRC;
5. utilizar el resultado consolidado para construir la recomendación.

No deberá utilizar una suma o promedio arbitrario de resultados.

---

# 29. NO COMPENSACIÓN AUTOMÁTICA

EIOS no deberá asumir que una condición favorable compensa automáticamente una condición desfavorable.

Por ejemplo:

```text
Precio favorable
+
Riesgo financiero crítico
```

no implica automáticamente:

```text
COMPRAR
```

La resolución deberá seguir las reglas y mecanismos de autoridad establecidos.

---

# 30. SEGURIDAD FUNCIONAL DE LA RECOMENDACIÓN

La recomendación deberá ser coherente con:

- las reglas vigentes;
- los parámetros vigentes;
- la evidencia disponible;
- la resolución consolidada;
- las salvaguardas aplicables.

EIOS no deberá ocultar un bloqueo relevante para presentar una recomendación aparentemente favorable.

---

# 31. CAPACIDADES NO INCLUIDAS

No forman parte de esta especificación:

- ejecución automática de pedidos;
- negociación automática con proveedores;
- modificación automática de parámetros;
- modificación automática de reglas;
- eliminación de evidencias;
- alteración de decisiones históricas;
- anulación silenciosa de salvaguardas.

Cualquier incorporación futura de estas capacidades deberá someterse al gobierno y control documental de EIOS.

---

# 32. REQUISITOS DE CALIDAD FUNCIONAL

La funcionalidad deberá favorecer:

- trazabilidad;
- explicabilidad;
- coherencia;
- reproducibilidad;
- control humano;
- evidencia suficiente;
- separación de responsabilidades;
- ausencia de automatización silenciosa.

---

# 33. RELACIÓN CON OTROS DOCUMENTOS

Esta especificación deberá mantenerse coherente con los documentos vigentes de EIOS.

Especialmente:

- `Matriz_Autoridad_Documental.md` — autoridad documental;
- `Master_Project_Map.md` — mapa maestro del proyecto;
- `03_Arquitectura/Architecture_Blueprint.md` — arquitectura;
- `04_Reglas/Matriz_Reglas_MVP.md` — reglas;
- `04_Reglas/Capa_resolucion_conflictos.md` — resolución de conflictos;
- `05_Motor/Modelo_Empresarial_Decision.md` — modelo empresarial de decisión;
- documentación de `02_Parametros` — parametrización.

Las dependencias documentales deberán corresponder a archivos existentes y vigentes.

---

# 34. PRINCIPIOS FUNCIONALES

EIOS deberá respetar los siguientes principios:

1. **Recomendación, no sustitución del decisor.**
2. **Evidencia antes que conclusión.**
3. **Trazabilidad de la recomendación.**
4. **Explicabilidad.**
5. **Separación entre reglas y resolución de conflictos.**
6. **Separación entre parámetros y lógica empresarial.**
7. **No compensación automática.**
8. **Control humano.**
9. **No automatización silenciosa.**
10. **Coherencia con la arquitectura EIOS.**
11. **Reproducibilidad.**
12. **Integridad de la información utilizada.**

---

# 35. ESTADO Y EVOLUCIÓN

Esta versión constituye la especificación funcional aprobada para el **EIOS Vertical MVP**.

Los aspectos que requieran decisiones adicionales de diseño deberán quedar documentados en la capa correspondiente.

La evolución posterior de esta especificación deberá conservar trazabilidad de versiones y no deberá modificar silenciosamente el significado de decisiones ya realizadas.

---

# 36. ESTADO DEL DOCUMENTO

**Versión:** 2.0  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP  
**Documento:** Especificación Funcional
