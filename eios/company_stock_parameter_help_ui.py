"""Explain received stock parameters without implying rule activation."""

HTML = '''<details class="files-subpanel" id="reception-stock-help" hidden><summary>Cómo rellenar los parámetros de stock y entrega</summary>
<p>Estos campos describen la política de cada artículo. Las cantidades se expresan en la misma unidad que su SKU; el plazo se expresa en días enteros.</p>
<div class="fields">
<div class="metric"><span>STOCK MÍNIMO · <code>minimum_stock</code></span><p>Umbral empresarial para identificar existencias bajas. El valor recibido queda documentado: no sustituye por sí solo el mínimo aplicado en la pantalla Stock.</p></div>
<div class="metric"><span>STOCK DE SEGURIDAD · <code>safety_stock</code></span><p>Reserva de planificación para cubrir retrasos o una demanda mayor de la prevista. No es producto reservado para un cliente ni se resta automáticamente del disponible al cargarla.</p></div>
<div class="metric"><span>PUNTO DE PEDIDO · <code>reorder_point</code></span><p>Cantidad que sirve de referencia para iniciar la reposición. Tiene en cuenta el consumo previsto mientras llega la mercancía y el stock de seguridad. Indica cuándo plantear una compra, no cuánto comprar.</p></div>
<div class="metric"><span>PLAZO DE ENTREGA · <code>lead_time_days</code></span><p>Días previstos desde que se cursa el pedido hasta que la mercancía está disponible. Es una duración: introduce, por ejemplo, <strong>4</strong>, sin escribir una fecha.</p></div>
</div>
<h3>EJEMPLO ORIENTATIVO · NO SE INCORPORA A TU ARCHIVO</h3>
<p>Si el consumo previsto es de <strong>5 unidades al día</strong>, la entrega tarda <strong>4 días</strong> y la seguridad es de <strong>10 unidades</strong>, un punto de pedido orientativo sería <strong>5 × 4 + 10 = 30 unidades</strong>. El consumo de 5 unidades/día es un supuesto del ejemplo; EIOS no lo deduce al cargar esta tabla.</p>
<h3>ANTES DE SUBIR LA PLANTILLA</h3>
<ul><li><code>article_id</code>: código exacto del artículo; conserva los ceros iniciales.</li><li><code>unit</code>: unidad de las cantidades, por ejemplo <strong>uds.</strong>. No mezcles unidades, cajas y palets.</li><li><code>observation_date</code>: fecha de referencia, si la aportas; debe coincidir con el corte indicado al subir el archivo.</li><li>Deja vacío lo que desconozcas. <strong>Cero</strong> es un valor declarado, no un dato ausente. No se admiten parámetros negativos ni días fraccionarios.</li><li>En «Parámetros de stock y entrega», informa al menos uno de los cuatro parámetros. En «Inventario» son opcionales.</li></ul>
<h3>QUÉ HACE EIOS ACTUALMENTE</h3>
<p>Conserva los valores con su archivo y fila para revisión. Puedes consultarlos en Carga de archivos, seleccionando los archivos del expediente y pulsando «Consultar artículos seleccionados», en «Parámetros documentados de stock».</p>
<p>Cargar estos campos no activa alarmas de punto de pedido, no calcula automáticamente ese punto ni genera compras. Los avisos de Stock utilizan el mínimo aplicado en esa pantalla.</p>
</details>'''
