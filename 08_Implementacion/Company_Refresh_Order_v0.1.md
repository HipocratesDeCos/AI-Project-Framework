# Orden de carga de la empresa seleccionada

La carga del estado de empresa usa una secuencia por actualización y conserva el dataset solicitado antes de esperar la respuesta HTTP. Una respuesta solo puede asignar el estado y continuar hacia la pantalla si su secuencia sigue siendo la última y el dataset sigue seleccionado. Además, el dataset recibido debe coincidir con el solicitado.

Esto evita que una respuesta lenta sustituya una carga posterior, tanto entre empresas distintas como al actualizar varias veces la misma empresa o seguir el recorrido A → B → A. Tras esperar la carga de parámetros se comprueba otra vez la vigencia antes de renderizar el resto de la pantalla.

Comenzar otra actualización invalida inmediatamente las peticiones anteriores de parámetros, retira la configuración en memoria y deshabilita su guardado durante la carga. Se mantienen los controles de secuencia y dataset ya presentes en `loadParameters`.

Los errores de una petición sustituida no sobrescriben el aviso de la actualización actual. Los errores de la petición vigente siguen llegando al manejador habitual, incluidos los de parámetros. No se introduce reintento automático ni se modifican los datos conservados en SQLite.

## Prueba de regresión

`python -m unittest tests.test_company_refresh_order -v`

La prueba ejecuta las funciones JavaScript publicadas en la página con respuestas HTTP controladas. Fuerza respuestas fuera de orden, parámetros antiguos pendientes, A → B → A, actualizaciones simultáneas del mismo dataset, errores antiguos, errores vigentes y una respuesta de estado con dataset incorrecto. Usa Node cuando está disponible y no requiere bibliotecas JavaScript externas ni una base de datos.
