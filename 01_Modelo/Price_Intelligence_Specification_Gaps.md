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
- La unidad económica de PR queda cerrada como **precio de transacción comparable normalizado**.
- La representatividad se mantiene como evaluación criterial y explicable; no se introduce un score numérico en el MVP.
- La representatividad y la suficiencia son conceptos independientes.

## 2. Orientación aprobada para PR

Se adopta como orientación de diseño la **opción C — modelo híbrido**:

1. determinar primero la comparabilidad de las referencias;
2. evaluar la representatividad contextual y seleccionar la evidencia comparable mediante una metodología explícita;
3. comprobar la suficiencia del conjunto seleccionado;
4. ponderar únicamente cuando exista una metodología autorizada;
5. obtener PR a partir del conjunto resultante, evitando que una única observación o una agregación ciega determine por sí sola el benchmark.

Esta orientación no autoriza todavía fórmulas, pesos, umbrales ni algoritmos concretos.

## 3. Elementos que pueden estructurarse sin fijar metodología

Una referencia de precio puede conservar, cuando estén disponibles, sus metadatos de identificación, unidad, cantidad, fecha, moneda, condiciones comerciales, proveedor, fuente y trazabilidad.

La ausencia o insuficiencia de dichos elementos no debe transformarse silenciosamente en comparabilidad.

Las exclusiones de referencias no comparables deben ser explícitas y trazables.

La normalización económica solo podrá modificar el precio observado cuando exista una regla metodológica expresamente autorizada.

## 4. Decisiones funcionales pendientes

Quedan pendientes de autoridad específica:

- criterios concretos de representatividad;
- tolerancias de cantidad y unidad;
- normalización de moneda y condiciones comerciales;
- tratamiento de transporte, impuestos, descuentos y rappels;
- selección de referencias cuando existen varias;
- tratamiento de outliers;
- tratamiento de una única referencia;
- tratamiento de referencias contradictorias;
- criterios operativos de suficiencia;
- metodología de ponderación, si resulta necesaria;
- metodología de agregación de PR;
- metodología de determinación de PO;
- metodología de cálculo de PPV;
- metodología y fórmula de PMR.

### Decisiones ya resueltas

- **GAP-PI-TEMP-01:** para `R-PRE-001`, “reciente” = dentro de `P-PRE-001` en el diseño MVP. `P-PRE-002` conserva su función de periodo ampliado y `P-DAT-002` su función de antigüedad máxima histórica.
- **GAP-PI-SEM-01:** PR = precio de transacción comparable normalizado.
- Representatividad: enfoque criterial y explicable, sin `representativeness_score` en MVP.
- Representatividad ≠ suficiencia.
- Ponderación no es obligatoria y no recibe pesos implícitos.
- Outlier ≠ error y no implica exclusión automática.
- Contradicción ≠ outlier y no se resuelve mediante heurística implícita.

## 5. Límites

Este documento no crea fórmulas, pesos, umbrales ni algoritmos de cálculo que todavía no dispongan de autoridad metodológica.

No autoriza implementación de Pricing.

PMR permanece expresamente congelado hasta disponer de especificación aprobada.

## 6. Próximo paso

Desarrollar el diseño normativo de PR a partir de la orientación híbrida aprobada, manteniendo separadas las decisiones que todavía requieren especificación funcional.

## 7. Invariantes de gobierno

- Dato disponible ≠ criterio metodológico autorizado.
- Evidencia fiable ≠ representatividad económica.
- Comparabilidad precede a representatividad.
- Representatividad precede a selección.
- Selección precede a ponderación.
- Ponderación no corrige deficiencias de comparabilidad o representatividad.
- Representatividad ≠ suficiencia.
- N referencias ≠ N referencias suficientes.
- Outlier ≠ error.
- Contradicción ≠ outlier.
- Ninguna normalización económica puede introducirse implícitamente.
- PR no incorpora por defecto TCO ni decisiones empresariales posteriores.
- La selección no puede depender retrospectivamente de la conveniencia del PR resultante.