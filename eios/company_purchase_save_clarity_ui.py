"""Explain saved-study progress without changing evidence or execution contracts."""
CSS = '''
#review-panel .review-header{background:#edf4ff;border-bottom-color:#c6d7ed}#review-panel .review-status-label{color:#274b79}
#review-panel .review-finance-card{border-left-color:#b8cee9}
#review-finance .review-pending-note,#review-amount .review-pending-note{background:#eef4fc;border-left-color:#9bb8dc;color:#355372}
.po-save-progress{margin:16px 0;padding:14px;border:1px solid #bfd2ed;border-radius:8px;background:#f5f9ff}.po-save-progress h3{margin:0 0 10px;font-size:15px}.po-save-progress p{line-height:1.5;margin:7px 0!important}
.po-save-status{padding:12px;border-radius:6px;background:#edf4ff;margin:10px 0}.po-save-status strong{display:block;font-size:14px}.po-save-status.is-complete{background:#e4f4e9;color:#195d32}.po-save-status.is-action{background:#fff3db;border-left:4px solid #bd801c;color:#744c0c}.po-save-status.is-conflict{background:#fde6e4;border-left:4px solid #b83d32;color:#862820}
#review-panel .po-save-technical{margin-top:16px;padding:12px;border:1px solid #cfdbeb;border-radius:6px;background:#fbfdff}#review-panel .po-save-technical>summary{font-weight:bold;color:#173e76;cursor:pointer}
.po-user-tasks{line-height:1.6}.po-user-tasks li{margin:8px 0}.po-user-tasks button{margin-left:8px}
'''
JS = r'''
(function clarifyPurchaseSave(){
 const save=$('po-save'),heading=save.querySelector('.po-heading');heading.querySelector('h2').textContent='GUARDAR Y CONSULTAR EL ESTUDIO';heading.querySelector('p').textContent='Indica una referencia y guarda. Después verás qué se ha calculado y qué requiere revisión. Guardar no confirma un pedido.';
 $('save').textContent='Guardar propuesta y consultar estudio';
 function paragraph(box,text){const p=document.createElement('p');p.textContent=text;box.append(p);return p}
 function status(box,title,text,kind='info'){const card=document.createElement('div');card.className='po-save-status'+(kind==='info'?'':' is-'+kind);const h=document.createElement('strong');h.textContent=title;card.append(h);paragraph(card,text);box.append(card);return card}
 const oldPlan=renderPaymentPlan;
 renderPaymentPlan=function(container,plan,report){oldPlan(container,plan);if(!plan||plan.status==='NOT_DECLARED')return;const notes=container.querySelectorAll('.review-note'),last=notes[notes.length-1];if(last)last.remove();const title=Array.from(container.querySelectorAll('h3')).find(n=>n.textContent.startsWith('CALENDARIO DECLARADO'));if(title)title.textContent='CALENDARIO GUARDADO · IMPORTES COMPROBADOS';
  paragraph(container,'Las cuotas suman los costes declarados con IVA y sus fechas cumplen las comprobaciones del formulario.');
  const cash=report?.proposal?.cash_orientation_at_save;
  paragraph(container,cash?.scenario&&cash.payment_basis==='DECLARED_INSTALLMENTS'?'Estas cuotas se han usado en la simulación guardada de esta compra.':'El calendario está guardado. Su uso en la simulación se indica en el estado financiero de este estudio.');
  paragraph(container,'Guardar cuotas no crea movimientos en el libro ni acredita un acuerdo con el proveedor. El soporte y las relaciones con pagos existentes se revisan por separado.');
 };
 const oldFinance=renderFinancialContext;
 renderFinancialContext=function(report){oldFinance(report);const box=$('review-finance'),technical=document.createElement('details'),technicalTitle=document.createElement('summary');technical.id='po-financial-checks';technical.className='po-save-technical';technicalTitle.textContent='Abrir revisiones documentales y detalle financiero';technical.append(technicalTitle,...Array.from(box.childNodes));box.append(technical);
  const overview=document.createElement('section');overview.className='po-save-progress';overview.id='po-save-progress';const h=document.createElement('h3');h.textContent='ESTADO DEL ESTUDIO GUARDADO';overview.append(h);technical.before(overview);
  const proposal=report.proposal||{},plan=proposal.payment_plan,cash=proposal.cash_orientation_at_save,execution=report.finance_execution,projection=execution?.finance_result?.projection,coverage=report.payment_associations?.declared_calendar_coverage,review=report.payment_documentary_review,context=report.financial_context;
  status(overview,'GUARDADO COMPLETADO','La propuesta y su estudio se conservan. Puedes consultar el informe o preparar un borrador comercial. No se ha enviado un pedido ni registrado una aceptación.','complete');
  const tasks=[];
  if(cash?.scenario&&['WITHIN_DECLARED_SCENARIO','SHORTFALL'].includes(cash.status)){
   status(overview,cash.status==='SHORTFALL'?'SIMULACIÓN CALCULADA · RESERVA INSUFICIENTE':'SIMULACIÓN CALCULADA · RESERVA RESPETADA',(cash.payment_basis==='DECLARED_INSTALLMENTS'?'Incluye las cuotas de esta propuesta. ':'Usa las hipótesis de pago indicadas en el estudio. ')+(cash.status==='SHORTFALL'?'Faltan '+money(cash.scenario.deficit)+' euros para respetar el mínimo. Revisa condiciones, cuotas o financiación antes de decidir.':'El escenario declarado respeta el mínimo de tesorería. Esto no confirma disponibilidad bancaria ni autoriza la compra.'),cash.status==='SHORTFALL'?'action':'complete');
   if(cash.status==='SHORTFALL')tasks.push({text:'Antes de decidir: revisa las condiciones de pago o una financiación documentada. La propuesta ya está guardada.',target:'conditions'});
  }else{
   status(overview,'SIMULACIÓN NO CALCULADA',cash?.message||'Este estudio no conserva una simulación de la compra. No afecta al guardado de la propuesta.','action');
   const message=cash?.message||'completa los datos y prepara una nueva propuesta con el expediente vigente.';
   if(message.includes('fictici'))paragraph(overview,'Es un límite de la simulación actual, no un dato que debas corregir ni una instrucción para cambiar la naturaleza del expediente.');
   else tasks.push({text:'Para obtener una simulación: '+message,target:message.includes('Parámetros')?'parameters':message.includes('saldo de tesorería')||message.includes('cobros y pagos')||message.includes('vencidos al corte')?'files':message.includes('coincide en fecha e importe')?'checks':'conditions'});
  }
  if(context?.financial_snapshot&&context.financial_snapshot.available_treasury!==null&&context.financial_snapshot.available_treasury!==undefined)status(overview,'DATOS FINANCIEROS VINCULADOS','Saldo al '+stockDate(context.as_of_date)+': '+money(context.financial_snapshot.available_treasury)+' '+context.financial_snapshot.currency+'. Son los datos documentales usados por el estudio; no requieren volver a cargarse por el mero hecho de ver una nota informativa.');
  else {status(overview,'FALTA EL SALDO FINANCIERO VINCULADO','Para calcular la tesorería, revisa la empresa, fecha de corte y datos de caja/bancos de la versión activa.','action');tasks.push({text:'Vincula un saldo de caja/bancos de la misma empresa y fecha de corte. No añadas una aportación ficticia para eliminar el aviso.',target:'files'});}
  if(execution?.status==='EXECUTED'&&projection?.status==='DETERMINED')status(overview,'PROYECCIÓN DEL LIBRO CALCULADA','Muestra los movimientos financieros documentados. Se consulta aparte de la simulación de esta nueva compra para evitar confundir sus alcances.');
  else {status(overview,'PROYECCIÓN DEL LIBRO NO DISPONIBLE',execution?.message||'Consulta los requisitos en el detalle financiero. El guardado ya está completado.','action');tasks.push({text:'Para calcular la proyección del libro: '+(execution?.message||'revisa los datos financieros vinculados.'),target:!context?.financial_snapshot?'files':execution?.parameter_configurations?.length===2?'checks':'parameters'});}
  if(plan&&plan.status!=='NOT_DECLARED'){
   const conflict=coverage?.status==='CONFLICTING_DECLARATIONS'||Number(review?.conflict_count)>0;
   const reviewed=review?.status==='FINDINGS_RECORDED';
   status(overview,conflict?'REVISIÓN DOCUMENTAL · CONFLICTOS REGISTRADOS':reviewed?'REVISIÓN DOCUMENTAL · COMPROBACIONES REGISTRADAS':'REVISIÓN DOCUMENTAL · POR COMPLETAR',reviewed?'Confirmaciones registradas: '+(review.confirmed_count||0)+' · No confirmadas: '+(review.not_confirmed_count||0)+' · Conflictos: '+(review.conflict_count||0)+' · Controles pendientes: '+(review.pending_control_count??review.pending_controls?.length??0)+'. Registrar comprobaciones no equivale a una validación automática del acuerdo.':'Las cuotas están cuadradas. Antes de tratarlas como compromisos confirmados, contrasta el acuerdo y comprueba si algún pago ya está en tesorería.',conflict?'conflict':'info');
   tasks.push({text:'Antes de confirmar la operación: coteja pedido o confirmación, cuotas y vencimientos. Identifica pagos ya existentes por operación y soporte; coincidir en fecha e importe no basta. '+(coverage?'Asociaciones declaradas: '+(coverage.associated_count||0)+' de '+(coverage.installment_count||0)+'.':''),target:'checks'});
  }else status(overview,'CALENDARIO SIN CUOTAS DECLARADAS','No se ha guardado un reparto en cuotas. Si deseas fraccionar el pago, prepara el calendario en Organizar los pagos; no es un error de guardado.');
  const tasksTitle=document.createElement('h3');tasksTitle.textContent='QUÉ TIENES QUE HACER';overview.append(tasksTitle);const list=document.createElement('ul');list.id='po-save-user-tasks';list.className='po-user-tasks';
  const seen=new Set();for(const task of tasks){if(seen.has(task.text))continue;seen.add(task.text);const item=document.createElement('li');item.append(document.createTextNode(task.text));const button=document.createElement('button');button.type='button';button.className='review-button';button.textContent={checks:'Abrir revisión',parameters:'Ir a Parámetros',files:'Ir a Carga de archivos',conditions:'Preparar cambios en un borrador'}[task.target];button.onclick=()=>{if(task.target==='checks'){technical.open=true;technical.scrollIntoView({behavior:'smooth',block:'start'})}else if(task.target==='parameters')view('parametros');else if(task.target==='files')view('archivos');else{document.querySelector('.po-nav a[href="#po-conditions"]').click();const create=$('po-create-study-draft');if(create){create.focus({preventScroll:true});create.scrollIntoView({block:'center'})}}};item.append(button);list.append(item)}overview.append(list);if(!tasks.length)paragraph(overview,'No hay una acción adicional indicada para consultar este estudio. Revisa los resultados antes de decidir.');
  paragraph(overview,'Revisar otros gastos y confirmar la disponibilidad bancaria corresponde a la revisión de la operación. Los límites técnicos de EIOS no se resuelven añadiendo datos inventados al Excel.');
  $('review-title').textContent='PROPUESTA GUARDADA';$('review-reason').textContent=(report.reference||proposal.reference||'')+' · El guardado está completado. Consulta el estado del cálculo y las acciones de abajo.';
  paragraph(technical,'Resultado técnico conservado: '+(report.title||'')+' · '+(report.reason||''));
 };
})();
'''
