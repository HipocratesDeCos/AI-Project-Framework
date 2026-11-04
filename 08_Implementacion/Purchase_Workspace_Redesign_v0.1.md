# EIOS · Espacio de compras v0.1

Primera implementación del rediseño acordado: identidad del proveedor y artículo en una cinta compacta, seguida de cantidad, disponible, reservas, referencia de precio y cobertura. Las cintas permanecen visibles durante el recorrido de su formulario o revisión. Los importes destacan y el precio indica euros bajo la cifra.

La entrada se distribuye en cuatro pestañas que conservan los campos anteriores: proveedor/artículo, condiciones, cuotas/portes y guardar/documentos. Los detalles de artículo e historial quedan desplegables. El acceso «Ver stock, demanda y fuentes» los abre. La orientación de tesorería ocupa la columna lateral.

El descuento se edita mediante las modalidades comerciales existentes. Cambiar desde precio neto pide introducir el precio antes de descuentos; no reutiliza automáticamente un neto como precio bruto.

La revisión compara propuesta original, mi propuesta y respuesta del proveedor, con origen y referencia propios. Conserva el historial mediante el contrato existente, sin modificar el original. La cantidad y proveedor siguen siendo los mismos en una comparación. El calendario alternativo editable corresponde a «Mi propuesta»; la respuesta conserva el calendario original y puede requerir completar el estudio si cambia su importe.

No se calcula rotación a partir del stock. La cobertura solo muestra el resultado FINITE del motor existente cuando coinciden fecha y unidad del inventario; sin datos compatibles se indica pendiente. Disponible y reservado proceden de inventario documental. El precio de referencia exige una última compra única comparable. Las propuestas nuevas conservan descripción y referencia de precio al guardar; las antiguas sin esos campos no reconstruyen datos con el catálogo actual.

## Validación

- Suite completa del proyecto: 2.966 pruebas superadas antes de añadir dos casos de conservación documental.
- Pruebas específicas: persistencia de identidad y precio, ausencia de referencia cuando los últimos precios son ambiguos, comparación y totales.
- Navegador Chromium real: pestañas, activación explícita del descuento, total con IVA, guardado, dos alternativas y sus importes, cintas persistentes, independencia entre borrador y estudio, historial y anchura de 900 px.
- Datos sintéticos aislados: no se modifica la base de la empresa.

Esta entrega requiere revisión visual del usuario antes de integrar. No cambia decisiones financieras, saldos contables ni la autoridad de aceptación de ofertas.

## Revisión: negociación dentro de Condiciones

La pestaña Condiciones contiene ahora las tres columnas desde la entrada, antes de guardar: Oferta original, Mi propuesta y Respuesta del proveedor. Cantidad, IVA y fecha de pedido son comunes. Cada alternativa tiene precio, modalidad de descuento, vencimiento, origen y soporte independientes. Cada columna termina en una cinta de total con IVA y portes. Los campos conservan los modos NET, BEFORE_DISCOUNT, NONE, PERCENT y LINE_AMOUNT.

Los totales utilizan el endpoint comercial existente: no hay un segundo calculador en JavaScript. Un cambio borra el resultado anterior mientras se recalcula; datos incompletos y portes desconocidos permanecen pendientes. Las alternativas activadas se validan y calculan de nuevo en servidor al guardar, y se capturan dentro de la propuesta. Se recuperan en la revisión, donde se puede conservar una comparación financiera. No se ejecuta una compra ni se confirma aceptación.

El panel de tesorería incorpora una gráfica escalonada de los saldos al cierre de cada fecha del escenario de la oferta original y una línea de reserva mínima. Sus puntos salen de la misma acumulación que calcula saldo mínimo y saldo final; no se interpolan cobros ni se muestra una curva con información pendiente. La gráfica identifica expresamente su escenario. No incluye todavía las alternativas sin comparar.

Validación adicional: captura/reapertura de alternativas, rechazo de doble descuento, campos inyectados, duplicación de columnas y oferta documentada sin referencia; conciliación de los puntos gráficos con los saldos del motor. Chromium comprueba las tres columnas en Condiciones, los tres totales, invalidación inmediata, gráfica y recuperación tras guardar, además del recorrido de revisión anterior.

## Revisión: filas alineadas y descuento documental

La entrada se dispone en filas comunes entre las tres columnas: Coste de adquisición, Descuento, Coste neto, Portes, Vencimiento de propuesta e IVA de la mercancía. Los selectores visibles de modo de precio se eliminan. El coste unitario de entrada es antes de descuento y sin IVA; se conserva el calculador comercial existente. El soporte de precios NET de propuestas previas no se reinterpreta al abrir su revisión.

Cantidad y fecha de pedido permanecen comunes. Portes e IVA son independientes por alternativa y se conservan tanto en la captura como al recuperar la comparación financiera. Los detalles de factura, IVA y vencimiento de los portes se despliegan debajo de las filas principales. La cuadrícula comparte alturas de fila, incluidas las cintas de totales.

La cinta superior añade Descuento del libro. Se muestra el porcentaje explícito de la última compra única comparable, con su fecha; se conserva su fuente al guardar. No se presenta como tarifa de proveedor de vigencia verificada ni se aplica otra vez al precio histórico neto. Un 0 % documentado se distingue de un campo ausente. Sin porcentaje de compra se indica No documentado. La recepción admite el campo opcional discount_percent / Descuento (%) en compras históricas y valida el rango 0–100. Los registros antiguos sin ese campo no se rellenan con porcentajes de ventas ni con supuestos.

Validación: medición en Chromium de la misma posición vertical para las cinco filas solicitadas y los totales; ausencia de selector visible de modo de precio; descuento cero frente a ausente; recepción/selección/guardado de procedencia; recálculo y comparación de IVA y portes independientes.

## Revisión: columna de etiquetas, tipografía y calendarios

La tabla incorpora una primera columna de etiquetas en negrita. Se eliminan las etiquetas visuales repetidas de las tres columnas de valores manteniendo los nombres accesibles de los controles. Las filas y los totales permanecen alineados mediante una cuadrícula común; en pantallas estrechas la tabla dispone de desplazamiento horizontal dentro de su marco.

Los valores editables y los costes netos utilizan 18 px y la misma familia sans serif. Las etiquetas de fila son de 16 px en negrita; los encabezados y totales tienen mayor peso. Los detalles comerciales, procedencia, portes e importes se mantienen desplegables para compactar la tabla.

Tras confirmar el usuario que el calendario corresponde a vencimientos, las tres celdas de Vencimiento de propuesta tienen botón visible de calendario. El IVA permanece numérico. Los botones de alternativas se deshabilitan cuando no está activada su columna y abren el selector de su propio campo sin modificar el resto.

Validación de navegador: cuatro columnas, etiquetas en negrita, valores de al menos 18 px, alturas y posiciones compartidas, tres botones principales de calendario y apertura del campo correcto; conservación del recorrido previo de cálculo, guardado y comparación.

## Revisión: origen documental no editable y alineación de cabeceras

Cantidad y Fecha de pedido comparten posición vertical de entrada. Los vistos de Mi propuesta y Añadir respuesta recibida se anclan en la misma línea de las cabeceras, con independencia de la longitud de los títulos y del estado de sus campos. Los textos e importes de la cinta Datos de la compra se centran.

Oferta original deja de ser un formulario de entrada: muestra únicamente la última compra única comparable del libro activo, con fecha y fuente. Se identifican su coste neto y descuento explícito sin descontarlo otra vez. Los datos no documentados —IVA, portes o vencimiento si faltan— se indican como tales; el total no se inventa. No hay controles editables en esa columna ni se presenta el histórico como una oferta actual verificada.

La operación que calcula y guarda el formulario corresponde a Mi propuesta si está activa; si solo está activa Respuesta del proveedor, corresponde a esta. Las alternativas se conservan con la operación y la referencia documental se captura por separado mediante price_reference_at_save. La gráfica identifica la propuesta activa, sin representar la compra histórica como un nuevo pago. La revisión posterior denomina su base Propuesta guardada para distinguirla de la referencia del libro.

Desactivar una alternativa la excluye del cálculo y del guardado, conservando lo escrito si se reactiva. Cambiar de artículo o versión documental limpia sus datos. Validación en Chromium: original sin inputs/selects, precio documental independiente de los importes negociados, ambos pares alineados, cinta centrada, alternancia de la propuesta activa, conservación al reactivar y recorrido completo de cálculo/guardado/comparación.

## Corrección: importes sin fechas de calendario

El endpoint de cotización calcula importes aunque falten fecha de pedido o vencimientos. Los devuelve como ausentes, sin inventar fechas, y señala PENDING_DATES. El mismo calculador continúa exigiendo fechas por defecto: guardado, captura de alternativas y simulación de tesorería conservan su validación estricta. Los portes desconocidos siguen impidiendo conocer el total completo.

Regresión de la captura del usuario: 100 unidades a 13,50 y 14 euros, descuento 0 %, IVA 21 % y portes del proveedor producen 1.633,50 y 1.694,00 euros respectivamente, sin fecha de pedido. Chromium verifica ambos importes y que intentar guardar sin la fecha recibe 400. Las pruebas unitarias cubren fechas ausentes y portes conocidos sin vencimiento, manteniendo el rechazo del guardado estricto.

## Revisión: coste del encabezado, IVA documental y celdas no aplicables

La referencia de Coste de adquisición de Oferta original coincide con el precio del artículo seleccionado en el encabezado: última compra única comparable, neta y sin IVA. Coste neto unitario se obtiene del neto documental dividido por su cantidad incluso cuando no existe porcentaje de descuento. Informar un descuento no vuelve a restarlo del neto ya documentado.

La recepción de compras históricas admite Descuento (%) e IVA de la mercancía (%), con el alias IVA (%). Son campos opcionales, explícitos y numéricos en puntos porcentuales (21 representa 21 %). Se valida el rango 0–100 y se rechazan cabeceras de IVA ambiguas. Se conservan ambos valores en la referencia seleccionada y al guardar; su ausencia no se transforma en cero. No se modifica el libro del usuario en esta revisión.

Portes y Vencimiento de propuesta de Oferta original se muestran en controles deshabilitados, con fondo #f0f5fc igual a Condiciones. Sin dato se presenta un guion. El resto de referencias documentales permanece en solo lectura.

Validación: 26 pruebas unitarias de recepción, selección, historial y guardado; Chromium verifica coincidencia entre coste del encabezado y de la oferta, neto disponible sin descuento, controles deshabilitados y color de fondo, además del recorrido de importes, calendarios, guardado y comparación.

## Corrección: carga de un libro revisado sobre un expediente existente

Una recepción con 0 errores puede quedar bloqueada por coincidencias con archivos recibidos del mismo corte. Comprobar únicamente una base vacía no cubre esta situación. Se distingue el cambio de versión de los errores de formato del Excel.

Cuando está marcado Usar este libro como expediente activo, la comprobación solicita conservar la versión anterior. Esta opción ya promete mantenerla como histórico; ahora el parámetro preserve_revision es coherente con esa promesa aunque la casilla secundaria no esté marcada. El backend conserva las comprobaciones de formato, referencias, identidad y transacción.

Si se elige recepción sin activación y sin conservar revisión, los cambios permanecen bloqueados. La pantalla explica que los datos no tienen errores de formato y ofrece Conservar la versión anterior y volver a comprobar. La acción vuelve a validar y no guarda automáticamente.

Regresión: recepción previa y libro modificado con inventario y balance cambiados; bloqueo sin preserve_revision; READY con preserve_revision; guardado y activación efectivos conservando identificadores y bytes de las recepciones anteriores. Chromium verifica la opción de recuperación y el caso exacto de activación marcada con conservación secundaria desmarcada. Pasan 19 pruebas unitarias de recepción/mapeo.

Se reproduce también con el libro reparado completo frente al expediente anterior: 10 hojas con 0 errores; CONFLICT sin conservar revisión, READY con revisión y bytes anteriores intactos. No se vuelven a modificar los datos del Excel para evitar esta comprobación.

### Generador del calendario de cuotas

En Cuotas y portes, el calendario declarado incorpora un selector para repartir por número de cuotas o importe fijo. Genera las columnas número, importe con IVA y fecha de vencimiento; ajusta los céntimos o el remanente en la última cuota y permite editar el resultado. Generar sustituye expresamente el calendario anterior. Las fechas intermedias deben introducirse según el acuerdo; no se inventa periodicidad. Se conserva el último vencimiento declarado de cada concepto.

El cálculo usa el total comercial vigente y exige portes conocidos. Mantiene el contrato existente de mercancía y portes separados: cuando procede, muestra líneas desglosadas por concepto, sin atribuir al proveedor los portes del transportista. Se mantiene el máximo de 20 líneas y la validación de sumas y vencimientos al guardar. Los cambios posteriores del precio o descuento requieren revisar/regenerar las cuotas.

Validación: recorrido Chromium para reparto por número, importe fijo, redondeo, conservación de totales por concepto, rechazo de entrada inválida sin borrar el calendario y total pendiente; 15 pruebas unitarias de calendario y simulación de tesorería satisfactorias.
