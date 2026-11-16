"""Application adapter: read a LOCAL SYNTHETIC finance activation as a version source.

No manifest or version table is created. The source reads the configurations
stored *at activation*, independently of current Parameter Centre reads.
It is a local historical correspondence adapter, NOT an externally
authenticated business authority and NOT a production version service.
"""
from __future__ import annotations

from datetime import date, datetime, time, timezone
import sqlite3

from eios.company_finance_activation_guard import _read_json
from eios.company_finance_parameters import IDS
from eios.company_parameter_bindings import describe_company_parameter_bindings

from eios.parameters.center import Configuration
from eios.parameters.version_binding import (
    ParameterVersionBindingError,
    ParameterVersionManifest,
    fingerprint_historical_parameter_configurations,
)


def _reject(code: str, message: str) -> None:
    raise ParameterVersionBindingError(code, message)


def _canonical_id(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip()


def _historical_configuration(row: object) -> Configuration:
    """Decode only the approved, exact canonical Configuration record."""
    fields = tuple(Configuration.__dataclass_fields__)
    if not isinstance(row, dict) or set(row) != set(fields):
        _reject("HISTORICAL_CONFIGURATION_INVALID", "History record fields differ from Configuration")
    values = dict(row)
    for key in ("valid_from", "valid_to", "created_at", "updated_at"):
        raw = values[key]
        if raw is None and key == "valid_to":
            continue
        if not isinstance(raw, str):
            _reject("HISTORICAL_CONFIGURATION_INVALID", "Historical timestamp must be ISO text")
        try:
            stamp = datetime.fromisoformat(raw)
        except ValueError:
            _reject("HISTORICAL_CONFIGURATION_INVALID", "Historical timestamp is invalid")
        if stamp.utcoffset() is None or stamp.isoformat() != raw:
            _reject("HISTORICAL_CONFIGURATION_INVALID", "Historical timestamp must carry a canonical offset")
        values[key] = stamp
    try:
        config = Configuration(**values)
    except (TypeError, ValueError):
        _reject("HISTORICAL_CONFIGURATION_INVALID", "Cannot decode historical Configuration")
    if type(config.configuration_id) is not int or config.configuration_id < 0:
        _reject("HISTORICAL_CONFIGURATION_INVALID", "Configuration identity is invalid")
    if not all(_canonical_id(v) for v in (config.company_id, config.parameter_id)):
        _reject("HISTORICAL_CONFIGURATION_INVALID", "Configuration scope is invalid")
    return config


class LocalSyntheticFinanceVersionSource:
    """F2.4 port backed exclusively by an existing SQLite activation record.

    Call only inside an active SQLite read transaction. The connection MUST
    point to the SAME DB as the ParameterConfigurationCenter repository.
    The passed expected_company_id is scoped by the caller; this class
    cannot authenticate the business identity behind that claim.
    """

    source_authentication = "NOT_EXTERNALLY_AUTHENTICATED"
    operational_path = "FORBIDDEN"
    decision_authority = False

    def __init__(
        self, *,
        connection: sqlite3.Connection,
        dataset_id: str,
        expected_company_id: str,
    ) -> None:
        if not isinstance(connection, sqlite3.Connection):
            raise TypeError("connection must be sqlite3.Connection")
        if not _canonical_id(dataset_id) or not _canonical_id(expected_company_id):
            _reject("INVALID_SCOPE", "Dataset and expected company are mandatory")
        self._connection = connection
        self._dataset_id = dataset_id
        self._expected_company_id = expected_company_id

    def get_version_manifest(
        self, company_id: str, parameters_version: str, effective_at: datetime,
    ) -> ParameterVersionManifest | None:
        if not self._connection.in_transaction:
            _reject("READ_TRANSACTION_REQUIRED", "Version reads require a shared SQLite read transaction")
        if not _canonical_id(company_id) or company_id != self._expected_company_id:
            _reject("COMPANY_SCOPE_MISMATCH", "Version source cannot read another company")
        if not _canonical_id(parameters_version):
            _reject("INVALID_VERSION", "Version identifier is invalid")
        if not isinstance(effective_at, datetime) or effective_at.utcoffset() is None:
            _reject("INVALID_EFFECTIVE_AT", "An aware cutoff is required")
        cutoff = effective_at.astimezone(timezone.utc)
        if cutoff != datetime.combine(cutoff.date(), time.min, timezone.utc):
            _reject("CUTOFF_MISMATCH", "Activation versions are bound to the UTC cutoff day")
        date_text = cutoff.date().isoformat()

        try:
            dataset = self._connection.execute(
                "SELECT company_id,as_of_date,manifest_json "
                "FROM documentary_company_snapshot WHERE dataset_id=?",
                (self._dataset_id,),
            ).fetchall()
        except sqlite3.Error:
            _reject("VERSION_SOURCE_UNAVAILABLE", "Cannot read the documentary dataset")
        if len(dataset) != 1:
            _reject("DATASET_UNAVAILABLE", "Dataset is absent or ambiguous")
        owner, stored_date, manifest_json = dataset[0]
        if owner != company_id or stored_date != date_text:
            _reject("DATASET_SCOPE_MISMATCH", "Dataset belongs to another company or date")
        try:
            material = _read_json(manifest_json)
        except ValueError:
            _reject("INVALID_DATASET_MANIFEST", "Dataset manifest is malformed")
        if material.get("material_nature") != "SYNTHETIC":
            _reject("NON_SYNTHETIC_SOURCE", "Only synthetic dataset version history is available")

        try:
            rows = self._connection.execute(
                "SELECT payload FROM company_finance_parameter_activation "
                "WHERE company_id=? AND as_of_date=?",
                (company_id, date_text),
            ).fetchall()
        except sqlite3.Error:
            _reject("VERSION_SOURCE_UNAVAILABLE", "Cannot read the historical activation")
        if not rows:
            return None
        if len(rows) != 1:
            _reject("AMBIGUOUS_ACTIVATION", "More than one historical activation matches")
        try:
            activation = _read_json(rows[0][0])
        except ValueError:
            _reject("INVALID_ACTIVATION", "Historical activation JSON is malformed")
        revision = activation.get("request_revision")
        if type(revision) is not int or revision < 1:
            _reject("INVALID_ACTIVATION", "Activation revision is invalid")
        try:
            report = describe_company_parameter_bindings(
                catalogue=tuple({"parameter_id": pid} for pid in IDS),
                activation=activation, company_id=company_id,
                dataset_id=self._dataset_id, as_of_date=date_text,
                current_revision=revision,
            )
        except (ValueError, TypeError, KeyError):
            _reject("INVALID_ACTIVATION", "Historical activation failed existing checks")
        if any(
            report["entries"][pid]["status"] != "ACTIVE_LOCAL_SYNTHETIC_AT_CUTOFF"
            for pid in IDS
        ):
            _reject("INVALID_ACTIVATION", "Activation is not internally consistent")

        fingerprint = activation["fingerprint"]
        if parameters_version != fingerprint:
            return None
        configs = tuple(_historical_configuration(c) for c in activation["configurations"])
        if len(configs) != len(IDS) or set(c.parameter_id for c in configs) != set(IDS):
            _reject("INCOMPLETE_HISTORICAL_SELECTION", "Activation does not contain the full finance selection")
        if any(c.company_id != company_id for c in configs):
            _reject("HISTORICAL_COMPANY_MISMATCH", "Historical configuration belongs to another company")

        digest = fingerprint_historical_parameter_configurations(
            company_id=company_id,
            parameters_version=parameters_version,
            effective_at=effective_at,
            configurations=configs,
        )
        return ParameterVersionManifest(
            company_id=company_id,
            parameters_version=parameters_version,
            effective_at=effective_at,
            parameter_ids=IDS,
            selection_fingerprint=digest,
            source_ref="local_synthetic_finance_activation:" + fingerprint,
        )


__all__ = ["LocalSyntheticFinanceVersionSource"]
