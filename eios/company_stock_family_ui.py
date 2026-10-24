"""Filter stock by the family documented in the active article catalogue."""

JS = r'''
function stockArticleFamily(article){return String(article.family??'').trim()}
function renderStockFamilies(){
 const select=$('stock-family'),previous=select.value,counts=new Map();let missing=0;
 (state.articles||[]).forEach(article=>{const family=stockArticleFamily(article);if(family)counts.set(family,(counts.get(family)||0)+1);else missing++});
 select.replaceChildren();option(select,'','Todas las familias');[...counts].sort((a,b)=>a[0].localeCompare(b[0],'es',{numeric:true})).forEach(([family,count])=>option(select,'family:'+family,family+' ('+stockNumber(count)+')'));if(missing)option(select,'missing','Sin familia documentada ('+stockNumber(missing)+')');
 if([...select.options].some(item=>item.value===previous))select.value=previous;
}
function stockFamilyMatches(article){const value=$('stock-family').value,family=stockArticleFamily(article);return !value||(value==='missing'?!family:value==='family:'+family)}
'''
