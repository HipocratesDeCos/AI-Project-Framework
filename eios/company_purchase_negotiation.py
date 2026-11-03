"""Conserve pre-save negotiation inputs and server-calculated costs, without acceptance."""
from .company_commercial_terms import commercial_terms
from .company_purchase_comparison import condition

REQUIRED = {'unit_price', 'pricing_mode', 'discount_mode', 'discount_value', 'due_date'}
FIELDS = REQUIRED | {'vat_percent','shipping_mode','shipping_net','shipping_vat_percent','shipping_billed_by','shipping_due_date'}


def capture(base, variants):
    if variants is None:
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
        quote = commercial_terms(values)
        entries.append(dict(slot=slot, label='Mi propuesta' if slot == 'mine' else 'Respuesta del proveedor',
                            patch={key: quote['due_date'] if key == 'due_date' else patch[key] for key in patch},
                            condition=metadata, quote=quote))
    return dict(schema='PURCHASE-NEGOTIATION-DRAFT-01', alternatives=entries,
                decision_authority=False, acceptance_status='UNVERIFIED')
