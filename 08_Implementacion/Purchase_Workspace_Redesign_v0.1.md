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

### Ajustes visuales del calendario de pagos

El bloque de calendario se abre por defecto, sin activar automáticamente la declaración de cuotas. Cada fila alinea número y concepto, importe, vencimiento y papelera roja accesible. El número crece un 30 %. Todos los vencimientos incorporan un selector de fecha que conserva la entrada DD/MM/YYYY. El pie muestra la suma con IVA en la columna de importes y se actualiza al generar, editar, añadir o eliminar filas; si hay importes inválidos, indica que deben revisarse.

Verificación Chromium: apertura inicial, papelera y calendario por fila, selección de fecha, suma inicial y edición, eliminación con renumeración y comprobación geométrica de alineación, además de los casos de reparto existentes. La selección de propuesta activa sigue siendo una base de simulación, sin registrar aceptación contractual.

### Selección compacta de proveedor y artículo

La sección Proveedor y artículo muestra «Proveedor de esta propuesta» con código y razón social en una fila, y contacto/localidad debajo. «Artículo de esta propuesta» contiene SKU y descripción/unidad en otra fila, con familia y contador de resultados debajo. Los pares de desplegables comparten la selección existente: cambiar cualquiera de ellos actualiza su pareja y conserva los eventos de catálogo, referencias, stock y propuesta. Se oculta el buscador textual de esta sección según el nuevo esquema; sus controles internos y el filtro de familia mantienen el contrato anterior. En pantallas estrechas las parejas se apilan.

Verificación Chromium: cambio de proveedor desde código y razón social, sincronización SKU/descripción en ambos sentidos, filtro de familia, contador y alineación geométrica de las parejas sin errores de JavaScript.

### Importes calculables con fechas incoherentes y calendario fijo

La consulta de importes devuelve netos, IVA y totales aunque los vencimientos sean anteriores al pedido; acompaña el resultado de `INVALID_DATES` y mensajes visibles junto al total de cada columna. Guardar y evaluar tesorería mantienen la validación estricta de fechas. Los errores de consulta también se muestran en la columna, evitando un «Pendiente» sin explicación. La referencia original sigue requiriendo condiciones documentadas completas para mostrar un total.

El calendario de pagos es una sección fija, sin summary ni control de plegado, y su editor permanece visible aunque no se declare un plan. Generar cuotas activa expresamente la declaración; desmarcarla conserva las filas visibles deshabilitadas y no envía el plan.

Verificación: 30 pruebas unitarias de importes, calendario y tesorería; Chromium con la captura reproducida (1.000 unidades, 2,60/10 % y 2,75/5 %, IVA 21 %, vencimiento anterior al pedido) muestra 2.831,40 y 3.161,12 euros con aviso visible. Recorrido de generación, suma, fechas, eliminación y alineación de cuotas satisfactorio.

### IVA del libro y ajustes de encabezado

Las dos columnas editables precargan el IVA de la misma última compra única comparable que sustenta la referencia original del artículo en el libro. Se conserva el cero documentado y se deja vacío el dato ausente; no se presupone un tipo general. El tipo sigue editable: un cambio explícito del usuario se conserva al recalcular y se reinicia al cambiar de artículo/proveedor/expediente. El título del campo indica la fecha documental de origen.

Cantidad y fecha del pedido usan fuente de 18 px como los campos inferiores. La cinta Datos de la compra incorpora una chincheta azul vectorial, sin imagen externa.

Verificación Chromium: precarga del IVA en ambas columnas, cero frente a dato ausente, conservación de un tipo editado, igualdad de tamaño de fuente e icono presente. Regresión del cálculo de columnas con aviso de fechas y calendario fijo satisfactoria.

### Total original y diferencias entre columnas

La fila TOTAL CON IVA muestra en las tres columnas el total de mercancía para la misma cantidad: neto de línea e IVA redondeados por el calculador comercial. El original usa el coste neto histórico único comparable y su IVA documentado; no reaplica el descuento histórico. Los portes mantienen su desglose independiente y el total completo de operación conserva su cálculo para cuotas y tesorería. Se explicita esta base común junto a la tabla.

Se añaden los recuadros «Mi propuesta − Oferta original» y «Respuesta del proveedor − Mi propuesta». La resta se hace en céntimos enteros: negativo verde, positivo rojo y cero neutro, con texto que explica el signo. Los recuadros esperan a disponer de ambos cálculos vigentes y descartan resultados asíncronos obsoletos. Si falta referencia, IVA, cantidad o datos válidos de una columna, la diferencia permanece pendiente.

Validación Chromium: cálculo original sin doble descuento, ambas restas, inversión de signos y colores al editar, cero neutro, exclusión consistente de portes de la base comparada y dato ausente pendiente. Regresiones de IVA del libro y cálculo con avisos de fecha satisfactorias.

### Claridad de Guardar y documentos

La revisión guardada presenta primero un estado derivado del informe: guardado completado, simulación calculada o pendiente con causa, datos financieros vinculados, proyección del libro y revisión documental. La simulación hipotética de la compra se distingue de la proyección de los movimientos del expediente. Un déficit se presenta como incidencia para decidir, sin afirmar que falló el guardado. Una asociación declarada o una comprobación registrada no se presenta como aceptación ni validación automática.

Las acciones indicadas llevan a Condiciones, Parámetros, Carga de archivos o al detalle de revisión, según el requisito. No se pide modificar la naturaleza de un expediente para eludir un límite de simulación. Las notas explicativas del bloque financiero y del importe usan fondo azul neutro; el ámbar se reserva en el resumen para requisitos o incidencias concretas y el rojo para conflictos. Los avisos de stock y precio conservan su presentación. Todos los formularios documentales y mensajes técnicos siguen disponibles en el desplegable «Abrir revisiones documentales y detalle financiero».

El calendario guardado indica que sus sumas y fechas han pasado la validación de captura y, solo si el escenario conservado lo acredita, que se usó en esa simulación. Se elimina la afirmación fija «No incorporados a la proyección». Se aclara que guardar no crea movimientos del libro ni acredita aceptación del proveedor. No cambia el cálculo, evidencia, admisión, autoridad ni la ruta operacional.

Validación: 30 pruebas de calendario, cálculo comercial y simulación de tesorería; recorrido Chromium con guardado y revisión reales en expediente aislado, acceso a informe, estados de simulación pendiente/calculada/déficit, conflictos documentales y apertura de los formularios existentes. Los escenarios adicionales de presentación se comprueban mediante variantes del informe en memoria sin alterar datos financieros.

### Primer bloque de alternativas justificadas con y sin déficit

Se reutilizan `purchase_history` (historial filtrado por artículo, proveedor, corte, moneda y unidad), `commercial_terms`, `payment_plan` y el comprobador de escenarios de `company_purchase_cash_preview`. El nuevo adaptador `company_purchase_opportunities` propone únicamente hipótesis con fuentes identificadas:

- Precio neto de la última compra única comparable, si reduce el coste final y el escenario recalculado respeta la reserva. No se reaplica el descuento histórico. Con cuotas declaradas se redistribuye la mercancía proporcionalmente, en céntimos, conservando fechas y portes; si aparece una cuota inválida no se propone.
- Desplazamiento de pagos hasta una fecha de cobro de la previsión (hasta 64 fechas candidatas), si mejora el saldo mínimo y respeta la reserva. Se conservan importes; no se presenta ahorro económico ni garantía de cobro.

Ambas búsquedas se ejecutan también sin déficit. Se conservan las alternativas anteriores para déficit, sin duplicar parches. Cada opción muestra fuente, base, ahorro con IVA y portes, variación del saldo mínimo y efecto sobre cantidad. Origen hipotético, aceptación no confirmada, sin autoridad ni ruta operacional. No se elige ganadora.

Aplicar una alternativa actualiza explícitamente Mi propuesta y su calendario, dispara los cálculos existentes y conserva la respuesta del proveedor y la referencia histórica. Guardar utiliza la captura de negociación existente, con procedencia declarada y aceptación sin verificar. Las alternativas y explicaciones generadas se incluyen en el estudio de tesorería conservado al guardar.

El inventario disponible se muestra como referencia documental. Este bloque no optimiza cantidades ni acredita cobertura futura o necesidad: los datos de demanda, entregas y criterios autorizados siguen siendo requisitos del siguiente tramo. No ejecuta ni simula haber ejecutado el motor completo de Scenario Engine, NI o Decision Twin: sus contratos canónicos requieren contexto y autoridades que el formulario no aporta aún. Se integra una primera capacidad útil sin duplicar el cálculo comercial ni crear autoridad de precios.

Validación: 34 pruebas de calendario, cálculo y tesorería; incluyen generación sin déficit, repetición independiente de candidatos, ambigüedad, unidad/moneda, historial futuro/obsoleto, cuotas recalculadas e inmutabilidad. Chromium con servidor y expediente aislados: generación real sin déficit, aplicación, recálculo de Mi propuesta, conservación de respuesta y guardado real de negociación con origen HYPOTHETICAL y aceptación UNVERIFIED.

### Cantidad y stock: referencias, cobertura existente y requisitos de necesidad

`company_purchase_stock_review.review_quantity` adapta el inventario, los mínimos ya resueltos por EIOS y la cobertura de `company_planning` calculada con `eios.stock.engine.calculate_coverage`. No introduce una fórmula de reposición ni publica `JustifiedNeedState`: conserva `quantity_assessment=NOT_DETERMINED` y no emite una cantidad recomendada.

Se muestran disponible, reservado (ya descontado), mínimo y origen, diferencia hasta el mínimo al corte y cantidad introducida. Se validan unidad, identidad de artículo/expediente, fecha, no obsolescencia y coherencia físico menos reservado. Un mínimo automático se identifica expresamente como referencia histórica, sin elevarlo a política autorizada.

Solo se reutiliza cobertura cuando coincide con artículo/unidad/inventario y la previsión está dentro de vigencia para el pedido. Se muestra su fecha y alcance: inventario de referencia, sin proyectar la recepción de la nueva compra. Se compara con el plazo de entrega para señalar una cobertura inferior al plazo bajo ese supuesto. Consumo cero no se convierte en una recomendación ni en garantía de cobertura ilimitada.

El checklist identifica previsión ausente/caducada, movimientos entre inventario y pedido, plazo de entrega, entradas pendientes/demanda comprometida y criterio de reposición autorizado. El análisis se muestra incluso cuando falta el cálculo financiero. No se solicita añadir columnas arbitrarias al libro ni se presume que el importador ya admite toda la planificación necesaria. La interfaz permite consultar Stock; el siguiente tramo requiere captura/vinculación de previsión y políticas con sus contratos de autoridad.

El contexto se conserva dentro del estudio de tesorería guardado y se muestra al revisar propuestas que lo contienen. Las propuestas antiguas mantienen su captura original. Validación: 46 ejecuciones de pruebas en los módulos de stock/planificación, calendario, importes y tesorería; Chromium con generación de alternativa, referencias de stock visibles, checklist de necesidad, aplicación y guardado real conservando el contexto de cantidad sin autoridad.

### Captura de hipótesis de planificación y alternativa de cantidad

Condiciones incorpora «Simular cantidad con demanda y cobertura declaradas». Activar el escenario exige artículo y fecha del pedido; captura stock libre al inicio (reservas ya descontadas), consumo diario adicional a esas reservas, plazo de entrega, cobertura objetivo desde recepción, seguridad, múltiplo de compra y hasta 20 entradas fechadas. Se requieren responsable, referencia y confirmación explícita del alcance hipotético. Se invalida al cambiar artículo, fecha o contexto documental, y se limpia al reiniciar el formulario.

`company_purchase_stock_scenario` calcula sensibilidad al cierre diario con consumo constante declarado, entradas pendientes y recepción supuesta. El objetivo explícito conserva la seguridad desde recepción hasta fin de cobertura; la cantidad se redondea hacia arriba al múltiplo indicado. Los horizontes se acotan a 365 días de entrega y 365 de cobertura. Se identifican faltas previas a recepción, sin afirmar que una mayor cantidad en esa entrega resolvería el pasado. Cero necesidad en el escenario se informa sin ejecutar una cancelación.

El resultado es una hipótesis analítica distinta del motor STK canónico: no crea `JustifiedNeedState`, no resuelve parámetros del Centro, no eleva evidencia y no modifica stock ni políticas empresariales. El objetivo introducido es un criterio de simulación del usuario, no una política física autorizada. Se conservan entradas canónicas, contexto y huella en `stock_planning_at_save` y en el estudio de tesorería.

Las cantidades diferentes de la actual se someten al calculador comercial y a la comprobación financiera existentes. Solo se ofrecen si respetan la reserva y el calendario; con cuotas, se recalcula la mercancía en céntimos preservando fechas y portes. Las reducciones anteriores motivadas por caja se descartan si incumplen el objetivo de stock declarado o hay una falta antes de entrega. Aplicar modifica Mi propuesta y la cantidad común, conservando las hipótesis. Precio, descuento, IVA y portes siguen declarados: sus condiciones por volumen quedan sujetas a confirmación del proveedor.

Validación: 49 ejecuciones de pruebas de planificación, stock, cuotas, cálculo y tesorería. Cobertura de entradas fechadas, faltas previas, demanda cero, redondeo a múltiplos, contexto cambiado, entradas inválidas, persistencia e incompatibilidad entre recorte por caja y objetivo de stock. Chromium con captura real y validación de campos, alternativa generada y comprobada financieramente, aplicación, guardado con hipótesis y desactivación al cambiar la fecha.

### Comparación central y revisión de extremo a extremo

Condiciones muestra «Comparar alternativas calculadas» junto a la negociación: propuesta activa de referencia y candidatos del servidor, con cantidad/unidad, neto unitario, operación completa con IVA y portes, ahorro, saldo mínimo y su fecha, vencimiento y acción. Cada opción conserva fundamento, fuente y pagos desplegables. No se calcula ni selecciona una ganadora en el cliente. La referencia es la propuesta activa simulada, distinta de la referencia histórica de la columna Oferta original.

`current_terms` y los campos de comparación de cada candidato proceden del cálculo comercial y escenario ya ejecutados, incluidos en la huella del estudio. Se comprueban por repetición independiente. El cliente muestra esos valores y reutiliza la aplicación a Mi propuesta existente; no sustituye el cálculo ni altera condiciones documentadas del proveedor.

Al cambiar entradas se elimina inmediatamente toda la tabla anterior y se muestra recalculando. Las respuestas continúan sujetas al control de secuencia/contexto del cálculo de tesorería. Un cálculo pendiente no deja acciones sobre alternativas viejas. La revisión guardada muestra la tabla de su captura sin botones de aplicación; las capturas anteriores sin estos metadatos lo indican y no se reconstruyen con el catálogo actual.

Validación: 50 ejecuciones de pruebas de stock, escenarios hipotéticos, cuotas, importes y tesorería. Chromium con alternativa real de precio, valores coincidentes entre tabla y cálculo, retiro síncrono de tabla al editar, respuesta nueva, aplicación a Mi propuesta, conservación de respuesta del proveedor, guardado y tabla de revisión de solo lectura. Regresión del recorrido de hipótesis de stock, generación de cantidad, aplicación y persistencia satisfactoria. CI del bloque previo completa y satisfactoria.

### Búsqueda combinada, comparación parcial y sensibilidad de cobros

`company_purchase_scenario_search` combina de forma acotada valores sustentados: precio neto de la última compra comparable, cantidad del objetivo hipotético y fechas de cobros ya documentadas para desplazar pagos. No inventa descuentos, proveedores ni una política empresarial. Explora hasta 64 combinaciones de al menos dos variables, dando paso primero a combinaciones sin aplazamiento y después a las fechas tempranas; registra presupuesto agotado, comprobaciones, descartes con causa y opciones conservadas. No se presenta como una exploración exhaustiva ni como ejecución del Scenario Engine/NI canónicos.

Los candidatos se recalculan conjuntamente con `commercial_terms`, el reparto existente de cuotas y la proyección financiera del expediente. Esto permite encontrar una combinación que respeta la reserva cuando los cambios aislados no lo hacen. Se conserva el objetivo de stock declarado; no se combinan modificaciones que pretendan resolver una falta anterior a entrega sin cambiar su fecha. Se mantienen las fronteras de hipótesis, evidencia, aceptación y ruta operacional.

Cada opción recibe una observación descriptiva sobre coste total y saldo mínimo, comparándose solo con otras de la misma cantidad. Se identifican opciones que mejoran una métrica sin empeorar la otra; no se clasifican volúmenes distintos como equivalentes ni se valora calidad, fiabilidad, condiciones comerciales omitidas o preferencias. No hay puntuación agregada ni ganadora automática.

Se añade una sensibilidad explícita: eliminar el mayor cobro individual positivo dentro del horizonte. La selección es determinista por importe y referencia. Se reutiliza el proyector, sin modificar los flujos originales ni el escenario base, para mostrar saldo mínimo, déficit y reserva respetada bajo esa única hipótesis. No es previsión de impago ni certificación de robustez ante todos los riesgos; la ausencia de cobros se informa sin generar un resultado de tensión ficticio.

La tabla central, el estudio guardado y el informe imprimible conservan métricas, fuentes, sensibilidad y resultados de búsqueda. Los textos extensos de negociación se despliegan aparte, y la tabla limita su altura con encabezado fijo. Las fuentes y mensajes se escapan en el informe y se presentan como texto en el navegador.

Validación: 55 ejecuciones de pruebas. Casos: combinación viable con dos cambios aislados inviables, repetición y no mutación de datos, límite y determinismo de búsqueda, descartes, comparación restringida a igual volumen y sensibilidad con déficit identificable. Chromium: generación del caso combinado real, guardado previo con comparaciones, revisión sin acciones, informe imprimible conservado, aplicación conjunta de precio/cantidad y recálculo sin déficit. Regresiones de precio y planificación de stock satisfactorias. CI del bloque anterior completa y satisfactoria.

## Condiciones: lectura visual y estudio guardado

El bloque «Estado del estudio guardado» se presenta después de la matriz de negociación y antes de la síntesis. Tres tarjetas combinan color, punto y texto: guardado, dinero previsto y comprobaciones. Verde indica el resultado concreto mostrado; ámbar, un paso pendiente; rojo, insuficiencia de la reserva prevista o conflicto registrado. Los colores no representan aprobación global ni aceptación del proveedor.

Los textos iniciales usan lenguaje sencillo («Hay margen», «Falta dinero», «Por revisar»). La síntesis conserva cifras clave, una línea de stock y una acción breve. Explicaciones completas, sensibilidad, fuentes y acciones documentales se conservan bajo «Saber más». La evaluación lateral conserva su gráfico y veredicto; stock, cuotas y demás detalle se pliegan. La tabla de alternativas mantiene sus filas; su explicación y criterios quedan plegados.

Consultar un estudio muestra su referencia, síntesis y alternativas históricas en modo de consulta, sin aplicar condiciones al formulario. Un aviso identifica que el formulario superior es un borrador separado. «Volver al borrador» recalcula los datos actuales. Editar cualquier dato o cambiar de versión retira inmediatamente la síntesis guardada y restablece «Sin guardar», evitando conservar un semáforo verde del estudio anterior. Los controles documentales y sus acciones se desplazan, no se clonan ni se eliminan. No cambian los cálculos ni la persistencia.

Validación: recorrido Chromium de posición de bloques, semáforos con estados distintos, plegado inicial, apertura de acciones, consulta sucesiva de dos estudios, tabla histórica sin botones de aplicar y retirada inmediata al editar. Regresiones de guardado/revisión documental y combinación aplicada desde el borrador. Pruebas Python de síntesis e informe.

### Alternativas minimalistas

La tabla ancha de diez columnas se sustituye por tarjetas adaptables, tanto en borrador como en consulta guardada. Encabezado breve («Ajustar la cantidad», «Pagar más tarde»), identificador estable, cantidad, total con IVA y portes, diferencia frente a referencia y señal de reserva prevista. La propuesta de referencia ocupa una sola línea. No hay tabla ni desplazamiento horizontal.

Si cambia la cantidad, la diferencia se etiqueta como desembolso de otra cantidad, no como ahorro comparable a igual volumen. Cada «Ver detalle», cerrado inicialmente, conserva precio neto, saldo mínimo y fecha, vencimientos, pagos, fuente, alcance, sensibilidad y comparación parcial. «Saber más · criterios y comprobaciones» conserva la referencia completa, prueba de cobro, descartes, límites y huella. Los botones de aplicar solo existen en el borrador. Se mantienen cálculos, procedencia y persistencia.

Verificación Chromium: tarjetas sin tabla, detalle accesible y plegado inicial, contenedor sin desbordamiento a 390 px, consulta guardada sin aplicación, transición a borrador y aplicación/recalculado de una combinación. Revisión visual de tarjetas en escritorio.

### Stock unificado y gráfica de consulta compacta

En la revisión guardada, el contenido de mínimo de stock se integra en la tarjeta izquierda de stock y cobertura. Las etiquetas Disponible de referencia y Fecha del inventario se muestran una sola vez cuando sus valores coinciden. Si las capturas difieren, se mantienen las cifras históricas bajo etiquetas explícitas (Disponible al guardar / Fecha de inventario al guardar) y una nota breve; no se elimina una discrepancia como si fuese un duplicado.

La tarjeta derecha pasa a mostrar la gráfica de dinero previsto del estudio guardado. Se desplaza el mismo elemento SVG desde la evaluación inferior, con altura máxima de 260 px, leyenda y descripción. No se duplica ni se cambia la proyección. Cambiar de estudio sustituye la gráfica; si el siguiente no conserva previsión, se retira la anterior y se explica su ausencia. Los estudios antiguos sin mínimo mantienen su aviso histórico.

Validación Chromium: ubicación y tamaño, campos coincidentes sin repetición, conservación de campos específicos del mínimo, referencias distintas identificadas, actualización entre estudios y retirada de gráfica/datos ausentes. Verificación visual de ambas tarjetas.
