"""Explicit workbook reception beside the existing per-sheet workflow."""
HTML = '''<section class="card"><h2>Cargar un libro con varias hojas</h2>
<p>Se utilizarán los datos de empresa del paso 1. Selecciona el libro preparado para EIOS, que incluye la hoja <strong>97_Guia_Carga</strong> para identificar automáticamente sus tablas.</p>
<p>Se comprueban formatos, referencias y coincidencias con archivos recibidos del mismo corte. El catálogo activo y las propuestas se conservan. Esta comprobación no concilia financieramente todo el expediente.</p>
<label>Libro Excel <input id="workbook-file" type="file" accept=".xlsx"></label>
<button id="workbook-check" type="button">Comprobar todas las hojas</button>
<div id="workbook-summary" role="status"></div><div id="workbook-results" class="scroll"></div>
<div id="workbook-details"></div><button id="workbook-save" type="button" class="primary" hidden>Confirmar y guardar las hojas comprobadas</button>
<p>Las hojas auxiliares se conservan en el archivo original, sin importarse como registros. Los precios sin vigencia no se activan como tarifas. Tras guardar, revisa el expediente y selecciona expresamente los datos para las propuestas.</p></section>'''

JS = r'''
let workbookTicket=null,workbookSequence=0,workbookBusy=false;
function workbookInvalidate(){workbookSequence++;workbookTicket=null;$('workbook-save').hidden=true;$('workbook-results').replaceChildren();$('workbook-details').replaceChildren();$('workbook-summary').textContent='Revisa y comprueba el libro con los datos actuales.'}
['workbook-file','reception-company-id','reception-company-name','reception-material','reception-cutoff','reception-numbers'].forEach(id=>$(id).addEventListener('input',workbookInvalidate));
$('workbook-check').onclick=async()=>{
 if(workbookBusy)return;workbookInvalidate();const revision=workbookSequence,file=$('workbook-file').files[0];
 if(!file||!file.name.toLowerCase().endsWith('.xlsx')||file.size>10*1024*1024){$('workbook-summary').textContent='Selecciona un XLSX de hasta 10 MiB.';return}
 const options={company_id:$('reception-company-id').value,legal_name:$('reception-company-name').value,material_nature:$('reception-material').value,as_of_date:$('reception-cutoff').value,number_format:$('reception-numbers').value};
 workbookBusy=true;$('workbook-check').disabled=true;$('workbook-summary').textContent='Comprobando hojas y referencias…';
 try{const r=await api('/api/reception/workbook/preview',{method:'POST',headers:{'Content-Type':'application/octet-stream','X-EIOS-Token':token,'X-EIOS-Filename':encodeURIComponent(file.name),'X-EIOS-Workbook':encodeURIComponent(JSON.stringify(options))},body:file});
 if(revision!==workbookSequence)return;workbookTicket=r.ticket;
 receptionTable('workbook-results',['Hoja','Contenido','Filas','Errores','Recepción'],r.sheets.map(s=>[s.sheet,receptionLabels[s.kind]||s.kind,s.rows,s.error_count,({NEW:'Nueva',UNCHANGED:'Ya recibida: se conserva',CONFLICT:'Conflicto: revisar'})[r.comparison?.find(c=>c.sheet===s.sheet)?.status]||'No preparada']));
 const messages=[...(r.ignored_sheets?.length?['Hojas auxiliares conservadas: '+r.ignored_sheets.join(', ')]:[]),...r.sheets.flatMap(s=>[...s.errors.map(e=>s.sheet+' · fila '+e.row+': '+e.messages.join('; ')),...s.warnings.map(w=>s.sheet+': '+w)]),...(r.reference_issues||[]).map(i=>i.message)];
 messages.forEach(m=>{const p=document.createElement('p');p.textContent=m;$('workbook-details').append(p)});
 $('workbook-summary').textContent=r.ticket?'Revisión preparada. Confirma para recibir el lote completo; no se activará para tomar decisiones.':'No se puede guardar el lote. Revisa los errores o las referencias coincidentes.';$('workbook-save').hidden=!r.ticket;
 }catch(e){if(revision===workbookSequence)$('workbook-summary').textContent=e.message}finally{workbookBusy=false;$('workbook-check').disabled=false}
};
$('workbook-save').onclick=async()=>{if(!workbookTicket||workbookBusy)return;const ticket=workbookTicket,revision=workbookSequence;workbookBusy=true;$('workbook-save').disabled=true;$('workbook-check').disabled=true;
 try{const r=await api('/api/reception/workbook/commit',{method:'POST',headers:{'Content-Type':'application/json','X-EIOS-Token':token},body:JSON.stringify({ticket})});if(revision!==workbookSequence)return;workbookTicket=null;$('workbook-save').hidden=true;$('workbook-summary').textContent=r.batch_ids.length+' hojas recibidas; '+r.unchanged_batch_ids.length+' ya existentes conservadas. Consulta Expedientes recibidos. Pendiente de admisión y selección para propuestas.';try{await received()}catch(e){$('workbook-summary').textContent+=' No se pudo actualizar la lista: '+e.message}}
 catch(e){if(revision===workbookSequence){workbookTicket=null;$('workbook-save').hidden=true;$('workbook-summary').textContent=e.message}}
 finally{workbookBusy=false;$('workbook-save').disabled=false;$('workbook-check').disabled=false}
};
'''
