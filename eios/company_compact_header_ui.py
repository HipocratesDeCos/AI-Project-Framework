"""Compact company identity; retain the actual live documentary source nodes."""
CSS='''
.context .po-company-line{display:flex;align-items:center;gap:9px;min-width:0;margin:3px 0 5px}
.context>div:first-child{min-width:0;max-width:100%}
.context #company{font-size:calc(20px + 2pt);margin:0;min-width:0;overflow-wrap:anywhere}
.po-company-info{display:inline-flex;align-items:center;flex-shrink:0}
.context #company-info-button{display:inline-grid;place-items:center;flex-shrink:0;width:23px;height:23px;min-height:0;padding:0;margin:0;border:1px solid #8299bd;border-radius:50%;background:transparent;color:#214a85;cursor:pointer;font-family:var(--eios-font);font-size:15px;font-weight:600;line-height:1}
.context #company-info-button:hover,.context #company-info-button:focus-visible{background:#eaf0ff;border-color:#1950f5;outline:2px solid #a9bdff;outline-offset:2px}
#company-source-tooltip{position:fixed;z-index:1000;box-sizing:border-box;width:min(520px,calc(100vw - 32px));max-height:65vh;overflow:auto;padding:17px 20px;background:#fff;color:#172b4d;border:1px solid #cad8ed;border-radius:12px;box-shadow:0 10px 30px #10264b26;text-align:justify;font-family:var(--eios-font);font-size:14px;line-height:1.65;overflow-wrap:anywhere}
#company-source-tooltip[hidden]{display:none!important}
#company-source-tooltip #summary{color:inherit;font-size:14px;line-height:1.65;margin:0 0 12px;text-align:justify}
#company-source-tooltip .badge{display:block;color:inherit;font-size:13px;line-height:1.65;text-align:justify}
[data-theme=dark] .context #company-info-button{color:#d4e2ff;border-color:#8ca3c6}
[data-theme=dark] .context #company-info-button:hover,[data-theme=dark] .context #company-info-button:focus-visible{background:#243b61}
[data-theme=dark] #company-source-tooltip{background:#16243a;color:#e4edff;border-color:#526984;box-shadow:0 10px 30px #0006}
[data-view=propuestas] .po-intro{margin-bottom:14px}
'''

JS=r'''
(function compactCompanyHeader(){
 const company=$('company'),context=company.closest('.context'),host=company.parentElement,summary=$('summary');
 const line=document.createElement('div');line.className='po-company-line';company.before(line);line.append(company);
 const wrapper=document.createElement('span');wrapper.className='po-company-info';const button=document.createElement('button');button.type='button';button.id='company-info-button';button.textContent='i';button.setAttribute('aria-label','Información de la empresa y fuente documental');button.setAttribute('aria-expanded','false');button.setAttribute('aria-controls','company-source-tooltip');button.setAttribute('aria-describedby','company-source-tooltip');
 const panel=document.createElement('div');panel.id='company-source-tooltip';panel.setAttribute('role','tooltip');panel.hidden=true;panel.append(summary);
 const nature=Array.from(host.children).find(node=>node.matches('.badge')&&node.textContent.includes('Empresa ficticia'));if(nature)panel.append(nature);wrapper.append(button,panel);line.append(wrapper);
 let pinned=false,closeTimer;
 function position(){if(panel.hidden)return;const r=button.getBoundingClientRect(),width=panel.offsetWidth,height=panel.offsetHeight;panel.style.left=Math.max(12,Math.min(r.left,innerWidth-width-12))+'px';panel.style.top=(r.bottom+10+height<=innerHeight?r.bottom+10:Math.max(12,r.top-height-10))+'px'}
 function show(){panel.hidden=false;button.setAttribute('aria-expanded','true');position()}
 function hide(){panel.hidden=true;button.setAttribute('aria-expanded','false')}
 wrapper.addEventListener('mouseenter',()=>{clearTimeout(closeTimer);show()});wrapper.addEventListener('mouseleave',()=>{clearTimeout(closeTimer);closeTimer=setTimeout(()=>{if(!pinned&&!wrapper.contains(document.activeElement))hide()},150)});wrapper.addEventListener('focusin',show);wrapper.addEventListener('focusout',e=>{if(!pinned&&!wrapper.contains(e.relatedTarget))hide()});
 button.onclick=()=>{pinned=!pinned;pinned?show():hide()};wrapper.addEventListener('keydown',e=>{if(e.key==='Escape'){pinned=false;hide();e.stopPropagation()}});document.addEventListener('pointerdown',e=>{if(!wrapper.contains(e.target)){pinned=false;hide()}});
 addEventListener('resize',position);addEventListener('scroll',position,{capture:true,passive:true});new MutationObserver(position).observe(summary,{childList:true,subtree:true,characterData:true});
})();
'''

from eios.company_purchase_topbar_ui import CSS as TOPBAR_CSS, JS as TOPBAR_JS
CSS += TOPBAR_CSS
JS += TOPBAR_JS

from eios.company_purchase_review_gate_ui import CSS as REVIEW_GATE_CSS, JS as REVIEW_GATE_JS
CSS += REVIEW_GATE_CSS
JS += REVIEW_GATE_JS

from eios.company_purchase_lifecycle_ui import CSS as LIFECYCLE_CSS, JS as LIFECYCLE_JS
CSS += LIFECYCLE_CSS
JS += LIFECYCLE_JS

from eios.company_sidebar_ui import CSS as SIDEBAR_CSS, JS as SIDEBAR_JS
CSS += SIDEBAR_CSS
JS += SIDEBAR_JS

from eios.company_purchase_conditions_layout_ui import CSS as CONDITIONS_LAYOUT_CSS, JS as CONDITIONS_LAYOUT_JS
CSS += CONDITIONS_LAYOUT_CSS
JS += CONDITIONS_LAYOUT_JS
