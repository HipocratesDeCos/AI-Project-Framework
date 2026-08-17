# EIOS — Salvaguarda de continuidad del proyecto
**Fecha:** 13/08/2026
**Estado:** continuidad de trabajo; NO sustituye los documentos oficiales.

## 1. Identidad y objetivo
EIOS — Enterprise Intelligent Operations System.
Sistema de apoyo a la decisión de adquisiciones para CEO/compras, basado en histórico, comparabilidad, precio, margen, stock, demanda, liquidez, proveedor, riesgo y condiciones comerciales.
**Principio:** EIOS recomienda y explica; el CEO decide.

La auditoría del Manual Maestro y la posible discrepancia SIDA/EIOS quedaron expresamente APLAZADAS. No reabrir esa tarea salvo petición del usuario.

## 2. Arquitectura aceptada
- CAPA 0 — Gatekeeper de entrada / calidad de datos
- CAPA 1 — Inteligencia de Precio
- CAPA 2 — TCO (Total Cost of Ownership)
- CAPA 3 — Stock y demanda
- CAPA 4 — Finanzas / liquidez
- CAPA 5 — Proveedor / riesgo
- CAPA 6 — Resolución de conflictos y recomendación

Existe un motor transversal de escenarios y recálculo.

## 3. Motor de escenarios
Cada cambio relevante de la negociación genera un escenario conservado:
S0 oferta inicial → S1 descuento → S2 plazo → S3 cantidad → etc.
Nunca sobrescribir escenarios anteriores.
Toda modificación relevante debe provocar recálculo.
EIOS no compensa automáticamente bloqueos críticos mediante una puntuación.

## 4. Estados
- FAVORABLE
- NEGOCIABLE
- CONDICIONADA
- DESFAVORABLE
- NO COMPRAR
- INFORMACIÓN INSUFICIENTE

## 5. CAPA 0
Variables conceptuales:
Producto_ID, RFP (Referencia Funcional de Producto), Comparabilidad, Unidad_Compra, Cantidad_Propuesta, Fecha_Propuesta, Precio_Oferta, descuentos, rappels, umbral de rappel, plazo de pago, cantidad mínima, transporte, seguro, otros costes y calidad de datos.

RFP: agrupa productos funcionalmente comparables.
EIOS puede proponer automáticamente la comparabilidad y una persona puede validarla/modificarla.
Comparables secundarios: aproximadamente 90–75 %.
Ante duda sobre pertenencia a más de una RFP: No.
No se considera necesaria una fecha de vigencia de la RFP.

## 6. CAPA 1 — Inteligencia de Precio
Tres conceptos separados:
- **PR — Precio de Referencia:** histórico comparable ponderado.
- **PO — Precio Objetivo:** precio que se intenta conseguir negociando.
- **PMR — Precio Máximo Recomendado:** máximo aceptable dadas todas las circunstancias.

No cerrar todavía la fórmula definitiva del PMR.

Las referencias históricas se filtran por producto/RFP, comparabilidad, unidad, cantidad, fecha, condiciones, proveedor y calidad de datos.
Las operaciones excluidas no desaparecen: quedan trazadas con motivo.
Peso conceptual: comparabilidad × recencia × equivalencia de condiciones.
PPV (Purchase Price Variance) es una señal, no una decisión automática.

El precio objetivo puede considerar histórico, proveedores alternativos, cantidad, tendencia y condiciones.
El PMR podrá verse afectado por margen, TCO, stock, liquidez, proveedor, riesgo y alternativas.

## 7. CEA, descuentos y rappels
**CEA — Coste Efectivo de Adquisición**.
Diferenciar:
- CEA inmediato: beneficio ya aplicable.
- CEA potencial: beneficio condicionado futuro.

Principio:
> Un beneficio futuro condicionado no se utiliza como beneficio cierto para justificar una decisión actual.

El CEO puede cambiar precio, descuento, rappel, cantidad, plazo, transporte o garantías durante la reunión y EIOS recalcula el escenario.

## 8. CAPA 2 — TCO, punto exacto actual
Objetivo: determinar el coste real de adquirir la operación más allá del precio unitario.

Distinción:
- Precio ≠ CEA ≠ TCO.

Clasificación acordada:

### Grupo A — TCO directo
En principio:
- precio;
- transporte;
- seguro de transporte;
- aranceles;
- impuestos no recuperables;
- manipulación directamente asociada;
- inspecciones necesarias;
- merma prevista;
- otros costes directamente imputables.

### Grupo B — costes derivados
- almacenamiento;
- exceso de stock;
- obsolescencia;
- devoluciones;
- incidencias de calidad.
Se analizarán principalmente en CAPA 3.

### Grupo C — finanzas/oportunidad
- financiación;
- coste de capital;
- liquidez;
- coste de oportunidad.
Se analizarán principalmente en CAPA 4.

Regla: un coste debe tener una capa principal; no duplicarlo como coste decisorio en varias capas.

**PRÓXIMO PASO:** decidir/cerrar la frontera de CAPA 2 antes de construir transporte, seguros y aranceles.

## 9. CAPA 3 — Stock y demanda
Pendiente de construcción detallada.
Conceptos aceptados:
- rotación;
- días de cobertura;
- demanda histórica/proyectada;
- sobrestock;
- permanencia máxima;
- obsolescencia;
- overtrading;
- impacto de cantidad;
- costes derivados de almacenamiento.

La permanencia máxima debe ser parametrizable. Ejemplo: compra 01/09/2025, límite 12 meses, alerta si la compra proyecta permanencia superior.

Debe analizarse la compra considerando pedidos ya comprometidos y, cuando proceda, excluir del histórico el pedido extraordinario del cliente que distorsiona la demanda.

## 10. CAPA 4 — Finanzas / liquidez
Arquitectura aceptada conceptualmente, todavía NO implementada.
Variables núcleo:
- liquidez inmediata;
- test ácido;
- rotación;
- PMP (Período Medio de Pago) vs PMC (Período Medio de Cobro);
- CCC (Cash Conversion Cycle);
- overtrading;
- crédito comercial;
- obsolescencia;
- permanencia máxima;
- impacto financiero proyectado.

Variables moduladoras:
- endeudamiento;
- costes de almacenamiento;
- CCC.

Posterior:
- divisa/cobertura.

No usar umbrales universales como bloqueos automáticos. Los umbrales serán parametrizables por empresa.

EIOS debe comparar:
**situación actual → impacto de la compra → situación proyectada → recomendación.**

## 11. CAPA 5 — Proveedor / riesgo
Conceptos previstos:
Supplier Reliability Score, OTIF (On-Time In-Full), SRM, concentración, compliance, ESG, BATNA, Dual Sourcing y riesgo.

Para proveedor de fiabilidad baja se definieron cinco familias de salvaguardas:
1. garantías contractuales;
2. garantías financieras;
3. pago diferido/condiciones comerciales;
4. entrega dividida;
5. inspecciones de seguridad en origen.

Regla del usuario:
- proveedor rechaza los 5 puntos → **NO COMPRAR**;
- acepta algunos → **COMPRA CONDICIONADA**;
- rechaza uno pero renegocia otro con aceptación del proveedor y conformidad del CEO → puede ser **COMPRA CONDICIONADA**, si el riesgo queda suficientemente mitigado.

## 12. Negociación
Si el precio es desfavorable pero negociable:
- negociar;
- buscar precio objetivo;
- standby si procede;
- buscar proveedores alternativos si el proveedor rechaza;
- recurrir a oferta alternativa si es mejor.
Analizar coste de oportunidad.

## 13. Salida para el CEO
No saturar con cálculos.
Formato preferido:
**Precio:** desfavorable
Pequeña línea contextual.
**Margen:** aceptable
Pequeña línea contextual.
**Stock:** adecuado
**Liquidez:** tensionada
**Plazo actual:** 30 días

El margen porcentual debe ser muy visual.
Usar “económico”, no “barato”.

## 14. Principios de continuidad
1. EIOS recomienda; CEO decide.
2. No compensación automática de bloqueos.
3. Explicabilidad y trazabilidad.
4. Control humano.
5. Información insuficiente es resultado válido.
6. Descuento confirmado y rappel condicionado no son equivalentes.
7. Precio, CEA y TCO son distintos.
8. PR, PO y PMR son distintos.
9. Cambios relevantes generan recálculo.
10. Conservar escenarios.
11. No duplicar costes entre capas.
12. No implementar decisiones en archivos sin aprobación explícita del usuario.
13. Mantener acrónimos con su significado durante las iteraciones.

## 15. Acrónimos clave
EIOS — Enterprise Intelligent Operations System
RFP — Referencia Funcional de Producto
CEA — Coste Efectivo de Adquisición
TCO — Total Cost of Ownership
PR — Precio de Referencia
PO — Precio Objetivo
PMR — Precio Máximo Recomendado
PPV — Purchase Price Variance
OTIF — On-Time In-Full
SRM — Supplier Relationship Management
BATNA — Best Alternative to a Negotiated Agreement
CCC — Cash Conversion Cycle
PMP — Período Medio de Pago
PMC — Período Medio de Cobro
ESG — Environmental, Social and Governance

## 16. Punto exacto para retomar
Continuar en **CAPA 2 — TCO**, concretamente en la frontera entre:
- Grupo A: costes directamente atribuibles;
- Grupo B: costes derivados del stock;
- Grupo C: costes financieros/oportunidad.

No saltar todavía a CAPA 3.
No cerrar todavía las fórmulas definitivas de PO/PMR.
No reabrir la auditoría aplazada del Manual Maestro.
