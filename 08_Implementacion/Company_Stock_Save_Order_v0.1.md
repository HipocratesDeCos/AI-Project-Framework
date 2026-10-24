# Guardado de mínimos vinculado al estado de origen

El guardado conserva el dataset, la referencia al estado en memoria y la secuencia de actualización de empresa que lo iniciaron. Tras cada respuesta HTTP se comprueba que los tres siguen vigentes antes de solicitar o aplicar la recarga. La respuesta recargada también debe identificar el dataset solicitado.

Una respuesta o error de una operación sustituida no cambia la pantalla actual. Esto cubre cambiar de empresa, volver a la misma empresa y actualizar el mismo dataset mientras el guardado o su lectura posterior siguen pendientes. No cancela escrituras que el servidor ya haya aceptado; la modificación permanece en la empresa a la que se envió y se consulta al volver a cargar sus datos.

Mientras una operación vigente guarda, se bloquean «Guardar mínimos» y las casillas de la tabla. El bloqueo se aplica también a las filas reconstruidas al filtrar o cambiar de página. Finalizar una operación anterior no desbloquea otra operación más reciente. Al fallar la vigente se conservan los borradores y se habilitan de nuevo los controles actuales.

Se mantienen validación de casillas visibles, recogida de borradores fuera de página, límite de 100 cambios y comprobaciones del servidor por unidad/revisión. Se comparan valores como texto para evitar considerar cambiado un cero numérico frente a la casilla `"0"`. No se cambian los cálculos ni las reglas de mínimos.

## Regresión

`python -m unittest tests.test_company_stock_save_order -v`

La prueba ejecuta el manejador real con respuestas controladas: recogida de borrador oculto, cero sin cambio, bloqueo y doble clic, operaciones superpuestas entre empresas, lectura retrasada tras actualización, A → B → A, errores vigentes/obsoletos, respuesta con dataset incorrecto, ausencia de cambios y límite de 100. No requiere SQLite ni bibliotecas JavaScript externas; usa Node cuando está disponible.

La comprobación DOM del JavaScript completo verifica además el bloqueo de casillas reconstruidas en otra página y la recuperación de los controles. Se mantienen las pruebas Python existentes de mínimos, métricas, CSV y actualización de empresa.
