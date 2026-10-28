"""Conservative header suggestions; no inference from rows, names or amounts."""
from collections import Counter
import re
import unicodedata

from eios.company_tables import FIELDS, tariff_mapping
from eios.company_workbook_fields import EXTENSIONS


def clean(value):
    text=unicodedata.normalize('NFD',str(value))
    return re.sub('[^a-z0-9]','', ''.join(c for c in text if not unicodedata.combining(c)).lower())


def suggestions(headers,kind):
    mapping={};conflicts=[];normalized=[clean(header) for header in headers]
    for key,label,_ in FIELDS[kind]:
        names={clean(key),clean(label)}
        names.update(clean(x) for x in {'supplier_id':['Cod.Proveedor'],'customer_id':['Cod.Cliente'],'article_id':['Sku'],'email':['Correo electrónico'],'postal_code':['C.P']}.get(key,[]))
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
        optional_new={key for key,_ in EXTENSIONS.get(kind,[])}
        used=[index for index in mapping.values() if index is not None]
        if len(headers)==len(used) and len(set(used))==len(headers) and all(index is not None for key,index in mapping.items() if key not in optional_new):
            exact.append(kind)
    profile=None
    if len(exact)==1:
        kind=exact[0];optional_new={key for key,_ in EXTENSIONS.get(kind,[])};profile=dict(kind=kind,mapping={k:v for k,v in proposals[kind]['mapping'].items() if v is not None or k not in optional_new},basis='EXACT_TEMPLATE_HEADERS')
    elif not exact:
        # Preserve the existing explicit tariff workbook, including read-only columns.
        tariff=tariff_mapping(headers)
        if tariff:profile=dict(kind='sale_price',mapping=tariff,basis='EXPLICIT_TARIFF_HEADERS')
    return dict(table_profile=profile,column_suggestions=proposals)
