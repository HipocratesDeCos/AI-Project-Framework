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
from tests.test_company_finance_activation import FinanceActivationTest


class LocalFinanceActivationSourceGuardTest(unittest.TestCase):
    setUp = FinanceActivationTest.setUp
    tearDown = FinanceActivationTest.tearDown
    prepare = FinanceActivationTest.prepare
    activate = FinanceActivationTest.activate
    financial_data = FinanceActivationTest.financial_data
    context = FinanceActivationTest.context

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


if __name__ == "__main__":
    unittest.main()
