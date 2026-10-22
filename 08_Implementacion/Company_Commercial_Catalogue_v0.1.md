# Catálogo comercial seleccionado para una empresa ficticia

## Uso desde Carga de archivos

La sección **CATÁLOGO COMERCIAL · EMPRESA ACTIVA** conecta un catálogo XLSX/CSV con las fichas que se utilizan en Propuestas de compra y Propuestas de venta. Se selecciona primero la empresa activa en el selector superior. No utiliza ni activa por sí sola los expedientes ordinarios recibidos.

1. Seleccionar el archivo, hoja de Excel si no es la primera y formato numérico de textos.
2. Confirmar expresamente naturaleza ficticia, venta por unidades y coste/PVP por unidad en EUR sin IVA. La confirmación es una declaración del usuario, no una extracción del archivo.
3. Pulsar **Comprobar catálogo y ver cambios**. No escribe datos persistentes. Revisar altas, coincidencias de SKU, bajas excluidas, PVP pendientes, errores y muestra con filas de origen.
4. Indicar responsable y motivo. Pulsar **Incorporar catálogo a las propuestas**. Se conservan los bytes originales y una revisión append-only ligada a la versión documental exacta. Se refrescan la empresa y los selectores.
5. Seleccionar cliente y artículo en Propuestas de venta. El coste/PVP y la fuente aparecen en Ficha e historial. La última compra comparable mantiene prioridad como coste; en su ausencia puede usarse el coste del catálogo como referencia expresamente diferenciada. No se crean compras para simular un coste histórico.
6. Para deshacer la selección, indicar responsable y motivo y pulsar **Retirar el catálogo seleccionado**. No borra el archivo ni las propuestas ya guardadas. Estas conservan sus valores y su contexto; las revisiones posteriores detectan el cambio de contexto.

## Contrato y límites

Cabeceras únicas esperadas: `sku`, `descripcion`, `proveedor`, `coste`, `precio_pvp_recomendado`, `estado_baja`, `subfama`. Se comparan sin distinguir mayúsculas y quitando espacios exteriores. La API también permite un mapeo explícito por índice, aunque esta primera pantalla utiliza las cabeceras anteriores. Hoja con cabecera en fila 1; CSV con detección de separador y UTF-8. Un libro puede tener otras columnas: permanecen en los bytes originales, sin activarse.

Hasta 20.000 filas y 10 MiB, manteniendo los controles existentes de XLSX, XML, macros, dimensiones y 80 columnas. La recepción ordinaria conserva su límite de 5.000 filas. SKU textual de hasta 64 caracteres, único tras quitar espacios exteriores; descripción y nombre de proveedor obligatorios. Coste fijo no negativo y finito. PVP fijo no negativo, o pendiente si está vacío, contiene fórmula o error. No se ejecutan fórmulas ni se admiten sus resultados en caché. No se recalcula ni valida la columna de margen o los códigos de IVA del origen. El margen comercial se calcula con las referencias mostradas y los parámetros preparados.

`estado_baja` admite True/False o 1/0. Las bajas se excluyen de la incorporación; no se eliminan fichas originales, aunque el archivo marque una de ellas de baja. Un SKU existente solo admite unidad exacta `uds.` en esta ruta, conserva identidad, descripción y proveedor originales, y recibe referencias comerciales de catálogo. No se convierten palets, litros ni cajas ni se unen productos por descripción.

Los nombres de proveedores generan códigos propuestos estables por empresa y nombre exacto. No se atribuye NIF ni se unen automáticamente a proveedores históricos por parecido de nombre. Se conserva su condición de identificación solo por nombre de catálogo. Un archivo seleccionado sustituye a la selección comercial anterior completa; no acumula automáticamente las altas de todas las revisiones. Las fichas documentales originales siempre se conservan. Repetir los mismos bytes y registros seleccionados es idempotente.

No hay fecha de catálogo ni vigencia acreditada en este archivo. Se expone esa ausencia y no se utiliza el corte financiero como fecha del catálogo. Los PVP fijos son referencias para la simulación; no equivalen a una tarifa vigente validada. Una tarifa ya seleccionada conserva la lógica de prioridad/vigencia existente. Para corregir PVP con fórmulas, preparar una copia de origen con valores fijos revisados y repetir vista previa/selección; el archivo original permanece intacto.

## Persistencia y alcance

`company_commercial_catalogue` conserva por dataset y revisión: metadatos, responsable, motivo, fecha de selección, registros normalizados, huellas y bytes originales. La capa de pantalla combina temporalmente esas referencias con el catálogo documental; no reescribe `documentary_company_record`, `documentary_source` ni el manifiesto. El contexto de propuestas incluye la huella de la selección comercial y de su contenido. Una selección o retirada invalida vistas previas antiguas. Los tickets son aleatorios, de un uso y caducan a los diez minutos. Se comprueba integridad al consultar; no se convierte en admisión ni evidencia operacional.

No se modifican inventario, planificación, balances, previsiones, cuotas, compras ni ventas. Los artículos nuevos muestran existencias desconocidas, no cero, sin cobertura ni rotación inventadas. Se pueden declarar mínimos manuales; sin compra histórica comparable no se genera el mínimo automático del 10 %. La tabla Stock muestra hasta 100 filas por página, con filtros y ordenación sobre el catálogo completo, y conserva borradores de mínimos al cambiar de página. Guarda hasta 100 cambios de mínimos por operación.

La consulta de los expedientes recibidos ordinarios, sus versiones, la integración general de otras empresas y la admisión operacional siguen siendo circuitos distintos. Esta implementación cierra el recorrido concreto de un catálogo comercial ficticio seleccionado hacia las propuestas de una empresa documental activa. No importa balance, tesorería o inventario desde este catálogo.

## Comprobación con el archivo aportado

En una copia de A Monkey, `stock_MITG(1).xlsx`, hoja `articulos`, contiene 11.706 SKU únicos: 11.703 activos y tres bajas; 114 nombres de proveedor. No coincide ningún SKU activo con los 18 artículos documentales originales. Tras seleccionar: 11.721 fichas de artículo y 120 registros de proveedor (seis originales más 114 identificaciones propuestas por nombre; no acredita 120 entidades fiscales distintas). 286 PVP permanecen pendientes por fórmula. No se incorporan cantidades de stock.

Ejemplo comprobado: ADV-050001, coste de catálogo 44 EUR/unidad, PVP fijo 88 EUR/unidad, margen sobre venta 50 %. Orientación sin última compra ni inventario comparables. Todos los registros documentales y bytes de soporte permanecieron iguales antes/después. La retirada devolvió los 18 artículos originales y los mismos inventarios.

Validación: cinco pruebas nuevas de vista previa, selección, orientación y evaluación de oferta, retirada, idempotencia, concurrencia, SKU duplicados, incompatibilidad de unidad, preservación de proveedor/coste histórico, fórmula pendiente e integridad. Recorrido DOM/HTTP con el Excel completo: confirmación, conteos, selección, autocompletado coste/PVP, inventario desconocido, paginación/búsqueda de Stock y retirada. Comprobación de sintaxis JavaScript y de cambios. La inspección visual en navegador queda pendiente.
