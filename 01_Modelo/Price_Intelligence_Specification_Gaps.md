# EIOS — Price Intelligence — Specification Gaps

## Estado

**Estado:** DISEÑO — NO AUTORIZA IMPLEMENTACIÓN  
**Referencia:** EIOS-BL-001  
**Propósito:** separar lo ya autorizado de las decisiones funcionales pendientes para PR/PO/PPV/PMR.

## 1. Elementos autorizados

- Price Intelligence constituye la Capa 1 posterior a Quality & Trust.
- La capa contempla Precio de Referencia (PR), Precio Objetivo (PO), Precio Máximo Recomendado (PMR) y PPV como señal.
- La comparabilidad exige considerar, cuando sean aplicables, producto/concepto, unidad, cantidad, fecha y condiciones comerciales.
- Los indicadores de precio deben mantener evidencia y trazabilidad.
- Price Intelligence no constituye por sí mismo un motor de decisión.
- QTG precede funcionalmente a Price Intelligence.

## 2. Orientación aprobada para PR

Se adopta como orientación de diseño la **opción C — modelo híbrido**:

1. determinar primero la comparabilidad de las referencias;
2. seleccionar y/o ponderar la evidencia comparable mediante una metodología explícita;
3. obtener PR a partir del conjunto resultante, evitando que una única observación o una agregación ciega determine por sí sola el benchmark.

Esta orientación no autoriza todavía fórmulas, pesos, umbrales ni algoritmos concretos.

## 3. Elementos que pueden estructurarse sin fijar metodología

Una referencia de precio puede conservar, cuando estén disponibles, sus metadatos de identificación, unidad, cantidad, fecha, moneda, condiciones comerciales, fuente y trazabilidad.

La ausencia o insuficiencia de dichos elementos no debe transformarse silenciosamente en comparabilidad.

Las exclusiones de referencias no comparables deben ser explícitas y trazables.

## 4. Decisiones funcionales pendientes

Quedan pendientes de autoridad específica:

- definición operacional de comparabilidad;
- ventana temporal de referencia;
- tolerancias de cantidad y unidad;
- normalización de moneda y condiciones comerciales;
- tratamiento de transporte, impuestos y descuentos;
- selección de referencias cuando existen varias;
- tratamiento de outliers;
- tratamiento de una única referencia;
- tratamiento de referencias contradictorias;
- metodología de agregación de PR;
- metodología de determinación de PO;
- metodología de cálculo de PPV;
- metodología y fórmula de PMR.

## 5. Límites

Este documento no crea fórmulas, pesos, umbrales ni algoritmos de cálculo.

No autoriza implementación de Pricing.

PMR permanece expresamente congelado hasta disponer de especificación aprobada.

## 6. Próximo paso

Desarrollar el diseño normativo de PR a partir de la orientación híbrida aprobada, manteniendo separadas las decisiones que todavía requieren especificación funcional.
