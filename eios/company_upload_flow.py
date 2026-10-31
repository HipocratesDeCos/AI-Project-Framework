"""Registered identities for guided uploads; selecting one never merges companies."""
from contextlib import closing
import json
import sqlite3


def companies(db):
    with closing(sqlite3.connect(db)) as c:
        result={}
        if c.execute("SELECT 1 FROM sqlite_master WHERE name='received_company'").fetchone():
            for code,name,nature in c.execute('SELECT company_id,legal_name,material_nature FROM received_company'):
                result[code]=dict(company_id=code,legal_name=name,material_nature=nature,registered=True)
        for raw, in c.execute('SELECT manifest_json FROM documentary_company_snapshot ORDER BY as_of_date DESC'):
            manifest=json.loads(raw);company=manifest['company'];code=company['company_id']
            result.setdefault(code,dict(company_id=code,legal_name=company.get('legal_name') or code,material_nature=manifest.get('material_nature','SYNTHETIC'),registered=False))
    return sorted(result.values(),key=lambda r:(r['legal_name'].casefold(),r['company_id']))
