"""Read-only latest-cutoff policy for synthetic sales financial references."""
import json
from eios.company_selected_inventory import source


def candidates(c,dataset,verify=True):
    from eios.company_sales_treasury import scope,identity_status
    target=scope(c,dataset);result=[]
    if target[2]!='SYNTHETIC' or not c.execute("SELECT 1 FROM sqlite_master WHERE name='received_company_batch'").fetchone():return result
    for bid,received,ordinal,raw in c.execute('SELECT batch_id,received_at,rowid,metadata_json FROM received_company_batch'):
        try:meta=json.loads(raw)
        except (ValueError,TypeError):continue
        if not isinstance(meta,dict):continue
        if meta.get('kind') not in ('balance','cash_flow'):continue
        cutoff=meta.get('as_of_date')
        if not cutoff or identity_status(meta,(*target[:3],cutoff))=='INCOMPATIBLE':continue
        if verify:_,records,fp,intact=source(c,bid)
        else:records,fp,intact=None,None,None
        result.append(dict(batch_id=bid,received_at=received,receipt_order=ordinal,metadata=meta,records=records,fingerprint=fp,intact=intact))
    return sorted(result,key=lambda r:(r['metadata']['as_of_date'],r['received_at'],r['receipt_order']),reverse=True)


def automatic(c,dataset):
    rows=candidates(c,dataset,verify=False)
    if not rows:return None
    cutoff=rows[0]['metadata']['as_of_date'];current=[r for r in rows if r['metadata']['as_of_date']==cutoff]
    balance=next((r for r in current if r['metadata']['kind']=='balance'),None)
    flow=next((r for r in current if r['metadata']['kind']=='cash_flow'),None)
    selected=dict(mode='AUTO',revision=0,cleared=False,dataset_id=dataset,as_of_date=cutoff,
        actor='Política automática de últimas fuentes',reason='Último corte y última recepción por contenido; bancos 572, caja 570 solo por excepción manual.',
        balance_batch=balance['batch_id'] if balance else None,flow_batch=flow['batch_id'] if flow else None,
        account_codes=[],confirm_identity=True,identity_basis='MATCHED_NORMALIZED_LEGAL_NAME_AUTOMATIC_POLICY',
        source_fingerprints={r['batch_id']:r['fingerprint'] for r in (balance,flow) if r},
        received_at={r['batch_id']:r['received_at'] for r in (balance,flow) if r})
    for item in (balance,flow):
        if item:
            _,item['records'],item['fingerprint'],item['intact']=source(c,item['batch_id'])
    selected['source_fingerprints']={r['batch_id']:r['fingerprint'] for r in (balance,flow) if r}
    problems=[]
    from eios.company_sales_treasury import scope,identity_status
    target=scope(c,dataset);unclassified=[]
    for bid,company_id,raw in c.execute('SELECT batch_id,company_id,metadata_json FROM received_company_batch'):
        try:
            parsed=json.loads(raw)
            if isinstance(parsed,dict):continue
        except (ValueError,TypeError):pass
        name=None
        if c.execute("SELECT 1 FROM sqlite_master WHERE name='received_company'").fetchone():
            party=c.execute('SELECT legal_name FROM received_company WHERE company_id=?',(company_id,)).fetchone()
            name=party[0] if party else None
        same=company_id==target[0] or (name and identity_status(dict(company_id=company_id,legal_name=name,material_nature='SYNTHETIC',as_of_date=target[3]),target)!='INCOMPATIBLE')
        if same:unclassified.append(dict(batch_id=bid,metadata=raw))
    if unclassified:
        selected['unclassified_sources']=unclassified
        problems.append('Hay recepciones de la empresa con identificación ilegible. Revisa esos archivos antes de elegir automáticamente una versión financiera.')
    if balance is None:problems.append('Faltan saldos contables del último corte '+cutoff+'. No se recuperan saldos de cortes anteriores.')
    if flow is None:problems.append('Falta el calendario de cobros y pagos del último corte '+cutoff+'. No se mezcla con un calendario anterior.')
    if any(not r['intact'] for r in (balance,flow) if r):problems.append('Un archivo de la última recepción no conserva su integridad. Revisa el origen; no se sustituye por una versión antigua.')
    if balance:
        codes=[r['data']['account_code'] for r in balance['records'] if r['kind']=='balance' and r['data']['account_code'].startswith('572')]
        # Use the highest documented level in each branch; never add its children.
        selected['account_codes']=sorted(code for code in set(codes) if not any(other!=code and code.startswith(other) for other in codes))
        if not codes:problems.append('El último archivo no contiene cuentas de bancos 572. Caja 570 requiere selección manual excepcional.')
        if len(codes)!=len(set(codes)):problems.append('El último archivo repite cuentas de bancos; revisa las filas antes de utilizarlas.')
    if problems:selected['resolution_error']=' '.join(problems)
    return selected


def effective(c,dataset):
    from eios.company_sales_treasury import latest
    saved=latest(c,dataset)
    if saved and not saved.get('cleared') and saved.get('mode')=='MANUAL':return saved
    return automatic(c,dataset)
