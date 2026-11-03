// Real Chromium check. EIOS_PLAYWRIGHT_MODULE and EIOS_CHROMIUM_EXECUTABLE are optional.
const {chromium}=require(process.env.EIOS_PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.EIOS_CHROMIUM_EXECUTABLE||undefined,headless:true,args:['--no-sandbox','--disable-gpu','--disable-software-rasterizer','--single-process','--no-zygote']});
 try{
  const page=await browser.newPage({viewport:{width:1600,height:1100},locale:'es-ES'}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(process.env.EIOS_TEST_URL);await page.locator('#article').waitFor({state:'attached'});await page.waitForFunction(()=>document.getElementById('article').value==='A');
  await page.locator('[data-nav=propuestas]').click();const form=page.locator('#form'),ribbon=page.locator('#po-draft-ribbons');
  assert((await ribbon.innerText()).includes('2'));assert.equal(await ribbon.locator('.po-identity strong').count(),3);assert.equal(await ribbon.locator('.po-metric').count(),5);
  await page.getByRole('link',{name:'Condiciones',exact:true}).click();
  await form.locator('[name=quantity]').fill('2');await form.locator('[name=unit_price]').fill('100');
  page.once('dialog',d=>d.accept());await page.getByRole('button',{name:'Introducir precio y descuento',exact:true}).click();assert.equal(await form.locator('[name=unit_price]').inputValue(),'');
  await form.locator('[name=unit_price]').fill('100');await form.locator('[name=discount_value]').fill('10');await form.locator('[name=vat_percent]').fill('21');
  await page.getByRole('link',{name:'Cuotas y portes',exact:true}).click();await form.locator('[name=order_date]').fill('22/10/2026');await form.locator('[name=due_date]').fill('30/11/2026');await form.locator('[name=shipping_mode]').selectOption('NONE');
  await page.waitForFunction(()=>document.getElementById('po-totals').textContent.includes('217,80'));
  await page.getByRole('link',{name:'Guardar y documentos',exact:true}).click();await form.locator('[name=reference]').fill('UX-NUEVA');
  await ribbon.getByRole('button',{name:'Ver stock, demanda y fuentes'}).click();assert.equal(await page.locator('.po-context>details[open]').count(),2);await page.locator('#po-save').scrollIntoViewIfNeeded();await page.evaluate(()=>window.scrollBy(0,600));const pos=await ribbon.boundingBox();assert(pos.y>=-1&&pos.y<12,'Draft ribbon is pinned');
  if(process.env.EIOS_SCREENSHOT_DIR)await page.screenshot({path:process.env.EIOS_SCREENSHOT_DIR+'/purchase-draft.png'});
  await page.getByRole('button',{name:'Guardar propuesta y abrir revisión',exact:true}).click();await page.locator('#purchase-comparison').waitFor();
  const saved=page.locator('#po-saved-ribbons');assert((await saved.innerText()).includes('ESTUDIO GUARDADO'));assert((await saved.innerText()).includes('2'));
  const comp=page.locator('#purchase-comparison');assert.equal(await comp.locator('.po-negotiation-grid>section').count(),3);
  await comp.getByLabel('Responsable',{exact:true}).fill('QA visual');await comp.getByLabel('Nuevo precio por unidad (opcional)',{exact:true}).fill('100');await comp.getByLabel('Descuento porcentual alternativo (opcional)',{exact:true}).fill('5');
  await comp.getByLabel('Comparar respuesta recibida').check();await comp.getByLabel('Precio de respuesta antes de descuentos',{exact:true}).fill('100');await comp.getByLabel('Descuento de respuesta (%)',{exact:true}).fill('8');
  await comp.getByRole('button',{name:'Comparar y conservar estudio',exact:true}).click();await comp.locator('.comparison-status').filter({hasText:'ESTUDIO GUARDADO.'}).waitFor();
  const row=comp.locator('.comparison-result').last();assert((await row.innerText()).includes('Respuesta del proveedor'));assert((await row.innerText()).includes('222,64'));assert((await row.innerText()).includes('229,90'));
  // Editing a draft must not change the saved proposal ribbon.
  const before=await saved.innerText();await page.getByRole('link',{name:'Condiciones',exact:true}).click();await form.locator('[name=quantity]').fill('99');assert.equal(await saved.innerText(),before);assert((await ribbon.innerText()).includes('99'));
  await comp.scrollIntoViewIfNeeded();const savedPos=await saved.boundingBox();assert(savedPos.y>=-1&&savedPos.y<12,'Saved ribbon pinned inside review');
  if(process.env.EIOS_SCREENSHOT_DIR)await page.screenshot({path:process.env.EIOS_SCREENSHOT_DIR+'/purchase-comparison.png'});
  await page.setViewportSize({width:900,height:1100});await comp.scrollIntoViewIfNeeded();assert(!await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth));if(process.env.EIOS_SCREENSHOT_DIR)await page.screenshot({path:process.env.EIOS_SCREENSHOT_DIR+'/purchase-narrow.png'});
  assert.deepEqual(errors,[]);console.log('PASS purchase experience: pinned ribbons, real source values, explicit discount, tabs, save, two alternatives, history and 900px layout.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
