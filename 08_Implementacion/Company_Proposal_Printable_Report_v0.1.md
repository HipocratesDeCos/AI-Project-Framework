# Informe imprimible de propuesta v0.1

## Alcance
Botón «Generar informe imprimible» en la revisión de una propuesta guardada. Abre una vista HTML independiente con estilos A4 y botón «Imprimir / Guardar como PDF». El PDF se genera mediante el diálogo del navegador: no se incorpora un conversor PDF de servidor ni se envía correo.

## Fuente y conservación
POST /api/purchases/report requiere el token de sesión existente y dataset_id, proposal_id, review_id. Busca la revisión persistida por las tres identidades; no calcula una nueva revisión, no consulta fuentes actuales y no modifica la propuesta. Una revisión histórica puede exportarse aunque el contexto documental actual haya cambiado. Eso no permite reevaluar la propuesta con contenido cambiado. La revisión y su fecha permanecen identificadas.

## Contenido
Identidad de empresa y versión, corte y fechas, artículo y proveedor identificados por código, cantidades y unidad, importes e IVA declarados, descuentos y portes, referencia de precio histórico cuando es comparable, inventario y cobertura de referencia, mínimo conservado al guardar, evaluación financiera pendiente, comprobaciones pendientes y fuentes con metadatos conservados. Las propuestas antiguas sin captura permanecen expresamente sin captura. No se fabrica nombre de artículo o proveedor que no conste en la revisión.

La relación de fuentes identifica el conjunto vinculado; no atribuye intervención en cálculos a todas ellas. Las huellas no acreditan autenticidad ni admisión. Rotación, necesidad y cantidad recomendada permanecen pendientes. No registra decisión humana ni genera aceptación al proveedor. La ruta operacional sigue FORBIDDEN.

## Presentación
Bloques esquemáticos, dos columnas de datos, contraste de estado y tablas con encabezado repetido al imprimir. El control de impresión queda oculto en papel. Los valores y metadatos se escapan como texto; no hay imágenes, fuentes ni servicios externos.

## Validación
Pruebas de secciones y pendientes, escape de contenido, estabilidad tras modificación de fuentes actuales, aislamiento entre empresas/propuestas/revisiones, captura antigua ausente, sintaxis JavaScript mediante Node cuando está instalado y recorrido HTTP real con token y respuesta HTML. El entorno local estaba desconectado: ejecución Python/SQL mediante CI de GitHub. La comprobación visual de paginación con navegador e impresora queda pendiente; CI no equivale a esa comprobación.
