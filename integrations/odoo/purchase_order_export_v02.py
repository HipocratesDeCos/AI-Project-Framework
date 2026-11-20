"""Read-only preview for Odoo purchase.order exports containing draft orders.

Uses the v0.1 numeric validation; preserves pending headers and external line IDs.
Never creates or admits company/operational records.
"""

from decimal import Decimal
import hashlib
import json

from integrations.odoo.purchase_orders import (
    HEADER, OPTIONAL, KNOWN_CURRENCIES, ALLOWED_STATES, _money, normalize_table,
)

ORDER_ID_VARIANTS = ("ID externo", "ID")
PRODUCT_COLUMN_VARIANTS = (
    HEADER["product_display"],
    "Líneas del pedido/Producto",
)
LINE_ID = "Líneas del pedido/ID"


def normalize_export(table):
    """Prepare a non-persistable preview of complete and line-less Odoo orders."""
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    errors = []
    warnings = []
    variants = [(i, h) for i, h in enumerate(headers) if h in PRODUCT_COLUMN_VARIANTS]
    if len(variants) != 1:
        errors.append({"code": "PRODUCT_HEADER_AMBIGUOUS", "message": "Se requiere una sola columna de producto de línea de Odoo."})
    order_ids = [(i, h) for i, h in enumerate(headers) if h in ORDER_ID_VARIANTS]
    if len(order_ids) != 1:
        errors.append({"code": "ORDER_ID_HEADER_AMBIGUOUS", "message": "Se requiere una sola columna ID/ID externo de pedido."})
    line_id_positions = [i for i, h in enumerate(headers) if h == LINE_ID]
    if len(line_id_positions) > 1:
        errors.append({"code": "LINE_ID_HEADER_AMBIGUOUS", "message": "La columna ID de línea está duplicada."})
    if errors:
        return _output([], [], errors, warnings, len(rows), {})

    # Translate exactly one verified Odoo variant to the v0.1 canonical header.
    mapped = list(headers)
    mapped[variants[0][0]] = HEADER["product_display"]
    mapped[order_ids[0][0]] = HEADER["external_id"]
    idx = {h: i for i, h in enumerate(mapped) if h}
    mandatory = [HEADER[k] for k in HEADER]
    missing = [h for h in mandatory if mapped.count(h) != 1]
    if missing:
        errors.append({"code": "HEADER", "message": "Cabeceras ausentes o repetidas: " + ", ".join(missing)})
        return _output([], [], errors, warnings, len(rows), {})

    id_col = line_id_positions[0] if line_id_positions else None
    valid_rows, pending_orders = [], []
    line_by_row = {}
    seen_line_ids = set()
    pending_order_ids = set()
    seen_order_ids = set()
    external_id_by_reference = {}
    line_fields = [HEADER[k] for k in ("product_display", "sku", "quantity", "unit_price", "subtotal")]
    for index, row in enumerate(rows):
        source_row = row.get("row", index + 2)
        values = row.get("values", [])
        try:
            def value(field):
                cell = values[idx[field]]
                if isinstance(cell, dict):
                    raise ValueError("La fila contiene una fórmula o celda inválida.")
                return cell

            external_id = str(value(HEADER["external_id"]) or "").strip()
            reference = str(value(HEADER["reference"]) or "").strip()
            supplier = str(value(HEADER["supplier"]) or "").strip()
            status = str(value(HEADER["status"]) or "").strip()
            currency = str(value(HEADER["currency"]) or "").strip()
            raw_line_id = values[id_col] if id_col is not None else None
            if isinstance(raw_line_id, dict):
                raise ValueError("La identidad de línea es una fórmula.")
            line_id = str(raw_line_id or "").strip()
            if not external_id or not reference or not supplier:
                raise ValueError("Falta el ID de pedido, su referencia o el proveedor.")
            if status not in ALLOWED_STATES or currency not in KNOWN_CURRENCIES:
                raise ValueError("Estado o moneda no reconocidos.")
            other_id = external_id_by_reference.get(reference)
            if other_id is not None and other_id != external_id:
                raise ValueError("Referencia de pedido repetida con un ID externo diferente.")
            external_id_by_reference[reference] = external_id
            all_line_values = [value(f) for f in line_fields]
            no_line = all(v is None or v == "" for v in all_line_values) and not line_id
            if no_line:
                if external_id in pending_order_ids or external_id in seen_order_ids:
                    raise ValueError("Cabecera pendiente duplicada o mezclada con líneas de pedido.")
                amount = _money(value(HEADER["total"]))
                taxes = value(OPTIONAL["tax_amount"]) if OPTIONAL["tax_amount"] in idx else None
                if amount != 0 or (taxes not in (None, "") and _money(taxes) != 0):
                    raise ValueError("Pedido sin líneas, pero con importe distinto de cero.")
                pending_order_ids.add(external_id)
                pending_orders.append({
                    "external_id": external_id, "reference": reference,
                    "supplier_name": supplier, "status": status,
                    "currency": KNOWN_CURRENCIES[currency], "source_row": source_row,
                    "reason": "NO_ORDER_LINES", "total": "0.00",
                })
                warnings.append({"code": "ORDER_WITHOUT_LINES", "source_row": source_row,
                                 "reference": reference, "message": "Pedido sin líneas: excluido del análisis económico."})
                continue
            if external_id in pending_order_ids:
                raise ValueError("Un pedido sin líneas también contiene líneas en este archivo.")
            if id_col is not None and not line_id:
                raise ValueError("Falta el ID externo de una línea existente.")
            if line_id:
                if line_id in seen_line_ids:
                    raise ValueError("ID externo de línea duplicado.")
                seen_line_ids.add(line_id)
            elif id_col is None:
                warnings.append({"code": "LINE_ID_NOT_EXPORTED", "source_row": source_row,
                                 "message": "No se ha exportado identidad de línea; no es apto para conciliación de líneas."})
            seen_order_ids.add(external_id)
            line_by_row[source_row] = line_id or None
            valid_rows.append(row)
        except (ValueError, IndexError, KeyError) as error:
            errors.append({"code": "ROW", "source_row": source_row, "message": str(error)})

    legacy = normalize_table({"headers": mapped, "rows": valid_rows}) if valid_rows else None
    if legacy and legacy["errors"]:
        errors += legacy["errors"]
    if legacy:
        warnings += legacy["warnings"]
    orders = legacy["orders"] if legacy and legacy["accepted"] else []
    for order in orders:
        for line in order["lines"]:
            line["external_line_id"] = line_by_row[line["source_row"]]

    # Preview remains useful, but the batch is deliberately not accepted while
    # any order is missing lines; this is never an operational admission.
    return _output(orders, pending_orders, errors, warnings, len(rows), line_by_row)


def _output(orders, pending, errors, warnings, row_count, identities):
    base = sum((Decimal(o["base"]) for o in orders), Decimal("0.00"))
    total = sum((Decimal(o["total"]) for o in orders), Decimal("0.00"))
    return {
        "accepted": bool(orders) and not errors and not pending,
        "preview_only": True,
        "persistence_allowed": False,
        "source_model": "purchase.order",
        "source_nature": "UNVERIFIED_EXTERNAL_EXPORT",
        "admission_status": "PENDING",
        "decision_authority": False,
        "operational_path": "FORBIDDEN",
        "orders_preview": orders if not errors else [],
        "pending_orders": pending,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "source_rows": row_count,
            "complete_orders": len(orders) if not errors else 0,
            "pending_orders": len(pending),
            "lines_with_external_id": sum(bool(x) for x in identities.values()),
            "base": str(base if not errors else Decimal("0.00")),
            "total": str(total if not errors else Decimal("0.00")),
            "tax": str((total-base) if not errors else Decimal("0.00")),
        },
    }


def preview_file(data, filename):
    from eios.company_tables import read_table
    result = normalize_export(read_table(data, filename))
    result["sha256"] = hashlib.sha256(data).hexdigest()
    return result


def main():
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description="Odoo purchase.order v0.2 — vista previa sin escritura")
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = preview_file(args.source.read_bytes(), args.source.name)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0 if not result["errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
