import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from collections import Counter

from eios.company_data import CompanyDataStore, SCHEMA


class CompanyIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = self.root / "company.sqlite3"
        self.store = CompanyDataStore(self.db)

    def tearDown(self):
        self.temp.cleanup()

    def package(self, transform=None, corrupt_document=False):
        ref = [{"document_ref": "DOC"}]
        records = [
            {"kind": "company_identity", "record_id": "COMP", "data": {"company_id": "COMP"}, "source_refs": ref},
            {"kind": "financial_snapshot", "record_id": "SNAPSHOT", "data": {"company_scope": "COMP", "as_of_date": "2026-09-30", "data_snapshot_id": "SNAP", "currency": "EUR", "available_treasury": None}, "source_refs": ref},
            {"kind": "article", "record_id": "SKU", "data": {"stock_quantity": None, "demand_forecast": None}, "source_refs": ref},
            {"kind": "cash_flow", "record_id": "FLOW", "data": {"canonical": {"flow_id": "FLOW", "flow_type": "PAYMENT", "amount": "0.01", "currency": "EUR", "due_date": "2026-10-01", "evidence_state": "NOT_EVIDENCED", "due_date_evidenced": False}}, "source_refs": ref},
        ]
        if transform:
            transform(records)
        raw = json.dumps(records).encode()
        document = b"synthetic source"
        manifest = {"schema_version": SCHEMA, "material_nature": "SYNTHETIC", "operational_path": "FORBIDDEN", "company": {"company_id": "COMP"}, "as_of_date": "2026-09-30", "records": {"path": "records.json", "sha256": hashlib.sha256(raw).hexdigest()}, "documents": [{"document_ref": "DOC", "path": "source.txt", "bytes": len(document), "sha256": hashlib.sha256(document).hexdigest()}], "record_counts": dict(Counter(r["kind"] for r in records))}
        target = self.root / "package.zip"
        with zipfile.ZipFile(target, "w") as z:
            z.writestr("company_manifest.json", json.dumps(manifest))
            z.writestr("records.json", raw)
            z.writestr("source.txt", b"different bytes" if corrupt_document else document)
        return target

    def test_reopen_nulls_exact_money_and_idempotence(self):
        package = self.package()
        imported = self.store.import_dataset(package)
        self.assertEqual("IMPORTED", imported["status"])
        reopened = CompanyDataStore(self.db)
        self.assertIsNone(reopened.financial_snapshot(imported["dataset_id"]).available_treasury)
        self.assertIsNone(reopened.records(imported["dataset_id"], "article")[0]["data"]["stock_quantity"])
        self.assertEqual("0.01", str(reopened.cash_flows(imported["dataset_id"])[0].amount))
        self.assertEqual("UNCHANGED", reopened.import_dataset(package)["status"])
        self.assertEqual(1, reopened.describe(imported["dataset_id"])["record_counts"]["cash_flow"])

    def test_duplicate_ids_rejected_without_damaging_existing_snapshot(self):
        good = self.store.import_dataset(self.package())
        package = self.package(lambda rows: rows.append(dict(rows[-1])))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.store.import_dataset(package)
        self.assertEqual(1, len(self.store.cash_flows(good["dataset_id"])))

    def test_corrupt_source_rejected_before_database_creation(self):
        with self.assertRaisesRegex(ValueError, "Document content hash"):
            self.store.import_dataset(self.package(corrupt_document=True))
        self.assertFalse(self.db.exists())

    def test_company_mismatch_and_foreign_scope_rejected(self):
        def change(rows):
            rows[1]["data"]["company_scope"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "company/cutoff"):
            self.store.import_dataset(self.package(change))
        self.assertFalse(self.db.exists())

    def test_prior_simulation_stock_and_evidence_cannot_be_loaded(self):
        def stock(rows):
            rows[2]["data"]["stock_quantity"] = "3"
        with self.assertRaisesRegex(ValueError, "null"):
            self.store.import_dataset(self.package(stock))
        def promote(rows):
            rows[-1]["data"]["canonical"]["evidence_state"] = "DEMONSTRATED"
            rows[-1]["data"]["canonical"]["source_ref"] = "fixture"
        with self.assertRaisesRegex(ValueError, "promote"):
            self.store.import_dataset(self.package(promote))

    def test_changed_dataset_preserves_old_snapshot_and_unknown_id_fails(self):
        first = self.store.import_dataset(self.package())
        def changed(rows):
            rows[-1]["data"]["canonical"]["amount"] = "0.02"
        second = self.store.import_dataset(self.package(changed))
        self.assertNotEqual(first["dataset_id"], second["dataset_id"])
        self.assertEqual("0.01", str(self.store.cash_flows(first["dataset_id"])[0].amount))
        self.assertEqual("0.02", str(self.store.cash_flows(second["dataset_id"])[0].amount))
        with self.assertRaises(KeyError):
            self.store.records("NOT-A-DATASET", "cash_flow")


if __name__ == "__main__":
    unittest.main()
