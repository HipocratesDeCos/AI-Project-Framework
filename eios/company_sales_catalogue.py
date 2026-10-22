"""Prepare source-linked catalogue references from unlinked sales, without inferring identity."""
from copy import deepcopy
from hashlib import sha256


def expanded_catalogue(dataset, articles, sales):
    known={article['article_id'] for article in articles}
    pending=[]
    used=set(known)
    for invoice in sales.get('invoices',[]):
        for line in invoice['lines']:
            if line.get('article_id') in known:
                continue
            # The code identifies a preparation for one source line. It is not a
            # documentary SKU, a description-based join, or a confirmed product.
            identity=sha256((dataset+'\0'+line['record_id']).encode()).hexdigest().upper()
            proposed='VTA-PROP-'+identity[:10]
            if proposed in used:proposed='VTA-PROP-'+identity
            while proposed in used:proposed+='-P'
            used.add(proposed)
            pending.append(dict(proposed_article_id=proposed,description=line.get('description'),
                documented_article_id=line.get('article_id'),unit_as_documented=line.get('unit'),
                reference_unit_cost=None,recommended_sale_price=None,inventory=None,
                invoice_number=invoice['invoice_number'],issue_date=invoice['issue_date'],
                customer_id=invoice['customer_id'],source_line_id=line['record_id'],
                quantity=line.get('quantity'),net_amount=line.get('net_amount'),currency=line.get('currency'),
                source_refs=deepcopy(line.get('source_refs',[])),
                missing=['Confirmar identidad y SKU']+([] if line.get('unit') else ['Unidad de venta'])+['Coste de compra','Tarifa de venta','Existencias'],
                status='PREPARED_NOT_ACTIVATED',code_origin='EIOS_PROPOSED_NOT_DOCUMENTARY',
                selectable_for_proposal=False,decision_authority=False))
    pending.sort(key=lambda row:(row['invoice_number'],row['source_line_id']))
    return dict(catalogue_article_count=len(articles),prepared_reference_count=len(pending),
        total_reference_count=len(articles)+len(pending),prepared_references=pending,
        scope='SOURCE_LINE_PREPARATIONS_NOT_CONFIRMED_DISTINCT_PRODUCTS',decision_authority=False)
