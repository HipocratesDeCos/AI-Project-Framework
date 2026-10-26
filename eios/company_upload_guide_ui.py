"""Progressive upload guide; moves existing controls without changing reception contracts."""
CSS = '''
[data-view=archivos] .upload-guide{max-width:1200px;margin:0 auto 32px}
[data-view=archivos] .upload-guide p,[data-view=archivos] .upload-guide label,[data-view=archivos] .upload-tools p,[data-view=archivos] .upload-tools label{font-size:16px;line-height:1.65;color:#24364b}
[data-view=archivos] .upload-guide small,[data-view=archivos] .upload-tools small{font-size:15px;line-height:1.6}
[data-view=archivos] .upload-step{border:2px solid #a7c5e6;border-radius:14px;background:#edf5ff;margin:18px 0;padding:22px}
[data-view=archivos] .upload-step:nth-of-type(2){background:#edf8f2;border-color:#a3cdb7}
[data-view=archivos] .upload-step:nth-of-type(3){background:#fff6e9;border-color:#dec39a}
[data-view=archivos] .upload-step:nth-of-type(4){background:#f4effc;border-color:#c7b6df}
[data-view=archivos] .upload-step>summary{font-size:21px;font-weight:700;cursor:pointer;padding:8px 0;color:#16365a}
[data-view=archivos] .upload-step input,[data-view=archivos] .upload-step select{font-size:16px;min-height:44px}
[data-view=archivos] .upload-guide button,[data-view=archivos] .upload-tools button{font-size:16px;margin:8px 12px 8px 0;padding:12px 18px}
[data-view=archivos] .upload-guide .card{background:transparent;border:0;box-shadow:none;padding:0}
[data-view=archivos] .upload-tools{background:#f1f3f5;border:2px solid #b6c0cb;border-radius:14px;padding:24px;margin-top:36px}
[data-view=archivos] .upload-tool{background:white;border:1px solid #b6c0cb;border-radius:10px;padding:18px;margin:16px 0}
[data-view=archivos] .upload-tool>summary{font-size:19px;font-weight:650;cursor:pointer;line-height:1.5}
[data-view=archivos] .upload-tools h3{font-size:18px}
[data-view=archivos] .upload-step [role=status]:not(:empty){padding:14px;border-left:4px solid #315b88;background:white;margin:16px 0;font-size:16px;line-height:1.6}
[data-view=archivos] .upload-guide :focus-visible,[data-view=archivos] .upload-tools :focus-visible{outline:3px solid #194f99;outline-offset:3px}
@media(max-width:700px){[data-view=archivos] .upload-step,[data-view=archivos] .upload-tools{padding:14px}[data-view=archivos] .upload-guide .fields{grid-template-columns:1fr}}
'''
JS = r'''
(()=>{
 const view=document.querySelector('[data-view="archivos"]');
 const guide=document.createElement('section');guide.className='upload-guide';guide.id='upload-guide';
 guide.innerHTML=`<h2>Carga de archivos · paso a paso</h2><p>Empieza por identificar la empresa. Después selecciona el archivo, comprueba el resultado y confirma su recepción. Puedes abrir cualquier paso para revisar lo que has indicado.</p><p><strong>¿Ya has cargado el archivo?</strong> Ve al paso 4 para consultar lo recibido antes de volver a subirlo.</p>
 <details class="upload-step" id="upload-step-1" open><summary>1 · Identifica la empresa</summary><p>Estos datos indican a qué empresa pertenece el archivo. Utiliza el mismo código en todas sus cargas; para A Monkey, conserva el código de su expediente existente. La fecha de corte indica a qué fecha se refieren los datos.</p><div id="upload-context"></div><p>El código admite letras sin acentos, números, puntos, guiones y guiones bajos (hasta 80 caracteres). La razón social es el nombre completo de la empresa.</p><p id="upload-context-error" role="status"></p><button type="button" id="upload-next-file" class="primary">Continuar al paso 2</button></details>
 <details class="upload-step" id="upload-step-2"><summary>2 · Elige el archivo y comprueba su contenido</summary><p>Para el libro que hemos preparado con varias hojas, utiliza la primera opción. Si recibes un archivo independiente, elige la segunda.</p><label>Qué vas a cargar<select id="upload-route"><option value="workbook">Libro Excel completo con guía de carga</option><option value="single">Una tabla Excel/CSV o un PDF de soporte</option></select></label><div id="upload-workbook"></div><div id="upload-single" hidden></div><button type="button" id="upload-next-review">Ver revisión · paso 3</button></details>
 <details class="upload-step" id="upload-step-3"><summary>3 · Revisa los avisos y confirma la recepción</summary><p>Primero pulsa «Comprobar» en el paso 2. Aquí aparecerá el resultado. Si hay errores, corrige el archivo y vuelve a comprobarlo. El botón de guardar aparecerá cuando la comprobación permita recibir los datos.</p><div id="upload-review-workbook"></div><div id="upload-review-single" hidden></div><p><strong>Guardar conserva el archivo en el expediente.</strong> Su uso en las propuestas requiere la revisión y selección posteriores; esta comprobación no acredita la viabilidad de una compra o venta.</p><button type="button" id="upload-next-finish">Consultar recepción · paso 4</button></details>
 <details class="upload-step" id="upload-step-4"><summary>4 · Localiza lo recibido y revisa el siguiente paso</summary><p>Abre los expedientes recibidos y selecciona la empresa y fecha de corte. Comprueba que el archivo aparece, consulta sus filas y revisa las incidencias antes de preparar una versión para las propuestas.</p><button type="button" id="upload-open-dossiers" class="primary">Abrir expedientes recibidos</button><p>Puedes conservar una selección como versión desde ese apartado. Las opciones de preparación y activación explican qué datos pueden utilizarse y cuáles siguen pendientes.</p></details>`;
 const toolsPanel=document.createElement('section');toolsPanel.className='upload-tools';toolsPanel.id='upload-tools';toolsPanel.innerHTML='<h2>Consultas y otras opciones</h2><p>Esta zona está separada del recorrido de carga. Abre únicamente la herramienta que necesites para consultar expedientes, preparar plantillas o gestionar datos ya recibidos.</p>';
 const reception=$('files-reception'),workbook=$('workbook-file').closest('section');
 const context=$('reception-company-id').closest('.files-step');context.querySelector('h3').remove();$('reception-numbers').closest('label') && context.querySelector('.fields').append($('reception-numbers').closest('label'));
 guide.querySelector('#upload-context').append(context);
 const review=guide.querySelector('#upload-review-workbook');['workbook-summary','workbook-results','workbook-details','workbook-save'].forEach(id=>review.append($(id)));
 guide.querySelector('#upload-workbook').append(workbook);
 const single=guide.querySelector('#upload-single');
 Array.from(reception.children).filter(el=>el.classList.contains('files-step')).forEach(el=>{if(el.id==='reception-preview-panel')guide.querySelector('#upload-review-single').append(el);else single.append(el)});
 single.querySelectorAll('h3').forEach(el=>el.textContent=el.textContent.replace(/^\d+\. /,''));
 reception.remove();view.querySelector('.files-heading')?.remove();view.querySelector('.files-routes')?.remove();
 const extras=Array.from(view.children);view.prepend(guide);view.append(toolsPanel);
 extras.forEach(el=>{const wrapper=document.createElement('details');wrapper.className='upload-tool';const title=document.createElement('summary');title.textContent=el.querySelector('h2,h3')?.textContent||'Otras herramientas';wrapper.append(title,el);toolsPanel.append(wrapper)});
 const openStep=n=>{const step=$('upload-step-'+n);step.open=true;step.querySelector('summary').focus();step.scrollIntoView?.({behavior:'smooth',block:'start'})};
 function checkContext(){const ids=['reception-company-id','reception-company-name','reception-material','reception-cutoff'];const missing=ids.find(id=>!$(id).value.trim());const invalid=missing||(!/^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$/.test($('reception-company-id').value)?'reception-company-id':null);if(invalid){openStep(1);$('upload-context-error').textContent='Completa los datos de empresa antes de comprobar el archivo. Revisa el campo señalado.';$(invalid).focus();return false}$('upload-context-error').textContent='Datos de empresa indicados. Continúa con el archivo; EIOS comprobará su validez.';return true}
 $('upload-next-file').onclick=()=>{if(checkContext())openStep(2)};
 $('upload-next-review').onclick=()=>openStep(3);$('upload-next-finish').onclick=()=>openStep(4);
 ['workbook-check','reception-read','reception-check'].forEach(id=>$(id).addEventListener('click',e=>{if(!checkContext()){e.preventDefault();e.stopImmediatePropagation()}},true));
 $('upload-route').onchange=()=>{const wb=$('upload-route').value==='workbook';$('upload-workbook').hidden=!wb;$('upload-single').hidden=wb;$('upload-review-workbook').hidden=!wb;$('upload-review-single').hidden=wb};
 $('upload-open-dossiers').onclick=()=>{const panel=$('files-dossiers').closest('.upload-tool');panel.open=true;panel.querySelector('summary').focus();panel.scrollIntoView?.({behavior:'smooth',block:'start'})};
 new MutationObserver(()=>{if($('workbook-summary').textContent) $('upload-step-3').open=true}).observe($('workbook-summary'),{childList:true,subtree:true});
 new MutationObserver(()=>{if(!$('reception-preview-panel').hidden)$('upload-step-3').open=true}).observe($('reception-preview-panel'),{attributes:true,attributeFilter:['hidden']});
})();
'''
