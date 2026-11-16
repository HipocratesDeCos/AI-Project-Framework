"""F3.11 — fail-closed local opening treasury snapshot correspondence.

The local synthetic Finance Basic consumer MUST re-read the exact source
snapshot used to supply opening cash, inside its already opened SQLite read
transaction. This protects the provenance of the *saved data record*, but it
does NOT prove bank reconciliation, cash availability or corporate identity.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
import sqlite3

from eios.company_proposal_context import _hash
from eios.finance.models import FinancialSnapshot


class OpeningTreasuryScopeError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class LocalOpeningTreasuryReceipt:
    company_dataset_id: str
    source_record_id: str
    source_record_fingerprint: str
    snapshot_source_ref: str | None
    support_record_count: int
    support_issues: tuple[str, ...]
    status: str = "MATCHED_RECORDED_OPENING_NOT_BANK_RECONCILED"
    opening_treasury_reconciled: bool | None = None
    account_balance_reconciliation: str = "NOT_PERFORMED"
    source_authentication: str = "NOT_EXTERNALLY_AUTHENTICATED"
    decision_authority: bool = False
    operational_path: str = "FORBIDDEN"


def _fail(code: str, message: str) -> None:
    raise OpeningTreasuryScopeError(code, message)


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    out = {}
    for key, value in pairs:
        if key in out:
            _fail("INVALID_SAVED_OPENING", "El registro financiero contiene claves duplicadas.")
        out[key] = value
    return out


def _invalid_constant(value: str) -> None:
    _fail("INVALID_SAVED_OPENING", "El registro financiero contiene valores JSON inválidos.")


def verify_local_opening_treasury(
    *,
    connection: sqlite3.Connection,
    dataset_id: str,
    expected_company_id: str,
    snapshot: FinancialSnapshot,
    proposal_context: dict | None,
) -> LocalOpeningTreasuryReceipt:
    """Verify exactly one stored snapshot and its stated source reference.

    The saved proposal's frozen inventory is checked if provided; no invented
    company identity, numeric bank sum, or evidence promotion is performed.
    """
    if not isinstance(connection, sqlite3.Connection) or not connection.in_transaction:
        _fail("READ_TRANSACTION_REQUIRED", "La lectura del saldo requiere una transacción SQLite abierta.")
    if not isinstance(dataset_id, str) or not dataset_id or dataset_id != dataset_id.strip():
        _fail("INVALID_DATASET_SCOPE", "El conjunto documental no está identificado.")
    if not isinstance(expected_company_id, str) or not expected_company_id:
        _fail("INVALID_COMPANY_SCOPE", "No se ha identificado la empresa de la situación.")
    if not isinstance(snapshot, FinancialSnapshot):
        _fail("INVALID_OPENING_SNAPSHOT", "Se requiere la situación financiera canónica.")
    try:
        rows = connection.execute(
            "SELECT record_id, record_json FROM documentary_company_record "
            "WHERE dataset_id=? AND kind='financial_snapshot' ORDER BY record_id",
            (dataset_id,),
        ).fetchall()
    except sqlite3.Error as exc:
        raise OpeningTreasuryScopeError(
            "SAVED_OPENING_UNAVAILABLE", "La situación financiera conservada no se puede leer."
        ) from exc
    if len(rows) != 1:
        _fail("OPENING_SNAPSHOT_NOT_UNIQUE", "La empresa debe conservar una única situación financiera.")
    stored_id, raw = rows[0]
    try:
        record = json.loads(raw, object_pairs_hook=_unique_pairs, parse_constant=_invalid_constant)
        if (
            not isinstance(record, dict)
            or record.get("kind") != "financial_snapshot"
            or record.get("record_id") != stored_id
            or not isinstance(record.get("data"), dict)
            or not isinstance(record.get("source_refs"), list)
            or not record["source_refs"]
        ):
            _fail("INVALID_SAVED_OPENING", "La situación financiera conservada no tiene origen válido.")
        stored_snapshot = FinancialSnapshot.model_validate(record["data"])
    except OpeningTreasuryScopeError:
        raise
    except (ValueError, KeyError, TypeError, OverflowError) as exc:
        raise OpeningTreasuryScopeError(
            "INVALID_SAVED_OPENING", "La situación financiera conservada es inválida."
        ) from exc

    if stored_snapshot != snapshot or stored_snapshot.company_scope != expected_company_id:
        _fail(
            "OPENING_SNAPSHOT_CONTENT_MISMATCH",
            "El saldo inicial recibido no coincide con la situación financiera conservada.",
        )
    source_ref = stored_snapshot.treasury_evidence_ref
    refs = [
        item.get("document_ref") if isinstance(item, dict) else None
        for item in record["source_refs"]
    ]
    if any(not isinstance(ref, str) or not ref or ref != ref.strip() for ref in refs):
        _fail("INVALID_SAVED_OPENING", "La referencia de origen de la situación es inválida.")
    if source_ref is not None and (refs.count(source_ref) != 1 or len(refs) != len(set(refs))):
        _fail(
            "OPENING_SOURCE_REFERENCE_MISMATCH",
            "La referencia del saldo inicial no coincide con los soportes declarados.",
        )
    record_hash = _hash(record)
    if proposal_context is not None:
        if (
            not isinstance(proposal_context, dict)
            or proposal_context.get("dataset_id") != dataset_id
            or not isinstance(proposal_context.get("records"), list)
        ):
            _fail("OPENING_PROPOSAL_SCOPE_MISMATCH", "La propuesta no conserva el mismo expediente.")
        candidates = [
            item for item in proposal_context["records"]
            if isinstance(item, dict)
            and item.get("kind") == "financial_snapshot"
            and item.get("record_id") == stored_id
        ]
        if len(candidates) != 1 or candidates[0].get("fingerprint") != record_hash:
            _fail(
                "OPENING_CHANGED_SINCE_PROPOSAL",
                "La situación financiera ha cambiado desde el guardado de la propuesta.",
            )

    # Account balances must never be summed blindly: ledger parents and
    # their children may be present together, and bank availability is not
    # established by matching an account figure to an asserted opening.
    issues: set[str] = set()
    seen_accounts: list[str] = []
    support_count = 0
    support_rows = connection.execute(
        "SELECT kind, record_id, record_json FROM documentary_company_record "
        "WHERE dataset_id=? AND kind IN "
        "('treasury_balances','account_balance','bank_statement_entry','cash_count') "
        "ORDER BY kind,record_id",
        (dataset_id,),
    ).fetchall()
    for kind, ref, raw in support_rows:
        support_count += 1
        try:
            entry = json.loads(raw, object_pairs_hook=_unique_pairs, parse_constant=_invalid_constant)
            if (
                not isinstance(entry, dict) or entry.get("kind") != kind
                or entry.get("record_id") != ref or not isinstance(entry.get("data"), dict)
            ):
                raise ValueError("Invalid support envelope")
        except (ValueError, TypeError, OverflowError):
            issues.add("SUPPORT_RECORD_INVALID")
            continue
        data = entry["data"]
        for label, expected in (
            ("currency", snapshot.currency),
            ("as_of_date", snapshot.as_of_date.isoformat()),
        ):
            declared = data.get(label)
            if declared is not None and declared != expected:
                issues.add("SUPPORT_" + label.upper() + "_MISMATCH")
        if kind == "account_balance":
            code = data.get("account_code")
            if isinstance(code, str) and code.startswith(("570", "572")) and code.isdigit():
                seen_accounts.append(code)
    if any(count > 1 for count in Counter(seen_accounts).values()):
        issues.add("DUPLICATED_CASH_BANK_ACCOUNT")
    if any(a != b and b.startswith(a) for a in seen_accounts for b in seen_accounts):
        issues.add("CASH_BANK_PARENT_CHILD_OVERLAP")

    return LocalOpeningTreasuryReceipt(
        company_dataset_id=dataset_id,
        source_record_id=stored_id,
        source_record_fingerprint=record_hash,
        snapshot_source_ref=source_ref,
        support_record_count=support_count,
        support_issues=tuple(sorted(issues)),
    )


__all__ = [
    "LocalOpeningTreasuryReceipt", "OpeningTreasuryScopeError",
    "verify_local_opening_treasury",
]
