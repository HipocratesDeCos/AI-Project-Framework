"""Company/article/unit minimums: manual settings and dated descriptive alerts."""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_CEILING, localcontext
import sqlite3


def schema(c):
    c.execute('''CREATE TABLE IF NOT EXISTS company_stock_minimum (
        company_id TEXT,article_id TEXT,unit TEXT,value TEXT,revision INTEGER NOT NULL,
        updated_at TEXT NOT NULL,PRIMARY KEY(company_id,article_id,unit))''')
    c.execute('''CREATE TABLE IF NOT EXISTS company_stock_minimum_history (
        id INTEGER PRIMARY KEY,company_id TEXT,article_id TEXT,unit TEXT,
        old_value TEXT,new_value TEXT,revision INTEGER,updated_at TEXT,dataset_id TEXT)''')


def decimal(value):
    if value is None or value == '' or isinstance(value,bool): return None
    try:
        result=Decimal(str(value))
        return result if result.is_finite() else None
    except (ValueError,InvalidOperation): return None


def alert(inventory, minimum, unit):
    available=decimal((inventory or {}).get('available'))
    target=decimal(minimum)
    if not inventory or inventory.get('unit')!=unit or available is None or target is None:
        return dict(status='UNKNOWN',label='SIN DATOS SUFICIENTES',shortage=None)
    status,label=('EMPTY','SIN EXISTENCIAS') if available<=0 else ('LOW','BAJO MÍNIMO') if available<target else ('LIMIT','EN EL MÍNIMO') if available==target else ('OK','SOBRE EL MÍNIMO')
    return dict(status=status,label=label,shortage=format(max(Decimal(0),target-available),'f'))


def automatic_minimum(history, unit):
    if not history: return None
    latest_date=max(row['issue_date'] for row in history)
    latest=[row for row in history if row['issue_date']==latest_date]
    if len(latest)!=1: return None
    row=latest[0];quantity=decimal(row.get('quantity'))
    if row.get('unit')!=unit or quantity is None or quantity<=0 or quantity>Decimal('1000000000'): return None
    with localcontext() as context:
        context.prec=60
        value=quantity*Decimal('0.10')
        indivisible=unit.strip().lower().rstrip('.') in {'ud','uds','unidad','unidades','unit','units','pcs'}
        if indivisible: value=value.to_integral_value(rounding=ROUND_CEILING)
    return dict(value=format(value.normalize(),'f'),quantity=str(quantity),unit=unit,
                invoice_number=row.get('invoice_number'),issue_date=row['issue_date'],
                source_refs=row.get('source_refs',[]),percentage='10',
                rounding='CEILING_WHOLE_UNIT' if indivisible else 'EXACT')


def read_minimums(db, company, articles, inventory, history=None):
    with sqlite3.connect(db) as c:
        schema(c)
        saved={(a,u):(v,r,t) for a,u,v,r,t in c.execute('SELECT article_id,unit,value,revision,updated_at FROM company_stock_minimum WHERE company_id=?',(company,))}
    result={}
    for a in articles:
        key=a['article_id'];unit=a.get('unit_as_documented','')
        value,revision,updated=saved.get((key,unit),(None,0,None))
        file_value=decimal((inventory.get(key) or {}).get('minimum_stock')) if (inventory.get(key) or {}).get('source')=='EXCLUSIVE_RECEIVED_WORKBOOK' else None
        automatic=automatic_minimum((history or {}).get(key,[]),unit) if value is None and file_value is None else None
        effective=value if value is not None else str(file_value) if file_value is not None else automatic['value'] if automatic else None
        result[key]=dict(value=effective,manual_value=value,source='MANUAL' if value is not None else 'WORKBOOK' if file_value is not None else 'AUTOMATIC' if automatic else 'UNCONFIGURED',automatic=automatic,revision=revision,updated_at=updated,unit=unit,**alert(inventory.get(key),effective,unit))
    return result


def save_minimums(db, store, data):
    dataset=data['dataset_id'];info=store.describe(dataset);company=dataset if info.get('exclusive_workbook') else info['company']['company_id']
    from eios.company_commercial_catalogue import apply_catalogue
    with sqlite3.connect(db) as c:
        active_articles,_,_=apply_catalogue(c,dataset,[r['data'] for r in store.records(dataset,'article')],[r['data'] for r in store.records(dataset,'supplier')])
    articles={a['article_id']:a for a in active_articles}
    changes=data.get('changes')
    if not isinstance(changes,list) or not changes or len(changes)>500: raise ValueError('Indica entre 1 y 500 mínimos modificados.')
    prepared=[];seen=set()
    for change in changes:
        key=change['article_id'];a=articles.get(key)
        if not a or key in seen: raise ValueError('Artículo no válido o duplicado.')
        seen.add(key);unit=a.get('unit_as_documented','')
        if not unit or change.get('unit')!=unit: raise ValueError('La unidad no coincide con la del artículo.')
        raw=change.get('value');value=None if raw in (None,'') else decimal(raw)
        if raw not in (None,'') and (value is None or value<0 or value>Decimal('1000000000')): raise ValueError('El mínimo debe ser un número no negativo y finito, hasta 1.000.000.000.')
        revision=change.get('revision')
        if type(revision) is not int or revision<0: raise ValueError('Revisión del mínimo no válida.')
        prepared.append((key,unit,None if value is None else format(value.normalize(),'f'),revision))
    now=datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db) as c:
        schema(c);c.execute('BEGIN IMMEDIATE')
        for key,unit,value,revision in prepared:
            old=c.execute('SELECT value,revision FROM company_stock_minimum WHERE company_id=? AND article_id=? AND unit=?',(company,key,unit)).fetchone()
            if (old[1] if old else 0)!=revision: raise ValueError('Otro cambio modificó estos mínimos. Recarga antes de guardar.')
            previous=old[0] if old else None
            if previous==value: continue
            c.execute('INSERT INTO company_stock_minimum VALUES(?,?,?,?,?,?) ON CONFLICT(company_id,article_id,unit) DO UPDATE SET value=excluded.value,revision=excluded.revision,updated_at=excluded.updated_at',(company,key,unit,value,revision+1,now))
            c.execute('INSERT INTO company_stock_minimum_history(company_id,article_id,unit,old_value,new_value,revision,updated_at,dataset_id) VALUES(?,?,?,?,?,?,?,?)',(company,key,unit,previous,value,revision+1,now,dataset))
    return dict(status='SAVED',message='Mínimos guardados. Avisos referidos a la fecha del inventario; no son órdenes de compra.')
