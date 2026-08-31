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

## 2. Elementos que pueden estructurarse sin fijar metodología

Una referencia de precio puede conservar, cuando estén disponibles, sus metadatos de identificación, unidad, cantidad, fecha, moneda, condiciones comerciales, fuente y trazabilidad.

La ausencia o insuficiencia de dichos elementos no debe transformarse silenciosamente en comparabilidad.

Las exclusiones de referencias no comparables deben ser explícitas y trazables.

## 3. Decisiones funcionales pendientes

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

## 4. Límites

Este documento no crea fórmulas, pesos, umbrales ni algoritmos de cálculo.

No autoriza implementación de Pricing.

PMR permanece expresamente congelado hasta disponer de especificación aprobada.

## 5. Próximo paso

La siguiente fase deberá obtener autoridad funcional para resolver los gaps anteriores antes de cerrar un contrato de implementación de Price Intelligence.
