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
