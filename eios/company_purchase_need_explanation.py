"""Explain the existing closing-day stock scenario; never compute a new target."""
from datetime import date
from decimal import Decimal, localcontext


def explain(result):
    with localcontext() as ctx:
        ctx.prec=60
        return _explain(result)


def _explain(result):
    a=result['assumptions'];points=result['points']
    after=[p for p in points if p['date']>=result['arrival_date']]
    critical=min(after,key=lambda p:Decimal(p['without_purchase']))
    end=points[-1];daily=Decimal(a['daily_demand']);safety=Decimal(a['safety_stock'])
    days=(date.fromisoformat(result['target_end'])-date.fromisoformat(a['order_date'])).days
    receipts=sum((Decimal(r['quantity']) for r in a['receipts']),Decimal(0))
    available=Decimal(a['available_at_order']);consumed=daily*days
    needed=max(Decimal(0),safety-Decimal(critical['without_purchase']))
    computed=Decimal(result['scenario_quantity']);current=Decimal(result['current_quantity'])
    def comparison(q):
        minimum=min(Decimal(p['without_purchase'])+q for p in after)
        return dict(quantity=str(q),end_stock=str(Decimal(end['without_purchase'])+q),
                    minimum_after_receipt=str(minimum),margin_over_safety=str(minimum-safety))
    return dict(schema='PURCHASE-NEED-EXPLANATION-01',horizon_days=days,
                period_consumption=str(consumed),gross_period_need=str(consumed+safety),
                pending_receipts=str(receipts),available_in_period=str(available+receipts),
                net_need_at_critical_date=str(needed),critical_date=critical['date'],
                aggregate_net_need=str(max(Decimal(0),consumed+safety-available-receipts)),
                timing_matters=needed!=max(Decimal(0),consumed+safety-available-receipts),
                calculated=comparison(computed),current=comparison(current),
                excess_quantity=str(current-computed),source_fingerprint=result['fingerprint'],
                decision_authority=False,operational_path='FORBIDDEN')
