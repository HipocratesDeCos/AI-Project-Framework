# EIOS — Especificación Visual de Interfaz v0.1

**Estado:** DISEÑO VISUAL / NO IMPLEMENTACIÓN
**Baseline:** `3c4d5cb7e02d5d7d88bb8bcf1a20a3992dc06c38`
**Rama:** `reconcile/stk-authority-baseline-2026-09-05`
**Fecha:** 2026-09-06

## 1. Propósito

Definir la arquitectura visual prevista para la pantalla de interacción de EIOS sin convertir todavía ninguna regla cuantitativa STK en lógica de aplicación.

La interfaz debe separar claramente:

1. entrada de la propuesta;
2. contexto operativo;
3. análisis económico-financiero;
4. resultado de evaluación;
5. explicación y evidencia;
6. trazabilidad.

## 2. Pantalla principal — Nueva evaluación

### Cabecera

- Logotipo EIOS.
- Identificación de la pantalla: **Nueva evaluación de compra**.
- Estado de borrador/evaluación.
- Acción **Guardar borrador**.
- Acción **Evaluar propuesta**.

### Navegación lateral

- Inicio.
- Evaluar compra.
- Propuestas.
- Artículos.
- Proveedores.
- Stock y demanda.
- Compras históricas.
- Ventas y rentabilidad.
- Finanzas.
- Configuración.
- Trazabilidad.
- Informes.

## 3. Zona A — Datos de la propuesta

Campos visuales previstos:

- Artículo.
- Descripción del artículo.
- Proveedor.
- Cantidad propuesta.
- Precio unitario.
- Importe total.
- Fecha de propuesta.
- Fecha prevista de entrega.
- Plazo de entrega.
- Plazo de pago.
- Condiciones de pago.
- Descuento.
- Rappel.
- Otras condiciones.

Los campos que sean calculados deberán mostrarse como solo lectura.

## 4. Zona B — Contexto operativo

Tarjetas visuales previstas para:

- Stock actual.
- Stock comprometido.
- Pedidos pendientes.
- Compras en tránsito.
- Consumo histórico.
- Demanda.
- Cobertura.
- Rotación.
- Recepciones previstas.

**Regla de seguridad:** mientras la autoridad cuantitativa STK no esté cerrada, estos elementos pueden existir como espacios visuales/datos de entrada, pero no deben ejecutar fórmulas STK no autorizadas.

## 5. Zona C — Ventas y rentabilidad

Tarjetas:

- Precio de venta.
- Margen.
- Margen porcentual.
- Ventas.
- Evolución de demanda.

## 6. Zona D — Situación financiera

Tarjetas:

- Tesorería disponible.
- Pagos previstos.
- Liquidez.
- Impacto económico estimado.
- Capacidad financiera relevante.

## 7. Zona E — Resultado

Panel de alta visibilidad para uno de los cinco resultados funcionales:

- `COMPRAR`
- `NEGOCIAR`
- `COMPRAR CONDICIONADO`
- `NO COMPRAR`
- `INFORMACIÓN INSUFICIENTE`

El estado visual debe distinguir resultado, motivos y condiciones sin convertir colores o iconos en la única representación del significado.

## 8. Zona F — Explicación

Panel desplegable o lateral con:

- Principales motivos.
- Factores relevantes.
- Reglas activadas.
- Evidencia utilizada.
- Excepciones.
- Riesgos.
- Información faltante.

## 9. Zona G — Condiciones recomendadas

Cuando proceda, mostrar:

- Cantidad recomendada.
- Precio objetivo.
- Plazo de pago.
- Plazo de entrega.
- Descuento/condición requerida.
- Otras condiciones.

Estas salidas son recomendaciones y no órdenes de compra.

## 10. Trazabilidad

La interfaz debe permitir acceder al detalle de:

- ID de evaluación.
- Datos utilizados.
- Fecha de los datos.
- Parámetros vigentes.
- Reglas aplicadas.
- Evidencia.
- Excepciones.
- Resultado consolidado.
- Versión de componentes.
- Fecha/hora de evaluación.

## 11. Pantallas secundarias previstas

### Detalle del análisis

Desglose por criterio, resultado, evidencia y trazabilidad.

### Historial de propuestas

Listado filtrable por:

- ID.
- Fecha.
- Artículo.
- Proveedor.
- Resultado.
- Estado.

### Ficha de artículo

Resumen del artículo, stock, demanda, histórico, ventas y proveedores.

### Panel de indicadores

Indicadores agregados de actividad y resultados, sin introducir nuevas reglas de decisión.

## 12. Principios UX

- Una pantalla principal orientada a decisión.
- Información jerarquizada, no saturada.
- Datos de entrada claramente diferenciados de resultados calculados.
- Resultados explicables y trazables.
- Estados de información insuficiente visibles.
- No ocultar incertidumbre mediante indicadores visuales.
- Responsive para escritorio y tablet.
- Accesibilidad: contraste, etiquetas, estados no dependientes exclusivamente del color y navegación por teclado.

## 13. Relación con STK

Este documento **no cierra M01–M10** y no constituye autoridad cuantitativa.

No se autoriza mediante esta especificación:

- fórmula de `consumption`;
- fórmula de demanda;
- cálculo de cobertura;
- parámetros de seguridad;
- relación parámetro→regla;
- Test_ID;
- integración con el Plan de Pruebas;
- implementación cuantitativa.

## 14. Estado

**Diseño visual aprobado como referencia de interfaz.**

**Implementación:** pendiente de la materialización técnica correspondiente y, para cualquier componente STK cuantitativo, de la resolución previa de la autoridad M01–M10.
