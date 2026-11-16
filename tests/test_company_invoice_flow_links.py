"""F3.10: explicit invoice/instalment/flow linkage over existing synthetic data.

No matching by amount alone, no source-trust promotion and no additions to the
Finance Basic cash-flow inventory or operation payment proposal.
"""
import json
import sqlite3
import unittest

from eios.company_finance_execution import execute_documentary_finance
from tests.test_company_finance_activation import FinanceActivationTest as Fixture


class InvoiceInstallmentFlowLinksTest(unittest.TestCase):
    setUp = Fixture.setUp
    tearDown = Fixture.tearDown
    add = Fixture.add
    financial_data = Fixture.financial_data
    prepare = Fixture.prepare
    activate = Fixture.activate
    context = Fixture.context

    def add_invoice(self, kind="purchase", **patch):
        if kind == "purchase":
            data = dict(invoice_id="PI-1", invoice_number="F-P-1",
                        supplier_id="S", currency="EUR")
            data.update(patch)
            self.add("purchase_invoice", "PI-1", data)
        else:
            data = dict(invoice_number="SI-1", customer_id="C", currency="EUR")
            data.update(patch)
            self.add("sales_invoice", "SI-1", data)

    def add_installment(self, kind="purchase", record_id=None, **patch):
        if kind == "purchase":
            data = dict(invoice_id="PI-1", supplier_id="S", flow_id="P-1",
                        currency="EUR", pending_amount="500",
                        due_date="2026-10-15", amount="500")
            data.update(patch)
            self.add("purchase_installment", record_id or "P-Q1", data)
        else:
            data = dict(invoice_number="SI-1", customer_id="C", flow_id="C-1",
                        currency="EUR", pending_amount="1000",
                        due_date="2026-10-15", amount="1000")
            data.update(patch)
            self.add("sales_installment", record_id or "S-Q1", data)

    def run_report(self):
        self.prepare()
        self.activate()
        proposal = self.desk.save(self.data)
        result = execute_documentary_finance(self.path, proposal, self.context())
        self.assertEqual(result["status"], "EXECUTED")
        self.assertFalse(result["decision_authority"])
        self.assertEqual(result["operational_path"], "FORBIDDEN")
        return proposal, result

    def test_no_invoice_rows_does_not_infer_a_relationship(self):
        self.financial_data()
        _, result = self.run_report()
        report = result["invoice_installment_flow_links"]
        self.assertEqual(report["status"], "NO_RECORDED_INSTALLMENTS")
        self.assertEqual(report["installment_count"], 0)
        self.assertEqual(report["consistent_link_count"], 0)
        self.assertEqual(report["bank_payment_reconciliation"], "NOT_PERFORMED")
        self.assertEqual(result["finance_result"]["projection"]["status"], "NOT_EVIDENCED")

    def test_explicit_purchase_and_sale_references_consistent_but_not_reconciled(self):
        self.financial_data()
        self.add_invoice("purchase")
        self.add_installment("purchase")
        self.add_invoice("sale")
        self.add_installment("sale")
        _, result = self.run_report()
        report = result["invoice_installment_flow_links"]
        self.assertEqual(report["status"], "EXPLICIT_LINKS_CONSISTENT_NOT_RECONCILED")
        self.assertEqual(report["invoice_header_count"], 2)
        self.assertEqual(report["installment_count"], 2)
        self.assertEqual(report["consistent_link_count"], 2)
        self.assertTrue(all(
            row["status"] == "EXPLICIT_LINK_CONSISTENT_NOT_RECONCILED"
            and not row["problems"] and not row["pending_checks"]
            for row in report["rows"]
        ))
        self.assertEqual(report["invoice_totals_reconciled"], "NOT_PERFORMED")
        self.assertEqual(report["bank_payment_reconciliation"], "NOT_PERFORMED")
        self.assertEqual(report["source_authentication"], "NOT_EXTERNALLY_AUTHENTICATED")
        self.assertEqual(report["evidence_upgrade_status"], "NOT_PERFORMED")
        self.assertEqual(result["finance_result"]["projection"]["status"], "NOT_EVIDENCED")
        self.assertEqual(len(result["finance_input"]["cash_flows"]), 2)
        self.assertEqual(result["purchase_effect_status"], "NOT_EVALUATED")
        self.assertFalse(report["decision_authority"])
        self.assertEqual(report["operational_path"], "FORBIDDEN")

    def test_amount_date_currency_coincidence_without_flow_id_is_not_a_link(self):
        self.financial_data()
        self.add_invoice()
        self.add_installment(flow_id=None)
        _, result = self.run_report()
        report = result["invoice_installment_flow_links"]
        self.assertEqual(report["status"], "EXPLICIT_LINKS_PARTIAL")
        self.assertEqual(report["consistent_link_count"], 0)
        self.assertIn("NO_EXPLICIT_FLOW_LINK", report["rows"][0]["pending_checks"])
        self.assertIsNone(report["rows"][0]["flow_id"])

    def test_original_invoice_installment_amount_does_not_establish_pending_balance(self):
        self.financial_data()
        self.add_invoice()
        self.add_installment(pending_amount=None, amount="500")
        _, result = self.run_report()
        row = result["invoice_installment_flow_links"]["rows"][0]
        self.assertEqual(row["status"], "EXPLICIT_LINK_INCOMPLETE")
        self.assertIn("OUTSTANDING_AMOUNT_NOT_DECLARED", row["pending_checks"])

    def test_foreign_invoice_in_other_dataset_cannot_satisfy_reference(self):
        self.financial_data()
        self.add(
            "purchase_invoice", "PI-1",
            dict(invoice_id="PI-1", supplier_id="S", currency="EUR"),
            dataset="two",
        )
        self.add_installment()
        _, result = self.run_report()
        row = result["invoice_installment_flow_links"]["rows"][0]
        self.assertIn("INVOICE_NOT_FOUND", row["problems"])

    def test_explicit_flow_reference_not_in_inventory_does_not_infer_nearest_payment(self):
        self.financial_data()
        self.add_invoice()
        self.add_installment(flow_id="NONEXISTENT")
        _, result = self.run_report()
        row = result["invoice_installment_flow_links"]["rows"][0]
        self.assertIn("FLOW_NOT_IN_VERIFIED_INVENTORY", row["problems"])
        self.assertEqual(result["finance_result"]["projection"]["status"], "NOT_EVIDENCED")

    def test_one_payment_cannot_be_used_as_two_distinct_invoice_installments(self):
        self.financial_data()
        self.add_invoice()
        self.add_installment(record_id="P-Q1")
        self.add_installment(record_id="P-Q2")
        _, result = self.run_report()
        report = result["invoice_installment_flow_links"]
        self.assertEqual(report["status"], "EXPLICIT_LINKS_CONFLICTING")
        self.assertEqual(report["conflicting_link_count"], 2)
        self.assertTrue(all(
            "FLOW_REUSED_BY_MULTIPLE_INSTALLMENTS" in r["problems"]
            for r in report["rows"]
        ))

    def test_flow_direction_conflict_is_not_promoted_to_payment_proof(self):
        self.financial_data()
        self.add_invoice()
        self.add_installment(flow_id="C-1", amount="1000", pending_amount="1000")
        _, result = self.run_report()
        row = result["invoice_installment_flow_links"]["rows"][0]
        self.assertIn("FLOW_DIRECTION_MISMATCH", row["problems"])

    def test_invoice_counterparty_mismatch_detected(self):
        self.financial_data()
        self.add_invoice()
        self.add_installment(supplier_id="S-FOREIGN")
        _, result = self.run_report()
        row = result["invoice_installment_flow_links"]["rows"][0]
        self.assertIn("COUNTERPARTY_MISMATCH", row["problems"])

    def test_explicit_link_with_different_due_date_is_contradictory(self):
        self.financial_data()
        self.add_invoice()
        self.add_installment(due_date="2026-10-20")
        _, result = self.run_report()
        row = result["invoice_installment_flow_links"]["rows"][0]
        self.assertIn("FLOW_DUE_DATE_MISMATCH", row["problems"])

    def test_explicit_link_with_different_pending_amount_is_contradictory(self):
        self.financial_data()
        self.add_invoice()
        self.add_installment(pending_amount="550")
        _, result = self.run_report()
        row = result["invoice_installment_flow_links"]["rows"][0]
        self.assertIn("FLOW_OUTSTANDING_AMOUNT_MISMATCH", row["problems"])

    def test_explicit_link_with_different_currency_is_contradictory(self):
        self.financial_data()
        self.add_invoice()
        self.add_installment(currency="USD")
        _, result = self.run_report()
        row = result["invoice_installment_flow_links"]["rows"][0]
        self.assertIn("INVOICE_CURRENCY_MISMATCH", row["problems"])
        self.assertIn("FLOW_CURRENCY_MISMATCH", row["problems"])

    def test_modified_invoice_or_installment_after_proposal_cannot_be_consistent(self):
        self.financial_data()
        self.add_invoice()
        self.add_installment()
        self.prepare()
        self.activate()
        proposal = self.desk.save(self.data)
        captured = self.context()
        initial = execute_documentary_finance(self.path, proposal, captured)
        self.assertEqual(
            initial["invoice_installment_flow_links"]["consistent_link_count"], 1,
        )
        with sqlite3.connect(self.path) as c:
            raw = c.execute(
                "SELECT record_json FROM documentary_company_record "
                "WHERE dataset_id='one' AND kind='purchase_installment' AND record_id='P-Q1'"
            ).fetchone()[0]
            changed = json.loads(raw)
            changed["data"]["pending_amount"] = "510"
            c.execute(
                "UPDATE documentary_company_record SET record_json=? "
                "WHERE dataset_id='one' AND kind='purchase_installment' AND record_id='P-Q1'",
                (json.dumps(changed),),
            )
        changed_result = execute_documentary_finance(self.path, proposal, captured)
        report = changed_result["invoice_installment_flow_links"]
        self.assertEqual(changed_result["status"], "EXECUTED")
        self.assertIn("RECORD_CHANGED_SINCE_PROPOSAL", report["rows"][0]["problems"])
        self.assertNotEqual(initial["fingerprint"], changed_result["fingerprint"])
        self.assertEqual(report["consistent_link_count"], 0)
        self.assertEqual(changed_result["finance_input"], initial["finance_input"])

    def test_missing_invoice_or_invalid_sales_reference_is_explicit(self):
        self.financial_data()
        self.add_installment("sale", invoice_number="MISSING")
        _, result = self.run_report()
        row = result["invoice_installment_flow_links"]["rows"][0]
        self.assertIn("INVOICE_NOT_FOUND", row["problems"])

    def test_presentation_order_does_not_change_link_report_or_projection(self):
        self.financial_data()
        self.add_invoice()
        self.add_installment()
        self.prepare()
        self.activate()
        proposal = self.desk.save(self.data)
        source = self.context()
        result = execute_documentary_finance(self.path, proposal, source)
        source["cash_flows"].reverse()
        again = execute_documentary_finance(self.path, proposal, source)
        self.assertEqual(
            result["invoice_installment_flow_links"],
            again["invoice_installment_flow_links"],
        )
        self.assertEqual(result["finance_result"], again["finance_result"])


if __name__ == "__main__":
    unittest.main()
