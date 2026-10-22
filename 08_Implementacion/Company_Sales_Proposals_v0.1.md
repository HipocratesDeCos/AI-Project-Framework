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

## Plan explícito de cobros y pagos

Cada oferta guardada dispone de `Plan de cobros y pagos`. El formulario permite hasta treinta movimientos, con tipo, importe de caja con impuestos, vencimiento, concepto y clasificación como nuevo o ya documentado. Los cobros deben sumar exactamente el total con IVA de la oferta. El cobro único sugerido al abrir un plan es una propuesta editable, no una evidencia de vencimiento. Se requiere responsable declarado y confirmación explícita antes de guardar.

Los pagos de logística, merchandising u otros costes se declaran con su importe bruto y fecha, sin convertir automáticamente costes netos en salidas de caja. El inventario de costes permanece de completitud no establecida. Todos los movimientos del plan deben ser posteriores al corte y no anteriores a la fecha de oferta.

Un movimiento ya documentado exige coincidencia exacta de tipo, moneda, importe y vencimiento. Conserva las referencias de origen y se reutiliza sin añadir otro flujo. No puede aparecer dos veces en el mismo plan ni vincularse al plan vigente de otra oferta del mismo dataset. Eliminarlo de una revisión posterior libera la vinculación; el historial anterior permanece conservado. Si una declaración nueva coincide con la previsión, se exige vincularla o confirmar expresamente que es otro movimiento y explicarlo en el concepto; se conservan las identidades coincidentes y dicha declaración. Esto no acredita la distinción ni eleva evidencia.

`company_sales_cash_plan` conserva revisiones sucesivas, huella canónica, huella de oferta, filas, fuentes, contexto financiero, responsable y ejecución. Se rechazan revisiones concurrentes, cambios de documentación y ofertas de otra versión. Una oferta con contexto anterior permite consultar el plan congelado; requiere una oferta nueva para modificar el plan con documentación actual.

### Ejecución financiera conservada

Se utiliza `run_provenanced_finance_basic` con los contratos existentes, sin crear una compra ficticia. Horizonte P-FIN-001 y tesorería mínima P-FIN-002 se obtienen del Centro real para la empresa y corte y se conserva su versión. Se calcula una ejecución con los movimientos documentados y otra incorporando únicamente declaraciones nuevas. Los movimientos asociados ya documentados no se duplican.

Las declaraciones nuevas se convierten en CashFlow NOT_EVIDENCED, con fecha no evidenciada y referencia de declaración local. Los movimientos documentados conservan su estado original. El motor no publica capacidad ni puntos cuando su resultado no es determinable; las fechas futuras no sirven para fabricar evidencia de exclusión del horizonte. Sin activación de parámetros se conserva el plan y se indica ejecución pendiente, sin inventar valores.

Este paso no crea facturas, movimientos en el libro de tesorería, aceptación, conciliación o admisión de venta. La clasificación de asociación es una declaración local. No se acredita identidad del declarante, completitud de costes, QTG, crédito ni viabilidad; decision_authority=false y operational_path=FORBIDDEN. El documento para el cliente continúa excluyendo el plan interno.

Validación: ocho pruebas específicas de cuotas/IVA, pagos explícitos, motor y horizonte activado, ausencia de parámetros, conservación de evidencia, coincidencias, reutilización de cobros/pagos, exclusión de doble vinculación, historial, documentación cambiada e integridad. Suite general previa al último caso: 2745 correctas; comprobación focal posterior correcta. Recorrido DOM/HTTP: abrir plan de oferta guardada, guardar cobro, observar evidencia pendiente, añadir un pago, guardar revisión y limpiar al cambiar contexto. La inspección visual continúa pendiente.

## Corrección del flujo de negociación: referencia → propuesta de pedido → evaluación

El formulario es la Propuesta de pedido. Seleccionar artículo carga las referencias de coste, precio recomendado y margen; cliente y artículo determinan el historial comparable. El precio neto anterior del cliente se copia por defecto con descuento adicional cero. Si hay varios precios distintos en la última fecha se requiere elegir una referencia del historial completo; no se escoge una factura arbitrariamente. Sin historial único se usa el precio recomendado disponible, sin rellenar precios ausentes. Puede consultarse el artículo sin seleccionar aún cliente.

Un `recommended_sale_price` con `sale_currency=EUR` documentado en el catálogo tiene prioridad absoluta sobre el cálculo orientativo anterior. Dicho cálculo se conserva solo como referencia identificada cuando no hay PVP mapeado. La copia local inspeccionada de A Monkey contiene costes históricos, pero no este campo documental; además, sus líneas de venta contienen `article_id=None` y unidades ausentes. Se señala la ausencia de vínculo y no se identifican artículos por parecido de descripción. Hace falta un vínculo documentado de SKU/unidad y de tarifa para autorrellenar esos datos en ese expediente concreto.

La propuesta registra quién la plantea (comercial/cliente), motivo (inicial, precio, stock del cliente, pago u otro) y explicación. Se mantiene la referencia de origen al editar el precio negociado. El botón Evaluar propuesta de pedido ejecuta comprobaciones comerciales explícitas; guardar conserva el borrador y sus comprobaciones sin aceptar un pedido.

Las comprobaciones contrastan el margen porcentual exacto sin ocultar incumplimientos por redondeo, el mínimo absoluto cuando está configurado, los costes comparables, el cobro aplazado ante saldos vencidos documentados y el indicio de fondo de maniobra negativo. Las cuotas se vinculan a facturas elegibles de ese cliente y corte. Se considera una fecha revisada expresamente documentada cuando existe; una cuota futura pendiente no se convierte en impago. Se conserva la diferencia entre saldo vencido al corte e historial de impagos verificado. Ausencia de cuotas no acredita buen comportamiento.

Las alternativas aparecen después de detectar una propuesta no apropiada, no como ofertas precalculadas por defecto. Sus precios respetan también el mínimo absoluto; ante vencidos o fondo negativo se evita proponer aplazamiento. Son alternativas condicionadas, pendientes de calidad, crédito, costes completos y efecto financiero. Una declaración de stock del cliente solicita confirmar necesidad/cantidad/fecha, sin inventar su inventario ni su demanda.

### Protocolo existente revisado

Se revisaron `05_Motor/Negotiation_Intelligence.md`, `05_Motor/Negotiation_Ladder.md`, ambos contratos de implementación y `08_Implementacion/Negotiation_C0_Trace_Binding_Contract_v0.1.md`. NI determina contenido justificado; Ladder representa y ordena; ninguna aprueba ni determina viabilidad. Los vinculadores físicos revisados exigen contexto y trazas C0 de una compra. Esta corrección no fabrica una compra, un escenario formal, una traza C0 ni una autorización para una venta. La interfaz conserva referencias al protocolo y muestra `SALES_BINDING_PENDING`. Las comprobaciones comerciales son un prechequeo declarado, no una ejecución de Rules/NI/Ladder ni un resultado del decisor. La aceptación automática permanece deshabilitada incluso si no se detectan incumplimientos.

Pruebas añadidas: selección y precio anterior, prioridad del PVP documental, historial ambiguo, vencidos sin financiación nueva, fechas revisadas, crédito desconocido, motivo y autor de la propuesta, mínimo absoluto y redondeo del margen. Recorrido DOM/HTTP: autorrellenado del precio neto, historial, referencia de origen, evaluación explícita, ausencia de alternativas antes de resultado adverso, contraoferta, alternativas, traslado, recálculo y guardado. Suite general inicial 2753 correctas y comprobación focal posterior; inspección visual pendiente.

## Corrección de usabilidad y respuestas asíncronas

La pantalla separa cliente/artículos, condiciones negociadas, evaluación y documento final. Referencia, vigencia, entrega y datos fiscales pueden quedar pendientes durante el prechequeo comercial; guardar exige completarlos. Un IVA ausente se conserva como desconocido: ni el impuesto ni el total se presentan como cero. Un IVA cero expresamente declarado sigue siendo válido. No se exige clasificación fiscal de portes cuando no existe cargo. Las fechas iniciales y el contado son propuestas visibles, no condiciones documentadas del cliente.

La logística distingue pendiente, declaración expresa de ausencia de coste y coste previsto. Las alternativas sin fecha de cobro determinada no pueden trasladarse al formulario. Cada cambio invalida la evaluación y bloquea guardar hasta recalcular; añadir o quitar artículos también lo hace. Una consulta de ficha pendiente bloquea evaluar. Las respuestas antiguas se descartan y una referencia recibida después de una edición manual no sobrescribe el precio negociado.

Validación: seis pruebas nuevas de evaluación parcial, impuestos desconocidos/cero, portes, datos opcionales inválidos, alternativas sin entrega inventada y equivalencia al completar y guardar. Suite general: 2761 correctas; comprobación focal posterior de propuestas y previsualización: 11 correctas. Recorrido DOM/HTTP con servidor real y expediente de prueba: precio anterior, evaluación parcial, completar documento, invalidación y consulta retrasada durante edición. JavaScript comprobado sintácticamente. La inspección visual en navegador sigue pendiente. Esta corrección no modifica la autoridad de decisión ni implementa el vinculador de ventas pendiente.

## Vinculación explícita de líneas históricas sin SKU o unidad

En Ficha e historial, el apartado «Vincular una línea histórica con este artículo» permite seleccionar una línea del cliente activo y vincularla al SKU seleccionado. Exige responsable, motivo/referencia y confirmación expresa de que la cantidad histórica se expresa en la unidad de catálogo. Se conserva el documento y la fila originales. No se infiere correspondencia por texto, precio o parecido. Un SKU documental distinto o una unidad incompatible bloquean el vínculo.

Los vínculos son declaraciones manuales identificadas como tales, limitadas a la misma versión sintética. Se registran revisiones append-only en `company_sales_line_link`; retirar un vínculo añade una revisión y restaura la lectura original. Los hashes de fuente y catálogo invalidan vínculos si cambian sus contenidos. La huella de contexto incluye estas revisiones, de modo que una pantalla antigua no puede evaluar/guardar con una vinculación desactualizada. Esto no admite material ni activa autoridad operacional.

La consulta comercial utiliza el vínculo activo para recuperar el historial comparable (misma unidad y EUR); el precio anterior se calcula con importe neto/cantidad. Una última fecha ambigua sigue requiriendo elegir una referencia. La orientación conserva actor, motivo, revisión y fuentes; la consulta de facturas advierte de los vínculos manuales. Las propuestas guardadas conservan su instantánea incluso tras retirar el vínculo.

Validación: seis pruebas específicas de recuperación/retirada, conservación de originales y propuestas, rechazo de campos y referencias inválidas, incompatibilidad de SKU/unidad, invalidación por cambio documental y concurrencia de pantallas. Recorrido DOM/HTTP con servidor real: selección de línea, guardado, precio histórico cargado, etiqueta manual, evaluación invalidada y retirada. JavaScript comprobado sintácticamente. Inspección visual pendiente. El PVP documental ausente continúa pendiente de aportar/mapear; este vínculo no lo inventa ni lo sustituye.

## PVP desde tarifas recibidas

Carga de archivos admite «Tarifa de venta: PVP por unidad sin IVA» (`sale_price`) en Excel/CSV. Sus seis campos obligatorios son SKU, unidad, PVP recomendado sin IVA, moneda, vigencia inicial y vigencia final. El mapeo y el formato numérico son explícitos. No se extraen tarifas de PDF ni se calcula un PVP faltante como si fuera documental.

En Ficha e historial, «Seleccionar PVP desde una tarifa» presenta exclusivamente filas de la misma empresa, razón social, naturaleza, corte, SKU, unidad y EUR. El usuario selecciona archivo/fila, indica responsable y motivo y confirma la base unitaria sin IVA. La selección se conserva en `company_sales_tariff` con revisiones append-only y puede retirarse. La referencia muestra archivo, hoja, fila, huella, responsable y vigencia; permanece como tarifa recibida pendiente de admisión, sin autoridad decisional.

El PVP elegido se conserva exactamente. Se comprueba contra la fecha de propuesta tanto en la ficha como al evaluar/guardar. Fuera de vigencia, con fecha ausente o con cambios en archivo/catálogo, no se presenta como un PVP válido ni se sustituye silenciosamente por el cálculo del margen. El historial comparable del cliente sigue teniendo prioridad para iniciar el precio de pedido. El comercial puede trasladar expresamente el PVP a la negociación. Cambiar la fecha actualiza referencias sin sustituir el precio ya editado.

La huella de contexto incluye selección y contenido del archivo recibido. Se rechaza una selección si el archivo cambió desde su consulta. Una propuesta guardada conserva su referencia de tarifa aunque se retire posteriormente. Las tablas originales no se sobrescriben; esta vinculación no activa Rules/NI/Ladder ni transforma la recepción en evidencia admitida.

### Uso

1. En Carga de archivos, identifica exactamente la empresa activa y su corte. Selecciona los datos ficticios para esta prueba.
2. Carga la tabla, elige el contenido Tarifa de venta y relaciona sus seis columnas. Comprueba y guarda.
3. En Propuestas de venta, selecciona artículo y abre Seleccionar PVP desde una tarifa. Si se cargó mientras la ficha estaba abierta, vuelve a seleccionar el artículo para consultar las referencias recibidas.
4. Elige la fila y registra la selección. Revisa la vigencia, el precio anterior del cliente y el margen antes de evaluar.

Ejemplo de cabecera CSV con separador punto y coma (cumplimentar exclusivamente con los datos de la tarifa):

```text
SKU;Unidad;PVP_sin_IVA;Moneda;Valida_desde;Valida_hasta
```

Validación: seis pruebas específicas de precio exacto, margen, precedencia del historial, vigencia, conservación de propuestas, fuente modificada, unidades/monedas/empresas incompatibles, concurrencia y formato. Suite general inicial: 2773 correctas; comprobación focal posterior tras exigir la huella de la fila. Recorrido DOM/HTTP con servidor real: selección, procedencia, PVP, historial, traslado, caducidad sin sobrescribir el precio negociado y retirada. JavaScript comprobado. Inspección visual pendiente.

## Plantilla de tarifa de la empresa activa

El botón «Descargar plantilla de tarifa de esta empresa», en Ficha e historial, descarga un XLSX con SKU, descripción de consulta y unidad del catálogo activo. Los SKU se conservan como texto, incluidos ceros iniciales. PVP y fechas de vigencia permanecen vacíos y sus celdas se resaltan en amarillo. EUR figura como moneda propuesta, que debe confirmarse al cumplimentar la tarifa.

La hoja Tarifa es la primera y contiene cabecera en fila 1. Una segunda hoja identifica empresa, naturaleza y corte y explica cómo completar, eliminar filas que no se vayan a usar y relacionar columnas al cargar el Excel. La descripción sirve únicamente para consulta; no se utiliza para vincular el artículo. La plantilla no modifica datos ni registra una tarifa, precios o aprobaciones. Rechaza catálogos vacíos, SKU repetidos o sin unidad. Si cambia la empresa mientras se genera, el navegador descarta la descarga antigua.

Validación: tres pruebas de conservación de identificadores y ausencia de precios/fórmulas, recorrido Excel cumplimentado → lector real → normalización de tarifa, y rechazo de catálogos incompletos o ambiguos. Nueve pruebas focales correctas incluyendo las seis de tarifas. Recorrido DOM/HTTP: botón, XLSX descargado legible por recepción y descarte al cambiar empresa durante la respuesta. JavaScript comprobado sintácticamente.

## Reconocimiento asistido de columnas de tarifa

Al leer Excel/CSV, la recepción propone el contenido Tarifa de venta y las seis columnas cuando los encabezados de la plantilla, sus nombres técnicos o las etiquetas explícitas de esos campos forman una correspondencia completa y única. Se admiten cambios de orden, mayúsculas y acentos; no se usa parecido de texto ni se interpreta una columna de precio con IVA como precio sin IVA. Una cabecera ambigua o incompleta no genera este perfil; el usuario puede asignar las columnas manualmente.

El formulario muestra que el mapeo es una propuesta pendiente de revisión. No se deduce empresa, corte, moneda, vigencia ni formato numérico a partir de este reconocimiento. Comprobar y guardar siguen siendo acciones expresas. Una edición manual del mapeo invalida el ticket anterior y obliga a comprobar de nuevo. Para los demás contenidos, los encabezados genéricos repetidos dejan de resolverse arbitrariamente por la primera coincidencia.

Validación: 23 pruebas focales correctas, incluidas tres nuevas de reordenación/ambigüedad, plantilla XLSX → recepción → validación, y archivos no compatibles. Recorrido DOM/HTTP con servidor real: lectura, contenido y seis asignaciones propuestos, comprobación, invalidación tras editar una columna y mapeo vacío con SKU duplicado. JavaScript comprobado sintácticamente. La integración anterior #510 y su CI posterior se comprobaron como satisfactorias antes de este cambio.

## Carga expresa por lote de una tarifa ficticia

`python -m eios.company_sales_tariff_load --db RUTA_DB --file RUTA_XLSX --actor "Responsable de prueba"` recibe una tarifa sintética cumplimentada con la hoja Tarifa y los encabezados de EIOS. Cuando hay varias versiones documentales exige `--dataset`. Valida todas las filas antes de recibir el archivo: SKU único por fila, unidad exacta de catálogo, EUR, precio no negativo y fechas válidas. Solo permite la empresa sintética. No interpreta descripciones como SKU.

El archivo se conserva mediante recepción y sus filas se seleccionan con el vinculador de tarifa existente. Las tarifas ya seleccionadas y los PVP explícitos del catálogo se conservan; repetir la carga no añade selecciones para esos artículos. El resultado indica `selected_count`, `preserved_count` y los SKU correspondientes. No registra ventas ni reservas ni activa parámetros de margen. El margen usado para crear una tarifa no se convierte en límite empresarial aprobado.

Cada selección es una revisión independiente append-only. La respuesta del vinculador incluye la huella tras su propia escritura; la carga utiliza esa huella exacta en la siguiente revisión para rechazar cambios concurrentes. La recepción y las selecciones no constituyen una única transacción: ante una interrupción se conserva el archivo y las revisiones ya registradas, se informa del número completado y puede repetirse la carga conservándolas.

### A Monkey: tarifa ficticia al 30 %

Se preparó una tarifa de 18 artículos a partir de sus últimas compras comparables, con margen sobre venta del 30 %: coste / 0,70 y redondeo al céntimo superior. Las fuentes del coste se conservan en la hoja de cálculo de soporte. La vigencia 22/10/2026–31/12/2026 es una hipótesis explícita para la prueba. La hoja Tarifa contiene valores fijos importables; la hoja Calculo conserva el cálculo y las referencias. No se presenta como tarifa original ni como precios de mercado.

Validación: cuatro pruebas nuevas de carga, repetición, conservación, incompatibilidades, versiones/actor explícitos y bloqueo de material real; diez pruebas focales correctas. Suite general inicial: 2783 correctas. Recorrido con una copia de la base de A Monkey: 18 filas seleccionadas, 18 PVP/defaults recuperados y márgenes exactos >=30 %; segunda carga conserva los 18 sin nuevas selecciones. El archivo se calculó, verificó y revisó visualmente. La base original no se modificó durante estas pruebas. Las 24 líneas históricas sin SKU/unidad siguen pendientes de correspondencia expresa.

## Referencias de ventas pendientes de ficha

«Propuestas de venta → Catálogo ampliado» presenta las fichas actuales y las referencias históricas sin correspondencia expresa con ellas. Cada preparación pertenece a una línea de factura: conserva descripción, factura, fecha y referencias documentales. El código VTA-PROP es propuesto por EIOS, depende de la versión documental y de la línea de origen y no se presenta como SKU documental. Ni siquiera descripciones iguales se fusionan automáticamente como un mismo producto.

Las preparaciones no se incorporan al catálogo activo ni son seleccionables para evaluar pedidos. Aparecen deshabilitadas en el selector; el servidor también rechaza su uso como artículo. Se muestran los datos pendientes de confirmar: identidad y SKU, unidad si falta, coste de compra, tarifa y existencias. No se deduce un coste de un artículo parecido ni se utiliza un precio histórico como tarifa vigente. Una vinculación expresa a una ficha existente retira esa línea de la lista de preparaciones.

La lista permite buscar por código propuesto, descripción o factura; esta búsqueda solo filtra la presentación, nunca establece correspondencias. La tabla separa origen, descripción, unidad, referencias comerciales y datos pendientes. Las facturas y registros documentales originales permanecen intactos.

En A Monkey se obtienen 18 fichas actuales y 24 preparaciones de líneas de venta; esto no afirma que existan 42 productos distintos confirmados ni activa 24 SKU nuevos. Entre las diferencias documentales hay modelos y medidas distintos del catálogo de compras. La activación de nuevas fichas, con datos revisados, sigue pendiente.

Validación: cuatro pruebas nuevas de identidad, aislamiento entre versiones, conservación de fuentes, ausencia de uniones por descripción y rechazo de candidatos en propuestas. Quince pruebas focales correctas. Recorrido DOM/HTTP con una copia de A Monkey: 18 opciones activas, 24 deshabilitadas, búsqueda por modelo, reinicio al cambiar contexto y conservación de todos los registros documentales. JavaScript comprobado sintácticamente; inspección visual en navegador pendiente.
