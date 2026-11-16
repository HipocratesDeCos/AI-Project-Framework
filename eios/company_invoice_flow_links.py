"""F3.10 — explicit invoice/installment/flow references, synthetic read-only.

The existing sales-quality and proposal-payment association workflows remain
authoritative for their own scopes. This audit ONLY inspects explicit links in
canonical locally stored records after F3.8 inventory verification. Coinciding
amounts and dates do not create relationships or documentary evidence.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import sqlite3

from eios.company_proposal_context import _hash
from eios.finance.models import CashFlow


INVOICE_FOR = {
    "purchase_installment": "purchase_invoice",
    "sales_installment": "sales_invoice",
}
DIRECTION_FOR = {
    "purchase_installment": "PAYMENT",
    "sales_installment": "COLLECTION",
}
PARTY_FOR = {
    "purchase_installment": "supplier_id",
    "sales_installment": "customer_id",
}


def _pairs_unique(pairs):
    record = {}
    for key, value in pairs:
        if key in record:
            raise ValueError("Duplicate JSON field")
        record[key] = value
    return record


def _constant_invalid(value):
    raise ValueError("Nonfinite JSON value")


def _money(value):
    try:
        if isinstance(value, bool) or value is None:
            return None
        amount = Decimal(str(value))
        return amount if amount.is_finite() and amount >= 0 else None
    except (ValueError, InvalidOperation, TypeError):
        return None


def _reference(value):
    return isinstance(value, str) and bool(value) and value == value.strip()


def _due_date(data):
    # A revised due date supersedes a historic original date, but an original
    # is retained only when no newer explicitly stated date exists.
    for field in ("revised_due_date", "due_date", "original_due_date"):
        value = data.get(field)
        if value is not None:
            if not isinstance(value, str):
                return None
            try:
                parsed = date.fromisoformat(value)
            except ValueError:
                return None
            return value if parsed.isoformat() == value else None
    return None


def audit_local_invoice_installment_links(
    *,
    connection: sqlite3.Connection,
    dataset_id: str,
    flows: tuple[CashFlow, ...],
    proposal_context: dict | None,
) -> dict:
    """Check only explicit source references within the verified dataset.

    Must run in the existing read transaction after F3.8. The saved proposal
    context protects against observable changes to the local invoice and
    installment records; it does not authenticate the source or the invoice.
    """
    if not isinstance(connection, sqlite3.Connection) or not connection.in_transaction:
        raise ValueError("La comprobación de referencias requiere la transacción financiera abierta.")
    if not _reference(dataset_id):
        raise ValueError("El ámbito del expediente no está identificado.")
    if not isinstance(flows, tuple) or not all(isinstance(f, CashFlow) for f in flows):
        raise ValueError("Se necesita el inventario de movimientos verificado.")
    flow_index = {f.flow_id: f for f in flows}
    if len(flow_index) != len(flows):
        raise ValueError("Los movimientos verificados presentan identidades repetidas.")
    if proposal_context is not None and (
        not isinstance(proposal_context, dict)
        or proposal_context.get("dataset_id") != dataset_id
    ):
        raise ValueError("El contexto de la propuesta pertenece a otro conjunto.")
    frozen: dict[tuple[str, str], str] = {}
    if proposal_context is not None:
        entries = proposal_context.get("records")
        if not isinstance(entries, list):
            raise ValueError("El contexto de la propuesta no tiene un inventario válido.")
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("El inventario congelado contiene una fila inválida.")
            key = (entry.get("kind"), entry.get("record_id"))
            if key in frozen:
                raise ValueError("El inventario congelado contiene identidades duplicadas.")
            frozen[key] = entry.get("fingerprint")

    stored = connection.execute(
        "SELECT kind, record_id, record_json FROM documentary_company_record "
        "WHERE dataset_id=? AND kind IN "
        "('purchase_invoice','purchase_installment','sales_invoice','sales_installment') "
        "ORDER BY kind, record_id",
        (dataset_id,),
    ).fetchall()

    invoices: dict[tuple[str, str], list[dict]] = defaultdict(list)
    installments: list[dict] = []
    duplicate_ids = Counter((kind, ref) for kind, ref, _ in stored)
    for kind, record_id, raw in stored:
        problem = None
        data = {}
        payload = None
        try:
            payload = json.loads(
                raw, object_pairs_hook=_pairs_unique, parse_constant=_constant_invalid,
            )
            if (
                not isinstance(payload, dict)
                or payload.get("kind") != kind
                or payload.get("record_id") != record_id
                or not isinstance(payload.get("data"), dict)
            ):
                raise ValueError("Unexpected stored envelope")
            data = payload["data"]
        except (ValueError, TypeError, OverflowError):
            problem = "INVALID_STORED_RECORD"
        key = (kind, record_id)
        frozen_status = (
            "NO_SAVED_PROPOSAL_CONTEXT" if proposal_context is None
            else "DUPLICATE_STORED_RECORD" if duplicate_ids[key] > 1
            else "RECORD_NOT_IN_SAVED_PROPOSAL" if key not in frozen
            else "RECORD_CHANGED_SINCE_PROPOSAL"
            if payload is None or _hash(payload) != frozen[key]
            else None
        )
        item = {
            "kind": kind,
            "record_id": record_id,
            "data": data,
            "source_issue": problem or frozen_status,
        }
        if kind in INVOICE_FOR:
            installments.append(item)
        elif kind == "purchase_invoice":
            # Purchase installments refer to header record_id as invoice_id.
            if data.get("invoice_id") not in (None, record_id):
                item["source_issue"] = "INVOICE_IDENTITY_CONFLICT"
            invoices[(kind, record_id)].append(item)
        else:
            number = data.get("invoice_number")
            if _reference(number):
                invoices[(kind, number)].append(item)
            else:
                # Missing a canonical header identity cannot authorize a
                # match against another invoice with similar figures.
                item["source_issue"] = "INVOICE_IDENTITY_MISSING"

    rows: list[dict] = []
    usage: dict[str, list[int]] = defaultdict(list)
    for entry in installments:
        kind, rid, data = entry["kind"], entry["record_id"], entry["data"]
        header_kind = INVOICE_FOR[kind]
        expected_direction = DIRECTION_FOR[kind]
        invoice_ref_field = "invoice_id" if kind == "purchase_installment" else "invoice_number"
        invoice_ref = data.get(invoice_ref_field)
        flow_id = data.get("flow_id")
        problems: list[str] = []
        pending: list[str] = []
        if entry["source_issue"]:
            problems.append(entry["source_issue"])
        if not _reference(invoice_ref):
            problems.append("INVOICE_REFERENCE_MISSING")
            headers = []
        else:
            headers = invoices.get((header_kind, invoice_ref), [])
            if not headers:
                problems.append("INVOICE_NOT_FOUND")
            elif len(headers) > 1:
                problems.append("INVOICE_REFERENCE_AMBIGUOUS")
        header = headers[0] if len(headers) == 1 else None
        if header is not None:
            if header["source_issue"]:
                problems.append("INVOICE_RECORD_NOT_INTACT")
            party = PARTY_FOR[kind]
            hparty, qparty = header["data"].get(party), data.get(party)
            if hparty is None or qparty is None:
                pending.append("COUNTERPARTY_NOT_STATED")
            elif hparty != qparty:
                problems.append("COUNTERPARTY_MISMATCH")
            hcurrency, qcurrency = header["data"].get("currency"), data.get("currency")
            if hcurrency is not None and qcurrency is not None and hcurrency != qcurrency:
                problems.append("INVOICE_CURRENCY_MISMATCH")

        if not _reference(flow_id):
            pending.append("NO_EXPLICIT_FLOW_LINK")
            flow = None
        else:
            flow = flow_index.get(flow_id)
            usage[flow_id].append(len(rows))
            if flow is None:
                problems.append("FLOW_NOT_IN_VERIFIED_INVENTORY")
        if flow is not None:
            if flow.flow_type != expected_direction:
                problems.append("FLOW_DIRECTION_MISMATCH")
            quota_currency = data.get("currency")
            if not _reference(quota_currency):
                pending.append("INSTALLMENT_CURRENCY_NOT_STATED")
            elif flow.currency != quota_currency:
                problems.append("FLOW_CURRENCY_MISMATCH")
            pending_amount = data.get("pending_amount", data.get("pending"))
            amount = _money(pending_amount)
            if pending_amount is None:
                pending.append("OUTSTANDING_AMOUNT_NOT_DECLARED")
            elif amount is None:
                problems.append("INVALID_OUTSTANDING_AMOUNT")
            elif amount != flow.amount:
                problems.append("FLOW_OUTSTANDING_AMOUNT_MISMATCH")
            due = _due_date(data)
            if due is None or flow.due_date is None:
                pending.append("EFFECTIVE_DUE_DATE_NOT_DECLARED")
            elif due != flow.due_date.isoformat():
                problems.append("FLOW_DUE_DATE_MISMATCH")
        rows.append({
            "installment_kind": kind,
            "installment_record_id": rid,
            "invoice_record_kind": header_kind,
            "invoice_ref": invoice_ref if _reference(invoice_ref) else None,
            "flow_id": flow_id if _reference(flow_id) else None,
            "problems": problems,
            "pending_checks": pending,
        })

    # A declared payment/collection cannot cover two different installment
    # rows merely because their amounts and maturities happen to coincide.
    for indices in usage.values():
        if len(indices) > 1:
            for index in indices:
                rows[index]["problems"].append("FLOW_REUSED_BY_MULTIPLE_INSTALLMENTS")

    for row in rows:
        row["problems"] = sorted(set(row["problems"]))
        row["pending_checks"] = sorted(set(row["pending_checks"]))
        row["status"] = (
            "EXPLICIT_LINK_CONTRADICTED" if row["problems"]
            else "EXPLICIT_LINK_INCOMPLETE" if row["pending_checks"]
            else "EXPLICIT_LINK_CONSISTENT_NOT_RECONCILED"
        )
    conflicts = sum(row["status"] == "EXPLICIT_LINK_CONTRADICTED" for row in rows)
    incomplete = sum(row["status"] == "EXPLICIT_LINK_INCOMPLETE" for row in rows)
    consistent = sum(row["status"] == "EXPLICIT_LINK_CONSISTENT_NOT_RECONCILED" for row in rows)
    summary = {
        "schema": "COMPANY-LOCAL-INVOICE-INSTALLMENT-FLOW-LINKS-01",
        "dataset_id": dataset_id,
        "status": (
            "NO_RECORDED_INSTALLMENTS" if not rows
            else "EXPLICIT_LINKS_CONFLICTING" if conflicts
            else "EXPLICIT_LINKS_PARTIAL" if incomplete
            else "EXPLICIT_LINKS_CONSISTENT_NOT_RECONCILED"
        ),
        "invoice_header_count": sum(len(items) for items in invoices.values()),
        "installment_count": len(rows),
        "consistent_link_count": consistent,
        "incomplete_link_count": incomplete,
        "conflicting_link_count": conflicts,
        "scope": "EXPLICIT_LOCAL_RECORD_REFERENCES_ONLY",
        "invoice_totals_reconciled": "NOT_PERFORMED",
        "bank_payment_reconciliation": "NOT_PERFORMED",
        "proposal_payment_association": "SEPARATE_EXISTING_WORKFLOW",
        "accounting_completeness": "NOT_ESTABLISHED",
        "source_authentication": "NOT_EXTERNALLY_AUTHENTICATED",
        "evidence_upgrade_status": "NOT_PERFORMED",
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
        "rows": rows,
    }
    summary["fingerprint"] = _hash(summary)
    return summary


__all__ = ["audit_local_invoice_installment_links"]
