"""EIOS F3.11: opening treasury identity, saved-source and scope regressions.

Fixtures are local synthetic only. No asserted cash availability, bank
reconciliation or enterprise authority is treated as proven by these tests.
"""
import json
import sqlite3
import unittest

from eios.company_finance_execution import execute_documentary_finance
from tests.test_company_finance_activation import FinanceActivationTest as Base


class OpeningTreasuryDocumentaryGuardTest(unittest.TestCase):
    setUp = Base.setUp
    tearDown = Base.tearDown
    add = Base.add
    financial_data = Base.financial_data
    prepare = Base.prepare
    activate = Base.activate
    context = Base.context

    def setup_case(self):
        self.financial_data()
        self.prepare()
        self.activate()
        proposal = self.desk.save(self.data)
        return proposal, self.context()

    def execute(self, proposal, context):
        return execute_documentary_finance(self.path, proposal, context)

    def mutate_stored(self, mutate):
        with sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT record_json FROM documentary_company_record "
                "WHERE dataset_id='one' AND kind='financial_snapshot' AND record_id='SNAP'",
            ).fetchone()
            value = json.loads(row[0])
            mutate(value)
            conn.execute(
                "UPDATE documentary_company_record SET record_json=? "
                "WHERE dataset_id='one' AND kind='financial_snapshot' AND record_id='SNAP'",
                (json.dumps(value, ensure_ascii=False),),
            )

    def test_opening_matches_local_saved_record_but_bank_reconciliation_remains_unknown(self):
        proposal, captured = self.setup_case()
        output = self.execute(proposal, captured)
        self.assertEqual(output["status"], "EXECUTED")
        self.assertEqual(
            output["opening_treasury_status"],
            "MATCHED_RECORDED_OPENING_NOT_BANK_RECONCILED",
        )
        self.assertEqual(output["opening_treasury_source_ref"], "DOC-FIN")
        self.assertEqual(len(output["opening_treasury_source_fingerprint"]), 64)
        self.assertEqual(output["opening_treasury_support_count"], 0)
        self.assertIsNone(output["opening_treasury_reconciled"])
        self.assertEqual(
            output["opening_treasury_source_authentication"],
            "NOT_EXTERNALLY_AUTHENTICATED",
        )
        self.assertFalse(output["decision_authority"])
        self.assertEqual(output["operational_path"], "FORBIDDEN")

    def test_captured_amount_changed_without_changing_saved_record_is_rejected(self):
        proposal, captured = self.setup_case()
        captured["financial_snapshot"]["available_treasury"] = "5000000"
        result = self.execute(proposal, captured)
        self.assertEqual(result["status"], "NOT_EXECUTED")
        self.assertEqual(result["opening_treasury_status"], "REJECTED")
        self.assertEqual(
            result["opening_treasury_issue"], "OPENING_SNAPSHOT_CONTENT_MISMATCH",
        )
        self.assertIsNone(result["finance_result"])
        self.assertEqual(result["parameter_configurations"], [])
        self.assertNotIn("finance_package_fingerprint", result)

    def test_captured_snapshot_currency_or_source_ref_change_is_rejected(self):
        proposal, source = self.setup_case()
        for key, value in (("currency", "USD"), ("treasury_evidence_ref", "OTHER-DOC")):
            with self.subTest(key=key):
                case = json.loads(json.dumps(source))
                case["financial_snapshot"][key] = value
                result = self.execute(proposal, case)
                self.assertEqual(result["status"], "NOT_EXECUTED")
                self.assertEqual(
                    result["opening_treasury_issue"],
                    "OPENING_SNAPSHOT_CONTENT_MISMATCH",
                )
                self.assertNotIn("finance_input", result)

    def test_saved_balance_mutated_after_capture_cannot_reach_the_engine(self):
        proposal, captured = self.setup_case()
        self.mutate_stored(
            lambda obj: obj["data"].update(available_treasury="999999"),
        )
        result = self.execute(proposal, captured)
        self.assertEqual(result["status"], "NOT_EXECUTED")
        self.assertEqual(result["opening_treasury_issue"], "OPENING_SNAPSHOT_CONTENT_MISMATCH")
        self.assertIsNone(result["finance_result"])

    def test_matching_modified_snapshot_still_rejected_against_frozen_proposal(self):
        proposal, captured = self.setup_case()
        self.mutate_stored(
            lambda obj: obj["data"].update(available_treasury="20000"),
        )
        captured["financial_snapshot"]["available_treasury"] = "20000"
        result = self.execute(proposal, captured)
        self.assertEqual(result["status"], "NOT_EXECUTED")
        self.assertEqual(result["opening_treasury_issue"], "OPENING_CHANGED_SINCE_PROPOSAL")

    def test_treasury_evidence_ref_must_belong_to_stored_snapshot_source_refs(self):
        proposal, captured = self.setup_case()
        self.mutate_stored(
            lambda obj: obj.update(source_refs=[{"document_ref": "OTHER-DOCUMENT"}]),
        )
        captured = self.context()
        result = self.execute(proposal, captured)
        self.assertEqual(result["status"], "NOT_EXECUTED")
        self.assertEqual(result["opening_treasury_issue"], "OPENING_SOURCE_REFERENCE_MISMATCH")

    def test_missing_or_second_opening_record_does_not_produce_finance_output(self):
        proposal, captured = self.setup_case()
        with sqlite3.connect(self.path) as conn:
            conn.execute(
                "DELETE FROM documentary_company_record "
                "WHERE dataset_id='one' AND kind='financial_snapshot' AND record_id='SNAP'"
            )
        result = self.execute(proposal, captured)
        self.assertEqual(result["status"], "NOT_EXECUTED")
        self.assertEqual(result["opening_treasury_issue"], "OPENING_SNAPSHOT_NOT_UNIQUE")
        self.assertIsNone(result["finance_result"])

    def test_duplicate_json_keys_in_opening_source_are_rejected(self):
        proposal, captured = self.setup_case()
        with sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT record_json FROM documentary_company_record "
                "WHERE dataset_id='one' AND kind='financial_snapshot' AND record_id='SNAP'"
            ).fetchone()[0]
            conn.execute(
                "UPDATE documentary_company_record SET record_json=? "
                "WHERE dataset_id='one' AND kind='financial_snapshot' AND record_id='SNAP'",
                (row[:-1] + ',\"data\":{}}',),
            )
        result = self.execute(proposal, captured)
        self.assertEqual(result["status"], "NOT_EXECUTED")
        self.assertEqual(result["opening_treasury_issue"], "INVALID_SAVED_OPENING")

    def test_parent_and_child_bank_accounts_report_overlap_without_double_summing(self):
        proposal, captured = self.setup_case()
        self.add("account_balance", "B-PARENT",
                 dict(account_code="572", balance="5000", currency="EUR",
                      as_of_date="2026-09-30"))
        self.add("account_balance", "B-CHILD",
                 dict(account_code="572001", balance="5000", currency="EUR",
                      as_of_date="2026-09-30"))
        output = self.execute(proposal, captured)
        self.assertEqual(output["status"], "EXECUTED")
        self.assertEqual(output["opening_treasury_support_count"], 2)
        self.assertIn(
            "CASH_BANK_PARENT_CHILD_OVERLAP",
            output["opening_treasury_support_issues"],
        )
        self.assertIsNone(output["opening_treasury_reconciled"])
        self.assertEqual(output["finance_input"]["snapshot"]["available_treasury"], "5000")
        self.assertFalse(output["decision_authority"])

    def test_duplicate_cash_bank_account_and_wrong_support_cutoff_flagged(self):
        proposal, captured = self.setup_case()
        self.add("account_balance", "B-ONE",
                 dict(account_code="570", balance="200", currency="EUR",
                      as_of_date="2026-09-29"))
        self.add("account_balance", "B-TWO",
                 dict(account_code="570", balance="250", currency="USD",
                      as_of_date="2026-09-30"))
        output = self.execute(proposal, captured)
        self.assertEqual(output["status"], "EXECUTED")
        issues = output["opening_treasury_support_issues"]
        self.assertIn("DUPLICATED_CASH_BANK_ACCOUNT", issues)
        self.assertIn("SUPPORT_AS_OF_DATE_MISMATCH", issues)
        self.assertIn("SUPPORT_CURRENCY_MISMATCH", issues)
        self.assertIsNone(output["opening_treasury_reconciled"])

    def test_foreign_company_support_rows_never_enter_own_opening_report(self):
        proposal, captured = self.setup_case()
        self.add("account_balance", "OTHER-ACCOUNT",
                 dict(account_code="572", balance="999999", currency="EUR"),
                 dataset="two")
        output = self.execute(proposal, captured)
        self.assertEqual(output["status"], "EXECUTED")
        self.assertEqual(output["opening_treasury_support_count"], 0)

    def test_existing_mathematical_engine_unchanged_and_no_operational_promotion(self):
        proposal, captured = self.setup_case()
        initial = self.execute(proposal, captured)
        second = self.execute(proposal, self.context())
        self.assertEqual(initial["finance_result"], second["finance_result"])
        self.assertEqual(initial["fingerprint"], second["fingerprint"])
        self.assertEqual(initial["finance_result"]["projection"]["status"], "NOT_EVIDENCED")
        self.assertIsNone(initial["opening_treasury_reconciled"])
        self.assertFalse(initial["decision_authority"])
        self.assertEqual(initial["operational_path"], "FORBIDDEN")


if __name__ == "__main__":
    unittest.main()
