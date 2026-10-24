"""Read-only navigation from historical lines to an exact catalogue SKU in Stock."""

HTML = '''<div id="stock-article-scope" class="files-subpanel" hidden><p id="stock-article-scope-message" role="status"></p><div class="files-actions"><button id="stock-history-return" type="button" hidden title="Conserva los filtros y la página del historial de origen.">Volver al historial</button><button id="stock-article-scope-clear" type="button">Ver todo el stock</button></div></div>'''

JS = r'''
let stockExactArticle=null,stockHistoryOrigin=null;
function resetStockArticleScope(){stockExactArticle=null;stockHistoryOrigin=null;$('stock-history-return').hidden=true;$('stock-article-scope').hidden=true;$('stock-article-scope-message').textContent=''}
function addArticleStockLink(cell,articleId){
 const dataset=$('dataset').value;if(!cell||state?.info?.dataset_id!==dataset||!(state.articles||[]).some(article=>article.article_id===articleId))return;
 const button=document.createElement('button');button.type='button';button.className='review-button';button.textContent='Ver stock';button.setAttribute('aria-label','Ver stock de '+articleId);button.style.display='block';button.onclick=()=>openHistoryArticleStock(articleId,dataset,button);cell.append(button);
}
function validStockHistoryOrigin(origin){
 if(!origin||origin.dataset!==$('dataset').value||state?.info?.dataset_id!==origin.dataset||!origin.button.isConnected)return false;
 const panel=origin.button.closest('[data-view]');if(panel?.dataset.view!==origin.view)return false;for(let node=origin.button;node&&node!==panel;node=node.parentElement){if(node.hidden)return false}return true;
}
function openHistoryArticleStock(articleId,dataset,sourceButton){
 if(dataset!==$('dataset').value||state?.info?.dataset_id!==dataset)return;const article=(state.articles||[]).find(item=>item.article_id===articleId);if(!article)return;
 const panel=sourceButton?.closest('[data-view]'),labels={compras:'Compras',ventas:'Ventas',proveedores:'Proveedor',clientes:'Cliente',archivos:'Carga de archivos'},origin={dataset,view:panel?.dataset.view,button:sourceButton};stockHistoryOrigin=panel&&!panel.hidden&&labels[origin.view]&&validStockHistoryOrigin(origin)?origin:null;$('stock-history-return').hidden=!stockHistoryOrigin;$('stock-history-return').textContent=stockHistoryOrigin?'Volver a '+labels[origin.view]:'Volver al historial';
 stockExactArticle=articleId;stockPage=0;$('stock-search').value='';$('stock-provider').value='';$('stock-family').value='';$('stock-alert-only').checked=false;$('stock-order').value='SKU';
 $('stock-article-scope-message').textContent='ARTÍCULO DEL HISTORIAL · '+articleId+' · '+(article.description||'Sin descripción')+' · '+state.info.company.legal_name+' · corte '+stockDate(state.info.as_of_date)+'. Consulta de existencias y mínimos; la factura no acredita el stock disponible.';$('stock-article-scope').hidden=false;
 view('stock');renderStock();$('stock-article-scope-clear').focus();$('stock-article-scope').scrollIntoView({behavior:'smooth',block:'start'});
}
$('stock-history-return').onclick=()=>{const origin=stockHistoryOrigin;if(!validStockHistoryOrigin(origin)){stockHistoryOrigin=null;$('stock-history-return').hidden=true;return}view(origin.view);origin.button.focus();origin.button.scrollIntoView({behavior:'smooth',block:'center'})};
$('stock-article-scope-clear').onclick=()=>{resetStockArticleScope();$('stock-search').value='';$('stock-provider').value='';$('stock-family').value='';$('stock-alert-only').checked=false;stockPage=0;renderStock();$('stock-search').focus()};
'''
