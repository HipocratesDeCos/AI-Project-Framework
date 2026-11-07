const assert=require('node:assert/strict');
const {chromium}=require(process.env.EIOS_PLAYWRIGHT_MODULE||'playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.EIOS_CHROMIUM_EXECUTABLE,args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:1536,height:1000}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.EIOS_TEST_URL);await page.waitForFunction(()=>typeof state!=='undefined'&&state?.purchases?.length===5);await page.evaluate(()=>view('propuestas'));
 await page.evaluate(()=>{const f=document.querySelector('#form');f.elements.quantity.value='37';f.elements.order_date.value='07/11/2026';f.elements.reference.value='MI-FORMULARIO-SIN-GUARDAR';f.elements.quantity.dispatchEvent(new Event('input',{bubbles:true}))});
 const original=await page.evaluate(()=>structuredClone(state.purchases));
 const draft=await page.locator('#form input,#form select,#form textarea').evaluateAll(nodes=>nodes.map(n=>({id:n.id,name:n.name,value:n.value,checked:n.checked,disabled:n.disabled})));
 await page.evaluate(async()=>await reviewSaved(state.purchases.find(p=>p.reference==='DEMO-CUOTAS').proposal_id,document.querySelector('#save')));
 assert.equal(await page.locator('#po-save').isVisible(),true);
 for(const width of [1536,390]){
  await page.setViewportSize({width,height:1000});
  for(const id of ['po-selection','po-references','po-conditions','po-payments']){
   await page.locator('.po-nav a[href="#'+id+'"]').click();
   assert.equal(await page.locator('#'+id).isVisible(),true);
   assert.equal(await page.locator('#'+id+'-saved').isVisible(),true);
   assert.equal(await page.locator('#'+id+' .po-guide-editable').isVisible(),false);
   assert.match(await page.locator('#'+id+' .po-guide-result p').textContent(),/DEMO-CUOTAS/);
   assert.equal(await page.locator('#'+id+'-saved input,#'+id+'-saved select,#'+id+'-saved textarea').count(),0);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  }
 }
 assert.match(await page.locator('#po-payments-saved').innerText(),/4.477,00/);assert.equal(await page.locator('#po-payments-saved tbody tr').count(),2);
 assert.match(await page.locator('#po-references-saved').textContent(),/500/);assert(!await page.locator('#po-references-saved').textContent().then(t=>t.includes('07/11/2026')));
 assert.deepEqual(await page.locator('#form input,#form select,#form textarea').evaluateAll(nodes=>nodes.map(n=>({id:n.id,name:n.name,value:n.value,checked:n.checked,disabled:n.disabled}))),draft);
 await page.locator('.po-nav a[href="#po-guide-agreement"]').click();await page.locator('#po-guide-back-to-study').click();assert.equal(await page.locator('#po-save').isVisible(),true);assert.equal(await page.locator('.po-alt-card:visible').count(),3);
 await page.locator('.po-nav a[href="#po-selection"]').click();await page.locator('#po-selection-saved').getByRole('button',{name:'Volver a mi formulario',exact:true}).click();await page.waitForFunction(()=>document.body.dataset.purchaseMode==='draft');assert.equal(await page.locator('#po-selection').isVisible(),true);
 assert.equal(await page.locator('#form [name=quantity]').inputValue(),'37');assert.equal(await page.locator('#form [name=reference]').inputValue(),'MI-FORMULARIO-SIN-GUARDAR');
 await page.evaluate(async()=>await reviewSaved(state.purchases.find(p=>p.reference==='DEMO-CUOTAS').proposal_id,document.querySelector('#save')));await page.locator('.po-nav a[href="#po-payments"]').click();await page.route('**/api/purchases/draft',route=>route.fulfill({status:409,contentType:'application/json',body:JSON.stringify({error:'La versión documental ha cambiado. Recarga antes de crear el borrador.'})}));await page.locator('#po-payments-saved').getByRole('button',{name:'Crear borrador desde este estudio',exact:true}).click();await page.waitForFunction(()=>document.querySelector('#po-payments-saved [role=status]')?.textContent.includes('La versión documental ha cambiado'));assert.equal(await page.locator('body').getAttribute('data-purchase-mode'),'saved');await page.unroute('**/api/purchases/draft');await page.locator('#po-payments-saved').getByRole('button',{name:'Crear borrador desde este estudio',exact:true}).click();await page.waitForFunction(()=>document.body.dataset.purchaseMode==='draft'&&document.querySelector('#form').elements.reference.value==='DEMO-CUOTAS-BORRADOR');assert.equal(await page.locator('#form [name=quantity]').inputValue(),'500');assert.equal(await page.locator('#payment-plan-rows>*').count(),2);
 // Legacy studies expose absent captures rather than borrowing current catalogue data.
 await page.route('**/api/purchases/review',async route=>{const response=await route.fetch(),data=await response.json();for(const key of ['supplier_commercial_at_save','article_description_at_save','price_reference_at_save','stock_context_at_save','stock_planning_at_save'])delete data.proposal[key];await route.fulfill({response,json:data})});
 await page.evaluate(async()=>await reviewSaved(state.purchases.find(p=>p.reference==='DEMO-CUOTAS').proposal_id,document.querySelector('#save')));await page.locator('.po-nav a[href="#po-selection"]').click();assert.match(await page.locator('#po-selection-saved').textContent(),/No conservado en este estudio/);assert(!await page.locator('#po-selection-saved').textContent().then(t=>t.includes('Suministros Jardín Demo')));await page.locator('.po-nav a[href="#po-references"]').click();assert.match(await page.locator('#po-references-saved').textContent(),/No conservado en este estudio/);await page.unroute('**/api/purchases/review');
 assert.deepEqual(await page.evaluate(()=>state.purchases),original);assert.deepEqual(errors,[]);await browser.close();console.log('PASS saved navigation: four historical steps, read-only captures, unchanged draft, quotas, return/copy actions and direct access to alternatives.');
})().catch(e=>{console.error(e);process.exit(1)});
