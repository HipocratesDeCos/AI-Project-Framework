const assert=require('node:assert/strict'),{chromium}=require(process.env.EIOS_PLAYWRIGHT_MODULE||'playwright');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.EIOS_CHROMIUM_EXECUTABLE,args:['--no-sandbox']});const page=await browser.newPage({viewport:{width:1700,height:1100}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(process.env.EIOS_TEST_URL);await page.waitForFunction(()=>document.querySelector('#article').value==='A');await page.evaluate(()=>view('propuestas'));
 assert.equal(await page.locator('.po-intro h2').count(),0);const live=await page.locator('#po-guide-live').boundingBox();assert(live.width<=1&&live.height<=1);
 const size=await page.locator('#company').evaluate(e=>parseFloat(getComputedStyle(e).fontSize));assert(Math.abs(size-(20+8/3))<.05);
 const button=page.locator('#company-info-button'),panel=page.locator('#company-source-tooltip');assert.equal(await panel.isVisible(),false);await button.hover();await panel.waitFor({state:'visible'});assert.match(await panel.textContent(),/FUENTE EXCLUSIVA: Empresa.xlsx/);assert.match(await panel.textContent(),/Empresa ficticia/);
 const name=await page.locator('#company').boundingBox(),icon=await button.boundingBox();assert(icon.x>=name.x+name.width-1);
 await panel.hover();assert.equal(await panel.isVisible(),true);await page.mouse.move(1600,1000);await panel.waitFor({state:'hidden'});
 await button.focus();assert.equal(await panel.isVisible(),true);await page.keyboard.press('Escape');assert.equal(await panel.isVisible(),false);
 await button.click();assert.equal(await panel.isVisible(),true);await page.evaluate(()=>document.querySelector('#summary').textContent='FUENTE EXCLUSIVA: Nuevo.xlsx · Corte: 30/09/2026 · Documentos: 1 · Artículos: 10');assert.match(await panel.textContent(),/Nuevo.xlsx/);
 if(process.env.EIOS_SCREENSHOT_PATH)await page.screenshot({path:process.env.EIOS_SCREENSHOT_PATH+'-light.png'});
 await page.locator('#eios-theme-toggle').click();await button.click();assert.equal(await panel.isVisible(),true);
 await page.setViewportSize({width:390,height:900});await page.evaluate(()=>document.querySelector('#company').textContent='A Monkey in the Garden, S.L.');await button.click();await button.click();const bounds=await panel.boundingBox();assert(bounds.x>=0&&bounds.x+bounds.width<=390);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 if(process.env.EIOS_SCREENSHOT_PATH)await page.screenshot({path:process.env.EIOS_SCREENSHOT_PATH+'-mobile-dark.png'});
 assert.deepEqual(errors,[]);await browser.close();console.log('PASS compact header: removed title/status box, +2pt company, live source tooltip, hover/focus/Escape/click and mobile bounds');
})().catch(e=>{console.error(e);process.exit(1)});
