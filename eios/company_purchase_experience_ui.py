"""Purchase presentation: persistent source context without new calculation authority."""
CSS = '''
body{font-family:Arial,Helvetica,sans-serif;background:#f5f8fe;color:#132846}
[data-view=propuestas] input,[data-view=propuestas] select,[data-view=propuestas] button,[data-view=propuestas] table{font-family:inherit}
.po-context>details{background:white;border:1px solid #c6d7ed;border-radius:9px;padding:12px 16px;margin:0 0 12px}
.po-context>details>summary{font-size:13px;color:#24486e}
.po-context>details>.card{border:0;margin-top:12px;padding:0}
[data-view=propuestas]{--po-line:#c6d7ed;--po-blue:#1259e8}
[data-view=propuestas] .po-intro{margin-bottom:16px}
[data-view=propuestas] .po-intro h2{font-size:28px;font-weight:800;color:#102748}
[data-view=propuestas] .po-eyebrow{color:#3d6490}
[data-view=propuestas] .po-nav{margin:12px 0}
[data-view=propuestas] .po-nav a{border-radius:6px;font-size:14px}
[data-view=propuestas] .po-nav a[aria-current=true]{color:#0844be;background:#e5eeff;border-bottom:3px solid #1259e8}
[data-view=propuestas] .po-workspace{grid-template-columns:minmax(0,1fr) minmax(290px,.42fr);gap:18px}
[data-view=propuestas] .po-step{background:white!important;border:1px solid var(--po-line)!important;border-radius:10px;padding:20px!important}
[data-view=propuestas] .po-heading>span{display:none}
[data-view=propuestas] .po-heading h2{font-size:17px;font-weight:800}
[data-view=propuestas] .po-heading p{font-size:13px}
[data-view=propuestas] .po-total{background:#f2f7ff;border-color:#c6d7ed}
[data-view=propuestas] .po-grand{background:#e5eeff;border:1px solid #94b8f5}
[data-view=propuestas] #po-cash{margin-top:0;padding:16px;background:#f3f8ff;border-color:#c3d5ee}
[data-view=propuestas] #po-cash.is-short{background:#fff3f1;border-color:#c34a41}
[data-view=propuestas] #po-cash .po-cash-grid{grid-template-columns:1fr}
[data-view=propuestas] #review-panel{overflow:visible;border-color:#c6d7ed}
.po-ribbons{position:sticky;top:0;z-index:12;margin:0 0 18px;background:#f5f8fe;padding:8px 0 6px;box-shadow:0 5px 9px #203a5910;isolation:isolate}
.po-identity{display:grid;grid-template-columns:1.2fr .65fr 1.7fr;gap:16px;background:#f0f6ff;border:1px solid #b9cfee;border-radius:9px;padding:9px 16px;min-height:40px;align-items:center}
.po-identity>div{min-width:0}
.po-identity span,.po-metric-label{font-size:10px;letter-spacing:.025em;font-weight:700;display:block;color:#385774;text-transform:uppercase}
.po-identity strong{font-size:14px;display:block;margin-top:3px;overflow-wrap:anywhere}
.po-metric-ribbon{display:grid;grid-template-columns:1fr repeat(3,.7fr) 1.1fr .8fr .9fr;align-items:center;gap:10px;padding:14px 16px;margin-top:8px;min-height:84px;background:#e7f0ff;border:1px solid #b9cfee;border-radius:9px}
.po-metric-ribbon{text-align:center}.po-metric{padding-right:12px;text-align:center}
.po-ribbon-pin{display:inline-block;vertical-align:middle;margin-right:7px;color:#0757ff;flex-shrink:0}.po-ribbon-title{font-size:13px;font-weight:800;line-height:1.5}
.po-ribbon-title small{display:block;font-size:11px;font-weight:400;color:#385774}
.po-metric{border-left:1px solid #c1d3eb;padding-left:12px;min-width:0}
.po-metric-value{display:block;font-size:36px;line-height:1.18;font-weight:800;letter-spacing:-1px;margin:5px 0 2px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}
.po-metric-unit{font-size:12px;display:block;color:#334d70}
.po-ribbon-meta{display:flex;gap:12px;justify-content:space-between;align-items:center;flex-wrap:wrap;padding:6px 8px 0;font-size:11px;color:#49617b}
.po-ribbon-meta button,.po-ribbons button{font:inherit;cursor:pointer;color:#1259e8;background:transparent;border:0;padding:0;text-decoration:underline}
.po-discount-help{background:#edf4ff;border:1px solid #c2d6f6;padding:12px;border-radius:7px;margin-bottom:14px;font-size:13px;line-height:1.5}
.po-discount-help button{margin:7px 0 0!important;display:block}
.po-source{font-size:12px;margin-bottom:10px}
.po-saved-ribbon .po-metric-value{font-size:36px}
.po-review-tabs{display:flex;gap:8px;flex-wrap:wrap;padding:12px 20px;background:#edf4ff}
.po-review-tabs button{margin:0!important}
.po-original-summary{background:#f0f6ff;border:1px solid #c1d5f1;border-radius:8px;padding:14px;margin-bottom:14px}
.po-original-summary dl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:0}
.po-original-summary dt{font-size:11px;color:#49617b}.po-original-summary dd{margin:4px 0;font-weight:700;font-size:15px}
@media(min-width:1550px){.po-metric-value,.po-saved-ribbon .po-metric-value{font-size:42px}}
@media(max-width:1100px){[data-view=propuestas] .po-workspace{grid-template-columns:minmax(0,1fr)}[data-view=propuestas] #po-cash .po-cash-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.po-metric-ribbon{gap:6px;padding:12px}.po-metric{padding-left:8px}.po-metric-value,.po-saved-ribbon .po-metric-value{font-size:30px}.po-metric-ribbon{text-align:center}.po-metric{padding-right:12px;text-align:center}
.po-ribbon-title{font-size:11px}}
@media(max-width:760px){.po-identity{grid-template-columns:1fr .6fr;padding:8px 10px;gap:6px}.po-identity>div:last-child{grid-column:1/-1}.po-metric-ribbon{grid-template-columns:repeat(3,minmax(0,1fr));padding:8px;min-height:0}.po-ribbon-title{grid-column:1/-1}.po-ribbon-title small{display:inline;margin-left:8px}.po-metric-value,.po-saved-ribbon .po-metric-value{font-size:23px;letter-spacing:-.5px}.po-metric-label{font-size:8px}.po-metric-unit{font-size:10px}.po-metric{padding-left:5px}.po-ribbon-meta{font-size:10px}.po-identity strong{font-size:12px}.po-ribbons{padding-top:3px}.po-original-summary dl{grid-template-columns:1fr 1fr}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto!important}}
'''
JS = r'''
const purchaseRibbonWide=matchMedia('(min-width: 901px)');purchaseRibbonWide.addEventListener('change',()=>{for(const body of document.querySelectorAll('.po-ribbon-body'))body.open=purchaseRibbonWide.matches});
const purchaseRibbonObserver=typeof ResizeObserver==='function'?new ResizeObserver(entries=>{for(const {target} of entries){const height=target.getBoundingClientRect().height;if(height>0)target.closest('[data-view=propuestas]')?.style.setProperty('--po-ribbon-height',height+'px')}}):null;
function purchaseContextRibbons(id){
 const root=document.createElement('section');root.id=id;root.className='po-ribbons';root.setAttribute('aria-label','Contexto de la compra siempre visible');
 const header=document.createElement('header');header.className='po-ribbon-header';root.append(header);
 const headerMeta=document.createElement('div');headerMeta.className='po-ribbon-header-meta';header.append(headerMeta);
 const body=document.createElement('details');body.className='po-ribbon-body';const mobileSummary=document.createElement('summary');mobileSummary.textContent='Ver datos del proveedor, artículo e importes';body.append(mobileSummary);body.open=purchaseRibbonWide.matches;root.append(body);
 const identity=document.createElement('div');identity.className='po-identity';body.append(identity);
 const ids={};for(const key of ['supplier','description','sku','family']){const box=document.createElement('div'),label=document.createElement('span'),value=document.createElement('strong');label.textContent={supplier:'PROVEEDOR',sku:'SKU',description:'DESCRIPCIÓN DEL ARTÍCULO',family:'FAMILIA'}[key];box.append(label,value);identity.append(box);ids[key]=value}
 const article=ids.description.parentElement;article.classList.add('po-ribbon-article');article.querySelector('span').textContent='ARTÍCULO';ids.sku.classList.add('po-ribbon-sku');ids.sku.parentElement.remove();article.append(ids.sku);
 const metrics=document.createElement('div');metrics.className='po-metric-ribbon';const title=document.createElement('div');title.className='po-ribbon-title';title.innerHTML='<svg class="po-ribbon-pin" width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M8 2h8v2l-1 1v5l3 3v2h-5v7l-1 2-1-2v-7H6v-2l3-3V5L8 4z"/></svg><span>DATOS DE LA COMPRA</span>';const pin=document.createElement('small');pin.textContent='Siempre visible';title.append(pin);header.prepend(title);body.append(metrics);title.querySelector('svg').setAttribute('aria-hidden','true');
 for(const [key,label,unit] of [['quantity','CANTIDAD','unidades'],['available','STOCK DISPONIBLE','unidades'],['reserved','RESERVADAS','unidades'],['price','PRECIO UNITARIO DE REFERENCIA','euros'],['discount','DESCUENTO DEL LIBRO','%'],['coverage','COBERTURA ESTIMADA','días']]){const box=document.createElement('div');box.className='po-metric';box.dataset.metric=key;const heading=document.createElement('span'),value=document.createElement('strong'),suffix=document.createElement('span');heading.className='po-metric-label';heading.textContent=label;value.className='po-metric-value';suffix.className='po-metric-unit';suffix.textContent=unit;box.append(heading,value,suffix);metrics.append(box);ids[key]=value;ids[key+'Unit']=suffix}
 const currency=document.createElement('span');currency.className='po-ribbon-currency';currency.textContent='€';const priceLine=document.createElement('div');priceLine.className='po-ribbon-price-line';ids.price.before(priceLine);priceLine.append(ids.price,currency);
 const meta=document.createElement('div');meta.className='po-ribbon-meta';const source=document.createElement('span'),explain=document.createElement('button');explain.type='button';explain.textContent='Ver stock, demanda y fuentes';const status=document.createElement('span');status.className='po-ribbon-status';meta.append(status,source,explain);root.append(meta);source.className='po-ribbon-source';explain.append(document.createTextNode(' →'));purchaseRibbonObserver?.observe(root);
 function badgeText(target,value,pattern){target.replaceChildren();const full=String(value),match=full.match(pattern);target.setAttribute('aria-label',full);target.append(document.createTextNode(match?full.slice(0,match.index).trim():full));if(match){const badge=document.createElement('span');badge.className='po-ribbon-fiction';badge.textContent=match[1].toUpperCase();target.append(badge)}}
 function contextItem(value,kind){const item=document.createElement('span');item.className='po-ribbon-context-item';const icon=document.createElementNS('http://www.w3.org/2000/svg','svg');icon.setAttribute('viewBox','0 0 24 24');icon.setAttribute('width','16');icon.setAttribute('height','16');icon.setAttribute('fill','none');icon.setAttribute('stroke','currentColor');icon.setAttribute('stroke-width','1.8');icon.setAttribute('aria-hidden','true');icon.innerHTML={company:'<path d="M3 10 12 3l9 7v11h-6v-7H9v7H3z"/>',file:'<path d="M5 3h9l5 5v13H5zM14 3v6h5"/>',date:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 2v6M17 2v6M3 11h18"/>'}[kind];const text=document.createElement('span');text.textContent=value;item.append(icon,text);headerMeta.append(item);return text}
 const defined=v=>v!==null&&v!==undefined&&v!=='';
 function update({supplier,article,quantity,inventory,price,planning,cutoff,filename,discount,discountDate,companyName,materialNature,saved=false}){
  ids.supplier.textContent=supplier?.legal_name||supplier?.supplier_id||'Selecciona proveedor';ids.sku.textContent=article?.article_id||'Selecciona artículo';ids.description.textContent=article?.description||'Sin descripción documentada';
  ids.family.textContent=article?.family||'Sin familia documentada';
  badgeText(ids.supplier,ids.supplier.textContent,/\s*·\s*(fictici[oa])\s*$/i);badgeText(ids.description,ids.description.textContent,/\s*·\s*(artículo ficticio)\s*$/i);
  headerMeta.replaceChildren();const company=contextItem(companyName||(saved?'Empresa no conservada':'Selecciona empresa'),'company');badgeText(company,company.textContent,/\s*·\s*(fictici[oa])\s*$/i);contextItem(filename||(companyName?'Expediente documental base':'Fuente no conservada'),'file');contextItem('Corte '+stockDate(cutoff),'date');
  status.textContent=saved?'ESTUDIO GUARDADO':'BORRADOR';root.dataset.context=saved?'saved':'draft';root.dataset.material=materialNature||'NOT_DECLARED';
  ids.quantity.textContent=defined(quantity)?stockNumber(quantity):'—';ids.available.textContent=defined(inventory?.available)?stockNumber(inventory.available):'—';ids.reserved.textContent=defined(inventory?.reserved)?stockNumber(inventory.reserved):'—';
  const unit=inventory?.unit||article?.unit_as_documented||'unidades';for(const key of ['quantity','available','reserved'])ids[key+'Unit'].textContent=unit;
  ids.price.textContent=defined(price)?money(price):'—';ids.priceUnit.textContent=defined(price)?'Neto sin IVA':'Sin referencia única';currency.hidden=!defined(price);
  const validDiscount=defined(discount)&&Number.isFinite(Number(discount))&&Number(discount)>=0&&Number(discount)<=100;ids.discount.textContent=validDiscount?stockNumber(discount)+' %':'—';ids.discountUnit.textContent=validDiscount?'Última compra · '+stockDate(discountDate):'No documentado';
  // Display only the existing engine output, never derive demand from the current stock.
  const coverage=planning?.status==='FINITE'&&defined(planning.coverage_days)&&inventory?.as_of_date===planning.as_of_date&&inventory?.unit===planning.unit;
  ids.coverage.textContent=coverage?stockNumber(Math.floor(Number(planning.coverage_days))):'—';ids.coverageUnit.classList.toggle('po-ribbon-consumption-pending',!coverage&&planning?.status!=='UNBOUNDED');ids.coverageUnit.textContent=coverage?'días · según planificación':planning?.status==='UNBOUNDED'?'Sin consumo previsto':'Consumo por validar';
  source.textContent='Inventario '+stockDate(inventory?.as_of_date)+' · Corte: '+stockDate(cutoff)+' · '+(filename||'Fuente documental')+' · Disponible = físico − reservado';for(const value of root.querySelectorAll('.po-metric-value'))value.dataset.empty=String(value.textContent==='—');
 }
 return {root,update,explain};
}
(function purchaseExperience(){
 const form=$('form'),page=form.closest('[data-view]');
 const ribbons=purchaseContextRibbons('po-draft-ribbons');form.prepend(ribbons.root);
 const refs=document.querySelector('.po-context');for(const card of Array.from(refs.children)){const details=document.createElement('details'),summary=document.createElement('summary');summary.textContent=card.querySelector('h2')?.textContent||'Detalle documental';card.before(details);details.append(summary,card)}const cash=$('po-cash');if(cash)refs.prepend(cash);
 // Tabs reuse existing sections. No duplicate form fields or parallel price calculator.
 const nav=document.querySelector('.po-nav');const groups=[['po-selection','Proveedor y artículo'],['po-conditions','Condiciones'],['po-payments','Cuotas y portes'],['po-save','Guardar y documentos']];
 function show(id,focus=false){if(window.purchaseGuideNavigate){window.purchaseGuideNavigate(id,focus);return}for(const [key] of groups)$(key).hidden=key!==id;for(const a of nav.querySelectorAll('a'))a.setAttribute('aria-current',a.hash==='#'+id?'true':'false');if(focus){const target=$(id);target.setAttribute('tabindex','-1');target.focus({preventScroll:true});target.scrollIntoView({block:'start'})}}
 nav.replaceChildren();for(const [id,title] of groups){const a=document.createElement('a');a.href='#'+id;a.textContent=title;a.onclick=e=>{e.preventDefault();show(id)};nav.append(a)}show('po-selection');
 const help=document.createElement('div');help.className='po-discount-help';const text=document.createElement('span');text.textContent='¿El proveedor ofrece un descuento o quieres plantearlo? Introduce el precio antes de descuentos y registra la condición. Un precio ya neto no se descuenta otra vez.';const enable=document.createElement('button');enable.type='button';enable.textContent='Introducir precio y descuento';help.append(text,enable);$('po-conditions').querySelector('.po-heading').after(help);
 enable.onclick=()=>{const mode=form.elements.pricing_mode;if(mode.value==='NET'){const amount=form.elements.unit_price.value;if(amount!==''&&!confirm('El precio actual es neto. Para aplicar un descuento debes indicar el precio original antes de descuentos. ¿Quieres cambiar de modalidad y volver a introducirlo?'))return;mode.value='BEFORE_DISCOUNT';form.elements.unit_price.value='';form.elements.discount_value.value='';form.elements.discount_mode.value='PERCENT'}else if(form.elements.discount_mode.value==='NONE')form.elements.discount_mode.value='PERCENT';mode.dispatchEvent(new Event('change',{bubbles:true}));form.elements.unit_price.focus()};
 function render(){
  if(!state||state.info.dataset_id!==$('dataset').value){ribbons.update({});return}
  const article=state.articles.find(a=>a.article_id===$('article').value),supplier=state.suppliers.find(s=>s.supplier_id===$('supplier').value),inventory=state.inventory?.[article?.article_id];
  const history=state.history?.[article?.article_id]||[],latest=history.filter(r=>r.issue_date===history[0]?.issue_date),reference=latest.length===1&&latest[0].comparable?latest[0]:null;
  ribbons.update({supplier,article,inventory,quantity:form.elements.quantity.value,price:reference?.effective_net_unit_price,discount:reference?.discount_percent,discountDate:reference?.issue_date,planning:state.planning?.[article?.article_id],cutoff:state.info.as_of_date,companyName:state.info.company.legal_name||state.info.company.company_id,materialNature:state.info.material_nature,filename:state.info.exclusive_workbook?.filename});
 }
 ribbons.explain.onclick=()=>{for(const details of refs.querySelectorAll(':scope>details'))details.open=true;refs.scrollIntoView({block:'start'})};
 for(const event of ['input','change'])form.addEventListener(event,render);$('dataset').addEventListener('change',()=>ribbons.update({}));form.addEventListener('reset',()=>queueMicrotask(render));
 for(const id of ['summary','available','last-price','proposal-cost-summary'])new MutationObserver(render).observe($(id),{childList:true,subtree:true,characterData:true});
 form.addEventListener('invalid',e=>{for(const [id] of groups)if($(id).contains(e.target)){show(id);break}},true);
 render();
})();
function renderPurchaseSavedRibbons(proposal){
 let old=$('po-saved-ribbons');if(old){purchaseRibbonObserver?.unobserve(old);old.remove()}const ribbon=purchaseContextRibbons('po-saved-ribbons');ribbon.root.classList.add('po-saved-ribbon');$('review-panel').prepend(ribbon.root);
 // Saved identity and inventory stay tied to this proposal, never to the draft selection.
 const context=proposal.documentary_context_at_save,inventory=proposal.stock_context_at_save?.inventory;
 ribbon.update({supplier:proposal.supplier_commercial_at_save||{supplier_id:proposal.supplier_id},article:{article_id:proposal.article_id,description:proposal.article_description_at_save,family:proposal.article_family_at_save,unit_as_documented:proposal.unit},quantity:proposal.quantity,inventory,price:proposal.price_reference_at_save?.unit_price,discount:proposal.price_reference_at_save?.discount_percent,discountDate:proposal.price_reference_at_save?.issue_date,cutoff:context?.documentary_cutoff,companyName:context?.company_name,materialNature:context?.material_nature,filename:context?.exclusive_workbook?.filename,saved:true});
 ribbon.explain.onclick=()=>$('review-documentary-context').scrollIntoView({block:'start'});
}
'''
