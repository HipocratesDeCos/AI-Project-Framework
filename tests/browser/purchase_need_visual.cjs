const assert=require('node:assert/strict'),{chromium}=require(process.env.EIOS_PLAYWRIGHT_MODULE||'playwright');
(async()=>{
 const extra=process.env.EIOS_CHROMIUM_ARGS?JSON.parse(process.env.EIOS_CHROMIUM_ARGS):['--no-sandbox'];
 const browser=await chromium.launch({executablePath:process.env.EIOS_CHROMIUM_EXECUTABLE,args:extra});
 const page=await browser.newPage({viewport:{width:1700,height:1900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.EIOS_TEST_URL);await page.waitForFunction(()=>document.querySelector('#article').value==='A');
 await page.evaluate(()=>{view('propuestas');purchaseGuideNavigate('po-references');const f=document.querySelector('#form');for(const [key,v]of Object.entries({quantity:'400',order_date:'04/11/2026'})){f.elements[key].value=v;f.elements[key].dispatchEvent(new Event('change',{bubbles:true}))}const enabled=document.querySelector('#po-stock-enabled');enabled.checked=true;enabled.dispatchEvent(new Event('change',{bubbles:true}));for(const [key,v]of Object.entries({available_at_order:'60',daily_demand:'5',lead_time_days:'7',target_days:'30',safety_stock:'20',purchase_step:'10',actor:'Responsable ficticio',source_reference:'PRUEBA-UI-01'}))document.querySelector('#po-stock-'+key).value=v;document.querySelector('#po-stock-receipts').value='18/11/2026; 50';const ack=document.querySelector('#po-stock-ack');ack.checked=true;ack.dispatchEvent(new Event('change',{bubbles:true}))});
 await page.waitForSelector('#po-need-calculation table');await page.evaluate(()=>document.fonts.ready);
 assert.match(await page.locator('#po-need-calculation .po-need-total').textContent(),/100/);assert.match(await page.locator('#po-need-reading').textContent(),/300/);
 const cols=await page.locator('#po-references>.po-guide-editable').evaluate(e=>getComputedStyle(e).gridTemplateColumns);assert.equal(cols.split(' ').length,2);
 if(process.env.EIOS_SCREENSHOT_PATH)await page.locator('#po-references').screenshot({path:process.env.EIOS_SCREENSHOT_PATH+'-light.png'});
 await page.locator('#eios-theme-toggle').click();if(process.env.EIOS_SCREENSHOT_PATH)await page.locator('#po-references').screenshot({path:process.env.EIOS_SCREENSHOT_PATH+'-dark.png'});
 await page.setViewportSize({width:390,height:900});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 if(process.env.EIOS_SCREENSHOT_PATH)await page.locator('#po-references').screenshot({path:process.env.EIOS_SCREENSHOT_PATH+'-mobile.png'});
 await page.locator('#po-stock-daily_demand').fill('');await page.locator('#po-stock-daily_demand').dispatchEvent('change');await page.waitForFunction(()=>document.querySelector('#po-need-calculation').querySelectorAll('table').length===0);
 assert.deepEqual(errors,[]);await browser.close();console.log('PASS browser: reference example 100 vs 400, two columns, light/dark, mobile overflow and invalidation');
})().catch(e=>{console.error(e);process.exit(1)});
