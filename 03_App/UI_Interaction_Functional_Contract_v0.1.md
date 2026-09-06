# EIOS — Contrato Funcional de Interacción v0.1

**Estado:** DISEÑO FUNCIONAL / NO IMPLEMENTACIÓN
**Baseline:** `a3ea3992c992f04f12280146977c789ec6db9c0b`
**Rama:** `reconcile/stk-authority-baseline-2026-09-05`
**Fecha:** 2026-09-06

## 1. Propósito

Definir el comportamiento funcional de la interfaz EIOS desde la entrada de una propuesta hasta la presentación del resultado y su trazabilidad.

Este contrato define interacción, estados, validaciones y transiciones. No constituye contrato cuantitativo STK ni autoriza fórmulas M01–M10.

## 2. Principios de interacción

1. El usuario debe poder identificar en todo momento si está introduciendo datos, consultando datos o viendo un resultado.
2. Ninguna acción de evaluación debe ejecutarse si faltan datos obligatorios para el alcance autorizado.
3. La ausencia de información crítica debe producir un estado explícito de `INFORMACIÓN INSUFICIENTE`, cuando corresponda.
4. Las recomendaciones nunca se presentan como órdenes de compra.
5. Toda evaluación debe conservar contexto temporal, datos utilizados, configuración y resultado.
6. Los campos STK cuya metodología cuantitativa siga pendiente pueden visualizarse, pero no pueden ejecutar fórmulas no autorizadas.

## 3. Estados de la evaluación

| Estado | Descripción | Acción permitida |
|---|---|---|
| BORRADOR | Propuesta iniciada pero no enviada a evaluación | Editar / guardar / cancelar |
| VALIDANDO | Comprobación de integridad y suficiencia de datos | Esperar resultado de validación |
| LISTA_PARA_EVALUAR | Datos suficientes para el alcance autorizado | Evaluar |
| INFORMACION_INSUFICIENTE | Falta información necesaria para producir una evaluación válida | Completar datos / cancelar |
| EVALUANDO | Evaluación en ejecución | No editar campos críticos |
| EVALUADA | Resultado disponible | Consultar / guardar / nueva evaluación |
| ERROR | Fallo técnico o inconsistencia que impide completar la evaluación | Revisar / reintentar |
| CANCELADA | Evaluación abandonada | Consultar historial |

## 4. Flujo principal

`BORRADOR → VALIDANDO → LISTA_PARA_EVALUAR → EVALUANDO → EVALUADA`

Ramas alternativas:

- `VALIDANDO → INFORMACION_INSUFICIENTE`
- `VALIDANDO → ERROR`
- `EVALUANDO → ERROR`
- `BORRADOR → CANCELADA`
- `INFORMACION_INSUFICIENTE → BORRADOR`

## 5. Pantalla Nueva evaluación

### 5.1 Entrada de propuesta

El usuario puede introducir o seleccionar:

- Artículo.
- Proveedor.
- Cantidad propuesta.
- Precio unitario.
- Fecha propuesta.
- Fecha prevista de entrega.
- Plazo de entrega.
- Plazo de pago.
- Condiciones de pago.
- Descuento.
- Rappel.
- Otras condiciones.

El ID de propuesta se genera o conserva como identificador de trazabilidad.

### 5.2 Datos de contexto

La pantalla puede presentar datos de stock, demanda, compras, ventas, rentabilidad y finanzas según disponibilidad.

Los campos `UI-STK-*` sujetos a metodología pendiente se presentan como datos de contexto y no ejecutan lógica cuantitativa no autorizada.

## 6. Validación antes de evaluar

La validación debe comprobar, como mínimo:

- existencia de artículo;
- identificación de proveedor cuando sea necesaria;
- cantidad válida;
- precio válido cuando sea requerido;
- fechas coherentes;
- ausencia de campos obligatorios sin informar;
- consistencia básica de unidades y moneda cuando estén definidas;
- disponibilidad de información requerida por las reglas autorizadas.

La validación no debe sustituir un dato ausente por cero sin una regla autorizada que lo establezca.

## 7. Acción Evaluar propuesta

Al pulsar **Evaluar propuesta**:

1. se bloquean temporalmente los campos críticos;
2. se ejecuta la validación;
3. si la información es insuficiente, se muestra el motivo y se mantiene la evaluación fuera del estado EVALUADA;
4. si existe información suficiente para las reglas autorizadas, se ejecuta únicamente dicha lógica;
5. se registra la evidencia y el contexto;
6. se muestra el resultado permitido.

## 8. Resultado

El resultado consolidado solo puede adoptar uno de estos valores:

- `COMPRAR`
- `NEGOCIAR`
- `COMPRAR CONDICIONADO`
- `NO COMPRAR`
- `INFORMACIÓN INSUFICIENTE`

La interfaz debe mostrar junto al resultado:

- principales motivos;
- factores relevantes;
- reglas activadas;
- evidencia utilizada;
- excepciones;
- riesgos;
- información faltante cuando exista.

## 9. Condiciones recomendadas

Cuando el resultado las requiera, la interfaz puede presentar:

- cantidad recomendada;
- precio objetivo;
- plazo de pago recomendado;
- plazo de entrega recomendado;
- descuento o condición requerida;
- otras condiciones.

Estas salidas son recomendaciones y no generan por sí mismas una orden de compra.

## 10. Trazabilidad

Cada evaluación debe conservar o permitir recuperar:

- ID de evaluación;
- ID de propuesta;
- datos utilizados;
- fecha de los datos;
- fecha/hora de evaluación;
- parámetros/configuración vigentes;
- reglas aplicadas;
- evidencia;
- excepciones;
- resultado consolidado;
- versión de componentes.

## 11. Edición y re-evaluación

Antes de evaluar, el usuario puede modificar los datos de entrada.

Después de una evaluación, una modificación de un dato crítico debe iniciar una nueva versión de evaluación o un nuevo ciclo de evaluación, manteniendo trazabilidad del estado anterior.

No se debe sobrescribir silenciosamente el resultado histórico.

## 12. Cancelación y borradores

- `Guardar borrador` conserva los datos introducidos sin ejecutar una decisión.
- `Cancelar` abandona el flujo y conserva trazabilidad solo si la política de almacenamiento lo establece.
- Una evaluación cancelada no debe presentarse como evaluación completada.

## 13. Errores

Los errores técnicos deben distinguirse de `INFORMACIÓN INSUFICIENTE`.

Un error técnico no debe convertirse automáticamente en una decisión de negocio.

El usuario debe recibir una indicación accionable para revisar o reintentar cuando sea posible.

## 14. Frontera STK

Este contrato no autoriza:

- fórmula de `consumption`;
- fórmula de demanda;
- cálculo de cobertura;
- rotación cuantitativa pendiente;
- parámetros de seguridad;
- relación parámetro→regla M01–M10;
- Test_ID;
- integración con el Plan de Pruebas;
- implementación cuantitativa STK.

Los elementos STK sin autoridad deben permanecer en estado de presentación/contexto o no disponible, según el origen del dato, sin inferencia matemática.

## 15. Accesibilidad y UX

- Los estados no dependerán exclusivamente del color.
- Los campos tendrán etiquetas persistentes.
- Los errores deberán asociarse al campo afectado cuando corresponda.
- Las acciones principales serán distinguibles de acciones destructivas o de navegación.
- La navegación por teclado debe ser posible en los controles principales.
- El resultado deberá seguir siendo interpretable sin depender exclusivamente de iconos.

## 16. Estado

**Diseño funcional:** definido.

**Implementación:** no autorizada por este documento.

**STK cuantitativo:** permanece sujeto a la frontera de autoridad M01–M10.
