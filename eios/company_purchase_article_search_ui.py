"""Filter purchase article options within the supplier already selected."""

HTML = '''<div class="files-subpanel"><label>Buscar SKU, descripción o familia<input id="purchase-article-query" type="search" autocomplete="off" placeholder="Escribe varias palabras para afinar"></label><label>Familia del artículo<select id="purchase-article-family-filter"><option value="">Todas las familias</option></select></label><p id="purchase-article-search-count" role="status"></p><button id="purchase-article-search-clear" type="button">Limpiar búsqueda de artículos</button></div>'''

JS = r'''
function purchaseArticleFamily(article){return String(article.family??'').trim()}
function purchaseArticleText(value){return String(value??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('es')}
function purchaseSupplierArticles(){return state?.info?.dataset_id===$('dataset').value?(state.articles||[]).filter(article=>article.supplier_id===$('supplier').value):[]}
function resetPurchaseArticleSearch(preferredArticle){
 $('purchase-article-query').value='';$('purchase-article-family-filter').value='';const articles=purchaseSupplierArticles();renderPurchaseArticleOptions(preferredArticle||articles[0]?.article_id||'');
}
function renderPurchaseArticleOptions(preferredArticle=$('article').value){
 const current=state?.info?.dataset_id===$('dataset').value,articles=purchaseSupplierArticles(),family=$('purchase-article-family-filter'),savedFamily=family.value,query=$('purchase-article-query'),select=$('article');
 query.disabled=family.disabled=select.disabled=!current;if(!current){$('purchase-article-search-count').textContent='Actualizando el catálogo de la empresa seleccionada…';$('purchase-article-search-clear').disabled=true;return}
 family.replaceChildren();option(family,'','Todas las familias');[...new Set(articles.map(purchaseArticleFamily).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'es',{numeric:true})).forEach(value=>option(family,'family:'+value,value));if(articles.some(article=>!purchaseArticleFamily(article)))option(family,'missing','Sin familia documentada');if([...family.options].some(item=>item.value===savedFamily))family.value=savedFamily;
 const terms=purchaseArticleText(query.value.trim()).split(/\s+/).filter(Boolean),matches=articles.filter(article=>{const text=purchaseArticleText([article.article_id,article.description,purchaseArticleFamily(article)].join(' '));return terms.every(term=>text.includes(term))&&(!family.value||(family.value==='missing'?!purchaseArticleFamily(article):family.value==='family:'+purchaseArticleFamily(article)))}).sort((a,b)=>a.article_id.localeCompare(b.article_id,'es',{numeric:true})),visible=matches.slice(0,200),selected=articles.find(article=>article.article_id===preferredArticle);
 select.replaceChildren();option(select,'','Selecciona un artículo');visible.forEach(article=>option(select,article.article_id,article.article_id+' · '+(article.description||'')+' / '+article.unit_as_documented));const retained=selected&&!visible.some(article=>article.article_id===selected.article_id);if(retained){const group=document.createElement('optgroup');group.label='Artículo ya seleccionado · conservado fuera de estos resultados';option(group,selected.article_id,selected.article_id+' · '+(selected.description||'')+' / '+selected.unit_as_documented);select.append(group)}select.value=selected?.article_id||'';
 $('purchase-article-search-count').textContent=stockNumber(matches.length)+' de '+stockNumber(articles.length)+' artículos del proveedor seleccionado · mostrando '+stockNumber(visible.length)+'.'+(matches.length>200?' Afina la búsqueda para ver los demás resultados.':'')+(retained?' El artículo elegido se conserva aparte de los resultados visibles.':'')+(!matches.length?' Sin coincidencias; limpia o cambia los filtros.':'');$('purchase-article-search-clear').disabled=!query.value&&!family.value;
}
for(const id of ['purchase-article-query','purchase-article-family-filter'])for(const name of ['input','change'])$(id).addEventListener(name,event=>{event.stopPropagation();renderPurchaseArticleOptions()});
$('purchase-article-query').addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();event.stopPropagation()}});
$('purchase-article-search-clear').onclick=()=>{$('purchase-article-query').value='';$('purchase-article-family-filter').value='';renderPurchaseArticleOptions();$('purchase-article-query').focus()};
$('article').addEventListener('change',()=>renderPurchaseArticleOptions());
'''
