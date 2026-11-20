"""Read-only normalization of Odoo purchase.order Excel/CSV exports.

This is a company-app integration, NOT part of EIOS neutral motor.
No database writes, operational admission, or decision execution.
"""

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import hashlib
import json
import re

SOURCE_MODEL = "purchase.order"
CENT = Decimal("0.01")
HEADER = {
    "external_id": "ID externo",
    "reference": "Referencia del pedido",
    "supplier": "Proveedor",
    "status": "Estado",
    "currency": "Moneda/Nombre",
    "product_display": "Líneas del pedido/Referencia del pedido/Producto",
    "sku": "Producto/Referencia interna",
    "quantity": "Líneas del pedido/Cantidad",
    "unit_price": "Líneas del pedido/Precio unitario",
    "subtotal": "Líneas del pedido/Subtotal",
    "total": "Total",
}
OPTIONAL = {"tax_amount": "Impuestos", "order_date": "Fecha del pedido"}
KNOWN_CURRENCIES = {"Euro": "EUR", "EUR": "EUR"}
ALLOWED_STATES = {"SdP", "Solicitud de presupuesto", "Pedido de compra", "Compra", "Cancelado"}


def _amount(value, *, integer=False):
    if value is None or value == "" or isinstance(value, bool):
        raise ValueError("valor numérico ausente o inválido")
    if isinstance(value, str):
        value = value.strip()
        # Require unambiguous numeric input; the source workbook has numeric cells.
        if not re.fullmatch(r"-?\d+(?:\.\d+)?", value):
            raise ValueError("número de texto ambiguo: se requieren celdas numéricas")
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError("valor numérico inválido") from None
    if not d.is_finite() or (integer and d != d.to_integral_value()):
        raise ValueError("valor numérico no finito o no entero")
    return d


def _money(value):
    return _amount(value).quantize(CENT, rounding=ROUND_HALF_UP)


def normalize_table(table):
    """Read-only validation/normalization of a table from eios.company_tables.read_table.

    Every error fails the batch closed; no partial set is eligible for reception.
    """
    headers = table.get("headers", [])
    rows = table.get("rows", [])
    errors, warnings = [], []
    columns = {}
    for field, label in HEADER.items():
        indices = [i for i, h in enumerate(headers) if h == label]
        if len(indices) != 1:
            errors.append({"code": "HEADER", "field": field, "message": f"Se requiere exactamente una columna «{label}»."})
        else:
            columns[field] = indices[0]
    for field, label in OPTIONAL.items():
        indices = [i for i, h in enumerate(headers) if h == label]
        if len(indices) > 1:
            errors.append({"code": "HEADER", "field": field, "message": f"Columna ambigua: «{label}»."})
        elif indices:
            columns[field] = indices[0]
    if errors:
        return {"accepted": False, "orders": [], "errors": errors, "warnings": [], "source_model": SOURCE_MODEL}

    def read(row, field):
        value = row["values"][columns[field]] if field in columns else None
        if isinstance(value, dict):
            raise ValueError("fórmula o celda inválida: no se admiten resultados calculados de Excel")
        return value

    by_order = {}
    for ix, row in enumerate(rows):
        source_row = row.get("row", ix + 2)
        try:
            external_id = str(read(row, "external_id") or "").strip()
            reference = str(read(row, "reference") or "").strip()
            supplier = str(read(row, "supplier") or "").strip()
            status = str(read(row, "status") or "").strip()
            currency_label = str(read(row, "currency") or "").strip()
            product_display = str(read(row, "product_display") or "").strip()
            sku = str(read(row, "sku") or "").strip()
            order_date = read(row, "order_date") if "order_date" in columns else None
            if not external_id:
                raise ValueError("ID externo de pedido ausente")
            if not reference or not supplier or not product_display or not sku:
                raise ValueError("falta referencia, proveedor o producto/SKU")
            if status not in ALLOWED_STATES:
                raise ValueError(f"estado no reconocido: {status!r}")
            if currency_label not in KNOWN_CURRENCIES:
                raise ValueError(f"moneda no reconocida: {currency_label!r}")
            marker = re.match(r"^\[([^\]]+)\]", product_display)
            if marker and marker.group(1) != sku:
                raise ValueError("el SKU de producto contradice el código entre corchetes")
            quantity = _amount(read(row, "quantity"))
            unit_price = _money(read(row, "unit_price"))
            subtotal = _money(read(row, "subtotal"))
            total = _money(read(row, "total"))
            raw_tax = read(row, "tax_amount") if "tax_amount" in columns else None
            tax_amount = _money(raw_tax) if raw_tax not in (None, "") else None
            if quantity <= 0 or unit_price < 0 or subtotal < 0 or total < 0 or (tax_amount is not None and tax_amount < 0):
                raise ValueError("cantidad o importe fuera de rango")
            if (quantity * unit_price).quantize(CENT, rounding=ROUND_HALF_UP) != subtotal:
                raise ValueError("el subtotal no coincide con cantidad × precio unitario")
            if not order_date:
                warnings.append({"code": "ORDER_DATE_MISSING", "source_row": source_row, "message": "Fecha del pedido ausente: no se inventa."})
            line = {"source_row": source_row, "sku": sku, "product_display": product_display,
                    "quantity": str(quantity), "unit_price": str(unit_price), "subtotal": str(subtotal)}
            common = {"external_id": external_id, "reference": reference,
                      "supplier_name": supplier, "status": status,
                      "currency": KNOWN_CURRENCIES[currency_label], "order_date": order_date or None,
                      "tax_amount": str(tax_amount) if tax_amount is not None else None,
                      "total": str(total)}
            if external_id in by_order:
                old = by_order[external_id]
                if any(old[k] != v for k, v in common.items()):
                    raise ValueError("contradicción de cabecera entre líneas del mismo pedido")
                if any(x["sku"] == sku and x["quantity"] == line["quantity"] and
                       x["unit_price"] == line["unit_price"] for x in old["lines"]):
                    raise ValueError("línea de compra indistinguible sin identificador propio")
                old["lines"].append(line)
            else:
                by_order[external_id] = dict(**common, lines=[line])
        except (ValueError, IndexError, KeyError) as exc:
            errors.append({"code": "ROW", "source_row": source_row, "message": str(exc)})
    for order in by_order.values():
        base = sum((Decimal(x["subtotal"]) for x in order["lines"]), Decimal("0"))
        tax = Decimal(order["tax_amount"]) if order["tax_amount"] is not None else None
        order["base"] = str(base.quantize(CENT))
        if tax is not None and (base + tax).quantize(CENT) != Decimal(order["total"]):
            errors.append({"code": "ORDER_TOTAL", "external_id": order["external_id"],
                           "message": "base + impuestos no coincide con el total exportado"})
        elif tax is None:
            warnings.append({"code": "TAX_NOT_AVAILABLE", "external_id": order["external_id"],
                             "message": "Impuestos no exportados: total fiscal sin validar."})
    accepted = bool(by_order) and not errors
    return {"accepted": accepted, "source_model": SOURCE_MODEL,
            "source_nature": "UNVERIFIED_EXTERNAL_EXPORT",
            "admission_status": "PENDING", "decision_authority": False,
            "operational_path": "FORBIDDEN",
            "orders": list(by_order.values()) if accepted else [],
            "errors": errors, "warnings": warnings}


def preview_xlsx_or_csv(data, filename):
    """Use the bounded legacy company parser. No database side effects."""
    from eios.company_tables import read_table
    table = read_table(data, filename)
    result = normalize_table(table)
    result["sha256"] = hashlib.sha256(data).hexdigest()
    return result


def main():
    """Preview a file locally; never write to the EIOS company database."""
    import argparse
    from pathlib import Path
    parser = argparse.ArgumentParser(description="Odoo purchase.order -> EIOS read-only JSON preview")
    parser.add_argument("source", type=Path, help="Export original .xlsx or .csv from Odoo")
    parser.add_argument("--output", type=Path, help="Optional JSON preview path; never an EIOS database")
    args = parser.parse_args()
    result = preview_xlsx_or_csv(args.source.read_bytes(), args.source.name)
    rendered = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0 if result["accepted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
