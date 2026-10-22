"""Bulk-select an explicitly supplied synthetic tariff without overwriting existing choices."""
import argparse
import json
from pathlib import Path
import sqlite3

from eios.company_app import PurchaseDesk
from eios.company_reception import CompanyReception
from eios.company_sales_tariffs import save_tariff
from eios.company_tables import read_table, normalize, tariff_mapping


def load_tariff(db,file,actor,*,dataset=None):
    if not isinstance(actor,str) or not actor.strip() or len(actor)>500:raise ValueError('Indica un responsable de la carga.')
    desk=PurchaseDesk(db)
    if dataset is None:
        with sqlite3.connect(db) as c:datasets=[r[0] for r in c.execute('SELECT dataset_id FROM documentary_company_snapshot')]
        if len(datasets)!=1:raise ValueError('Hay varias versiones. Indica --dataset para elegir una expresamente.')
        dataset=datasets[0]
    state=desk.state(dataset);context=state['documentary_context']
    if context['material_nature']!='SYNTHETIC':raise ValueError('La carga por lote solo admite datos ficticios de prueba.')
    content=Path(file).read_bytes();filename=Path(file).name
    table=read_table(content,filename,sheet='Tarifa');mapping=tariff_mapping(table['headers'])
    if mapping is None:raise ValueError('Usa la hoja Tarifa con los seis encabezados de la plantilla de EIOS.')
    normalized=normalize(table,'sale_price',mapping,state['info']['as_of_date'],'ES')
    if normalized['error_count']:raise ValueError('Corrige la tarifa antes de cargarla: '+json.dumps(normalized['errors'][:10],ensure_ascii=False))
    records=normalized['records'];catalog={};seen=set();skip=[];pending=[]
    for article in state['articles']:
        sku=article['article_id']
        if sku in catalog:raise ValueError('Hay SKU duplicados en el catálogo de la empresa.')
        catalog[sku]=article
    for record in records:
        data=record['data'];sku=data['article_id'];article=catalog.get(sku)
        if sku in seen:raise ValueError('La carga por lote requiere una única fila de tarifa por SKU. Revisa '+sku+'.')
        seen.add(sku)
        if article is None or article['unit_as_documented']!=data['unit'] or data['currency']!='EUR':
            raise ValueError('SKU, unidad o moneda incompatibles con el catálogo: '+sku+'.')
        if article.get('received_sale_tariff') or article.get('recommended_sale_price') is not None:skip.append(sku)
        else:pending.append(record)
    result=dict(dataset_id=dataset,selected=[],preserved=skip,article_count=len(records),decision_authority=False,operational_path='FORBIDDEN')
    if not pending:return dict(result,status='EXISTING_REFERENCES_PRESERVED',batch_id=None,selected_count=0,preserved_count=len(skip))
    reception=CompanyReception(db);upload=reception.read(content,filename,sheet='Tarifa')
    preview=reception.preview(dict(upload=upload['upload'],company_id=context['company_id'],legal_name=context['company_name'],material_nature='SYNTHETIC',as_of_date=context['documentary_cutoff'],kind='sale_price',number_format='ES',mapping=mapping))
    if not preview.get('ticket'):raise ValueError('La recepción de la tarifa no se ha podido validar.')
    saved=reception.commit(preview['ticket']);batch_id=saved['batch_id']
    # Each revision is append-only. Preserve the exact context returned by our last
    # write, so concurrent changes cannot silently become accepted inputs.
    expected=context['fingerprint']
    from eios.company_sales_tariffs import candidates
    with sqlite3.connect(db) as c:
        choices={sku:candidates(c,context,catalog[sku]) for sku in [r['data']['article_id'] for r in pending]}
    for record in pending:
        sku=record['data']['article_id'];choice=next((r for r in choices[sku] if r['batch_id']==batch_id and r['source_row']==record['source_row']),None)
        if choice is None:raise ValueError('La fuente ha cambiado. Se conserva el archivo recibido; referencias seleccionadas hasta ahora: '+str(len(result['selected']))+'. Revisa y repite la carga.')
        try:
            reply=save_tariff(db,dict(dataset_id=dataset,article_id=sku,context_fingerprint=expected,batch_id=batch_id,source_row=record['source_row'],source_fingerprint=choice['source_fingerprint'],actor=actor.strip(),reason='Carga expresa de tarifa ficticia de prueba: '+filename,acknowledge_net_unit=True))
        except ValueError as error:
            raise ValueError('Carga interrumpida tras '+str(len(result['selected']))+' selecciones. Se conserva el archivo recibido. Revisa el motivo y repite; las referencias ya seleccionadas se conservarán. '+str(error)) from error
        expected=reply['context_fingerprint'];result['selected'].append(sku)
    return dict(result,status='SYNTHETIC_TARIFF_SELECTED',batch_id=batch_id,selected_count=len(result['selected']),preserved_count=len(skip))


def main():
    parser=argparse.ArgumentParser(description='Carga una tarifa ficticia de prueba y selecciona las filas de los SKU sin tarifa previa.')
    parser.add_argument('--db',required=True);parser.add_argument('--file',required=True);parser.add_argument('--actor',required=True);parser.add_argument('--dataset')
    args=parser.parse_args()
    try:result=load_tariff(args.db,args.file,args.actor,dataset=args.dataset)
    except (ValueError,KeyError,OSError) as error:parser.exit(1,str(error)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
