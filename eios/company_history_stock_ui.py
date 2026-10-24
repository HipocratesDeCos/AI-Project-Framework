"""Read-only navigation from historical lines to an exact catalogue SKU in Stock."""

HTML = '''<div id="stock-article-scope" class="files-subpanel" hidden><p id="stock-article-scope-message" role="status"></p><button id="stock-article-scope-clear" type="button">Ver todo el stock</button></div>'''

JS = r'''
let stockExactArticle=null;
function resetStockArticleScope(){stockExactArticle=null;$('stock-article-scope').hidden=true;$('stock-article-scope-message').textContent=''}
function addArticleStockLink(cell,articleId){
 const dataset=$('dataset').value;if(!cell||state?.info?.dataset_id!==dataset||!(state.articles||[]).some(article=>article.article_id===articleId))return;
 const button=document.createElement('button');button.type='button';button.className='review-button';button.textContent='Ver stock';button.setAttribute('aria-label','Ver stock de '+articleId);button.style.display='block';button.onclick=()=>openHistoryArticleStock(articleId,dataset);cell.append(button);
}
function openHistoryArticleStock(articleId,dataset){
 if(dataset!==$('dataset').value||state?.info?.dataset_id!==dataset)return;const article=(state.articles||[]).find(item=>item.article_id===articleId);if(!article)return;
 stockExactArticle=articleId;stockPage=0;$('stock-search').value='';$('stock-provider').value='';$('stock-alert-only').checked=false;$('stock-order').value='SKU';
 $('stock-article-scope-message').textContent='ARTÍCULO DEL HISTORIAL · '+articleId+' · '+(article.description||'Sin descripción')+' · '+state.info.company.legal_name+' · corte '+stockDate(state.info.as_of_date)+'. Consulta de existencias y mínimos; la factura no acredita el stock disponible.';$('stock-article-scope').hidden=false;
 view('stock');renderStock();$('stock-article-scope-clear').focus();$('stock-article-scope').scrollIntoView({behavior:'smooth',block:'start'});
}
$('stock-article-scope-clear').onclick=()=>{resetStockArticleScope();$('stock-search').value='';$('stock-provider').value='';$('stock-alert-only').checked=false;stockPage=0;renderStock();$('stock-search').focus()};
'''
