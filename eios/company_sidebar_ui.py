"""Collapsible application navigation with a persistent, keyboard-accessible toggle."""
CSS='''
body{--eios-menu-width:248px}
#eios-menu-toggle{position:fixed;top:18px;left:calc(var(--eios-menu-width) - 46px);z-index:80;width:36px;height:36px;border:1px solid #50617d;border-radius:9px;background:#152c56;color:#fff;display:grid;place-items:center;cursor:pointer;font-size:25px;line-height:1;padding:0}
#eios-menu-toggle:focus-visible{outline:3px solid #8fb5ff;outline-offset:3px}
.sidebar .brand{padding-right:38px}.sidebar .eios-menu-label{min-width:0}
body.eios-menu-collapsed .sidebar{width:72px;padding:66px 8px 18px}
body.eios-menu-collapsed .sidebar .brand,body.eios-menu-collapsed .eios-menu-label{display:none}
body.eios-menu-collapsed .sidebar .nav{justify-content:center;gap:0;padding:14px 8px}
body.eios-menu-collapsed .topbar,body.eios-menu-collapsed main{margin-left:72px}
body.eios-menu-collapsed #eios-menu-toggle{left:18px}
#eios-menu-backdrop{position:fixed;inset:0;z-index:49;border:0;background:#050b1a80}
@media(max-width:1000px){body{--eios-menu-width:210px}}
@media(max-width:700px){body{--eios-menu-width:248px}.sidebar{position:fixed;inset:0 auto 0 0;width:248px;height:100dvh;z-index:50;padding:66px 12px 18px}.sidebar .brand{font-size:28px;margin-bottom:20px}.sidebar nav{display:block;overflow:visible}.sidebar .nav{width:100%;flex-shrink:1;padding:14px 10px}.sidebar .nav svg{width:24px;height:24px}body.eios-menu-collapsed .sidebar{display:none}body .topbar,body main,body.eios-menu-collapsed .topbar,body.eios-menu-collapsed main{margin-left:0}.topbar{padding-left:64px;min-height:72px}body.eios-menu-mobile-open{overflow:hidden}}
'''
JS=r'''
(function(){
 const sidebar=document.querySelector('.sidebar');if(!sidebar)return;sidebar.id='eios-main-menu';const mobile=matchMedia('(max-width:700px)'),key='eios.sidebar.collapsed';let collapsed=mobile.matches;try{const value=localStorage.getItem(key);if(value!==null)collapsed=value==='true'}catch{}
 for(const item of sidebar.querySelectorAll('[data-nav]')){const label=item.textContent.trim();item.title=label;item.setAttribute('aria-label',label);const span=document.createElement('span');span.className='eios-menu-label';for(const child of Array.from(item.childNodes))if(child.nodeType===3)span.append(child);item.append(span)}
 const toggle=document.createElement('button');toggle.id='eios-menu-toggle';toggle.type='button';toggle.setAttribute('aria-controls',sidebar.id);const backdrop=document.createElement('button');backdrop.id='eios-menu-backdrop';backdrop.type='button';backdrop.tabIndex=-1;backdrop.setAttribute('aria-label','Cerrar menú principal');document.body.append(backdrop,toggle);
 function render(){document.body.classList.toggle('eios-menu-collapsed',collapsed);document.body.classList.toggle('eios-menu-mobile-open',mobile.matches&&!collapsed);toggle.setAttribute('aria-expanded',String(!collapsed));toggle.setAttribute('aria-label',collapsed?'Desplegar menú principal':'Contraer menú principal');toggle.title=toggle.getAttribute('aria-label');toggle.textContent=collapsed?'☰':'‹';backdrop.hidden=!mobile.matches||collapsed;sidebar.inert=mobile.matches&&collapsed;window.dispatchEvent(new Event('resize'))}
 function set(value){collapsed=value;try{localStorage.setItem(key,String(value))}catch{}render()}
 toggle.onclick=()=>set(!collapsed);backdrop.onclick=()=>{set(true);toggle.focus()};document.addEventListener('keydown',event=>{if(event.key==='Escape'&&mobile.matches&&!collapsed){set(true);toggle.focus()}});
 sidebar.addEventListener('click',event=>{if(mobile.matches&&event.target.closest('[data-nav]')){set(true);toggle.focus()}});mobile.addEventListener('change',()=>{if(mobile.matches)collapsed=true;render()});render();
})();
'''
