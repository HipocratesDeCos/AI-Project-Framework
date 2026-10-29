"""Presentation and payment controls for the sales negotiation workspace."""

JS = r'''
function syncSalesPayment(updateDue){
 const term=$('so-payment-term').value,method=$('so-payment-method').value,dateValue=$('so-date').value;
 if(updateDue&&term!=='CUSTOM'&&dateValue){
  const date=new Date(dateValue+'T12:00:00Z');
  if(Number.isFinite(date.getTime())){date.setUTCDate(date.getUTCDate()+Number(term));$('so-due').value=date.toISOString().slice(0,10)}
 }
 const note=$('so-payment-note');note.required=method==='OTHER';
 const methodText=method==='OTHER'?'Otra forma acordada':method;
 const termText=term==='CUSTOM'?'Fecha personalizada':term==='0'?'Contado / a la vista':term+' días desde la propuesta';
 const parts=[methodText,termText,note.value.trim()].filter(Boolean);
 $('so-payment').value=parts.join(' · ');
 $('so-payment-summary').textContent=method?parts.join(' · ')+' · Vencimiento: '+($('so-due').value?stockDate($('so-due').value):'pendiente'):'Selecciona la forma de pago y comprueba el plazo de cobro.';
}
function setSalesPaymentAlternative(text){
 $('so-payment-method').value='OTHER';$('so-payment-term').value='CUSTOM';$('so-payment-note').value=text||'';syncSalesPayment(false);
}
$('so-payment-method').onchange=()=>{syncSalesPayment(false);invalidateSalesProposal()};
$('so-payment-term').onchange=()=>{syncSalesPayment(true);invalidateSalesProposal()};
$('so-payment-note').oninput=()=>{syncSalesPayment(false);invalidateSalesProposal()};
$('so-due').onchange=()=>{$('so-payment-term').value='CUSTOM';syncSalesPayment(false);invalidateSalesProposal()};
document.querySelectorAll('.so-step-nav a').forEach(link=>link.addEventListener('click',event=>{
 event.preventDefault();const target=document.querySelector(link.getAttribute('href'));if(target.tagName==='DETAILS')target.open=true;target.scrollIntoView({behavior:'smooth',block:'start'});
}));
'''

CSS = '''
[data-view="propuestas-ventas"]{--so-blue:#163e78;--so-border:#bdcfe3;--so-ink:#172e49;color:var(--so-ink)}
[data-view="propuestas-ventas"] .so-page-intro{padding:24px 28px;margin-bottom:24px;background:#eaf2fc;border:1px solid #c5d7ec;border-radius:14px}
[data-view="propuestas-ventas"] .so-page-intro h2{font-size:28px;margin:6px 0 12px;line-height:1.2}
[data-view="propuestas-ventas"] .so-eyebrow{font-size:12px;font-weight:750;letter-spacing:.07em;color:#36577b;margin:0 0 8px}
[data-view="propuestas-ventas"] .so-step-nav{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}
[data-view="propuestas-ventas"] .so-step-nav a{padding:10px 16px;background:white;border:1px solid #b9cde9;border-radius:8px;color:#13346f;text-decoration:none;font-weight:650}
[data-view="propuestas-ventas"] .so-workspace{grid-template-columns:minmax(0,1.45fr) minmax(340px,1fr);gap:24px}
[data-view="propuestas-ventas"] .so-step{border:1px solid var(--so-border);border-top:5px solid #6793c9;border-radius:12px;padding:24px;margin:0 0 24px;background:#f5f9ff;scroll-margin-top:24px}
[data-view="propuestas-ventas"] .so-conditions{border-top-color:#528d80;background:#f0f8f5}
[data-view="propuestas-ventas"] .so-evaluation{border-top-color:#b7802e;background:#fff9ee}
[data-view="propuestas-ventas"] .so-document{border-top-color:#8871ae;background:#f7f4fb}
[data-view="propuestas-ventas"] .so-step-heading{display:flex;gap:14px;align-items:flex-start;margin-bottom:24px}
[data-view="propuestas-ventas"] .so-step-heading>span{display:grid;place-items:center;flex:0 0 40px;height:40px;border-radius:10px;background:#173e77;color:white;font-size:22px;font-weight:700}
[data-view="propuestas-ventas"] .so-conditions .so-step-heading>span{background:#396d61}
[data-view="propuestas-ventas"] .so-evaluation .so-step-heading>span{background:#8d611f}
[data-view="propuestas-ventas"] .so-step-heading h2{font-size:19px;line-height:1.35;margin:0 0 6px}
[data-view="propuestas-ventas"] .so-step-heading p{margin:0;color:#405871}
[data-view="propuestas-ventas"] p,[data-view="propuestas-ventas"] label{font-size:15px;line-height:1.6}
[data-view="propuestas-ventas"] small{display:block;font-size:13px;line-height:1.5;color:#52677e;margin-top:6px}
[data-view="propuestas-ventas"] .fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px 20px;align-items:start}
[data-view="propuestas-ventas"] label{display:block;min-width:0;font-weight:600}
[data-view="propuestas-ventas"] input,[data-view="propuestas-ventas"] select,[data-view="propuestas-ventas"] textarea{box-sizing:border-box;width:100%;min-width:0;min-height:46px;margin-top:8px;padding:11px 12px;font:inherit;font-weight:400;color:#172e49;background:white;border:1px solid #9eb5cc;border-radius:7px}
[data-view="propuestas-ventas"] select{appearance:auto;cursor:pointer;padding-right:8px}
[data-view="propuestas-ventas"] input:disabled{background:#eef1f5;color:#5b6a7a}
[data-view="propuestas-ventas"] input[readonly]{background:#eef3f9;font-size:13px}
[data-view="propuestas-ventas"] input[type=checkbox]{min-height:0;width:auto}
[data-view="propuestas-ventas"] .so-wide,[data-view="propuestas-ventas"] .so-customer-note{grid-column:1/-1}
[data-view="propuestas-ventas"] .so-customer-note textarea{min-height:150px;resize:vertical}
[data-view="propuestas-ventas"] .so-line,[data-view="propuestas-ventas"] .so-line-conditions{padding:18px;background:white;border:1px solid #c1d4e5;border-radius:10px;margin:16px 0}
[data-view="propuestas-ventas"] .so-line-conditions h4{font-size:16px;line-height:1.5;margin:0 0 18px;padding-bottom:12px;border-bottom:1px solid #d8e4e9;color:#265c50;overflow-wrap:anywhere}
[data-view="propuestas-ventas"] .so-subsection{min-width:0;margin:24px 0 0;padding:18px;border:1px solid #bed3cd;border-radius:10px;background:#fff}
[data-view="propuestas-ventas"] legend{font-size:16px;font-weight:700;padding:0 8px;color:#275e52}
[data-view="propuestas-ventas"] .so-payment-summary{padding:12px 15px;border-radius:7px;background:#eaf4f0;color:#245346;margin-bottom:0}
[data-view="propuestas-ventas"] button{box-sizing:border-box;display:inline-flex;align-items:center;justify-content:flex-start;gap:8px;min-height:46px;max-width:100%;margin:8px 10px 8px 0;padding:12px 16px;border:1px solid #b9cde9;border-radius:8px;background:#edf4ff;color:#13346f;text-align:left;font:inherit;font-size:14px;font-weight:650;line-height:1.45;white-space:normal;overflow-wrap:anywhere;box-shadow:none;cursor:pointer;transition:background .15s,border-color .15s}
[data-view="propuestas-ventas"] button:hover:not(:disabled){background:#dfeaff;border-color:#0a369d}
[data-view="propuestas-ventas"] button.primary{background:#163e78;color:white;border-color:#163e78;padding:15px 20px;font-size:16px}
[data-view="propuestas-ventas"] button.primary:hover:not(:disabled){background:#0e2d5d}
[data-view="propuestas-ventas"] button:disabled{opacity:.55;cursor:not-allowed}
[data-view="propuestas-ventas"] :is(button,a,input,select,textarea,summary):focus-visible{outline:3px solid #548bed;outline-offset:3px}
[data-view="propuestas-ventas"] .so-reference-actions button{width:100%;margin:0}
[data-view="propuestas-ventas"] .so-remove{color:#78534d;background:#faf2f0;border-color:#dec9c3;margin-bottom:0}
[data-view="propuestas-ventas"] summary{font-size:16px;font-weight:700;padding:10px 2px;cursor:pointer;line-height:1.5}
[data-view="propuestas-ventas"] details[open]>summary{margin-bottom:16px;border-bottom:1px solid #d6e0ec}
[data-view="propuestas-ventas"] .so-article-search,[data-view="propuestas-ventas"] .files-subpanel{border:1px solid #d0deec;border-radius:9px;padding:16px;background:#f5f8fd;margin:0 0 18px}
[data-view="propuestas-ventas"] .so-assistant{max-height:none;overflow:visible;position:static}
[data-view="propuestas-ventas"] .so-assistant>.card{border:1px solid #bdcfe3;border-top:5px solid #6793c9;border-radius:12px;background:#f8fbff;padding:22px}
[data-view="propuestas-ventas"] .so-advice-grid{gap:12px;margin:18px 0}
[data-view="propuestas-ventas"] .so-advice-grid div{padding:14px;background:#eaf2fc;border:1px solid #cfdeef;border-radius:8px;min-width:0;overflow-wrap:anywhere}
[data-view="propuestas-ventas"] .so-advice-grid strong{font-size:21px;line-height:1.3}
[data-view="propuestas-ventas"] .so-assistance>h3{line-height:1.5;overflow-wrap:anywhere}
[data-view="propuestas-ventas"] .so-result-pending{padding:18px;background:#fff;border:1px dashed #b6a581;border-radius:9px;color:#65532e}
[data-view="propuestas-ventas"] #so-evaluation-result{scroll-margin-top:24px}
[data-view="propuestas-ventas"] .so-verdict{border:2px solid #bd8426;border-left-width:8px;background:#fff0ce;color:#533a14;border-radius:10px;padding:22px;margin:22px 0}
[data-view="propuestas-ventas"] .so-verdict-stop{border-color:#b64940;background:#fff0ee;color:#792c26}
[data-view="propuestas-ventas"] .so-verdict-badge{display:inline-block;font-size:12px;letter-spacing:.05em;border:1px solid currentColor;border-radius:5px;padding:5px 9px;margin-bottom:10px}
[data-view="propuestas-ventas"] .so-verdict h3{font-size:23px;line-height:1.35;margin:4px 0 12px}
[data-view="propuestas-ventas"] .so-verdict h4{font-size:16px;margin:20px 0 8px}
[data-view="propuestas-ventas"] .so-verdict li{padding:5px 0;line-height:1.6}
[data-view="propuestas-ventas"] .so-scenario{border:1px solid #a7c0dc;border-left:5px solid #527da9;padding:20px;background:#f1f7ff;margin-top:20px}
[data-view="propuestas-ventas"] .so-scenario h3{font-size:19px;line-height:1.4}
[data-view="propuestas-ventas"] .so-scenario blockquote{margin:16px 0;padding:16px;border-left:4px solid #527da9;background:white;line-height:1.7}
[data-view="propuestas-ventas"] .so-totals{padding:18px;background:#e7f0fd;font-size:18px;font-weight:700;line-height:1.7;border-radius:8px;margin:20px 0}
[data-view="propuestas-ventas"] #so-notice:not(:empty){padding:14px;border:1px solid #c5a65f;border-radius:8px;background:#fff2d1;color:#59421d}
@media(max-width:1200px){[data-view="propuestas-ventas"] .so-workspace{grid-template-columns:minmax(0,1fr)}}
@media(max-width:640px){[data-view="propuestas-ventas"] .fields,[data-view="propuestas-ventas"] .so-advice-grid{grid-template-columns:minmax(0,1fr)}[data-view="propuestas-ventas"] .so-step,[data-view="propuestas-ventas"] .so-page-intro{padding:18px}[data-view="propuestas-ventas"] .so-step-nav a{flex:1 1 38%}}
'''
