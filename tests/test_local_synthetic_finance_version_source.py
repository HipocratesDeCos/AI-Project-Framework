"""F3.2: actual historical synthetic activation → F2.4 version manifest.

No self-made runtime manifest and no externally authenticated authority.
Synthetic documentary Evidence is supplied by tests only; the local finance
application does not gain operational decision authority from this suite.
"""
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from hashlib import sha256
import json
import sqlite3
import unittest

from eios.company_finance_parameters import Catalogue, Authorization, Repository, IDS
from eios.core.models import DecisionContext, Evidence
from eios.parameters.center import ParameterConfigurationCenter
from eios.company_local_finance_version_source import LocalSyntheticFinanceVersionSource
from eios.parameters import (
    ParameterVersionBindingError,
    configuration_evidence_source_ref,
    fingerprint_historical_parameter_configurations,
    read_version_bound_parameter_selection,
)
from eios.parameters.resolution import resolve_configuration_for_context
from tests.test_company_finance_activation import FinanceActivationTest as _FinanceActivationTest


class HistoricalFinanceVersionTest(unittest.TestCase):
    setUp = _FinanceActivationTest.setUp
    tearDown = _FinanceActivationTest.tearDown
    add = _FinanceActivationTest.add
    prepare = _FinanceActivationTest.prepare
    activate = _FinanceActivationTest.activate

    WHEN = datetime(2026, 9, 30, tzinfo=timezone.utc)

    def context(self, version):
        return DecisionContext(
            decision_id="DECISION-SYNTHETIC",
            scenario_id="FINANCE-SYNTHETIC",
            rules_version="NOT_EXECUTED",
            parameters_version=version,
            data_snapshot_id="SYNTHETIC-SNAPSHOT",
        )

    def saved_version(self, dataset="one"):
        from eios.company_finance_parameters import read_finance_activation
        company = self.desk.store.describe(dataset)["company"]["company_id"]
        return read_finance_activation(self.path, company, "2026-09-30")["fingerprint"]

    def binding(
        self, *,
        company="one", dataset="one", version=None,
        evidence=True, ids=IDS, changed_proof=None,
    ):
        version = version if version is not None else self.saved_version(dataset)
        context = self.context(version)
        with sqlite3.connect(self.path) as connection:
            connection.execute("BEGIN")
            center = ParameterConfigurationCenter(
                Catalogue(), Authorization(), Repository(connection),
            )
            selections = {
                pid: center.get_configuration_at(company, pid, self.WHEN)
                for pid in IDS
            }
            proofs = {}
            if evidence:
                for pid, config in selections.items():
                    if config is None:
                        continue
                    resolution = resolve_configuration_for_context(config, context, self.WHEN)
                    proofs[pid] = Evidence(
                        evidence_id="DOC-" + pid,
                        source_type="ParameterConfigurationEvidence",
                        source_ref=configuration_evidence_source_ref(
                            company_id=company, parameter_id=pid,
                            configuration_id=config.configuration_id,
                        ),
                        captured_at=self.WHEN.date(),
                        state="DEMONSTRATED",
                        demonstration_ref=resolution.configuration_ref,
                    )
                if changed_proof is not None:
                    proofs[IDS[0]] = proofs[IDS[0]].model_copy(update=changed_proof)
            source = LocalSyntheticFinanceVersionSource(
                connection=connection, dataset_id=dataset,
                expected_company_id=company,
            )
            try:
                bound = read_version_bound_parameter_selection(
                    center=center, version_source=source,
                    company_id=company, expected_company_id=company,
                    context=context, effective_at=self.WHEN,
                    parameter_ids=ids, evidence_by_parameter=proofs,
                )
                return bound
            finally:
                connection.rollback()

    def assert_refused(self, code, **kwargs):
        with self.assertRaises(ParameterVersionBindingError) as failure:
            self.binding(**kwargs)
        self.assertEqual(failure.exception.code, code)

    def test_real_history_port_matches_centre_and_is_not_an_authority(self):
        self.prepare()
        activation = self.activate()["finance_activation"]
        bound = self.binding()
        self.assertEqual(bound.manifest.parameters_version, activation["fingerprint"])
        self.assertEqual(bound.manifest.parameter_ids, IDS)
        self.assertEqual(bound.selection_fingerprint, bound.manifest.selection_fingerprint)
        self.assertEqual(bound.lookup.parameters_version, activation["fingerprint"])
        self.assertEqual(bound.status, "SOURCE_MANIFEST_MATCHED")
        self.assertEqual(bound.source_authentication, "ADAPTER_RESPONSIBILITY")
        self.assertTrue(bound.manifest.source_ref.startswith("local_synthetic_finance_activation:"))
        self.assertFalse(bound.decision_authority)
        self.assertEqual(bound.operational_path, "FORBIDDEN")
        with self.assertRaises(FrozenInstanceError):
            bound.manifest.parameters_version = "FORGED"

    def test_historical_fingerprint_matches_canonical_live_fingerprint(self):
        self.prepare(); self.activate()
        bound=self.binding()
        configs=tuple(item.resolution.configuration for item in bound.lookup.entries)
        digest=fingerprint_historical_parameter_configurations(
            company_id="one", parameters_version=self.saved_version(),
            effective_at=self.WHEN, configurations=configs,
        )
        self.assertEqual(digest, bound.selection_fingerprint)

    def test_saved_request_without_explicit_activation_cannot_mint_version(self):
        self.prepare()
        self.assert_refused("VERSION_SOURCE_UNAVAILABLE", version="FAKE-VERSION")

    def test_wrong_version_never_falls_back_to_current_configuration(self):
        self.prepare(); self.activate()
        self.assert_refused("VERSION_SOURCE_UNAVAILABLE", version="WRONG-VERSION")

    def test_other_company_and_other_dataset_cannot_replay_version(self):
        self.prepare(); self.activate()
        with sqlite3.connect(self.path) as connection:
            connection.execute("BEGIN")
            source=LocalSyntheticFinanceVersionSource(
                connection=connection,dataset_id="one",expected_company_id="one",
            )
            with self.assertRaises(ParameterVersionBindingError) as error:
                source.get_version_manifest("two",self.saved_version(),self.WHEN)
            self.assertEqual(error.exception.code,"COMPANY_SCOPE_MISMATCH")
            connection.rollback()
        self.assert_refused("DATASET_SCOPE_MISMATCH", dataset="two", version=self.saved_version())

    def test_separate_company_activation_yields_distinct_version(self):
        self.prepare(); self.activate()
        a=self.saved_version()
        self.prepare(dataset="two",minimum="100")
        self.activate(dataset="two")
        b=self.saved_version("two")
        self.assertNotEqual(a,b)
        with sqlite3.connect(self.path) as connection:
            connection.execute("BEGIN")
            source=LocalSyntheticFinanceVersionSource(
                connection=connection,dataset_id="two",expected_company_id="two",
            )
            self.assertIsNone(source.get_version_manifest("two",a,self.WHEN))
            self.assertEqual(source.get_version_manifest("two",b,self.WHEN).parameters_version,b)
            connection.rollback()

    def test_mutated_live_configuration_is_detected_against_saved_history(self):
        self.prepare(); self.activate()
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                "UPDATE company_finance_parameter_configuration SET value='3000' "
                "WHERE company_id='one' AND parameter_id='P-FIN-002'"
            )
        self.assert_refused("VERSION_CONTENT_MISMATCH")

    def test_mutated_live_metadata_is_detected_against_saved_history(self):
        self.prepare(); self.activate()
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                "UPDATE company_finance_parameter_configuration "
                "SET updated_at='2026-09-29T00:00:00+00:00' "
                "WHERE company_id='one' AND parameter_id='P-FIN-002'"
            )
        self.assert_refused("VERSION_CONTENT_MISMATCH")

    def test_manifest_denies_incomplete_parameter_selection(self):
        self.prepare(); self.activate()
        self.assert_refused("MANIFEST_SELECTION_MISMATCH",ids=(IDS[0],))

    def test_missing_or_detached_proof_cannot_bind_version(self):
        self.prepare(); self.activate()
        self.assert_refused("INCOMPLETE_DOCUMENTARY_COVERAGE",evidence=False)
        self.assert_refused(
            "INCOMPLETE_DOCUMENTARY_COVERAGE",
            changed_proof={"source_ref":"inconsistent:test"}
        )

    def test_corrupted_historical_activation_is_rejected(self):
        self.prepare(); self.activate()
        with sqlite3.connect(self.path) as connection:
            raw=connection.execute(
                "SELECT payload FROM company_finance_parameter_activation "
                "WHERE company_id='one'"
            ).fetchone()[0]
            record=json.loads(raw)
            record["values"]["P-FIN-002"]="3000"
            connection.execute(
                "UPDATE company_finance_parameter_activation SET payload=? WHERE company_id='one'",
                (json.dumps(record,ensure_ascii=False),)
            )
        self.assert_refused("INVALID_ACTIVATION")

    def test_rehashed_history_still_disagrees_with_live_selection(self):
        self.prepare(); self.activate()
        with sqlite3.connect(self.path) as connection:
            raw=connection.execute(
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
            connection.execute(
                "UPDATE company_finance_parameter_activation SET payload=? WHERE company_id='one'",
                (json.dumps(record,ensure_ascii=False),)
            )
        self.assert_refused("VERSION_CONTENT_MISMATCH",version=record["fingerprint"])

    def test_non_synthetic_dataset_must_never_generate_a_manifest(self):
        self.prepare(); self.activate()
        with sqlite3.connect(self.path) as connection:
            raw=connection.execute(
                "SELECT manifest_json FROM documentary_company_snapshot WHERE dataset_id='one'"
            ).fetchone()[0]
            record=json.loads(raw);record["material_nature"]="REAL"
            connection.execute(
                "UPDATE documentary_company_snapshot SET manifest_json=? WHERE dataset_id='one'",
                (json.dumps(record),)
            )
        self.assert_refused("NON_SYNTHETIC_SOURCE")

    def test_source_cannot_work_outside_shared_read_transaction(self):
        self.prepare(); self.activate()
        with sqlite3.connect(self.path) as connection:
            source=LocalSyntheticFinanceVersionSource(
                connection=connection, dataset_id="one", expected_company_id="one",
            )
            with self.assertRaises(ParameterVersionBindingError) as failed:
                source.get_version_manifest("one",self.saved_version(),self.WHEN)
            self.assertEqual(failed.exception.code,"READ_TRANSACTION_REQUIRED")

    def test_unrelated_prepared_request_does_not_rewrite_historical_version(self):
        self.prepare(); self.activate()
        version=self.saved_version()
        self.prepare(minimum="3000", revision=1)
        bound=self.binding()
        self.assertEqual(bound.manifest.parameters_version,version)

    def test_fabricated_historical_snapshot_without_canonical_columns_fails(self):
        self.prepare();self.activate()
        with sqlite3.connect(self.path) as connection:
            raw=connection.execute(
                "SELECT payload FROM company_finance_parameter_activation WHERE company_id='one'"
            ).fetchone()[0]
            record=json.loads(raw)
            record["configurations"][0]["unexpected_field"]="fake"
            record.pop("fingerprint")
            record["fingerprint"]=sha256(
                json.dumps(record,sort_keys=True,separators=(",",":"),
                           ensure_ascii=False).encode()
            ).hexdigest()
            connection.execute(
                "UPDATE company_finance_parameter_activation SET payload=? WHERE company_id='one'",
                (json.dumps(record,ensure_ascii=False),)
            )
        self.assert_refused("HISTORICAL_CONFIGURATION_INVALID",version=record["fingerprint"])


if __name__=="__main__":
    unittest.main()
