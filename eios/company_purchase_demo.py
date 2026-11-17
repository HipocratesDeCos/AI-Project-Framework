"""Build a complete isolated synthetic purchase demonstration through public adapters."""
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import tempfile
import zipfile

from eios.company_data import CompanyDataStore, SCHEMA
from eios.company_app import PurchaseDesk
from eios.company_parameters import save_parameters
from eios.company_finance_parameters import activate_finance_parameters


def build_demo(destination):
    destination=Path(destination)
    if destination.exists():raise ValueError('El destino ya existe. Elige otro nombre: no se sobrescribe ninguna base.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temp:
        root=Path(temp);db=root/'demo.sqlite3';records=[]
        def add(kind,identity,data):
            records.append(dict(kind=kind,record_id=identity,data=data,source_refs=[dict(document_ref='DEMO-01',section=kind)]))
        add('company_identity','EIOS-DEMO',dict(company_id='EIOS-DEMO',legal_name='Jardinería Demostración EIOS · FICTICIA'))
        add('supplier','4000001',dict(supplier_id='4000001',legal_name='Suministros Jardín Demo · FICTICIO',contact_name='Contacto de demostración',locality='Sabadell'))
        add('article','JAR-DEMO-001',dict(article_id='JAR-DEMO-001',supplier_id='4000001',description='Manguera de riego · artículo ficticio',family='Riego',unit_as_documented='Unidad',stock_quantity=None,demand_forecast=None))
        add('purchase_invoice','DEMO-HIST-01',dict(invoice_id='DEMO-HIST-01',invoice_number='DEMO-HIST-01',supplier_id='4000001',issue_date='2026-09-20',currency='EUR'))
        add('purchase_invoice_line','DEMO-HIST-01#1',dict(invoice_id='DEMO-HIST-01',article_id='JAR-DEMO-001',supplier_id='4000001',quantity='100',unit_price='12.50',net_amount='1250',unit_as_documented='Unidad',currency='EUR',vat_percent='21',discount_percent='0'))
        add('financial_snapshot','DEMO-CASH',dict(company_scope='EIOS-DEMO',as_of_date='2026-09-30',data_snapshot_id='DEMO-CASH',currency='EUR',available_treasury='15000',treasury_evidence_ref='DEMO-01'))
        add('working_capital','DEMO-WC',dict(company_scope='EIOS-DEMO',as_of_date='2026-09-30',currency='EUR',current_assets='45000',current_liabilities='18000',assets_source_ref='DEMO-01',liabilities_source_ref='DEMO-01'))
        for identity,kind,amount,day in [('DEMO-PAGO','PAYMENT','6000','2026-11-20'),('DEMO-COBRO','COLLECTION','5000','2026-11-25')]:
            add('cash_flow',identity,dict(canonical=dict(flow_id=identity,flow_type=kind,amount=amount,currency='EUR',due_date=day,due_date_evidenced=False,source_ref='DEMO-01',evidence_state='NOT_EVIDENCED')))
        document=json.dumps(dict(nature='SYNTHETIC',records=records,stock=dict(physical_at_cutoff='100',reserved_at_cutoff='10',free_at_cutoff='90',free_at_order='60',bridge='30 units of additional free stock consumed between cutoff and order; reservations unchanged',daily_demand='5 additional units/day from order',lead_days=7,receipt='50 units 2026-11-18',target_days=30,safety=20,step=10),policy=dict(horizon_days=90,reserve_eur=3000),notice='All figures are invented and are not evidence of real events.'),ensure_ascii=False,indent=2).encode()
        raw=json.dumps(records,ensure_ascii=False).encode();manifest=dict(schema_version=SCHEMA,material_nature='SYNTHETIC',operational_path='FORBIDDEN',company=dict(company_id='EIOS-DEMO',legal_name='Jardinería Demostración EIOS · FICTICIA'),as_of_date='2026-09-30',records=dict(path='records.json',sha256=sha256(raw).hexdigest()),record_counts=dict(Counter(r['kind'] for r in records)),documents=[dict(document_ref='DEMO-01',path='demo.json',filename='Soporte_Ficticio_Demo.json',bytes=len(document),sha256=sha256(document).hexdigest(),media_type='application/json')])
        package=root/'demo.zip'
        with zipfile.ZipFile(package,'w') as z:
            z.writestr('company_manifest.json',json.dumps(manifest,ensure_ascii=False));z.writestr('records.json',raw);z.writestr('demo.json',document)
        store=CompanyDataStore(db);dataset=store.import_dataset(package)['dataset_id']
        from eios.company_inventory import TABLE, VERSION
        inventory=dict(dataset_id=dataset,article_id='JAR-DEMO-001',unit='Unidad',as_of_date='2026-09-30',physical=100,reserved=10,available=90,source=VERSION,material_nature='SYNTHETIC',basis='EXPLICIT_DEMO_ASSUMPTION',accounting_reconciliation='NOT_RECONCILED')
        with sqlite3.connect(db) as c:
            c.execute(TABLE);c.execute('INSERT INTO synthetic_planning_inventory VALUES(?,?,?)',(dataset,'JAR-DEMO-001',json.dumps(inventory)))
        save_parameters(db,store,dict(dataset_id=dataset,revision=0,actor='Responsable ficticio de demostración',reason='Política exclusiva de esta demostración sintética',profile={},values={'P-FIN-001':'90','P-FIN-002':'3000'},references={},critical_acknowledged=True))
        activate_finance_parameters(db,store,dict(dataset_id=dataset,revision=1,actor='Responsable ficticio de demostración',reason='Activación sintética al corte',acknowledge=True))
        desk=PurchaseDesk(db);state=desk.sales_state(dataset)
        base=dict(dataset_id=dataset,documentary_context_fingerprint=state['documentary_context']['fingerprint'],supplier_id='4000001',article_id='JAR-DEMO-001',reference='DEMO-01-BASE',quantity='500',unit_price='14.80',vat_percent='21',pricing_mode='NET',discount_mode='NONE',shipping_mode='SUPPLIER',order_date='2026-11-04',due_date='2026-11-15')
        base['stock_planning']=dict(dataset_id=dataset,article_id='JAR-DEMO-001',unit='Unidad',documentary_fingerprint=state['documentary_context']['fingerprint'],order_date=base['order_date'],available_at_order='60',daily_demand='5',lead_time_days='7',target_days='30',safety_stock='20',purchase_step='10',receipts=[dict(date='2026-11-18',quantity='50')],actor='Responsable ficticio de demostración',source_reference='DEMO-01: puente de inventario y planificación ficticios',acknowledge=True)
        cases=[('BASE',{}),('CANTIDAD',dict(quantity='100')),('COMBINADA',dict(quantity='100',unit_price='12.50')),('APLAZADA',dict(due_date='2026-11-25')),('CUOTAS',dict(payment_installments=[dict(component='MERCHANDISE',amount='4477.00',due_date='2026-11-15'),dict(component='MERCHANDISE',amount='4477.00',due_date='2026-11-30')],due_date='2026-11-30'))]
        results=[]
        for name,patch in cases:
            data=deepcopy(base);data.update(patch,reference='DEMO-'+name)
            saved=desk.save(data);cash=saved['cash_orientation_at_save']
            if cash['status']=='PENDING':raise ValueError('Demo incompleta: '+cash['message'])
            if cash['quantity_review']['simulation_readiness']!='COMPLETE_HYPOTHETICAL':raise ValueError('Faltan supuestos de stock en la demo.')
            results.append(dict(reference=saved['reference'],total=cash['total'],minimum_balance=cash['scenario']['minimum_balance'],status=cash['status'],target_quantity=cash['stock_planning']['scenario_quantity']))
        # Publish exclusively; never replace an existing user file, including concurrent creation.
        with destination.open('xb') as target,db.open('rb') as source:
            import shutil
            shutil.copyfileobj(source,target)
    return dict(db=str(destination.resolve()),material_nature='SYNTHETIC',decision_authority=False,dataset_id=dataset,cases=results)


def main():
    parser=argparse.ArgumentParser(description='Crear una demostración completa de compra en una base nueva, sin modificar la empresa actual.')
    parser.add_argument('--db',type=Path,required=True);args=parser.parse_args()
    try:print(json.dumps(build_demo(args.db),ensure_ascii=False,indent=2))
    except ValueError as error:parser.exit(2,str(error)+'\n')


if __name__=='__main__':main()
