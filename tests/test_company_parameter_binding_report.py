"""Consumer-binding inventory: truthful local Finance activation, no new authority."""
import json
import sqlite3
import unittest

from eios.company_parameters import read_parameters
from eios.company_parameter_bindings import (
    LOCAL_FINANCE_CONSUMERS,
    describe_company_parameter_bindings,
)
from tests.test_company_finance_activation import FinanceActivationTest


class CompanyBindingReportTest(unittest.TestCase):
    setUp = FinanceActivationTest.setUp
    tearDown = FinanceActivationTest.tearDown
    prepare = FinanceActivationTest.prepare
    activate = FinanceActivationTest.activate

    def report(self, dataset="one"):
        return read_parameters(self.path, self.desk.store, dataset)[
            "parameter_binding_report"
        ]

    def test_no_active_parameter_before_explicit_activation(self):
        report = self.report()
        self.assertEqual(report["schema"], "COMPANY-PARAMETER-BINDINGS-01")
        self.assertFalse(report["decision_authority"])
        self.assertEqual(report["operational_path"], "FORBIDDEN")
        for key in LOCAL_FINANCE_CONSUMERS:
            item = report["entries"][key]
            self.assertEqual(item["status"], "AVAILABLE_NOT_ACTIVATED")
            self.assertIsNone(item["effective_value"])
            self.assertIsNone(item["activation_ref"])
        self.assertEqual(
            report["entries"]["P-PRE-001"]["status"],
            "PENDING_COMPANY_CONSUMER",
        )
        self.assertEqual(
            report["entries"]["P-STK-002"]["status"],
            "PENDING_COMPANY_CONSUMER",
        )

    def test_saved_request_does_not_make_parameter_active(self):
        state = self.prepare()
        report = state["parameter_binding_report"]
        self.assertEqual(state["current"]["values"]["P-FIN-001"], "90.0")
        self.assertEqual(
            report["entries"]["P-FIN-001"]["status"],
            "AVAILABLE_NOT_ACTIVATED",
        )
        self.assertIsNone(report["entries"]["P-FIN-002"]["effective_value"])

    def test_explicit_local_synthetic_activation_is_reported_with_evidence(self):
        self.prepare()
        activated = self.activate()
        report = activated["parameter_binding_report"]
        record = activated["finance_activation"]
        self.assertEqual(report["company_id"], record["company_id"])
        self.assertEqual(report["dataset_id"], record["dataset_id"])
        self.assertEqual(report["as_of_date"], record["as_of_date"])
        self.assertEqual(set(report["entries"]), set(
            item["parameter_id"] for item in activated["catalogue"]
        ))
        for pid, expected in (("P-FIN-001", "90.0"), ("P-FIN-002", "2000")):
            item = report["entries"][pid]
            self.assertEqual(item["status"], "ACTIVE_LOCAL_SYNTHETIC_AT_CUTOFF")
            self.assertEqual(item["scope"], "LOCAL_SYNTHETIC_ONLY")
            self.assertEqual(item["effective_value"], expected)
            self.assertEqual(item["activation_ref"], record["fingerprint"])
            self.assertIn("execute_documentary_finance", item["consumer"])
        self.assertEqual(
            report["entries"]["P-FIN-003"]["status"],
            "PENDING_COMPANY_CONSUMER",
        )

    def test_each_company_is_scoped_and_does_not_inherit_other_activation(self):
        self.prepare()
        self.activate()
        other = self.report("two")
        self.assertNotEqual(self.report()["company_id"], other["company_id"])
        self.assertEqual(other["entries"]["P-FIN-001"]["status"], "AVAILABLE_NOT_ACTIVATED")
        self.assertIsNone(other["entries"]["P-FIN-001"]["effective_value"])
        self.prepare(dataset="two", minimum="100")
        self.activate(dataset="two")
        self.assertEqual(self.report("two")["entries"]["P-FIN-002"]["effective_value"], "100")
        self.assertEqual(self.report()["entries"]["P-FIN-002"]["effective_value"], "2000")

    def test_later_saved_request_does_not_replace_activated_values(self):
        self.prepare()
        self.activate()
        new_request = self.prepare(revision=1, minimum="3000")
        report = new_request["parameter_binding_report"]
        item = report["entries"]["P-FIN-002"]
        self.assertEqual(item["status"], "ACTIVE_LOCAL_SYNTHETIC_PRIOR_REQUEST")
        self.assertEqual(item["effective_value"], "2000")
        self.assertNotEqual(
            new_request["current"]["values"]["P-FIN-002"],
            item["effective_value"],
        )
        self.assertFalse(report["decision_authority"])

    def test_corrupt_persisted_activation_does_not_claim_active(self):
        self.prepare()
        self.activate()
        with sqlite3.connect(self.path) as conn:
            row = conn.execute(
                "SELECT payload FROM company_finance_parameter_activation "
                "WHERE company_id=? AND as_of_date=?",
                (self.report()["company_id"], self.report()["as_of_date"]),
            ).fetchone()
            forged = json.loads(row[0])
            forged["values"]["P-FIN-002"] = "999999"
            conn.execute(
                "UPDATE company_finance_parameter_activation SET payload=? "
                "WHERE company_id=? AND as_of_date=?",
                (
                    json.dumps(forged),
                    forged["company_id"],
                    forged["as_of_date"],
                ),
            )
        item = self.report()["entries"]["P-FIN-002"]
        self.assertEqual(item["status"], "ACTIVATION_RECORD_UNVERIFIED")
        self.assertIsNone(item["effective_value"])
        self.assertIsNone(item["activation_ref"])

    def test_activation_scope_mismatch_is_not_active(self):
        self.prepare()
        self.activate()
        current = read_parameters(self.path, self.desk.store, "one")
        record = current["finance_activation"]
        desc = describe_company_parameter_bindings
        kwargs = dict(catalogue=current["catalogue"], activation=record,
                      company_id=current["company_id"], dataset_id="some-other-dataset",
                      as_of_date=current["as_of_date"], current_revision=1)
        self.assertEqual(
            desc(**kwargs)["entries"]["P-FIN-001"]["status"],
            "ACTIVATION_RECORD_UNVERIFIED",
        )
        kwargs["dataset_id"] = current["dataset_id"]
        kwargs["as_of_date"] = "2026-10-01"
        self.assertEqual(
            desc(**kwargs)["entries"]["P-FIN-002"]["status"],
            "ACTIVATION_RECORD_UNVERIFIED",
        )

    def test_report_rejects_bad_catalogue_and_revision(self):
        current = read_parameters(self.path, self.desk.store, "one")
        kwargs = dict(catalogue=current["catalogue"], activation=None,
                      company_id=current["company_id"],
                      dataset_id=current["dataset_id"],
                      as_of_date=current["as_of_date"], current_revision=0)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            describe_company_parameter_bindings(
                **(kwargs | {"catalogue": (current["catalogue"][0],) * 2})
            )
        with self.assertRaisesRegex(ValueError, "current_revision"):
            describe_company_parameter_bindings(
                **(kwargs | {"current_revision": True})
            )

    def test_catalogue_definition_is_not_mutated_by_the_read_only_report(self):
        state = read_parameters(self.path, self.desk.store, "one")
        self.assertEqual(
            state["catalogue"][0]["consumer_status"], "PENDING_ENGINE_BINDING"
        )
        self.assertNotIn("effective_value", state["catalogue"][0])
        self.assertIsNone(state["parameter_binding_report"]["entries"]["P-FIN-001"]["effective_value"])


if __name__ == "__main__":
    unittest.main()
