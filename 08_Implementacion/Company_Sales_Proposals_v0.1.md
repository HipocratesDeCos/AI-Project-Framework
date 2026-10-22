# Propuestas de venta v0.1

Primera versión para preparar ofertas sintéticas desde la empresa y versión documental activa. El menú lateral distingue Propuestas de compra y Propuestas de venta; Ventas continúa mostrando facturas históricas.

## Pantalla y datos

El formulario selecciona un cliente y entre 1 y 30 líneas del catálogo, con cantidad, precio antes de descuento, descuento porcentual e IVA explícitos por línea. Añade referencia única por versión, fecha, vigencia, entrega, lugar, cobro previsto, condiciones de cobro y portes facturados al cliente con IVA explícito. Fechas visibles DD/MM/AAAA, importes españoles y moneda EUR. No se deduce IVA de históricos ni se configura una política comercial implícita.

`Calcular oferta` calcula sin guardar; `Guardar propuesta de venta` conserva una oferta completa. Los cálculos monetarios utilizan Decimal, redondeo por línea a céntimos ROUND_HALF_EVEN y el calculador comercial existente. Base e IVA incluyen los portes facturados. El precio de cada línea es anterior al descuento porcentual; no se aplica un segundo descuento global.

## Referencias internas

Se reutiliza `documented_sales`: ventas documentadas emitidas hasta el corte, cliente y SKU exactos, misma unidad y EUR coherente en cabecera y línea. El precio histórico neto se calcula con neto/cantidad positiva; no se toma un precio antes de descuento como precio neto. Las líneas del día más reciente se muestran juntas; no se escoge arbitrariamente una como último precio único.

`purchase_history` aporta compras comparables del proveedor de catálogo, en la misma unidad y EUR. Una única referencia del último día permite calcular margen por línea sobre esa compra histórica: `(neto de venta - cantidad × coste unitario de referencia) / neto de venta × 100`. Varias referencias en el último día, ausencia de coste o neto cero producen margen no calculable. Este margen excluye portes y otros costes y no equivale al margen sobre coste completo ni a una recomendación de precio.

El inventario conserva cantidad física, reservada, disponible, unidad, fecha y naturaleza sintética. Una unidad distinta no se convierte implícitamente. Se avisa si la cantidad agregada por SKU supera el disponible de referencia o falta inventario comparable. Las facturas históricas no se utilizan para deducir stock.

## Persistencia y documento para el cliente

`manual_sales_proposal` conserva identificador, dataset, referencia, fecha de guardado y payload completo. Se guarda cliente, empresa, líneas, condiciones, cálculos y referencias internas, además de la huella del contexto documental. Se comprueba dicha huella con bloqueo de escritura antes de insertar; no se admiten referencias repetidas en el mismo dataset. No hay edición silenciosa: una nueva oferta usa otra referencia.

La primera versión exige naturaleza documental SYNTHETIC y mantiene decision_authority=false y operational_path=FORBIDDEN. Guardar no crea factura, reserva stock, registra un cobro ni modifica propuestas de compra. Los archivos recibidos sin admisión no se mezclan con la empresa activa.

El documento se descarga como HTML imprimible mediante el diálogo de impresión/Guardar PDF del navegador. Usa exclusivamente la oferta guardada, escapa textos y excluye márgenes, compras históricas, inventario, advertencias internas y contexto documental. Está identificado como prueba sintética; no acredita aceptación comercial. El acceso exige dataset e identificador exactos. Los nuevos endpoints POST mantienen el control de Host, token y tamaño del servidor existente.

## Validación

Cinco pruebas nuevas verifican cálculos de varias líneas, margen, persistencia, aislamiento por versión, referencias duplicadas, datos inválidos, comparabilidad, conservación de históricos e inventario, informe congelado y exclusión/escape de datos internos. Suite completa: 2732 pruebas correctas. Sintaxis del JavaScript completo comprobada con Node.

Recorrido DOM/HTTP con SQLite desechable: menú, referencias de cliente y artículo, cálculo sin escritura, guardado, descarga del documento y limpieza del formulario. La inspección visual queda pendiente: la descarga del navegador de pruebas devolvió archivos inválidos. No se modificó la base del usuario.

## Puesto de negociación comercial

La oferta se organiza en dos columnas: formulario a la izquierda y apoyo al comercial a la derecha. En pantallas inferiores a 1100 px, el apoyo aparece debajo. Por artículo se muestran unidad, descripción, coste de compra comparable, precio orientativo de origen, objetivo, descuento orientativo máximo antes de otros costes, inventario y últimas ventas comparables. Tras calcular se muestran también precio negociado, descuento y margen de mercancía de cada línea.

El origen se calcula con `coste histórico / (1 - margen objetivo / 100)`, redondeado hacia arriba al céntimo, únicamente si existe una referencia de coste única y un P-MGE-002 explícitamente preparado para la empresa. No se aplica el estándar del catálogo por defecto. P-MGE-001 determina el umbral orientativo de margen y el descuento de referencia, redondeado hacia abajo. Un objetivo inferior al mínimo no produce precio de origen. El botón de configuración lleva a Parámetros. Estos usos sirven a la simulación comercial y no activan Rules/MGE ni acreditan una tarifa aprobada.

Cambiar el precio negociado no cambia el origen. Usar el precio de origen es una acción explícita que elimina el descuento previo. Una modificación de parámetros actualiza las referencias al recalcular sin sobrescribir automáticamente el precio del comercial. La revisión de parámetros se comprueba al calcular y de nuevo antes de guardar.

### Costes y merchandising

El comercial declara el coste logístico previsto de la empresa y, opcionalmente, descripción y coste total del posible regalo. Los portes facturados al cliente son ingresos y se mantienen separados del coste logístico. El margen conjunto incorpora el coste histórico de mercancía, logística y regalo. Si faltan logística o referencias de coste, no se fabrica un margen. El presupuesto para regalo conserva el margen mínimo sobre los ingresos netos; no es una autorización de gasto.

El merchandising sigue siendo una opción interna, sin inferir inventario de regalos, tratamiento fiscal ni compromiso con el cliente. Se excluye del documento comercial. El margen calculado puede omitir costes de estructura, financiación u otros no declarados; no equivale al beneficio final.

### Alternativas condicionadas

Cuando hay costes comparables y margen mínimo explícito, se presentan tres tarjetas:

1. Mantener el objetivo de origen, considerando las concesiones declaradas; proponer anticipo si aparece un indicio documental de tensión. Sin objetivo configurado, esta tarjeta queda pendiente.
2. Reducir concesiones: sin regalo, repercutir el coste logístico al cliente y proponer cobro en la entrega, recalculando precios netos para el mínimo declarado.
3. Mantener el posible regalo, incluir portes en el precio y proponer cobro íntegro anticipado, recalculando precios para el mínimo declarado.

Los importes netos se distribuyen proporcionalmente al valor negociado de las líneas y se redondean hacia arriba; una base negociada nula impide proponer precios de línea mediante esa distribución. Se comprueba el margen conjunto resultante, no el cumplimiento de todas las reglas de cada artículo. Las tarjetas incluyen texto de apoyo para hablar con el cliente. Trasladar una opción al formulario requiere pulsar su botón: actualiza precios netos, elimina descuentos anteriores, cambia cobro/portes y retira el regalo si corresponde. Exige recalcular el IVA y los totales antes de guardar.

### Balance y vencimientos

Se enlaza `financial_context` de la misma empresa y corte. El panel muestra tesorería y fondo de maniobra, además de las sumas de pagos/cobros documentados posteriores al corte y anteriores al cobro negociado. Un fondo de maniobra negativo o pagos agregados superiores a tesorería más cobros declarados genera un indicio para proponer cobro anticipado. Esto no detecta todos los déficits intermedios: las sumas no son una proyección diaria ni acreditan el saldo actual. Fechas/importes/monedas ausentes dejan sumas parciales y aviso.

Se conservan los datos financieros, sus fuentes, huella, estado de evidencia y valores de margen utilizados junto a cada oferta. No se añade el cobro de la oferta a los movimientos documentados, evitando una incorporación sin conciliación o duplicada. No se modifica el motor Finance Basic ni se utiliza una compra ficticia para ejecutar ventas. Calidad, conciliación, completitud, crédito, costes completos y efecto financiero de la venta siguen pendientes; ninguna tarjeta se etiqueta como venta viable o autorizada. `decision_authority=false`, `operational_path=FORBIDDEN` y `viability_status=NOT_EVALUATED` permanecen vigentes.

Validación adicional: seis pruebas de origen estable, descuentos conservadores, margen, costes y regalos, datos financieros, cambio de condiciones ante fondo negativo, ausencia de datos, revisión de parámetros e historial privado congelado. Suite completa: 2738 pruebas correctas, más comprobación focal y sintaxis tras el ajuste de redondeo. Recorrido DOM/HTTP con SQLite desechable: panel derecho, origen, balance, tres opciones, traslado explícito, recálculo, guardado, descarga y limpieza. La inspección visual continúa pendiente por la indisponibilidad del navegador de pruebas.
