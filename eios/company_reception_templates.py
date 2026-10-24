"""Blank CSV templates derived from the same contracts as company reception."""
from eios.company_stock_parameter_help_ui import HTML as STOCK_PARAMETER_HELP_HTML
from html import escape
import json
from eios.company_tables import FIELDS
from eios.company_commercial_catalogue import FIELDS as CATALOGUE_FIELDS

LABELS=dict(supplier='Proveedores',customer='Clientes',article='Artículos',inventory='Inventario',
    stock_policy='Parámetros de stock y entrega',purchase_line='Compras históricas',
    sales_line='Ventas históricas',sales_installment='Vencimientos de venta (una fila por cuota)',sale_price='Tarifa de venta',cash_flow='Previsión de cobros y pagos',
    balance='Saldos contables',commercial_catalogue='Catálogo comercial de empresa ficticia')


def definitions():
    result={kind:dict(label=LABELS[kind],filename='EIOS_Plantilla_'+kind+'.csv',fields=[dict(key=key,label=label,required=required) for key,label,required in fields]) for kind,fields in FIELDS.items() if kind!='document'}
    result['commercial_catalogue']=dict(label=LABELS['commercial_catalogue'],filename='EIOS_Plantilla_catalogo_comercial.csv',fields=[dict(key=header,label=header,required=key not in ('recommended_sale_price','family')) for key,header in CATALOGUE_FIELDS.items()])
    return result


HTML='''<section class="card files-section" id="reception-template-panel"><h2>PLANTILLAS PARA GOOGLE SHEETS Y EXCEL</h2><p>Descarga una plantilla vacía, impórtala en Google Sheets y completa sus filas. Después descárgala como CSV o XLSX y vuelve a Carga de archivos. La descarga no crea documentos en tu cuenta de Google ni incorpora datos a EIOS.</p><div class="fields"><label>Contenido de la plantilla<select id="reception-template-kind">'''+''.join('<option value="'+escape(kind)+'">'+escape(item['label'])+'</option>' for kind,item in definitions().items())+'''</select></label><div class="files-actions"><button id="reception-template-download" type="button">Descargar plantilla para Google Sheets (.csv)</button></div></div><p id="reception-template-help"></p><div id="reception-template-fields" class="scroll"></div><p>Conserva las cabeceras. Antes de introducir datos, configura SKU, cuentas y otros códigos como texto para mantener ceros iniciales. Usa fechas DD/MM/AAAA y valores fijos en las columnas que vas a cargar. Completa los datos de empresa y corte al subir el archivo; la plantilla no los presupone.</p><p id="reception-template-notice" class="files-notice" role="status"></p></section>'''
HTML=HTML.replace('<div id="reception-template-fields" class="scroll"></div>','<div id="reception-template-fields" class="scroll"></div>'+STOCK_PARAMETER_HELP_HTML,1)
JS='const receptionTemplates='+json.dumps(definitions(),ensure_ascii=False,separators=(',',':'))+';'+r'''
function renderReceptionTemplate(){const kind=$('reception-template-kind').value,t=receptionTemplates[kind];$('reception-stock-help').hidden=!['stock_policy','inventory'].includes(kind);receptionTable('reception-template-fields',['Cabecera','Contenido','Necesario'],t.fields.map(f=>[f.key,f.label,f.required?'Obligatorio':'Opcional']));$('reception-template-help').textContent=kind==='commercial_catalogue'?'Destino al subir: CATÁLOGO COMERCIAL · EMPRESA ACTIVA. Solo datos ficticios y confirmación expresa de unidades y EUR sin IVA. estado_baja: True o False; PVP vacío: pendiente.':kind==='sales_installment'?'Destino: recepción ordinaria, Vencimientos de venta. Una fila por cuota, sin límite de tres. Vincula cliente y factura; informa pendiente al corte y la referencia del cobro ya previsto cuando exista.':kind==='sales_line'?'Destino: recepción ordinaria, Ventas históricas. Neto después de descuentos; IVA y total documentado permiten comprobar las cuotas. El total de factura se repite, no se suma por línea.':kind==='stock_policy'?'Destino al subir: recepción ordinaria, contenido Parámetros de stock y entrega. Además de SKU y unidad, completa al menos mínimo, seguridad, punto de pedido o plazo.':'Destino al subir: recepción ordinaria, contenido '+t.label+'. Revisa el mapeo y el formato numérico antes de guardar.';$('reception-template-notice').textContent=''}
$('reception-template-kind').onchange=renderReceptionTemplate;
$('reception-template-download').onclick=()=>{const t=receptionTemplates[$('reception-template-kind').value],csv='\uFEFF'+t.fields.map(f=>'"'+f.key.replaceAll('"','""')+'"').join(',')+'\r\n',blob=new Blob([csv],{type:'text/csv;charset=utf-8'}),url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=t.filename;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);$('reception-template-notice').textContent='Plantilla vacía descargada. Impórtala en Google Sheets, completa los datos y descárgala como CSV o XLSX para subirla a EIOS.'};
renderReceptionTemplate();
'''
