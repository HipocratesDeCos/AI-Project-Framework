"""Conserve pre-save negotiation inputs and server-calculated costs, without acceptance."""
from .company_commercial_terms import commercial_terms
from .company_purchase_comparison import condition

REQUIRED = {'unit_price', 'pricing_mode', 'discount_mode', 'discount_value', 'due_date'}
FIELDS = REQUIRED | {'vat_percent','shipping_mode','shipping_net','shipping_vat_percent','shipping_billed_by','shipping_due_date','payment_installments'}


def capture(base, variants, *, analyze=None):
    if variants is None:
        if base.get('negotiation_selected_slot') not in (None,''):
            raise ValueError('Selecciona una opción de negociación activa para guardar.')
        return None
    if not isinstance(variants, list) or len(variants) > 2:
        raise ValueError('Indica hasta dos alternativas de negociación.')
    entries = []
    seen = set()
    for variant in variants:
        if not isinstance(variant, dict) or set(variant) != {'slot', 'patch', 'condition'}:
            raise ValueError('Alternativa de negociación no válida.')
        slot = variant['slot']
        if slot not in ('mine', 'response') or slot in seen:
            raise ValueError('Columna de negociación no válida o duplicada.')
        seen.add(slot)
        patch = variant['patch']
        if not isinstance(patch, dict) or not REQUIRED <= set(patch) or set(patch) - FIELDS:
            raise ValueError('Completa precio, descuento y vencimiento de la alternativa.')
        metadata = condition(variant['condition'])
        values = dict(base, **patch)
        values['payment_installments'] = patch.get('payment_installments')
        quote = commercial_terms(values)
        entry=dict(slot=slot, label='Mi propuesta' if slot == 'mine' else 'Propuesta del proveedor',
                            patch={key: quote['due_date'] if key == 'due_date' else patch[key] for key in patch},
                            condition=metadata, quote=quote)
        from .company_payment_plan import payment_plan
        try:
            entry['payment_plan']=payment_plan(values,dict(quote,proposal_id='NEGOTIATION-'+slot,currency='EUR'))
        except ValueError as error:
            raise ValueError(entry['label']+' · Calendario de pagos: '+str(error)) from error
        if analyze is not None:entry['cash_orientation']=analyze(values)
        entries.append(entry)
    selected=base.get('negotiation_selected_slot')
    if selected is not None:
        chosen=next((entry for entry in entries if entry['slot']==selected),None)
        if chosen is None:raise ValueError('Selecciona una opción de negociación activa para guardar.')
        active= commercial_terms(base)
        if any(chosen['quote'][key]!=active[key] for key in ('unit_price','vat_percent','net','tax','total','operation_total','due_date')) or chosen['quote']['commercial_terms']['shipping']!=active['commercial_terms']['shipping']:
            raise ValueError('La opción seleccionada no coincide con las condiciones del estudio.')
        if chosen['payment_plan']['installments'] != payment_plan(base,dict(active,proposal_id='NEGOTIATION-'+selected,currency='EUR'))['installments']:
            raise ValueError('El calendario seleccionado no coincide con el estudio.')
    return dict(selected_slot=selected,schema='PURCHASE-NEGOTIATION-DRAFT-01', alternatives=entries,
                decision_authority=False, acceptance_status='UNVERIFIED')


def ensure_analysis_context(studies):
    """Do not preserve an apparent comparison across changing financial criteria."""
    usable=[study for study in studies if study.get('status')!='PENDING']
    fields=('documentary_context','financial_source_fingerprint','parameter_activation',
            'opening_balance','treasury_minimum','cutoff','horizon_end')
    if usable and any(any(study.get(field)!=usable[0].get(field) for field in fields) for study in usable[1:]):
        raise ValueError('Han cambiado las fuentes o criterios financieros durante el estudio. Recarga y vuelve a guardar.')
