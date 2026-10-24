"""Review unsaved stock minimum edits across filtered and paginated rows."""

HTML = '''<div class="files-subpanel"><p id="stock-minimum-pending-count" role="status"></p><details id="stock-minimum-pending-list" hidden><summary>Revisar mínimos pendientes de guardar</summary><p>Incluye artículos de otras páginas o fuera de los filtros. El aviso de stock y el CSV siguen utilizando el mínimo aplicado hasta que guardes los cambios. Vaciar una casilla solicita volver al mínimo automático.</p><div class="scroll"><table><thead><tr><th>SKU</th><th>Artículo</th><th>Mínimo aplicado</th><th>Edición sin guardar</th><th>Unidad</th></tr></thead><tbody id="stock-minimum-pending-rows"></tbody></table></div></details></div>'''

JS = r'''
function pendingStockMinimums(){
 if(state?.info?.dataset_id!==$('dataset').value)return [];
 return (state.articles||[]).filter(article=>{const minimum=state.stock_minimums?.[article.article_id];return minimum&&minimum.draft!==undefined&&String(minimum.draft)!==String(minimum.value??'')}).sort((a,b)=>a.article_id.localeCompare(b.article_id,'es'));
}
function renderPendingStockMinimums(){
 const articles=pendingStockMinimums(),rows=$('stock-minimum-pending-rows');rows.replaceChildren();$('stock-minimum-pending-list').hidden=!articles.length;
 if(state?.info?.dataset_id!==$('dataset').value){$('stock-minimum-pending-count').textContent='Actualizando los mínimos de la empresa seleccionada…';return}
 $('stock-minimum-pending-count').textContent=articles.length?stockNumber(articles.length)+(articles.length===1?' artículo con mínimo sin guardar en esta empresa.':' artículos con mínimos sin guardar en esta empresa.')+' Incluye otras páginas y filtros.'+(articles.length>100?' Hay más de 100 cambios: el guardado admite hasta 100 por operación. Se muestran los primeros 100.':''):'No hay mínimos editados pendientes de guardar.';
 articles.slice(0,100).forEach(article=>{const minimum=state.stock_minimums[article.article_id],row=document.createElement('tr');salesCells(row,[article.article_id,article.description,minimum.value===null||minimum.value===undefined||minimum.value===''?'Sin configurar':stockNumber(minimum.value),minimum.draft===''?'Volver al automático':stockNumber(minimum.draft),minimum.unit||'Sin unidad']);rows.append(row)});
}
'''
