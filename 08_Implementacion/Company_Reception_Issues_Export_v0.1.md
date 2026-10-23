# Descargar incidencias de una carga

Después de **Comprobar datos**, el botón **Descargar incidencias completas (.csv)** se habilita si hay errores o avisos. La pantalla conserva su muestra de hasta 100 errores y 100 avisos; el CSV incluye todas las incidencias obtenidas en esa comprobación, dentro de los límites del lector ordinario.

El informe contiene tipo (ERROR o AVISO), archivo, hoja, fila original, código y razón social de la empresa, naturaleza real o sintética, fecha de corte en DD/MM/AAAA, contenido declarado, formato numérico seleccionado, mensaje y huella del origen. Agrupa todos los mensajes de error de una fila en una celda; cada aviso ocupa su propia fila. Una misma fila puede tener errores y avisos. Si un aviso no tiene fila de origen —por ejemplo, un PDF conservado como soporte— la deja vacía. Las filas respetan la posición de la cabecera y la hoja leída, sin renumerar los registros válidos.

El CSV usa UTF-8 con BOM y punto y coma como separador, para abrirlo o importarlo en Excel/Google Sheets. Los textos que podrían interpretarse como fórmulas se escapan únicamente en el informe. Los documentos y códigos originales no se modifican.

## Recorrido de corrección

1. Lee el archivo, revisa empresa, corte, contenido, asignación de columnas y formato numérico.
2. Pulsa **Comprobar datos** y descarga el informe si hay incidencias.
3. Filtra por ERROR/AVISO y consulta las filas indicadas en el archivo original. Un error impide guardar; un aviso requiere revisión, pero no impide por sí solo la recepción.
4. Corrige el archivo original. El informe es una guía de revisión, no una plantilla para volver a cargar.
5. Vuelve a leer el original corregido y comprueba sus datos de nuevo antes de guardar.

La descarga corresponde a la última comprobación del archivo en memoria. Cambiar archivo o iniciar otra comprobación invalida el informe anterior; en la pantalla también se invalida al editar empresa, corte, tipo, formato o columnas. Caduca con la lectura/comprobación a los diez minutos y se contrasta la huella del contenido antes de exportar. No consume el permiso de guardar de una comprobación con avisos ni introduce identificadores temporales en los registros o huellas persistidos.

La descarga es de solo lectura y funciona aunque los errores impidan guardar o todavía no exista la base de datos de recepción. No corrige, carga ni activa registros. No incluye errores de lectura que impiden interpretar el archivo ni sustituye las comprobaciones posteriores de referencias entre documentos, cuotas, suficiencia financiera o admisión. Se mantienen `decision_authority=false` y `operational_path=FORBIDDEN`.
