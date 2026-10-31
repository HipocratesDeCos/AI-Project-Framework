"""Persistent documentary intake for synthetic companies, outside decision engines.

This adapter stores a source-bound snapshot. It is not the production SQL Server
schema, an admission result, a purchase, or an automatic source-trust upgrade.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import sqlite3
import zipfile

from eios.finance.models import CashFlow, FinancialSnapshot, WorkingCapitalInput

SCHEMA = "EIOS-COMPANY-DOCUMENT-DATASET-01/v0.1"
DOCUMENTARY_KINDS = frozenset({
    "company_identity", "company_address_variants", "supplier", "customer",
    "article", "purchase_invoice", "purchase_invoice_line", "purchase_installment",
    "historical_order", "historical_delivery_note", "sales_invoice", "sales_invoice_line",
    "sales_installment", "other_obligation", "cash_flow", "account_balance",
    "financial_snapshot", "working_capital", "treasury_balances", "bank_statement_entry",
    "cash_count", "daily_treasury_forecast", "parameter_candidate", "missing_or_conflicting",
    "document_text", "source_sheet_row",
})


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _path(name):
    p = PurePosixPath(name)
    if not name or "\\" in name or p.is_absolute() or str(p) != name or any(x in {".", ".."} for x in p.parts):
        raise ValueError("Invalid package path")
    return name


def read_dataset(path: Path):
    """Validate all bytes and canonical carriers before opening a write transaction."""
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP members")
        manifest = json.loads(z.read("company_manifest.json"))
        if manifest.get("schema_version") != SCHEMA:
            raise ValueError("Unsupported company intake schema")
        if manifest.get("material_nature") != "SYNTHETIC" or manifest.get("operational_path") != "FORBIDDEN":
            raise ValueError("This intake adapter only accepts synthetic, nonoperational material")
        company = manifest["company"]
        if not isinstance(company["company_id"], str) or not company["company_id"].strip():
            raise ValueError("Company ID is required")
        date.fromisoformat(manifest["as_of_date"])
        records_path = _path(manifest["records"]["path"])
        raw = z.read(records_path)
        if sha256(raw).hexdigest() != manifest["records"]["sha256"]:
            raise ValueError("Record content hash mismatch")
        records = json.loads(raw)
        if not isinstance(records, list):
            raise ValueError("Records must be a list")
        documents = []
        refs, paths = set(), {"company_manifest.json", records_path}
        for document in manifest["documents"]:
            ref = document["document_ref"]
            name = _path(document["path"])
            if ref in refs or name in paths:
                raise ValueError("Duplicate document reference or path")
            refs.add(ref); paths.add(name)
            content = z.read(name)
            if len(content) != document["bytes"] or sha256(content).hexdigest() != document["sha256"]:
                raise ValueError("Document content hash mismatch: " + ref)
            documents.append((document, content))
        if set(names) != paths:
            raise ValueError("Undeclared or missing package members")
        keys = set()
        for record in records:
            key = (record["kind"], record["record_id"])
            if record["kind"] not in DOCUMENTARY_KINDS:
                raise ValueError("Unknown documentary record kind; purchases and scenarios are not intake data")
            if not all(isinstance(x, str) and x.strip() for x in key) or key in keys:
                raise ValueError("Duplicate or invalid record identity")
            keys.add(key)
            if not record["source_refs"]:
                raise ValueError("Record requires source references")
            if any(x["document_ref"] not in refs for x in record["source_refs"]):
                raise ValueError("Record has foreign source reference")
            data = record["data"]
            if record["kind"] == "financial_snapshot":
                model = FinancialSnapshot.model_validate(data)
                if model.company_scope != company["company_id"] or model.as_of_date.isoformat() != manifest["as_of_date"]:
                    raise ValueError("Financial snapshot differs from company/cutoff")
            elif record["kind"] == "working_capital":
                model = WorkingCapitalInput.model_validate(data)
                if model.company_scope != company["company_id"] or model.as_of_date.isoformat() != manifest["as_of_date"]:
                    raise ValueError("Working capital differs from company/cutoff")
            elif record["kind"] == "cash_flow":
                model = CashFlow.model_validate(data["canonical"])
                if model.flow_id != record["record_id"]:
                    raise ValueError("Cash-flow identity mismatch")
                if model.evidence_state != "NOT_EVIDENCED" or model.due_date_evidenced:
                    raise ValueError("Documentary intake must not promote flow evidence")
            elif record["kind"] == "article":
                if data.get("stock_quantity") is not None or data.get("demand_forecast") is not None:
                    raise ValueError("This documentary dataset has no stock/demand evidence; values must remain null")
        declared = manifest["record_counts"]
        if dict(Counter(x["kind"] for x in records)) != declared:
            raise ValueError("Declared record counts differ")
        ids = {kind: {r["record_id"] for r in records if r["kind"] == kind} for kind in DOCUMENTARY_KINDS}
        if ids["company_identity"] != {company["company_id"]} or len(ids["financial_snapshot"]) != 1:
            raise ValueError("Exactly one matching company identity and financial snapshot required")
        for r in records:
            data = r["data"]
            for field, owner in (("supplier_id", "supplier"), ("customer_id", "customer")):
                if field in data and r["kind"] not in {"supplier", "customer"} and data[field] not in ids[owner]:
                    raise ValueError("Foreign counterparty reference")
            if r["kind"] in {"purchase_invoice_line", "purchase_installment", "historical_order", "historical_delivery_note"}:
                if data["invoice_id"] not in ids["purchase_invoice"]:
                    raise ValueError("Foreign purchase invoice reference")
            if r["kind"] in {"sales_invoice_line", "sales_installment"}:
                if data["invoice_number"] not in ids["sales_invoice"]:
                    raise ValueError("Foreign sales invoice reference")
    material = _canonical(manifest).encode()
    return manifest, records, documents, sha256(material).hexdigest()


class CompanyDataStore:
    """SQLite documentary snapshots; reads remain scoped to an exact dataset."""
    def __init__(self, path: Path):
        self.path = Path(path)

    def _connect(self):
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def import_dataset(self, package: Path):
        manifest, records, documents, identity = read_dataset(Path(package))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS documentary_company_snapshot (
                    dataset_id TEXT PRIMARY KEY, company_id TEXT NOT NULL,
                    as_of_date TEXT NOT NULL, manifest_json TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS documentary_source (
                    dataset_id TEXT NOT NULL REFERENCES documentary_company_snapshot(dataset_id),
                    document_ref TEXT NOT NULL, metadata_json TEXT NOT NULL, content BLOB NOT NULL,
                    PRIMARY KEY(dataset_id, document_ref));
                CREATE TABLE IF NOT EXISTS documentary_company_record (
                    dataset_id TEXT NOT NULL REFERENCES documentary_company_snapshot(dataset_id),
                    kind TEXT NOT NULL, record_id TEXT NOT NULL, record_json TEXT NOT NULL,
                    PRIMARY KEY(dataset_id, kind, record_id));
            """)
            if connection.execute("SELECT 1 FROM documentary_company_snapshot WHERE dataset_id=?", (identity,)).fetchone():
                return {"status": "UNCHANGED", "dataset_id": identity, "record_counts": manifest["record_counts"], "documents": len(documents)}
            with connection:
                connection.execute("INSERT INTO documentary_company_snapshot VALUES(?,?,?,?)", (identity, manifest["company"]["company_id"], manifest["as_of_date"], _canonical(manifest)))
                connection.executemany("INSERT INTO documentary_source VALUES(?,?,?,?)", [(identity, meta["document_ref"], _canonical(meta), content) for meta, content in documents])
                connection.executemany("INSERT INTO documentary_company_record VALUES(?,?,?,?)", [(identity, r["kind"], r["record_id"], _canonical(r)) for r in records])
        return {"status": "IMPORTED", "dataset_id": identity, "record_counts": manifest["record_counts"], "documents": len(documents)}

    def describe(self, dataset_id: str):
        with self._connect() as connection:
            row = connection.execute("SELECT manifest_json FROM documentary_company_snapshot WHERE dataset_id=?", (dataset_id,)).fetchone()
            if row is None:
                raise KeyError(dataset_id)
            manifest = json.loads(row[0])
            counts = dict(connection.execute("SELECT kind,COUNT(*) FROM documentary_company_record WHERE dataset_id=? GROUP BY kind", (dataset_id,)).fetchall())
            documents = connection.execute("SELECT COUNT(*) FROM documentary_source WHERE dataset_id=?", (dataset_id,)).fetchone()[0]
        return {"dataset_id": dataset_id, "company": manifest["company"], "as_of_date": manifest["as_of_date"], "record_counts": counts, "documents": documents, "scope": "PERSISTENT_DOCUMENTARY_INTAKE", "operational_path": "FORBIDDEN", **({"exclusive_workbook":manifest["exclusive_workbook"]} if manifest.get("exclusive_workbook") else {})}

    def records(self, dataset_id: str, kind: str):
        self.describe(dataset_id)  # A missing/foreign scope cannot silently return healthy emptiness.
        with self._connect() as connection:
            return tuple(json.loads(row[0]) for row in connection.execute("SELECT record_json FROM documentary_company_record WHERE dataset_id=? AND kind=? ORDER BY record_id", (dataset_id, kind)))

    def document(self, dataset_id: str, document_ref: str):
        with self._connect() as connection:
            row = connection.execute("SELECT content FROM documentary_source WHERE dataset_id=? AND document_ref=?", (dataset_id, document_ref)).fetchone()
            if row is None:
                raise KeyError((dataset_id, document_ref))
            return row[0]

    def cash_flows(self, dataset_id: str):
        return tuple(CashFlow.model_validate(r["data"]["canonical"]) for r in self.records(dataset_id, "cash_flow"))

    def financial_snapshot(self, dataset_id: str):
        records = self.records(dataset_id, "financial_snapshot")
        if len(records) != 1:
            raise ValueError("Expected exactly one financial snapshot")
        return FinancialSnapshot.model_validate(records[0]["data"])


def main():
    parser = argparse.ArgumentParser(description="Load/query a synthetic company documentary snapshot; never creates purchases")
    sub = parser.add_subparsers(dest="command", required=True)
    load = sub.add_parser("load"); load.add_argument("--package", type=Path, required=True); load.add_argument("--db", type=Path, required=True)
    inspect = sub.add_parser("inspect"); inspect.add_argument("--db", type=Path, required=True); inspect.add_argument("--dataset-id", required=True)
    args = parser.parse_args(); store = CompanyDataStore(args.db)
    result = store.import_dataset(args.package) if args.command == "load" else store.describe(args.dataset_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
