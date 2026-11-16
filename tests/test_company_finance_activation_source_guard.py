"""F3.1: real app consumer must match its saved local synthetic activation."""
from dataclasses import FrozenInstanceError
from datetime import datetime, time, timezone
from hashlib import sha256
import json
import sqlite3
import unittest

from eios.company_finance_execution import execute_documentary_finance
from eios.company_finance_activation_guard import (
    LocalFinanceActivationError,
    verify_local_finance_activation,
)
from eios.company_finance_parameters import (
    Authorization, Catalogue, IDS, Repository,
)
from eios.parameters.center import ParameterConfigurationCenter
from tests.test_company_finance_activation import FinanceActivationTest as _FinanceActivationTest


class LocalFinanceActivationSourceGuardTest(unittest.TestCase):
    setUp = _FinanceActivationTest.setUp
    tearDown = _FinanceActivationTest.tearDown
    add = _FinanceActivationTest.add
    prepare = _FinanceActivationTest.prepare
    activate = _FinanceActivationTest.activate
    financial_data = _FinanceActivationTest.financial_data
    context = _FinanceActivationTest.context

    def exercise(self):
        self.financial_data()
        proposal = self.desk.save(self.data)
        return execute_documentary_finance(self.path, proposal, self.context())

    def test_existing_valid_activation_is_consumed_without_operational_authority(self):
        self.prepare()
        record = self.activate()["finance_activation"]
        output = self.exercise()
        self.assertEqual(output["status"], "EXECUTED")
        self.assertEqual(output["parameter_source_status"], "MATCHED_LOCAL_SYNTHETIC_ACTIVATION")
        self.assertEqual(output["parameter_activation_ref"], record["fingerprint"])
        self.assertEqual(len(output["parameter_configurations"]), 2)
        self.assertFalse(output["decision_authority"])
        self.assertEqual(output["operational_path"], "FORBIDDEN")

    def test_saved_but_not_activated_finance_is_not_executed(self):
        self.prepare()
        output = self.exercise()
        self.assertEqual(output["status"], "NOT_EXECUTED")
        self.assertEqual(output["parameter_source_status"], "NOT_VERIFIED")
        self.assertIsNone(output["finance_result"])

    def test_deleted_historical_activation_blocks_existing_effective_configurations(self):
        self.prepare()
        self.activate()
        with sqlite3.connect(self.path) as c:
            c.execute("DELETE FROM company_finance_parameter_activation WHERE company_id='one'")
        output = self.exercise()
        self.assertEqual(output["status"], "NOT_EXECUTED")
        self.assertEqual(output["parameter_source_status"], "REJECTED")
        self.assertEqual(output["parameter_source_issue"], "ACTIVATION_MISSING")
        self.assertIsNone(output["finance_result"])
        self.assertEqual(output["parameter_configurations"], [])

    def test_changed_live_value_is_not_silently_used_despite_valid_activation_record(self):
        self.prepare()
        self.activate()
        with sqlite3.connect(self.path) as c:
            c.execute(
                "UPDATE company_finance_parameter_configuration SET value='3000' "
                "WHERE company_id='one' AND parameter_id='P-FIN-002'"
            )
        output = self.exercise()
        self.assertEqual(output["status"], "NOT_EXECUTED")
        self.assertEqual(output["parameter_source_issue"], "ACTIVATION_CONFIGURATION_MISMATCH")
        self.assertIsNone(output["finance_result"])

    def test_changed_live_timestamps_are_not_silently_used(self):
        self.prepare()
        self.activate()
        with sqlite3.connect(self.path) as c:
            c.execute(
                "UPDATE company_finance_parameter_configuration "
                "SET updated_at='2026-09-29T12:00:00+00:00' "
                "WHERE company_id='one' AND parameter_id='P-FIN-002'"
            )
        output = self.exercise()
        self.assertEqual(output["status"], "NOT_EXECUTED")
        self.assertEqual(output["parameter_source_issue"], "ACTIVATION_CONFIGURATION_MISMATCH")

    def test_unverified_activation_hash_is_rejected_without_recalculating_it(self):
        self.prepare()
        self.activate()
        with sqlite3.connect(self.path) as c:
            row=c.execute(
                "SELECT payload FROM company_finance_parameter_activation "
                "WHERE company_id='one'"
            ).fetchone()
            record=json.loads(row[0])
            record["values"]["P-FIN-002"]="3000"
            c.execute(
                "UPDATE company_finance_parameter_activation SET payload=? "
                "WHERE company_id='one'",
                (json.dumps(record,ensure_ascii=False),)
            )
        output = self.exercise()
        self.assertEqual(output["status"], "NOT_EXECUTED")
        self.assertEqual(output["parameter_source_issue"], "ACTIVATION_INVALID")

    def test_self_rehashed_activation_record_still_cannot_override_live_selection(self):
        self.prepare()
        self.activate()
        with sqlite3.connect(self.path) as c:
            raw=c.execute(
                "SELECT payload FROM company_finance_parameter_activation "
                "WHERE company_id='one'"
            ).fetchone()[0]
            record=json.loads(raw)
            record["values"]["P-FIN-002"]="3000"
            for config in record["configurations"]:
                if config["parameter_id"]=="P-FIN-002":
                    config["value"]="3000"
            record.pop("fingerprint")
            record["fingerprint"]=sha256(
                json.dumps(record,sort_keys=True,separators=(",",":"),
                           ensure_ascii=False).encode()
            ).hexdigest()
            c.execute(
                "UPDATE company_finance_parameter_activation SET payload=? "
                "WHERE company_id='one'",
                (json.dumps(record,ensure_ascii=False),)
            )
        output=self.exercise()
        self.assertEqual(output["status"],"NOT_EXECUTED")
        self.assertEqual(output["parameter_source_issue"],"ACTIVATION_CONFIGURATION_MISMATCH")

    def test_replayed_other_company_activation_is_rejected(self):
        self.prepare()
        self.activate()
        with sqlite3.connect(self.path) as c:
            record=json.loads(c.execute(
                "SELECT payload FROM company_finance_parameter_activation "
                "WHERE company_id='one'"
            ).fetchone()[0])
            record["company_id"]="two"
            record.pop("fingerprint")
            record["fingerprint"]=sha256(
                json.dumps(record,sort_keys=True,separators=(",",":"),
                           ensure_ascii=False).encode()
            ).hexdigest()
            c.execute(
                "UPDATE company_finance_parameter_activation SET payload=? "
                "WHERE company_id='one'",
                (json.dumps(record,ensure_ascii=False),)
            )
        output=self.exercise()
        self.assertEqual(output["status"],"NOT_EXECUTED")
        self.assertEqual(output["parameter_source_issue"],"ACTIVATION_INVALID")

    def test_duplicate_keys_in_activation_json_are_rejected(self):
        self.prepare()
        self.activate()
        with sqlite3.connect(self.path) as c:
            c.execute(
                "UPDATE company_finance_parameter_activation SET payload=? "
                "WHERE company_id='one'",
                ('{"company_id":"one","company_id":"two"}',)
            )
        output=self.exercise()
        self.assertEqual(output["status"], "NOT_EXECUTED")
        self.assertEqual(output["parameter_source_issue"], "INVALID_SOURCE_RECORD")

    def test_saved_new_request_does_not_change_previously_activated_settings(self):
        self.prepare()
        first=self.activate()["finance_activation"]["fingerprint"]
        self.prepare(minimum="3000", revision=1)
        output=self.exercise()
        self.assertEqual(output["status"],"EXECUTED")
        self.assertEqual(output["parameter_activation_ref"],first)
        self.assertEqual(output["parameter_source_status"],"MATCHED_LOCAL_SYNTHETIC_ACTIVATION")

    def test_real_snapshot_remains_forbidden(self):
        self.prepare()
        self.activate()
        with sqlite3.connect(self.path) as c:
            raw=c.execute(
                "SELECT manifest_json FROM documentary_company_snapshot "
                "WHERE dataset_id='one'"
            ).fetchone()[0]
            manifest=json.loads(raw)
            manifest["material_nature"]="REAL"
            c.execute(
                "UPDATE documentary_company_snapshot SET manifest_json=? "
                "WHERE dataset_id='one'",
                (json.dumps(manifest),)
            )
        output=self.exercise()
        self.assertEqual(output["status"],"NOT_EXECUTED")
        self.assertFalse(output["decision_authority"])
        self.assertEqual(output["operational_path"],"FORBIDDEN")

    def test_direct_read_requires_transaction_and_reports_no_external_authentication(self):
        self.prepare()
        self.activate()
        effective = datetime(2026, 9, 30, tzinfo=timezone.utc)
        with sqlite3.connect(self.path) as c:
            center=ParameterConfigurationCenter(Catalogue(),Authorization(),Repository(c))
            chosen=tuple(center.get_configuration_at("one",pid,effective) for pid in IDS)
            with self.assertRaises(LocalFinanceActivationError) as failed:
                verify_local_finance_activation(
                    connection=c, company_id="one", dataset_id="one",
                    as_of_date="2026-09-30", effective_at=effective,
                    configurations=chosen,
                )
            self.assertEqual(failed.exception.code,"READ_TRANSACTION_REQUIRED")
            c.execute("BEGIN")
            receipt=verify_local_finance_activation(
                connection=c, company_id="one", dataset_id="one",
                as_of_date="2026-09-30", effective_at=effective,
                configurations=chosen,
            )
            self.assertEqual(receipt.source_authentication,"NOT_EXTERNALLY_AUTHENTICATED")
            self.assertEqual(receipt.version_attestation,"NOT_ATTESTED")
            self.assertFalse(receipt.decision_authority)
            self.assertEqual(receipt.operational_path,"FORBIDDEN")
            with self.assertRaises(FrozenInstanceError):
                receipt.company_id="other"
            c.rollback()

    def test_cross_company_dataset_not_accepted_even_with_same_cutoff(self):
        self.prepare()
        self.activate()
        effective=datetime(2026,9,30,tzinfo=timezone.utc)
        with sqlite3.connect(self.path) as c:
            c.execute("BEGIN")
            center=ParameterConfigurationCenter(Catalogue(),Authorization(),Repository(c))
            chosen=tuple(center.get_configuration_at("one",pid,effective) for pid in IDS)
            with self.assertRaises(LocalFinanceActivationError) as failed:
                verify_local_finance_activation(
                    connection=c, company_id="one", dataset_id="two",
                    as_of_date="2026-09-30", effective_at=effective,
                    configurations=chosen,
                )
            self.assertEqual(failed.exception.code,"DATASET_SCOPE_MISMATCH")
            c.rollback()


    def test_foreign_balance_company_cutoff_or_currency_is_not_published_as_executed(self):
        self.prepare()
        self.activate()
        self.financial_data()
        proposal = self.desk.save(self.data)
        original = self.context()
        for field, foreign_value in (
            ("company_scope", "two"),
            ("as_of_date", "2026-09-29"),
            ("currency", "USD"),
        ):
            with self.subTest(field=field):
                documentary = json.loads(json.dumps(original))
                documentary["working_capital_input"][field] = foreign_value
                output = execute_documentary_finance(
                    self.path, proposal, documentary,
                )
                self.assertEqual(output["status"], "NOT_EXECUTED")
                self.assertIsNone(output["finance_result"])
                self.assertEqual(output["parameter_configurations"], [])
                self.assertNotIn("finance_input", output)
                self.assertNotIn("finance_package_fingerprint", output)
                self.assertNotIn("parameter_version", output)
                self.assertIn("balance", output["message"])
                self.assertEqual(
                    output["parameter_source_status"],
                    "MATCHED_LOCAL_SYNTHETIC_ACTIVATION",
                )
                self.assertEqual(output["purchase_effect_status"], "NOT_EVALUATED")
                self.assertEqual(output["viability_status"], "NOT_EVALUATED")
                self.assertFalse(output["decision_authority"])
                self.assertEqual(output["operational_path"], "FORBIDDEN")

        # Rejecting foreign documentary capital does not alter canonical
        # company configuration, source activation or later valid execution.
        valid = execute_documentary_finance(self.path, proposal, original)
        self.assertEqual(valid["status"], "EXECUTED")
        self.assertEqual(len(valid["parameter_configurations"]), 2)
        self.assertEqual(valid["finance_result"]["working_capital"]["status"], "DETERMINED")
        self.assertEqual(valid["finance_result"]["working_capital"]["value"], "8000")

    def test_incomplete_cash_flow_contract_does_not_publish_partial_configurations(self):
        self.prepare()
        self.activate()
        self.financial_data()
        proposal = self.desk.save(self.data)
        documentary = self.context()
        documentary["cash_flows"][1]["canonical"]["flow_id"] = documentary["cash_flows"][0]["record_id"]
        output = execute_documentary_finance(self.path, proposal, documentary)
        self.assertEqual(output["status"], "NOT_EXECUTED")
        self.assertIsNone(output["finance_result"])
        self.assertEqual(output["parameter_configurations"], [])
        self.assertNotIn("finance_package_fingerprint", output)
        self.assertNotIn("finance_input", output)
        self.assertFalse(output["decision_authority"])
        self.assertEqual(output["operational_path"], "FORBIDDEN")

    def test_missing_balance_still_reports_not_evidenced_without_inventing_current_assets(self):
        self.prepare()
        self.activate()
        self.financial_data()
        proposal = self.desk.save(self.data)
        documentary = self.context()
        documentary["working_capital_input"] = None
        output = execute_documentary_finance(self.path, proposal, documentary)
        self.assertEqual(output["status"], "EXECUTED")
        self.assertEqual(output["finance_result"]["working_capital"]["status"], "NOT_EVIDENCED")
        self.assertIsNone(output["finance_result"]["working_capital"]["value"])
        self.assertFalse(output["decision_authority"])
        self.assertEqual(output["operational_path"], "FORBIDDEN")


    def test_complete_stored_inventory_matches_without_promoting_accounting_completeness(self):
        self.prepare()
        self.activate()
        self.financial_data()
        proposal = self.desk.save(self.data)
        supplied = self.context()
        result = execute_documentary_finance(self.path, proposal, supplied)
        self.assertEqual(result["status"], "EXECUTED")
        self.assertEqual(
            result["cash_flow_inventory_status"],
            "MATCHED_RECORDED_LOCAL_FLOWS_NOT_RECONCILED",
        )
        self.assertEqual(len(result["cash_flow_inventory_fingerprint"]), 64)
        self.assertEqual(
            result["finance_result"]["projection"]["status"],
            "NOT_EVIDENCED",
        )
        self.assertEqual(result["purchase_effect_status"], "NOT_EVALUATED")
        self.assertEqual(result["viability_status"], "NOT_EVALUATED")
        self.assertFalse(result["decision_authority"])
        self.assertEqual(result["operational_path"], "FORBIDDEN")

    def test_same_number_and_ids_with_changed_cash_flow_fields_rejected(self):
        self.prepare()
        self.activate()
        self.financial_data()
        proposal = self.desk.save(self.data)
        captured = self.context()
        for field, unexpected in (
            ("amount", "900000"),
            ("due_date", "2026-10-16"),
            ("currency", "USD"),
            ("flow_type", "PAYMENT"),
            ("source_ref", "OTHER-DOCUMENT"),
            ("evidence_state", "DEMONSTRATED"),
        ):
            with self.subTest(field=field):
                altered = json.loads(json.dumps(captured))
                altered["cash_flows"][0]["canonical"][field] = unexpected
                result = execute_documentary_finance(
                    self.path, proposal, altered,
                )
                self.assertEqual(result["status"], "NOT_EXECUTED")
                self.assertEqual(result["cash_flow_inventory_status"], "REJECTED")
                self.assertEqual(
                    result["cash_flow_inventory_issue"],
                    "CASH_FLOW_CONTENT_MISMATCH",
                )
                self.assertIsNone(result["finance_result"])
                self.assertEqual(result["parameter_configurations"], [])
                self.assertNotIn("finance_input", result)
                self.assertNotIn("finance_package_fingerprint", result)
                self.assertEqual(result["operational_path"], "FORBIDDEN")

        valid = execute_documentary_finance(self.path, proposal, captured)
        self.assertEqual(valid["status"], "EXECUTED")
        self.assertEqual(len(valid["finance_input"]["cash_flows"]), 2)

    def test_changed_documentary_source_references_rejected(self):
        self.prepare()
        self.activate()
        self.financial_data()
        proposal = self.desk.save(self.data)
        captured = self.context()
        captured["cash_flows"][0]["source_refs"] = [{"document_ref": "OTHER-DOC"}]
        result = execute_documentary_finance(self.path, proposal, captured)
        self.assertEqual(result["status"], "NOT_EXECUTED")
        self.assertEqual(
            result["cash_flow_inventory_issue"], "CASH_FLOW_CONTENT_MISMATCH",
        )
        self.assertIsNone(result["finance_result"])

    def test_replaced_or_missing_stored_cash_flow_rejected_after_capture(self):
        self.prepare()
        self.activate()
        self.financial_data()
        proposal = self.desk.save(self.data)
        captured = self.context()

        with sqlite3.connect(self.path) as c:
            original = c.execute(
                "SELECT record_json FROM documentary_company_record "
                "WHERE dataset_id='one' AND kind='cash_flow' AND record_id='C-1'"
            ).fetchone()[0]
            modified = json.loads(original)
            modified["data"]["canonical"]["amount"] = "9999"
            c.execute(
                "UPDATE documentary_company_record SET record_json=? "
                "WHERE dataset_id='one' AND kind='cash_flow' AND record_id='C-1'",
                (json.dumps(modified, ensure_ascii=False),),
            )
        output = execute_documentary_finance(self.path, proposal, captured)
        self.assertEqual(output["status"], "NOT_EXECUTED")
        self.assertEqual(
            output["cash_flow_inventory_issue"], "CASH_FLOW_CONTENT_MISMATCH",
        )
        self.assertIsNone(output["finance_result"])
        with sqlite3.connect(self.path) as c:
            c.execute(
                "DELETE FROM documentary_company_record "
                "WHERE dataset_id='one' AND kind='cash_flow' AND record_id='P-1'"
            )
        output = execute_documentary_finance(self.path, proposal, captured)
        self.assertEqual(output["status"], "NOT_EXECUTED")
        self.assertEqual(
            output["cash_flow_inventory_issue"], "INVENTORY_COUNT_MISMATCH",
        )
        self.assertIsNone(output["finance_result"])

    def test_unseen_new_stored_cash_flow_blocks_old_captured_selection(self):
        self.prepare()
        self.activate()
        self.financial_data()
        proposal = self.desk.save(self.data)
        captured = self.context()
        with sqlite3.connect(self.path) as c:
            row = json.loads(c.execute(
                "SELECT record_json FROM documentary_company_record "
                "WHERE dataset_id='one' AND kind='cash_flow' AND record_id='P-1'"
            ).fetchone()[0])
            row["record_id"] = "P-NEW"
            row["data"]["canonical"]["flow_id"] = "P-NEW"
            c.execute(
                "INSERT INTO documentary_company_record VALUES(?,?,?,?)",
                ("one", "cash_flow", "P-NEW", json.dumps(row, ensure_ascii=False)),
            )
        output = execute_documentary_finance(self.path, proposal, captured)
        self.assertEqual(output["status"], "NOT_EXECUTED")
        self.assertEqual(
            output["cash_flow_inventory_issue"], "INVENTORY_COUNT_MISMATCH",
        )
        self.assertIsNone(output["finance_result"])

    def test_reordered_valid_cash_flow_capture_is_not_a_false_mismatch(self):
        self.prepare()
        self.activate()
        self.financial_data()
        proposal = self.desk.save(self.data)
        captured = self.context()
        baseline = execute_documentary_finance(self.path, proposal, captured)
        captured["cash_flows"].reverse()
        output = execute_documentary_finance(self.path, proposal, captured)
        self.assertEqual(output["status"], "EXECUTED")
        self.assertEqual(
            output["cash_flow_inventory_fingerprint"],
            baseline["cash_flow_inventory_fingerprint"],
        )
        self.assertEqual(
            output["finance_result"]["projection"],
            baseline["finance_result"]["projection"],
        )

    def test_duplicate_or_unrecorded_flow_with_matching_list_length_is_rejected(self):
        self.prepare()
        self.activate()
        self.financial_data()
        proposal = self.desk.save(self.data)
        original = self.context()
        duplicate = json.loads(json.dumps(original))
        duplicate["cash_flows"][1] = duplicate["cash_flows"][0]
        output = execute_documentary_finance(self.path, proposal, duplicate)
        self.assertEqual(output["cash_flow_inventory_issue"], "DUPLICATE_CAPTURED_FLOW")
        self.assertIsNone(output["finance_result"])
        foreign = json.loads(json.dumps(original))
        foreign["cash_flows"][1]["record_id"] = "FOREIGN-FLOW"
        foreign["cash_flows"][1]["canonical"]["flow_id"] = "FOREIGN-FLOW"
        output = execute_documentary_finance(self.path, proposal, foreign)
        self.assertEqual(output["cash_flow_inventory_issue"], "FOREIGN_OR_UNRECORDED_FLOW")
        self.assertIsNone(output["finance_result"])


if __name__ == "__main__":
    unittest.main()
