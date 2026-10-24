"""Make stock selection counts and active filters explicit."""

HTML = '''<div class="fields" aria-label="Resumen de artículos filtrados"><div class="metric"><span>ARTÍCULOS EN LA SELECCIÓN</span><strong id="stock-selection-count">—</strong><small>Incluye las demás páginas.</small></div><div class="metric"><span>CON AVISO EN LA SELECCIÓN</span><strong id="stock-selection-alerts">—</strong><small id="stock-selection-unknown"></small></div></div><p id="stock-active-filters" role="status"></p>'''

JS = r'''
function renderStockFilterScope(matching){
 let alerts=0,unknown=0;matching.forEach(article=>{const status=state.stock_minimums?.[article.article_id]?.status;alerts+=['EMPTY','LOW','LIMIT'].includes(status)?1:0;unknown+=!status||status==='UNKNOWN'?1:0});
 $('stock-selection-count').textContent=stockNumber(matching.length);$('stock-selection-alerts').textContent=stockNumber(alerts);$('stock-selection-unknown').textContent=stockNumber(unknown)+' sin datos suficientes en esta selección. Los avisos corresponden al inventario de referencia.';
 const filters=[],query=$('stock-search').value.trim(),provider=$('stock-provider'),family=$('stock-family');if(query)filters.push('Texto: '+query);if(provider.value)filters.push('Proveedor: '+(provider.selectedOptions[0]?.textContent||provider.value));if(family.value)filters.push('Familia: '+(family.value==='missing'?'Sin familia documentada':family.value.slice(7)));if($('stock-alert-only').checked)filters.push('Solo artículos con aviso');if(stockExactArticle)filters.push('SKU exacto del historial: '+stockExactArticle);
 const order=({SKU:'SKU',NAME:'nombre del artículo',PRIORITY:'avisos primero'})[$('stock-order').value]||'SKU';$('stock-active-filters').textContent=(filters.length?'Filtros aplicados · '+filters.join(' · '):'Sin filtros: se consulta todo el catálogo.')+' · Orden: '+order+'.';$('stock-clear-filters').disabled=state?.info?.dataset_id!==$('dataset').value||(!filters.length&&$('stock-order').value==='SKU'&&stockPage===0);
}
$('stock-clear-filters').onclick=()=>{if(state?.info?.dataset_id!==$('dataset').value)return;resetStockArticleScope();$('stock-search').value='';$('stock-provider').value='';$('stock-family').value='';$('stock-alert-only').checked=false;$('stock-order').value='SKU';stockPage=0;renderStock();$('stock-search').focus()};
'''
