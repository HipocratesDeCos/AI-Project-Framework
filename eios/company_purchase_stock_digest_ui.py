"""Read-only live stock explanation beside the negotiation table."""
CSS='''
#po-conditions:has(#po-conditions-width-layout){--po-condition-columns:180px 180px minmax(0,1fr) minmax(0,1fr)}
#po-conditions:has(#po-conditions-width-layout) #po-draft-negotiation{min-width:712px}
#po-conditions-width-layout{display:grid;grid-template-columns:180px 180px repeat(5,minmax(0,1fr));align-items:start;min-width:0}
#po-conditions-width-layout>.po-conditions-main{grid-column:1 / 7;min-width:0}
#po-conditions-stock-digest{grid-column:7;min-width:0;padding-left:12px;color:var(--guide-ink,#0d1e41);font-family:var(--eios-font);}
#po-conditions-stock-digest .po-need-kicker{font-size:9px;font-weight:600;letter-spacing:.06em;text-align:center;margin:0 0 8px;color:var(--guide-muted,#596b87)}
#po-conditions-stock-digest .po-need-intro,#po-conditions-stock-digest .po-need-note{font-size:10px;line-height:1.5;text-align:center;margin:0 0 12px;color:var(--guide-muted,#596b87);overflow-wrap:anywhere}
#po-conditions-stock-digest .po-need-table{width:100%;display:block;border:1px solid var(--guide-border,#dce4f2);border-radius:14px;overflow:hidden;background:var(--guide-surface,#fff);margin:0;table-layout:fixed}
#po-conditions-stock-digest .po-need-table tbody{display:block}
#po-conditions-stock-digest .po-need-table tr{display:block;border-bottom:1px solid var(--guide-border,#dce4f2);padding:9px 6px;text-align:center}
#po-conditions-stock-digest .po-need-table tr:last-child{border-bottom:0}
#po-conditions-stock-digest .po-need-table tr:has(th){padding:9px 5px;background:#eaf0ff;color:#12356e}
#po-conditions-stock-digest .po-need-table th{display:block;border:0;background:transparent;padding:0;text-align:center;font-size:9px;line-height:1.5;letter-spacing:.025em;color:inherit}
#po-conditions-stock-digest .po-need-table td{display:block;width:100%;padding:0;border:0;text-align:center;font-size:11px;line-height:1.4;overflow-wrap:anywhere;color:inherit}
#po-conditions-stock-digest .po-need-table td:last-child{font-size:16px;font-family:var(--eios-display);font-variant-numeric:tabular-nums;font-weight:600;margin-top:5px}
#po-conditions-stock-digest .po-digest-label{display:block;font-size:11px;line-height:1.35;text-align:center}
#po-conditions-stock-digest .po-need-letter{display:grid;place-items:center;width:21px;height:21px;margin:0 auto 4px;border-radius:5px;background:#eaf0ff;color:#12356e;font-size:10px;font-weight:600}
#po-conditions-stock-digest .po-need-formula{display:block;font-size:9px;line-height:1.4;margin-top:4px;color:var(--guide-muted,#596b87)}
#po-conditions-stock-digest .po-need-total{background:#eaf0ff;font-weight:600}
#po-conditions-stock-digest .po-need-total .po-need-letter{background:#1950f5;color:white}
#po-conditions-stock-digest .po-need-total td:last-child{font-size:20px}
[data-theme=dark] #po-conditions-stock-digest .po-need-table tr:has(th),[data-theme=dark] #po-conditions-stock-digest .po-need-total{background:#20375e;color:#e7eefc}
[data-theme=dark] #po-conditions-stock-digest .po-need-letter{background:#20375e;color:#b5ceff}
[data-theme=dark] #po-conditions-stock-digest .po-need-total .po-need-letter{background:#1950f5;color:white}
@media(max-width:1200px){#po-conditions-width-layout{display:block}#po-conditions-stock-digest{padding:0;margin:20px 8px}#po-conditions-stock-digest .po-need-table td{font-size:12px}#po-conditions-stock-digest .po-need-table td:last-child{font-size:18px}}
'''
JS=r'''
(function(){
 const source=$('po-need-calculation'),conditions=$('po-conditions'),table=conditions.querySelector('.po-negotiation-scroll'),row=$('po-negotiation-review-row');
 const layout=document.createElement('div');layout.id='po-conditions-width-layout';const main=document.createElement('div');main.className='po-conditions-main';const digest=document.createElement('aside');digest.id='po-conditions-stock-digest';digest.setAttribute('aria-label','De dónde salen los números del stock · consulta');table.before(layout);layout.append(main,digest);main.append(table,row);
 function sync(){const nodes=[];for(const child of source.children){if(child.matches('p,table')){const copy=child.cloneNode(true);copy.removeAttribute('id');for(const node of copy.querySelectorAll('[id]'))node.removeAttribute('id');if(copy.matches('table'))for(const cell of copy.querySelectorAll('td:first-child')){const texts=Array.from(cell.childNodes).filter(n=>n.nodeType===3),full=texts.map(n=>n.textContent).join('').trim(),label=document.createElement('span'),letter=cell.querySelector('.po-need-letter')?.textContent;label.className='po-digest-label';label.title=full;label.setAttribute('aria-label',full);label.textContent=({G:'Necesidad bruta',I:'Entradas pendientes',K:'Necesidad neta',L:'Compra para el objetivo'}[letter]||full);for(const node of texts)node.remove();const formula=cell.querySelector('.po-need-formula');if(formula)formula.before(label);else cell.append(label)}nodes.push(copy)}if(child.matches('table'))break}digest.replaceChildren(...nodes)}
 new MutationObserver(sync).observe(source,{childList:true,subtree:true,characterData:true});sync();
})();
'''
