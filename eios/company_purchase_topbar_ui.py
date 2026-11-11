"""Compact purchase heading and scroll-aware, read-only context strip."""
CSS='''
body:has([data-view=propuestas]:not([hidden])) .context{align-items:center;gap:20px;margin-bottom:16px}
body:has([data-view=propuestas]:not([hidden])) .context>div:first-child{position:relative;padding-left:50px}
body:has([data-view=propuestas]:not([hidden])) .context>div:first-child:before{content:'⌂';position:absolute;left:0;top:8px;display:grid;place-items:center;width:38px;height:38px;border-radius:12px;background:#eaf0ff;color:#1950f5;font-size:27px}
body:has([data-view=propuestas]:not([hidden])) .context>div:first-child>.badge{font-size:11px;font-weight:600;letter-spacing:.1em;text-transform:uppercase}
body:has([data-view=propuestas]:not([hidden])) .context .po-company-line{flex-wrap:wrap;margin:2px 0}
body:has([data-view=propuestas]:not([hidden])) .context #company{font-family:var(--eios-display);font-size:24px}
.po-area-pill{display:none}body:has([data-view=propuestas]:not([hidden])) .po-area-pill{display:inline-block;padding:6px 13px;margin-left:8px;border:1px solid #dce4f2;border-radius:24px;font-size:11px;font-weight:600;letter-spacing:.09em;color:#596b87;background:#fff}
body:has([data-view=propuestas]:not([hidden])) .context>label{display:flex;align-items:center;gap:12px;white-space:nowrap;font-size:12px;font-weight:600;margin:0}
body:has([data-view=propuestas]:not([hidden])) .context #dataset{max-width:360px;font-size:14px;min-height:42px;border-radius:12px;background:#fff}
[data-view=propuestas] .po-intro{display:none}
.po-top-dock{position:sticky;top:0;z-index:25;padding:8px 0;background:var(--guide-soft,#f4f6fb);isolation:isolate;margin-bottom:12px}
[data-view=propuestas].po-guided .po-top-dock .po-nav{margin:0;gap:8px}
[data-view=propuestas].po-guided .po-top-dock .po-nav a{position:relative;display:grid;grid-template-columns:28px minmax(0,1fr);gap:0 10px;align-content:center;min-height:62px;padding:9px 12px;border-radius:14px;font-size:14px;line-height:1.3;color:var(--guide-muted)}
.po-top-dock .po-nav a:before{content:attr(data-number);display:grid;place-items:center;grid-row:span 2;width:28px;height:28px;border-radius:50%;background:#eef2fa;color:#435574;font-size:14px;font-weight:600;align-self:center}
.po-top-dock .po-nav a[data-progress=complete]:before{content:'✓';background:#e3f4ee;color:#08735e}
[data-view=propuestas].po-guided .po-top-dock .po-nav a[aria-current=step]{box-shadow:0 0 0 3px #1950f519;border:1px solid #1950f5;color:var(--guide-ink)}
.po-top-dock .po-nav a[aria-current=step]:before{content:attr(data-number);background:#0d1e41;color:#fff}
.po-top-dock .po-nav a small{grid-column:2;margin-top:3px}.po-top-dock .po-nav a[data-progress=pending] small{display:none}
[data-view=propuestas] .po-ribbons{position:relative;top:auto}
[data-view=propuestas] .po-ribbon-header{display:none}
[data-view=propuestas] .po-identity{padding:17px 22px;grid-template-columns:1.1fr 1.25fr .55fr;border-bottom:1px solid var(--ribbon-line);gap:20px}
[data-view=propuestas] .po-identity strong{font-size:19px;line-height:1.25}
[data-view=propuestas] .po-identity>div>span:first-child{font-size:11px;margin-bottom:6px}
[data-view=propuestas] .po-metric-ribbon{padding:12px 22px 15px;grid-template-columns:.65fr .85fr .7fr 1.55fr 1.4fr 1.3fr}
[data-view=propuestas] .po-metric-label{display:block;min-height:23px;font-size:10px}
[data-view=propuestas] .po-metric-value,[data-view=propuestas] .po-saved-ribbon .po-metric-value{display:inline;font-size:34px;margin-right:5px;letter-spacing:-.04em;white-space:nowrap}
[data-view=propuestas] .po-metric-unit{display:inline;font-size:12px}.po-metric .po-ribbon-price-line{display:inline-flex}
[data-view=propuestas] .po-ribbon-currency{font-size:30px}
[data-view=propuestas] .po-metric[data-metric=price]{padding:7px 15px;border-radius:14px}
[data-view=propuestas] .po-ribbon-meta{padding:9px 22px;font-size:11px}
.po-top-strip{position:absolute;top:100%;left:0;right:0;display:grid;grid-template-columns:minmax(230px,1fr) minmax(0,1.3fr);align-items:center;gap:12px;margin-top:10px;padding:12px 18px;border:1px solid var(--guide-border);border-radius:18px;background:var(--guide-surface);box-shadow:0 8px 24px #10264b10;color:var(--guide-ink)}
.po-top-strip[hidden]{display:none!important}
.po-top-strip .po-strip-identity{min-width:0;padding-left:40px;position:relative;line-height:1.35}.po-top-strip .po-strip-pin{position:absolute;left:0;top:4px;box-sizing:border-box;padding:7px;background:#0d1e41;color:#fff;width:28px;height:34px;border-radius:9px}.po-top-strip .po-strip-identity:before{content:none;position:absolute;left:0;top:4px;background:#0d1e41;color:#fff;width:28px;height:34px;border-radius:9px;display:grid;place-items:center}
.po-top-strip .po-strip-supplier{display:block;font-family:var(--eios-display);font-size:16px;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.po-top-strip .po-strip-article{font-size:12px;color:var(--guide-muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.po-top-strip .po-strip-sku{margin-left:8px;background:#0d1e41;color:white;border-radius:5px;padding:3px 6px;font-size:10px;white-space:nowrap}
.po-top-strip .po-strip-metrics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr)) 1.25fr repeat(2,minmax(0,1fr));gap:8px}
.po-top-strip .po-strip-metric{padding:3px 8px;border-left:1px solid var(--guide-border);min-width:0}.po-top-strip .po-strip-metric span{display:block;font-size:9px;color:var(--guide-muted);font-weight:600;letter-spacing:.04em}.po-top-strip .po-strip-metric strong{font-family:var(--eios-display);font-size:23px;white-space:nowrap;letter-spacing:-.03em}.po-top-strip .po-strip-metric[data-key=price]{border:1px solid #bed0ff;border-radius:12px;background:#eaf0ff;color:#0d1e41}.po-top-strip .po-strip-metric[data-key=price] span{color:#1744bf}
[data-theme=dark] .po-area-pill,[data-theme=dark] body:has([data-view=propuestas]:not([hidden])) .context #dataset{background:#16243a;color:#e7eefc;border-color:#415675}
[data-theme=dark] .po-top-strip .po-strip-metric[data-key=price]{background:#20375e;color:#e7eefc;border-color:#6486c5}[data-theme=dark] .po-top-strip .po-strip-metric[data-key=price] span{color:#b5ceff}
@media(max-width:1200px){body:has([data-view=propuestas]:not([hidden])) .context{flex-wrap:wrap}.po-top-strip{grid-template-columns:minmax(180px,.8fr) minmax(0,1.5fr)}.po-top-strip .po-strip-metric strong{font-size:19px}[data-view=propuestas].po-guided .po-top-dock .po-nav a{font-size:12px;padding:8px;gap:0 6px}}
@media(max-width:900px){.po-top-dock{padding-top:4px}[data-view=propuestas].po-guided .po-top-dock .po-nav{display:flex;flex-wrap:nowrap;overflow-x:auto;padding:3px}[data-view=propuestas].po-guided .po-top-dock .po-nav a{flex:0 0 170px;min-height:54px}.po-top-strip{grid-template-columns:1fr;padding:9px 12px;gap:6px}.po-top-strip .po-strip-supplier{font-size:13px}.po-top-strip .po-strip-metric{padding:3px}.po-top-strip .po-strip-metric span{font-size:8px}.po-top-strip .po-strip-metric strong{font-size:18px}[data-view=propuestas] .po-identity{grid-template-columns:1fr;gap:10px}[data-view=propuestas] .po-metric-ribbon{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;padding:12px}[data-view=propuestas] .po-metric-value{font-size:27px}[data-view=propuestas] .po-ribbon-meta{flex-wrap:wrap}.po-area-pill{margin-left:0}body:has([data-view=propuestas]:not([hidden])) .context>label{flex-wrap:wrap;white-space:normal}body:has([data-view=propuestas]:not([hidden])) .context #dataset{max-width:100%;width:100%}[data-view=propuestas] .po-ribbon-body>summary{display:none}[data-view=propuestas] .po-ribbon-body[open]{max-height:none;overflow:visible}}
'''
JS=r'''
(function purchaseTopDock(){
 const page=document.querySelector('[data-view=propuestas]'),nav=page.querySelector('.po-nav'),form=$('form');
 const pill=document.createElement('span');pill.className='po-area-pill';pill.textContent='ÁREA DE COMPRAS';document.querySelector('.po-company-line').append(pill);
 const dock=document.createElement('div');dock.className='po-top-dock';page.querySelector('.po-intro').after(dock);dock.append(nav);const strip=document.createElement('section');strip.className='po-top-strip';strip.setAttribute('aria-label','Resumen fijo de la compra');strip.hidden=true;dock.append(strip);
 let root=null,frame=false,limit=Infinity;const observed=new WeakSet();
 function source(){return document.body.dataset.purchaseMode==='saved'?$('po-saved-ribbons'):$('po-draft-ribbons')}
 function paint(){const r=source();if(!r)return;root=r;strip.replaceChildren();const identity=document.createElement('div');identity.className='po-strip-identity';const pin=r.querySelector('.po-ribbon-pin')?.cloneNode(true);if(pin){pin.classList.add('po-strip-pin');identity.append(pin)}const supplier=document.createElement('strong');supplier.className='po-strip-supplier';supplier.textContent=r.querySelector('.po-identity>div:first-child strong')?.textContent||'Selecciona proveedor';const article=document.createElement('div');article.className='po-strip-article';article.textContent=r.querySelector('.po-ribbon-article>strong:not(.po-ribbon-sku)')?.textContent||'Selecciona artículo';const sku=document.createElement('span');sku.className='po-strip-sku';sku.textContent=r.querySelector('.po-ribbon-sku')?.textContent||'—';article.append(sku);identity.append(supplier,article);strip.append(identity);const metrics=document.createElement('div');metrics.className='po-strip-metrics';for(const [key,label] of [['quantity','CANTIDAD'],['available','STOCK'],['reserved','RESERV.'],['price','PRECIO REF.'],['discount','DTO. LIBRO'],['coverage','COBERTURA']]){const metric=document.createElement('div');metric.className='po-strip-metric';metric.dataset.key=key;const caption=document.createElement('span');caption.textContent=label;const value=document.createElement('strong');value.textContent=r.querySelector('[data-metric='+key+'] .po-metric-value')?.textContent||'—';if(key==='price'&&value.textContent!=='—')value.textContent+=' €';if(key==='coverage'&&value.textContent!=='—')value.textContent+=' d';metric.append(caption,value);metrics.append(metric)}strip.append(metrics);update()}
 function update(){frame=false;const r=source();if(!r||page.hidden||getComputedStyle(page).display==='none'){strip.hidden=true;return}const navHeight=nav.getBoundingClientRect().height+16;limit=r.getBoundingClientRect().bottom+scrollY-navHeight;strip.hidden=scrollY<=limit;page.style.setProperty('--po-ribbon-height',(dock.getBoundingClientRect().height+(strip.hidden?0:strip.getBoundingClientRect().height+10))+'px')}
 function schedule(){if(!frame){frame=true;requestAnimationFrame(update)}}
 function watch(){for(const r of page.querySelectorAll('.po-ribbons')){if(observed.has(r))continue;observed.add(r);r.querySelector('.po-ribbon-body').open=true;new MutationObserver(paint).observe(r,{childList:true,subtree:true,characterData:true});}paint()}
 new MutationObserver(watch).observe($('review-panel'),{childList:true});new MutationObserver(watch).observe(document.body,{attributes:true,attributeFilter:['data-purchase-mode','data-view']});addEventListener('scroll',schedule,{passive:true});addEventListener('resize',schedule);new ResizeObserver(schedule).observe(nav);new MutationObserver(schedule).observe(page,{attributes:true,attributeFilter:['hidden']});watch();
})();
'''
