"""F3.1: fail-closed admission of existing local synthetic finance activation.

The historical activation row is compared with the exact configurations that
the finance consumer is about to use. This is *not* source authentication:
both tables are inside the same editable local SQLite database. The guard
does not mint a version, issue evidence or enable operational decisions.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timezone
import json
import sqlite3

from eios.company_finance_parameters import IDS
from eios.company_parameter_bindings import describe_company_parameter_bindings
from eios.parameters.center import Configuration


class LocalFinanceActivationError(ValueError):
    """Stable error codes for fail-closed source correspondence."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class LocalFinanceActivationReceipt:
    """A local historical comparison, never an authenticated rule authority."""

    company_id: str
    dataset_id: str
    as_of_date: str
    activation_fingerprint: str
    request_revision: int
    configuration_ids: tuple[int, ...]
    status: str = "MATCHED_LOCAL_SYNTHETIC_ACTIVATION"
    source_authentication: str = "NOT_EXTERNALLY_AUTHENTICATED"
    version_attestation: str = "NOT_ATTESTED"
    atomicity: str = "SQLITE_READ_TRANSACTION_ONLY"
    decision_authority: bool = False
    operational_path: str = "FORBIDDEN"


def _error(code: str, message: str) -> None:
    raise LocalFinanceActivationError(code, message)


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            _error("INVALID_SOURCE_RECORD", "Duplicate JSON member in recorded source")
        result[key] = value
    return result


def _read_json(raw: object) -> dict:
    if not isinstance(raw, str):
        _error("INVALID_SOURCE_RECORD", "Source must be JSON text")
    try:
        result = json.loads(raw, object_pairs_hook=_unique_pairs)
    except (ValueError, TypeError, OverflowError) as exc:
        _error("INVALID_SOURCE_RECORD", "Source JSON is not valid")
    if not isinstance(result, dict):
        _error("INVALID_SOURCE_RECORD", "Source must be a JSON object")
    return result


def _encoded_configuration(item: Configuration) -> dict:
    if not isinstance(item, Configuration):
        _error("INVALID_CONFIGURATION", "Expected canonical Parameter Centre configuration")
    if type(item.configuration_id) is not int or item.configuration_id < 0:
        _error("INVALID_CONFIGURATION", "Configuration ID must be a nonnegative integer")
    result = asdict(item)
    for key in ("valid_from", "valid_to", "created_at", "updated_at"):
        value = result[key]
        if value is not None and (
            not isinstance(value, datetime) or value.utcoffset() is None
        ):
            _error("INVALID_CONFIGURATION", "Configuration timestamps require timezone")
        result[key] = value.isoformat() if value is not None else None
    return result


def verify_local_finance_activation(
    *,
    connection: sqlite3.Connection,
    company_id: str,
    dataset_id: str,
    as_of_date: str,
    effective_at: datetime,
    configurations: tuple[Configuration, ...],
) -> LocalFinanceActivationReceipt:
    """Compare an earlier explicit activation with the current Centre selection.

    Must be called inside the finance consumer's SQLite read transaction.
    No schema creation, updates, defaults, self-generated evidence or other
    parameter history is introduced.
    """
    if not isinstance(connection, sqlite3.Connection) or not connection.in_transaction:
        _error("READ_TRANSACTION_REQUIRED", "A shared active SQLite read transaction is required")
    if any(
        not isinstance(value, str) or not value or value != value.strip()
        for value in (company_id, dataset_id, as_of_date)
    ):
        _error("INVALID_SCOPE", "Company, dataset and cutoff are mandatory")
    try:
        cutoff = date.fromisoformat(as_of_date)
    except ValueError:
        _error("INVALID_SCOPE", "Cutoff date is invalid")
    if (
        not isinstance(effective_at, datetime)
        or effective_at.utcoffset() is None
        or effective_at != datetime.combine(cutoff, time.min, timezone.utc)
    ):
        _error("CUTOFF_MISMATCH", "Finance cutoff must equal the recorded UTC instant")
    if not isinstance(configurations, tuple) or len(configurations) != len(IDS):
        _error("INCOMPLETE_SELECTION", "Every required finance parameter must be selected")

    try:
        rows = connection.execute(
            "SELECT company_id, as_of_date, manifest_json "
            "FROM documentary_company_snapshot WHERE dataset_id=?",
            (dataset_id,),
        ).fetchall()
        if len(rows) != 1:
            _error("DATASET_NOT_ADMITTED", "Dataset reference is unavailable or ambiguous")
        source_company, source_date, source_manifest = rows[0]
        if source_company != company_id or source_date != as_of_date:
            _error("DATASET_SCOPE_MISMATCH", "Dataset belongs to another company or cutoff")
        if _read_json(source_manifest).get("material_nature") != "SYNTHETIC":
            _error("NON_SYNTHETIC_SOURCE", "This adapter accepts synthetic source material only")
        rows = connection.execute(
            "SELECT payload FROM company_finance_parameter_activation "
            "WHERE company_id=? AND as_of_date=?",
            (company_id, as_of_date),
        ).fetchall()
    except sqlite3.Error as exc:
        _error("SOURCE_UNAVAILABLE", "Local source could not be read")
    if not rows:
        _error("ACTIVATION_MISSING", "No explicit historical activation is recorded")
    if len(rows) != 1:
        _error("ACTIVATION_AMBIGUOUS", "Several activation records match the cutoff")
    activation = _read_json(rows[0][0])
    revision = activation.get("request_revision")
    if type(revision) is not int or revision < 1:
        _error("ACTIVATION_INVALID", "Recorded activation revision is invalid")

    try:
        report = describe_company_parameter_bindings(
            catalogue=tuple({"parameter_id": pid} for pid in IDS),
            activation=activation,
            company_id=company_id,
            dataset_id=dataset_id,
            as_of_date=as_of_date,
            current_revision=revision,
        )
    except (ValueError, TypeError, KeyError) as exc:
        _error("ACTIVATION_INVALID", "Activation failed existing company binding checks")
    if any(
        report["entries"][pid]["status"] != "ACTIVE_LOCAL_SYNTHETIC_AT_CUTOFF"
        for pid in IDS
    ):
        _error("ACTIVATION_INVALID", "Stored activation is not internally consistent")

    selected: dict[str, dict] = {}
    for item in configurations:
        data = _encoded_configuration(item)
        pid = data["parameter_id"]
        if pid not in IDS or pid in selected or data["company_id"] != company_id:
            _error("SELECTION_SCOPE_MISMATCH", "Unexpected, duplicate or foreign parameter")
        selected[pid] = data
    if set(selected) != set(IDS):
        _error("INCOMPLETE_SELECTION", "Finance parameter selection is incomplete")

    recorded = activation["configurations"]
    if any(not isinstance(item, dict) for item in recorded):
        _error("ACTIVATION_INVALID", "Activation configuration rows are malformed")
    by_id = {item["parameter_id"]: item for item in recorded}
    if (
        len(by_id) != len(IDS)
        or any(selected[pid] != by_id.get(pid) for pid in IDS)
    ):
        _error("ACTIVATION_CONFIGURATION_MISMATCH", "Current configurations differ from the recorded activation")

    return LocalFinanceActivationReceipt(
        company_id=company_id,
        dataset_id=dataset_id,
        as_of_date=as_of_date,
        activation_fingerprint=activation["fingerprint"],
        request_revision=revision,
        configuration_ids=tuple(selected[pid]["configuration_id"] for pid in IDS),
    )


__all__ = [
    "LocalFinanceActivationError",
    "LocalFinanceActivationReceipt",
    "verify_local_finance_activation",
]
