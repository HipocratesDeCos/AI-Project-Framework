"""F3.9: observation-only source coverage across the stored company flows.

Uses the existing synthetic company fixture and real SQLite consumer. No
document content is parsed, independently certified or promoted to evidence.
"""
from datetime import timedelta
from hashlib import sha256
import json
import sqlite3
import unittest

from eios.company_finance_execution import execute_documentary_finance
from tests.test_company_finance_activation import FinanceActivationTest as Fixture


class LocalFlowDocumentaryCoverageTest(unittest.TestCase):
    setUp = Fixture.setUp
    tearDown = Fixture.tearDown
    prepare = Fixture.prepare
    activate = Fixture.activate
    financial_data = Fixture.financial_data
    context = Fixture.context

    def seed_document(self, *, dataset="one", content=b"synthetic invoice terms",
                      metadata=None):
        with sqlite3.connect(self.path) as conn:
            columns = {
                item[1] for item in
                conn.execute("PRAGMA table_info(documentary_source)").fetchall()
            }
            for name, kind in (
                ("document_ref", "TEXT"),
                ("content", "BLOB"),
                ("metadata_json", "TEXT"),
            ):
                if name not in columns:
                    conn.execute(
                        "ALTER TABLE documentary_source ADD COLUMN " + name + " " + kind
                    )
            if metadata is None:
                metadata = {
                    "sha256": sha256(content).hexdigest(),
                    "bytes": len(content),
                    "filename": "soporte-sintetico.pdf",
                }
            conn.execute(
                "INSERT INTO documentary_source "
                "(dataset_id, document_ref, content, metadata_json) VALUES (?,?,?,?)",
                (dataset, "DOC-FIN", content, json.dumps(metadata)),
            )

    def run_case(self, *, add_source=False, metadata=None):
        self.financial_data()
        if add_source:
            self.seed_document(metadata=metadata)
        self.prepare()
        self.activate()
        proposal = self.desk.save(self.data)
        return proposal, self.context()

    def execute(self, proposal, documentary):
        return execute_documentary_finance(self.path, proposal, documentary)

    def test_full_source_bytes_coverage_not_mistaken_for_reconciled_invoices(self):
        proposal, data = self.run_case(add_source=True)
        output = self.execute(proposal, data)
        report = output["flow_documentary_coverage"]
        self.assertEqual(output["status"], "EXECUTED")
        self.assertEqual(report["status"], "SOURCE_BYTES_PRESENT_NOT_RECONCILED")
        self.assertEqual(report["flow_count"], 2)
        self.assertEqual(report["source_bytes_present_count"], 2)
        self.assertEqual(report["source_issues"], [])
        self.assertEqual(report["documentary_content_review"], "NOT_PERFORMED")
        self.assertEqual(report["invoice_and_bank_reconciliation"], "NOT_PERFORMED")
        self.assertEqual(report["inventory_completeness"], "NOT_ESTABLISHED")
        self.assertEqual(report["source_authentication"], "NOT_EXTERNALLY_AUTHENTICATED")
        self.assertEqual(report["evidence_upgrade_status"], "NOT_PERFORMED")
        self.assertFalse(report["decision_authority"])
        self.assertEqual(report["operational_path"], "FORBIDDEN")
        self.assertEqual(
            output["finance_result"]["projection"]["status"], "NOT_EVIDENCED",
        )
        self.assertTrue(all(
            f["evidence_state"] == "NOT_EVIDENCED"
            for f in output["finance_input"]["cash_flows"]
        ))
        self.assertTrue(all(
            row["document_sources"][0]["status"] == "BYTES_UNCHANGED_NOT_CONTENT_REVIEWED"
            for row in report["rows"]
        ))

    def test_old_minimal_dataset_cannot_claim_source_documents(self):
        proposal, data = self.run_case()
        output = self.execute(proposal, data)
        report = output["flow_documentary_coverage"]
        self.assertEqual(output["status"], "EXECUTED")
        self.assertEqual(report["status"], "SOURCE_LINKS_PENDING_OR_CONFLICTING")
        self.assertEqual(report["source_bytes_present_count"], 0)
        self.assertEqual(report["source_issues"], ["DOCUMENT_STORAGE_UNAVAILABLE"])
        self.assertEqual(output["finance_result"]["projection"]["status"], "NOT_EVIDENCED")

    def test_changed_source_bytes_after_proposal_downgrades_coverage_only(self):
        proposal, data = self.run_case(add_source=True)
        initial = self.execute(proposal, data)["flow_documentary_coverage"]
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "UPDATE documentary_source SET content=? "
                "WHERE dataset_id='one' AND document_ref='DOC-FIN'",
                (b"replaced synthetic invoice terms",),
            )
        output = self.execute(proposal, data)
        report = output["flow_documentary_coverage"]
        self.assertEqual(output["status"], "EXECUTED")
        self.assertEqual(report["status"], "SOURCE_LINKS_PENDING_OR_CONFLICTING")
        self.assertIn("DOCUMENT_METADATA_CONFLICT", report["source_issues"])
        self.assertNotEqual(initial["fingerprint"], report["fingerprint"])
        self.assertEqual(report["source_bytes_present_count"], 0)
        self.assertEqual(output["operational_path"], "FORBIDDEN")

    def test_changed_bytes_with_undeclared_metadata_detected_by_frozen_context(self):
        proposal, data = self.run_case(
            add_source=True, metadata={"filename": "soporte.pdf"},
        )
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "UPDATE documentary_source SET content=? WHERE dataset_id='one'",
                (b"altered unmanifested bytes",),
            )
        report = self.execute(proposal, data)["flow_documentary_coverage"]
        self.assertIn("DOCUMENT_CHANGED_SINCE_PROPOSAL", report["source_issues"])

    def test_wrong_declared_document_digest_not_treated_as_proof(self):
        proposal, data = self.run_case(add_source=True, metadata={
            "sha256": "0" * 64, "bytes": len(b"synthetic invoice terms"),
        })
        report = self.execute(proposal, data)["flow_documentary_coverage"]
        self.assertEqual(report["source_issues"], ["DOCUMENT_METADATA_CONFLICT"])
        self.assertEqual(report["source_bytes_present_count"], 0)

    def test_document_inserted_after_saved_context_cannot_become_support(self):
        proposal, data = self.run_case()
        self.seed_document()
        report = self.execute(proposal, data)["flow_documentary_coverage"]
        self.assertEqual(
            report["source_issues"], ["NOT_IN_SAVED_PROPOSAL_CONTEXT"],
        )
        self.assertEqual(report["source_bytes_present_count"], 0)

    def test_foreign_dataset_document_cannot_be_used_as_local_source(self):
        proposal, data = self.run_case()
        self.seed_document(dataset="two")
        report = self.execute(proposal, data)["flow_documentary_coverage"]
        self.assertIn("DOCUMENT_BYTES_MISSING", report["source_issues"])
        self.assertNotIn("BYTES_UNCHANGED_NOT_CONTENT_REVIEWED", str(report))

    def test_reordered_capture_has_same_documentary_coverage_fingerprint(self):
        proposal, data = self.run_case(add_source=True)
        previous = self.execute(proposal, data)
        data["cash_flows"].reverse()
        current = self.execute(proposal, data)
        self.assertEqual(
            previous["flow_documentary_coverage"]["fingerprint"],
            current["flow_documentary_coverage"]["fingerprint"],
        )
        self.assertEqual(previous["flow_documentary_coverage"]["rows"],
                         current["flow_documentary_coverage"]["rows"])

    def test_claimed_demonstrated_flows_remain_unreviewed_without_documents(self):
        self.financial_data()
        with sqlite3.connect(self.path) as conn:
            rows = conn.execute(
                "SELECT record_id, record_json FROM documentary_company_record "
                "WHERE dataset_id='one' AND kind='cash_flow'"
            ).fetchall()
            for flow_id, raw in rows:
                item = json.loads(raw)
                item["data"]["canonical"]["evidence_state"] = "DEMONSTRATED"
                item["data"]["canonical"]["due_date_evidenced"] = True
                conn.execute(
                    "UPDATE documentary_company_record SET record_json=? "
                    "WHERE dataset_id='one' AND kind='cash_flow' AND record_id=?",
                    (json.dumps(item), flow_id),
                )
        self.prepare()
        self.activate()
        proposal = self.desk.save(self.data)
        output = self.execute(proposal, self.context())
        report = output["flow_documentary_coverage"]
        # The existing Finance Basic synthetic demo is unchanged; this report
        # prevents confusing its declared flags with actual documentary proof.
        self.assertEqual(output["status"], "EXECUTED")
        self.assertEqual(report["evidence_declared_count"], 2)
        self.assertEqual(report["source_bytes_present_count"], 0)
        self.assertEqual(report["documentary_content_review"], "NOT_PERFORMED")
        self.assertEqual(report["evidence_upgrade_status"], "NOT_PERFORMED")
        self.assertEqual(report["invoice_and_bank_reconciliation"], "NOT_PERFORMED")
        self.assertFalse(report["decision_authority"])

    def test_invalid_metadata_never_upgrades_document_coverage(self):
        proposal, data = self.run_case(add_source=True)
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "UPDATE documentary_source SET metadata_json=? "
                "WHERE dataset_id='one'",
                ("not valid json {",),
            )
        report = self.execute(proposal, data)["flow_documentary_coverage"]
        self.assertEqual(report["source_issues"], ["DOCUMENT_METADATA_INVALID"])

    def test_direct_reference_not_in_source_links_is_explicit(self):
        proposal, data = self.run_case(add_source=True)
        # F3.8 protects against changing just the delivered capture. Update
        # the stored flow to model an actual synthetic source mismatch.
        with sqlite3.connect(self.path) as conn:
            raw = conn.execute(
                "SELECT record_json FROM documentary_company_record "
                "WHERE dataset_id='one' AND kind='cash_flow' AND record_id='P-1'"
            ).fetchone()[0]
            item = json.loads(raw)
            item["data"]["canonical"]["source_ref"] = "UNLINKED-DOCUMENT"
            conn.execute(
                "UPDATE documentary_company_record SET record_json=? "
                "WHERE dataset_id='one' AND kind='cash_flow' AND record_id='P-1'",
                (json.dumps(item),),
            )
        updated = self.context()
        # The proposal still holds the original frozen documentary context.
        report = self.execute(proposal, updated)["flow_documentary_coverage"]
        self.assertIn("DIRECT_SOURCE_REF_NOT_LINKED", report["source_issues"])
        entry = next(row for row in report["rows"] if row["flow_id"] == "P-1")
        self.assertFalse(entry["direct_source_reference_linked"])


if __name__ == "__main__":
    unittest.main()
