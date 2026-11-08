"""Align draft negotiation analysis and option cards under their condition columns."""
CSS='''
[data-view=propuestas].po-guided:has(#po-conditions:not([hidden])) .po-workspace{display:block}
#po-conditions{--po-condition-columns:180px 180px minmax(220px,1fr) minmax(220px,1fr)}
#po-conditions #po-draft-negotiation{grid-template-columns:var(--po-condition-columns);min-width:800px}
#po-negotiation-review-row{display:grid;grid-template-columns:var(--po-condition-columns);align-items:start;margin:16px 8px 0;border:1px solid transparent;min-width:0}
#po-negotiation-review-row>.po-context{grid-column:1 / 3;grid-row:1;position:static;max-height:none;overflow:visible;min-width:0;padding-right:12px;width:auto}
#po-negotiation-review-row #po-option-studies{grid-column:3 / 5;grid-row:1;display:block;margin:0;padding:0;border:0;background:transparent;min-width:0}
#po-negotiation-review-row .po-option-cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0;align-items:stretch}
#po-negotiation-review-row #po-option-studies>h3{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
#po-negotiation-review-row #po-option-studies>p{margin:0 12px 12px;font-size:12px}
#po-negotiation-review-row .po-option-card{margin:0 12px;min-width:0}
#po-negotiation-review-row .po-option-detail{margin:16px 12px 0;min-width:0}
@media(max-width:1200px){#po-negotiation-review-row{grid-template-columns:minmax(0,1fr);gap:16px}#po-negotiation-review-row>.po-context{grid-column:1;grid-row:1;padding-right:0}#po-negotiation-review-row #po-option-studies{grid-column:1;grid-row:2}}
@media(max-width:650px){#po-negotiation-review-row{margin-inline:0}#po-negotiation-review-row .po-option-cards{grid-template-columns:minmax(0,1fr);gap:12px}#po-negotiation-review-row .po-option-card,#po-negotiation-review-row .po-option-detail{margin-inline:0}}
'''
JS=r'''
(function(){
 const conditions=$('po-conditions'),aside=document.querySelector('[data-view=propuestas] .po-context'),panel=$('po-option-studies'),table=conditions.querySelector('.po-negotiation-scroll');
 const asideHome=document.createComment('context home'),panelHome=document.createComment('draft option home');aside.before(asideHome);panel.before(panelHome);const row=document.createElement('div');row.id='po-negotiation-review-row';table.after(row);
 function place(){const drafting=document.body.dataset.purchaseMode!=='saved',active=drafting&&!conditions.hidden;if(active){if(aside.parentElement!==row)row.prepend(aside);if(panel.parentElement!==row)row.append(panel)}else{if(aside.parentElement===row)asideHome.after(aside);if(drafting&&panel.parentElement===row)panelHome.after(panel)}row.hidden=!active}
 new MutationObserver(place).observe(conditions,{attributes:true,attributeFilter:['hidden']});new MutationObserver(place).observe(document.body,{attributes:true,attributeFilter:['data-purchase-mode']});place();
})();
'''
