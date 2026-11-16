"""F3.8: reconcile supplied cash flows against stored local synthetic records.

This is an exact correspondence check inside the consumer's SQLite read
transaction, NOT accounting completeness, reconciliation of invoices/bank
statements, external provenance, a new authority or an operational decision.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import sqlite3

from eios.finance.models import CashFlow


class CashFlowInventoryError(ValueError):
    """Stable fail-closed local cash-flow inventory contract error."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class LocalCashFlowInventoryReceipt:
    company_dataset_id: str
    flow_ids: tuple[str, ...]
    recorded_count: int
    recorded_fingerprint: str
    status: str = "MATCHED_RECORDED_LOCAL_FLOWS_NOT_RECONCILED"
    source_authentication: str = "NOT_EXTERNALLY_AUTHENTICATED"
    inventory_completeness: str = "NOT_ESTABLISHED"
    decision_authority: bool = False
    operational_path: str = "FORBIDDEN"


def _fail(code: str, message: str) -> None:
    raise CashFlowInventoryError(code, message)


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            _fail("INVALID_RECORDED_FLOW", "El registro contiene claves JSON duplicadas.")
        result[key] = value
    return result


def _invalid_numeric(value: str) -> None:
    _fail("INVALID_RECORDED_FLOW", "El registro contiene un valor numérico JSON inválido.")


def verify_local_cash_flow_inventory(
    *,
    connection: sqlite3.Connection,
    dataset_id: str,
    recorded_count: int,
    captured_flows: list[dict],
) -> tuple[tuple[CashFlow, ...], LocalCashFlowInventoryReceipt]:
    """Compare the *whole* captured selection to one stored dataset.

    The caller must already have checked its synthetic dataset scope and
    opened a SQLite read transaction (F3.1). The returned movement order is
    canonical by flow_id, not the UI input order; the content hash covers source
    record IDs, canonical flow data AND declared source references.
    """
    if not isinstance(connection, sqlite3.Connection) or not connection.in_transaction:
        _fail("READ_TRANSACTION_REQUIRED", "Se requiere una transacción SQLite activa.")
    if not isinstance(dataset_id, str) or not dataset_id or dataset_id != dataset_id.strip():
        _fail("INVALID_DATASET_SCOPE", "El conjunto documental no está identificado.")
    if type(recorded_count) is not int or recorded_count < 1:
        _fail("INVALID_FLOW_COUNT", "El inventario declarado no contiene movimientos válidos.")
    if not isinstance(captured_flows, list):
        _fail("INVALID_CAPTURE", "La selección de movimientos no es una lista canónica.")
    try:
        persisted_rows = connection.execute(
            "SELECT record_id, record_json FROM documentary_company_record "
            "WHERE dataset_id=? AND kind='cash_flow' ORDER BY record_id",
            (dataset_id,),
        ).fetchall()
    except sqlite3.Error as exc:
        raise CashFlowInventoryError(
            "RECORDED_INVENTORY_UNAVAILABLE",
            "No se ha podido leer el inventario financiero conservado.",
        ) from exc
    if len(persisted_rows) != recorded_count or len(captured_flows) != recorded_count:
        _fail(
            "INVENTORY_COUNT_MISMATCH",
            "El número de movimientos no coincide con el inventario conservado.",
        )

    persisted: dict[str, tuple[CashFlow, list[dict], dict]] = {}
    for stored_id, raw in persisted_rows:
        try:
            item = json.loads(
                raw, object_pairs_hook=_unique_pairs, parse_constant=_invalid_numeric,
            )
            if (
                not isinstance(item, dict)
                or item.get("kind") != "cash_flow"
                or item.get("record_id") != stored_id
                or not isinstance(item.get("data"), dict)
                or not isinstance(item.get("source_refs"), list)
                or not item["source_refs"]
            ):
                _fail("INVALID_RECORDED_FLOW", "El movimiento conservado es incoherente.")
            original = CashFlow.model_validate(item["data"]["canonical"])
            if original.flow_id != stored_id:
                _fail("RECORDED_FLOW_IDENTITY_MISMATCH", "El movimiento almacenado tiene otra identidad.")
            refs = item["source_refs"]
            if any(not isinstance(ref, dict) for ref in refs):
                _fail("INVALID_RECORDED_FLOW", "Las referencias de origen son incorrectas.")
        except CashFlowInventoryError:
            raise
        except (ValueError, KeyError, TypeError, OverflowError) as exc:
            raise CashFlowInventoryError(
                "INVALID_RECORDED_FLOW", "El registro documental no contiene un movimiento válido.",
            ) from exc
        persisted[stored_id] = (original, refs, {
            "record_id": stored_id,
            "canonical": original.model_dump(mode="json"),
            "source_refs": refs,
        })

    seen: set[str] = set()
    for captured in captured_flows:
        if not isinstance(captured, dict):
            _fail("INVALID_CAPTURE", "Se ha recibido un movimiento sin estructura documental.")
        try:
            flow = CashFlow.model_validate(captured["canonical"])
            claimed_id = captured["record_id"]
            claimed_refs = captured["source_refs"]
        except (ValueError, KeyError, TypeError) as exc:
            raise CashFlowInventoryError(
                "INVALID_CAPTURE", "El movimiento recibido no conserva su formato canónico.",
            ) from exc
        if not isinstance(claimed_id, str) or claimed_id != flow.flow_id:
            _fail("CAPTURE_IDENTITY_MISMATCH", "La identidad recibida no coincide con el movimiento.")
        if flow.flow_id in seen:
            _fail("DUPLICATE_CAPTURED_FLOW", "El inventario contiene un movimiento repetido.")
        seen.add(flow.flow_id)
        stored = persisted.get(flow.flow_id)
        if stored is None:
            _fail("FOREIGN_OR_UNRECORDED_FLOW", "Existe un movimiento no conservado en este conjunto.")
        original, refs, _ = stored
        if flow != original or claimed_refs != refs:
            _fail(
                "CASH_FLOW_CONTENT_MISMATCH",
                "El movimiento recibido difiere del importe, vencimiento, evidencia u origen conservados.",
            )
    if set(persisted) != seen:
        _fail("INVENTORY_SELECTION_INCOMPLETE", "El inventario omite movimientos conservados.")
    material = [
        persisted[flow_id][2] for flow_id in sorted(persisted)
    ]
    digest = sha256(json.dumps(
        material, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")).hexdigest()
    # Finance Basic diagnostics may otherwise depend on arbitrary UI ordering.
    # A stable canonical order preserves finance output and error-list fingerprints.
    canonical_flows = tuple(persisted[flow_id][0] for flow_id in sorted(persisted))
    return canonical_flows, LocalCashFlowInventoryReceipt(
        company_dataset_id=dataset_id,
        flow_ids=tuple(sorted(persisted)),
        recorded_count=len(persisted),
        recorded_fingerprint=digest,
    )


__all__ = [
    "CashFlowInventoryError", "LocalCashFlowInventoryReceipt",
    "verify_local_cash_flow_inventory",
]
