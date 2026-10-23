# Reconocimiento de plantillas en Carga de archivos

## Comportamiento

Al pulsar **Leer archivo**, la recepción propone el contenido de una plantilla ordinaria de EIOS cuando sus cabeceras corresponden de forma completa y única a un contrato de columnas. Admite claves técnicas y etiquetas de campo, otro orden, mayúsculas, acentos, espacios y separadores. Reconoce las once plantillas ordinarias: proveedores, clientes, artículos, inventario, parámetros de stock, compras históricas, ventas históricas, vencimientos de venta, tarifas, previsiones y saldos. También reconoce las columnas del CSV de cobros preparados como una previsión.

La propuesta no usa el nombre del archivo, valores de las filas, saldos o importes para adivinar el contenido. Si faltan cabeceras, hay columnas adicionales o la identificación no es única, se mantiene la selección manual del tipo y se ofrecen únicamente coincidencias explícitas por nombre para sus campos. Las cabeceras repetidas o varias cabeceras equivalentes al mismo campo quedan sin asignar. Tampoco se propone una misma columna para dos campos.

Se conserva la identificación anterior de la tarifa específica descargable, que permite sus columnas de consulta adicionales. El catálogo comercial sigue usando su apartado dedicado y el PDF sigue siendo soporte sin extracción automática de cifras.

## Revisión visible

En **Relacionar columnas**, el resumen indica campos asignados y obligatorios pendientes. Al editar una asignación avisa si una columna está utilizada más de una vez y descarta la comprobación previa. Cambiar el contenido vuelve a proponer las coincidencias de ese tipo; las asignaciones pueden corregirse manualmente antes de comprobar.

El usuario debe revisar empresa, naturaleza, corte, hoja, formato numérico y los datos. No se infiere el formato numérico ni se dan por correctos los valores por reconocer las cabeceras. **Comprobar datos** sigue siendo obligatorio antes de **Guardar** y el servidor sigue validando campos obligatorios, columnas distintas, códigos de texto, fechas, importes y demás controles de recepción.

Leer o reconocer un archivo no escribe registros ni selecciona referencias comerciales activas. Guardar mantiene la recepción pendiente de admisión, `decision_authority=false` y `operational_path=FORBIDDEN`. Las selecciones de catálogo, inventario e históricos conservan sus confirmaciones separadas.
