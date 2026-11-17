const {JSDOM,VirtualConsole}=require(process.env.EIOS_JSDOM_MODULE||'jsdom'),assert=require('node:assert/strict');
(async()=>{
 const url=process.env.EIOS_TEST_URL,errors=[],vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));
 const dom=new JSDOM(await(await fetch(url)).text(),{url,runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,beforeParse(w){w.AbortController=AbortController;w.matchMedia=q=>({matches:q.includes('min-width'),addEventListener(){},removeEventListener(){}});w.fetch=(p,o)=>fetch(new URL(p,url),o);w.HTMLElement.prototype.scrollIntoView=function(){};}});
 const w=dom.window,d=w.document,$=id=>d.getElementById(id),until=async f=>{for(let n=0;n<500;n++){if(f())return;await new Promise(r=>setTimeout(r,20))}throw Error('Timeout: '+$('po-need-calculation')?.textContent+' '+errors.join(' '))};
 await until(()=>$('article').value==='A');w.eval("view('propuestas');purchaseGuideNavigate('po-references')");const form=$('form');
 function input(name,v){form.elements[name].value=v;form.elements[name].dispatchEvent(new w.Event('change',{bubbles:true}))}
 input('quantity','10');input('order_date','30/09/2026');$('po-stock-use-workbook').click();
 assert.equal($('po-stock-ack').checked,false);assert.match($('po-need-calculation').textContent,/confirma|confirmación/i);
 $('po-stock-ack').checked=true;$('po-stock-ack').dispatchEvent(new w.Event('change',{bubbles:true}));
 await until(()=>$('po-need-calculation').querySelectorAll('table').length===2);
 assert.match($('po-need-calculation').textContent,/Necesidad neta en la fecha crítica/);assert.equal(d.querySelectorAll('#po-stock-daily_demand').length,1);
 assert.ok($('po-references').contains(form.elements.quantity));assert.ok($('po-stock-assumptions').open);assert.match($('po-need-reading').textContent,/Sin falta|Falta stock|seguridad/);
 $('po-stock-ack').checked=false;$('po-stock-ack').dispatchEvent(new w.Event('change',{bubbles:true}));assert.equal($('po-need-calculation').querySelectorAll('table').length,0);
 assert.deepEqual(errors,[]);dom.window.close();console.log('PASS step 2: preserved controls, book assumptions, explicit acknowledgment, independent stock calculation and stale-result clearing');
})().catch(e=>{console.error(e);process.exit(1)});
