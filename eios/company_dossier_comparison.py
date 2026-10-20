"""Read-only comparison of saved selections; no implicit replacement or admission."""
from collections import Counter

from eios.company_dossier import selected_batches
from eios.company_dossier_versions import version
from eios.company_reception import canonical
from eios.company_tables import FIELDS


def compare_versions(db, before_id, after_id):
    before, after = version(db,before_id), version(db,after_id)
    keys = ('company_id','legal_name','material_nature','as_of_date')
    if any(before['manifest'][key] != after['manifest'][key] for key in keys):
        raise ValueError('Compara versiones de la misma empresa, naturaleza de datos y fecha de corte.')
    def summarize(saved):
        batches = selected_batches(db,saved['manifest']['batch_ids'])
        files = {entry['batch_id']:dict(entry) for entry in saved['manifest']['files']}
        counters = {kind:Counter() for kind in FIELDS}
        for bid,meta,records in batches:
            files[bid]['record_count'] = len(records)
            for record in records:
                counters[record['kind']][canonical(record['data'])] += 1
        return files,counters
    old_files, old_rows = summarize(before)
    new_files, new_rows = summarize(after)
    old_ids,new_ids = set(old_files),set(new_files)
    categories = []
    for kind in FIELDS:
        old,new = old_rows[kind],new_rows[kind]
        categories.append(dict(kind=kind,before_rows=sum(old.values()),after_rows=sum(new.values()),
            added_exact_rows=sum((new-old).values()),removed_exact_rows=sum((old-new).values())))
    labels = dict(OUTSIDE_SCOPE='Fuera del alcance de conciliación',SOURCE_WARNINGS='Avisos de recepción',CONFLICTING_ID='Identificadores contradictorios',REPEATED_ID='Identificadores repetidos',MISSING_REFERENCE='Referencias ausentes',UNIT_MISMATCH='Unidades distintas',STOCK_CONFLICT='Stock o parámetros contradictorios',REPEATED_LINE='Líneas idénticas repetidas',INVOICE_CONFLICT='Fecha o moneda de factura contradictoria')
    comparable = before['check'].get('check_schema') == after['check'].get('check_schema')
    old_issues = Counter(issue['code'] for issue in before['check']['issues'])
    new_issues = Counter(issue['code'] for issue in after['check']['issues'])
    result = {key:before['manifest'][key] for key in keys}
    result.update(before=dict(dossier_id=before_id,name=before['name'],created_at=before['created_at'],issue_count=before['check']['issue_count']),
        after=dict(dossier_id=after_id,name=after['name'],created_at=after['created_at'],issue_count=after['check']['issue_count']),
        added_files=[new_files[bid] for bid in sorted(new_ids-old_ids)],
        removed_files=[old_files[bid] for bid in sorted(old_ids-new_ids)],
        shared_files=[new_files[bid] for bid in sorted(old_ids&new_ids)],categories=categories,
        checks_comparable=comparable,
        check_counts=[dict(code=code,label=labels.get(code,code),before_count=old_issues[code],after_count=new_issues[code],delta=new_issues[code]-old_issues[code] if comparable else None) for code in sorted(set(old_issues)|set(new_issues))],
        admission_status='PENDING',operational_path='FORBIDDEN',decision_authority=False,
        scope='Comparación documental sin modificar versiones. Las filas se comparan por contenido normalizado exacto, conservando multiplicidades; no identifica automáticamente una factura o línea corregida. Menos avisos no acredita mejora: puede haberse retirado documentación. Un mismo original con otro mapeo cuenta como lote distinto. No concilia importes ni admite datos para decisiones.')
    return result
