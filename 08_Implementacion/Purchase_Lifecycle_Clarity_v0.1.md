# Ciclo de trabajo de propuestas de compra

Base: rama `feat/purchase-workspace-redesign`, commit `88ff36a`.
Alcance: presentación y coordinación del formulario. No sustituye los motores,
no modifica los contratos de evidencia y no concede autoridad operacional.

## Capacidades conservadas

| Capacidad | Implementación reutilizada | Protección |
|---|---|---|
| Proveedor, artículo y empresa | selección y contexto documental | nueva propuesta conserva la empresa seleccionada |
| Cantidad, planificación y explicación | stock scenario / need | copiar exige revisar supuestos; no se actualiza inventario |
| Dos propuestas y alternativas | negotiation / option studies | analizar no elige; condiciones y calendarios independientes |
| Cuotas y portes | payment plan / installments | validaciones existentes y errores con destino de corrección |
| Guardado y consultas | purchases / guide / study draft | resultados históricos en solo lectura |
| Acuerdo y retirada | agreement | eventos históricos; declaración local, no autorización |

## Estados y acciones

- Nueva propuesta: formulario limpio, sin origen de copia ni cuotas anteriores.
- Borrador en edición: cambios en memoria, sin guardado automático.
- Estudio guardado: consulta de la referencia conservada; no edición del histórico.
- Acuerdo registrado: declaración del usuario vinculada al estudio, separada de
  su guardado. No se verifica automáticamente el soporte ni se envía un pedido.

La barra de acciones permite empezar desde cero, retomar el formulario de trabajo,
consultar los estudios y crear una versión desde un estudio. Descartar un borrador
requiere confirmación de interfaz; cancelar conserva sus datos. Crear una versión
usa el servicio de copia existente y no sobrescribe el estudio de origen.

La elegibilidad de la elección procede de una comprobación común de la opción y
sus condiciones actuales. Un visto significa datos preparados para ese paso,
no aprobación empresarial. El guardado mantiene la validación del servidor.
Los errores del calendario del paso 4 se muestran en ese mismo paso.

## Verificación

Prueba de navegador: retomar sin perder cambios, cancelar descarte, reiniciar sin
arrastrar cuotas ni procedencia, copiar estudio, consultar listado, no modificar
estudios anteriores, ausencia de errores JavaScript y límites visuales en móvil.
Regresión: comparación de ambas propuestas, calendarios, guardado y planificación.
El aislamiento de los datos persistentes sigue siendo responsabilidad de los
servicios existentes, cubiertos por sus pruebas de contexto y empresa.
