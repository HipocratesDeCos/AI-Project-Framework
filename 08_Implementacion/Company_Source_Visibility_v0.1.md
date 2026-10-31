# Identificación visible del expediente consultado

## Expedientes recibidos

La tabla incluye Estado de uso. Los lotes que pertenecen a un Excel activado aparecen como **ACTIVO · EN USO**, con identificador de versión y corte. Los demás se indican como **RECIBIDO · SIN ACTIVAR COMO EXPEDIENTE**. Recibir un archivo o marcar su casilla de revisión no lo activa. La marca describe la selección del expediente, no su validación financiera.

Un recuadro independiente identifica el expediente utilizado para propuestas por la empresa seleccionada en el selector principal; filtrar el listado de recepciones no cambia esa empresa ni su versión de trabajo. Después de activar un libro se actualizan también las marcas del listado.

## Propuesta de venta

Antes del formulario se muestra un recuadro permanente con estado, empresa, nombre completo del archivo, fecha de corte e identificador de versión. El nombre conserva la versión que el usuario haya incluido en él. El identificador distingue también archivos con el mismo nombre pero bytes diferentes. La recepción conserva además un nombre o unos bytes nuevos aunque las filas normalizadas coincidan: no descarta la versión indicada por el usuario. Repetir exactamente la misma recepción sigue siendo idempotente.

Los estados diferencian Excel activo, histórico de solo consulta, libro no activado y expediente documental base sin Excel exclusivo. No se presenta una versión base como si fuera el último Excel recibido.

La última evaluación muestra además la identidad documental que devolvió el servidor, capturada en la propia propuesta. No se obtiene del nombre de la selección actual. Al modificar condiciones o cambiar de empresa/versión se retira esa identificación de evaluación junto con el resultado invalidado. Durante la recarga se muestra Actualizando, sin conservar una etiqueta de uso anterior.

El informe imprimible conserva archivo, corte e identificador de la versión que consta en la propuesta guardada; no consulta el expediente activo posterior para etiquetar una oferta histórica.

## Verificación

Pruebas de estados base/activo/histórico, marcado de recepciones, cambio de bytes con el mismo nombre y procedencia del informe. Recorrido HTTP y DOM de activación, marcas en tabla, identidad del formulario, invalidación y cambio de versión. Se conservan las fronteras de evidencia y autoridad existentes.
