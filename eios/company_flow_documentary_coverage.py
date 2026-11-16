"""F3.9 — source-document coverage for already verified local cash flows.

Observe source bytes and their saved documentary context without parsing or
claiming to reconcile invoices, bank entries, amounts, due dates or accounts.
This audit never upgrades CashFlow.evidence_state or enables decisions.
"""
from __future__ import annotations

from hashlib import sha256
import json
import sqlite3

from eios.finance.models import CashFlow


def _digest(value: object) -> str:
    material = json.dumps(
        value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    return sha256(material).hexdigest()


def audit_local_flow_documentary_coverage(
    *, connection: sqlite3.Connection,
    dataset_id: str, flows: tuple[CashFlow, ...],
    captured_flows: list[dict],
    proposal_context: dict | None,
) -> dict:
    """Review source links inside the SAME F3.8 SQLite read transaction.

    F3.8 must already have matched captured_flows to the persisted inventory.
    The audit is structural/observational; even a full set of unchanged
    source bytes is NOT evidence of the commercial content of a document.
    """
    if not isinstance(connection, sqlite3.Connection) or not connection.in_transaction:
        raise ValueError("La comprobación documental requiere la transacción financiera abierta.")
    if not isinstance(dataset_id, str) or not dataset_id or dataset_id != dataset_id.strip():
        raise ValueError("El conjunto de documentos no está identificado.")
    if not isinstance(flows, tuple) or not all(isinstance(flow, CashFlow) for flow in flows):
        raise ValueError("Se necesita el inventario canónico previamente verificado.")
    if not isinstance(captured_flows, list) or len(captured_flows) != len(flows):
        raise ValueError("La selección documental no coincide con el inventario verificado.")
    records = {}
    for record in captured_flows:
        if not isinstance(record, dict) or not isinstance(record.get("record_id"), str):
            raise ValueError("La selección documental contiene una identidad inválida.")
        if record["record_id"] in records:
            raise ValueError("La selección documental contiene movimientos duplicados.")
        records[record["record_id"]] = record
    if set(records) != {flow.flow_id for flow in flows}:
        raise ValueError("La selección documental pertenece a otro inventario.")
    if proposal_context is not None and (
        not isinstance(proposal_context, dict)
        or proposal_context.get("dataset_id") != dataset_id
    ):
        raise ValueError("El contexto documental conservado pertenece a otra versión.")
    frozen_sources = {}
    if proposal_context is not None:
        raw_sources = proposal_context.get("sources", [])
        if not isinstance(raw_sources, list):
            raise ValueError("El contexto documental no contiene referencias válidas.")
        for source in raw_sources:
            if not isinstance(source, dict) or not isinstance(source.get("document_ref"), str):
                raise ValueError("Una referencia documental conservada es inválida.")
            if source["document_ref"] in frozen_sources:
                raise ValueError("El contexto conserva varias referencias al mismo documento.")
            frozen_sources[source["document_ref"]] = source

    # Historical miniature test datasets have only a dataset_id column.
    # Never interpret that missing schema as proof that source bytes exist.
    columns = {
        item[1] for item in
        connection.execute("PRAGMA table_info(documentary_source)").fetchall()
    }
    supports_documents = {"dataset_id", "document_ref", "content"} <= columns
    stored_sources: dict[str, list[tuple[bytes | None, object]]] = {}
    if supports_documents:
        metadata_column = "metadata_json" if "metadata_json" in columns else "NULL"
        statement = (
            "SELECT document_ref, content, " + metadata_column +
            " FROM documentary_source WHERE dataset_id=? ORDER BY document_ref"
        )
        for ref, content, metadata in connection.execute(statement, (dataset_id,)):
            stored_sources.setdefault(ref, []).append((content, metadata))

    rows = []
    problems = set()
    verified_count = 0
    unsupported_evidence_count = 0
    for flow in sorted(flows, key=lambda item: item.flow_id):
        record = records[flow.flow_id]
        raw_refs = record.get("source_refs")
        if not isinstance(raw_refs, list) or not raw_refs:
            raise ValueError("El movimiento verificado no contiene referencias documentales.")
        refs = []
        seen = set()
        for source in raw_refs:
            ref = source.get("document_ref") if isinstance(source, dict) else None
            if not isinstance(ref, str) or not ref or ref != ref.strip():
                state = "INVALID_REFERENCE"
                ref = str(ref)
            elif ref in seen:
                state = "DUPLICATED_REFERENCE"
            elif not supports_documents:
                state = "DOCUMENT_STORAGE_UNAVAILABLE"
            else:
                found = stored_sources.get(ref, [])
                frozen = frozen_sources.get(ref)
                if not found:
                    state = "DOCUMENT_BYTES_MISSING"
                elif len(found) != 1:
                    state = "DOCUMENT_REFERENCE_AMBIGUOUS"
                elif not isinstance(found[0][0], bytes) or not found[0][0]:
                    state = "DOCUMENT_BYTES_MISSING"
                else:
                    payload, raw_metadata = found[0]
                    digest = sha256(payload).hexdigest()
                    metadata = None
                    if raw_metadata is not None:
                        try:
                            metadata = json.loads(raw_metadata)
                        except (TypeError, ValueError):
                            metadata = False
                    if metadata is False or (metadata is not None and not isinstance(metadata, dict)):
                        state = "DOCUMENT_METADATA_INVALID"
                    elif metadata and (
                        ("sha256" in metadata and metadata["sha256"] != digest)
                        or ("bytes" in metadata and metadata["bytes"] != len(payload))
                    ):
                        state = "DOCUMENT_METADATA_CONFLICT"
                    elif frozen is None:
                        state = "NOT_IN_SAVED_PROPOSAL_CONTEXT"
                    elif frozen.get("stored_bytes_sha256") != digest:
                        state = "DOCUMENT_CHANGED_SINCE_PROPOSAL"
                    else:
                        state = "BYTES_UNCHANGED_NOT_CONTENT_REVIEWED"
            seen.add(ref)
            refs.append({"document_ref": ref, "status": state})
            if state != "BYTES_UNCHANGED_NOT_CONTENT_REVIEWED":
                problems.add(state)
        direct_source_linked = flow.source_ref is None or flow.source_ref in seen
        if not direct_source_linked:
            problems.add("DIRECT_SOURCE_REF_NOT_LINKED")
        all_present = bool(refs) and all(
            source["status"] == "BYTES_UNCHANGED_NOT_CONTENT_REVIEWED"
            for source in refs
        ) and direct_source_linked
        if all_present:
            verified_count += 1
        if flow.evidence_state == "DEMONSTRATED" or flow.due_date_evidenced:
            unsupported_evidence_count += 1
        rows.append({
            "flow_id": flow.flow_id,
            "flow_type": flow.flow_type,
            "evidence_state": flow.evidence_state,
            "due_date_evidenced": flow.due_date_evidenced,
            "direct_source_reference_linked": direct_source_linked,
            "document_sources": refs,
            "status": (
                "SOURCE_BYTES_PRESENT_NOT_RECONCILED"
                if all_present else "SOURCE_LINKS_PENDING_OR_CONFLICTING"
            ),
        })

    report = {
        "schema": "COMPANY-LOCAL-FLOW-DOCUMENTARY-COVERAGE-01",
        "dataset_id": dataset_id,
        "status": (
            "SOURCE_BYTES_PRESENT_NOT_RECONCILED" if verified_count == len(rows)
            else "SOURCE_LINKS_PENDING_OR_CONFLICTING"
        ),
        "scope": "STORED_SOURCE_BYTES_AND_DECLARED_FLOW_LINKS_ONLY",
        "flow_count": len(rows),
        "source_bytes_present_count": verified_count,
        "source_issues": sorted(problems),
        "evidence_declared_count": unsupported_evidence_count,
        "documentary_content_review": "NOT_PERFORMED",
        "invoice_and_bank_reconciliation": "NOT_PERFORMED",
        "inventory_completeness": "NOT_ESTABLISHED",
        "source_authentication": "NOT_EXTERNALLY_AUTHENTICATED",
        "evidence_upgrade_status": "NOT_PERFORMED",
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
        "rows": rows,
    }
    report["fingerprint"] = _digest(report)
    return report


__all__ = ["audit_local_flow_documentary_coverage"]
