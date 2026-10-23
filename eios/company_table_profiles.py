"""Conservative header suggestions; no inference from rows, names or amounts."""
from collections import Counter
import re
import unicodedata

from eios.company_tables import FIELDS, tariff_mapping


def clean(value):
    text=unicodedata.normalize('NFD',str(value))
    return re.sub('[^a-z0-9]','', ''.join(c for c in text if not unicodedata.combining(c)).lower())


def suggestions(headers,kind):
    mapping={};conflicts=[];normalized=[clean(header) for header in headers]
    for key,label,_ in FIELDS[kind]:
        names={clean(key),clean(label)}
        matches=[i for i,header in enumerate(normalized) if header in names]
        mapping[key]=matches[0] if len(matches)==1 else None
        if len(matches)>1:conflicts.append(key)
    # Never propose the same source column for two different fields.
    uses=Counter(i for i in mapping.values() if i is not None)
    for key,index in mapping.items():
        if index is not None and uses[index]>1:
            mapping[key]=None;conflicts.append(key)
    required=[key for key,_,must in FIELDS[kind] if must]
    return dict(mapping=mapping,ambiguous_fields=sorted(set(conflicts)),missing_required=[k for k in required if mapping[k] is None])


def profiles(headers):
    proposals={kind:suggestions(headers,kind) for kind in FIELDS if kind!='document'}
    exact=[]
    for kind,proposal in proposals.items():
        mapping=proposal['mapping']
        if len(headers)==len(mapping) and all(index is not None for index in mapping.values()) and len(set(mapping.values()))==len(headers):
            exact.append(kind)
    profile=None
    if len(exact)==1:
        kind=exact[0];profile=dict(kind=kind,mapping=proposals[kind]['mapping'],basis='EXACT_TEMPLATE_HEADERS')
    elif not exact:
        # Preserve the existing explicit tariff workbook, including read-only columns.
        tariff=tariff_mapping(headers)
        if tariff:profile=dict(kind='sale_price',mapping=tariff,basis='EXPLICIT_TARIFF_HEADERS')
    return dict(table_profile=profile,column_suggestions=proposals)
