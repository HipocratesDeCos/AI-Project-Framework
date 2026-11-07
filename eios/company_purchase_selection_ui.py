"""Compact, synchronized supplier and article selectors for the purchase workspace."""
CSS = '''
#po-selection .po-selection-pair{display:grid;grid-template-columns:minmax(150px,1fr) minmax(0,3fr);gap:14px;align-items:start}
#po-selection .po-selection-pair label{margin:0 0 14px}#po-selection .po-selection-family{display:grid;grid-template-columns:auto minmax(180px,1fr);gap:14px;align-items:center;max-width:580px}
#po-selection .po-selection-family select{margin-top:0}#po-selection .po-selection-pair select{font-size:16px}#po-selection #po-supplier-detail{margin:0 0 10px}
@media(max-width:580px){#po-selection .po-selection-pair{grid-template-columns:1fr}#po-selection .po-selection-family{grid-template-columns:1fr}}
'''
JS = r'''
(()=>{
 const supplier=$('supplier'),article=$('article'),oldCode=$('supplier-code'),code=document.createElement('select');code.id='supplier-code';code.setAttribute('aria-label','Código de proveedor');oldCode.replaceWith(code);
 const supplierBox=supplier.closest('section');supplierBox.querySelector('h2,h3').textContent='Proveedor de esta propuesta';
 const supplierPair=document.createElement('div');supplierPair.className='po-selection-pair';supplierPair.append(code.closest('label'),supplier.closest('label'));supplierBox.querySelector('h2,h3').after(supplierPair);
 const articleBox=article.closest('section');articleBox.querySelector('h3').textContent='Artículo de esta propuesta';
 const search=$('purchase-article-query').closest('.files-subpanel'),family=$('purchase-article-family-filter'),count=$('purchase-article-search-count');
 // Keep the existing search controls and filtering contract available to the app.
 search.hidden=true;
 const sku=document.createElement('select');sku.id='purchase-article-sku';const skuLabel=document.createElement('label');skuLabel.textContent='SKU';skuLabel.append(sku);
 const descriptionLabel=article.closest('label');descriptionLabel.firstChild.textContent='Descripción';
 const articlePair=document.createElement('div');articlePair.className='po-selection-pair';articlePair.append(skuLabel,descriptionLabel);
 const familyLabel=family.closest('label');familyLabel.firstChild.textContent='Familia';familyLabel.className='po-selection-family';articleBox.append(articlePair,familyLabel,count);
 function mirror(source,target,label){const fragment=document.createDocumentFragment();for(const item of source.children){if(item.tagName==='OPTGROUP'){const group=document.createElement('optgroup');group.label=item.label;for(const option of item.children){const copy=option.cloneNode(true);copy.textContent=label(option);group.append(copy)}fragment.append(group)}else{const copy=item.cloneNode(true);copy.textContent=label(item);fragment.append(copy)}}target.replaceChildren(fragment);target.value=source.value;target.disabled=source.disabled;}
 let identity='';
 function syncSupplier(){mirror(supplier,code,o=>o.value||'Selecciona un proveedor');}
 function syncArticle(){const articles=purchaseSupplierArticles();for(const option of article.options){const item=articles.find(a=>a.article_id===option.value);const text=item?(item.description||item.article_id)+(item.unit_as_documented?' / '+item.unit_as_documented:''):option.textContent;if(option.textContent!==text)option.textContent=text;}
 mirror(article,sku,o=>o.value||'Selecciona un artículo');
 const key=[$('dataset').value,supplier.value,article.value].join('|');if(key!==identity){identity=key;const selected=articles.find(a=>a.article_id===article.value),value=selected?(purchaseArticleFamily(selected)?'family:'+purchaseArticleFamily(selected):'missing'):'';if(family.value!==value&&[...family.options].some(o=>o.value===value)){family.value=value;renderPurchaseArticleOptions(article.value);}}
 }
 code.addEventListener('change',()=>{supplier.value=code.value;supplier.dispatchEvent(new Event('change',{bubbles:true}));syncSupplier();syncArticle()});
 sku.addEventListener('change',()=>{article.value=sku.value;article.dispatchEvent(new Event('change',{bubbles:true}));syncArticle()});
 supplier.addEventListener('change',syncSupplier);article.addEventListener('change',syncArticle);
 new MutationObserver(syncSupplier).observe(supplier,{childList:true,subtree:true,attributes:true});
 new MutationObserver(syncArticle).observe(article,{childList:true,subtree:true,attributes:true});
 syncSupplier();syncArticle();
})();
'''
