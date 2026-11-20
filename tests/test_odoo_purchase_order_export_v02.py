"""Odoo purchase.order exported line IDs and incomplete RFQ safety tests."""

from copy import deepcopy
from decimal import Decimal
import unittest

from integrations.odoo.purchase_order_export_v02 import normalize_export

HEADERS = [
    "ID", "Referencia del pedido", "Proveedor", "Fecha del pedido", "Estado",
    "Moneda/Nombre", "Líneas del pedido/ID", "Líneas del pedido/Producto",
    "Producto/Referencia interna", "Líneas del pedido/Cantidad",
    "Líneas del pedido/Precio unitario", "Líneas del pedido/Subtotal",
    "Impuestos", "Total",
]
CASES = [
    (10, "ILU-0001", 2, 415.8, 831.6, 174.64, 1006.24),
    (9, "SUS-0021", 40, 8.5, 340, 71.4, 411.4),
    (8, "SUS-0013", 36, 8.5, 306, 64.26, 370.26),
    (7, "SUS-0007", 48, 8.5, 408, 85.68, 493.68),
    (6, "CON-0151", 3, 64.35, 193.05, 40.54, 233.59),
    (5, "SUS-0001", 32, 8.42, 269.44, 56.58, 326.02),
    (4, "SUS-0025", 45, 8.5, 382.5, 80.33, 462.83),
    (3, "TUT-0001", 240, .35, 84, 17.64, 101.64),
    (1, "ILU-0012", 6, 28, 168, 35.28, 203.28),
]


def order_row(number, sku, qty, price, base, tax, total):
    return [
        f"__export__.purchase_order_{number}",
        f"EIOS-DEMO-PO-2026-{number:03}", f"Proveedor {number}", None, "SdP",
        "Euro", f"eios_demo.import_line_2026_{number:03}",
        f"[{sku}] Producto de prueba {number}", sku, qty, price, base, tax, total,
    ]


def pending():
    return ["__export__.purchase_order_2", "EIOS-DEMO-PO-2026-002",
            "Proveedor 2", None, "SdP", "Euro", None, None, None,
            None, None, None, 0, 0]


def table(*rows, headers=HEADERS):
    return {"headers": list(headers), "rows": [
        {"row": i + 2, "values": list(row)} for i, row in enumerate(rows)
    ]}


def ten_orders():
    values = [order_row(*case) for case in CASES]
    values.insert(-1, pending())
    return table(*values)


class OdooExportV02Tests(unittest.TestCase):
    def test_full_export_nine_lines_one_pending_and_totals(self):
        source = ten_orders()
        original = deepcopy(source)
        result = normalize_export(source)
        self.assertFalse(result["accepted"])
        self.assertFalse(result["persistence_allowed"])
        self.assertFalse(result["decision_authority"])
        self.assertEqual(result["operational_path"], "FORBIDDEN")
        self.assertEqual(result["admission_status"], "PENDING")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["summary"]["source_rows"], 10)
        self.assertEqual(result["summary"]["complete_orders"], 9)
        self.assertEqual(result["summary"]["pending_orders"], 1)
        self.assertEqual(result["summary"]["lines_with_external_id"], 9)
        self.assertEqual(result["summary"]["base"], "2982.59")
        self.assertEqual(result["summary"]["tax"], "626.35")
        self.assertEqual(result["summary"]["total"], "3608.94")
        self.assertEqual(result["pending_orders"][0]["reference"], "EIOS-DEMO-PO-2026-002")
        self.assertEqual(result["pending_orders"][0]["reason"], "NO_ORDER_LINES")
        self.assertEqual(len(result["orders_preview"]), 9)
        self.assertTrue(all(o["lines"][0]["external_line_id"] for o in result["orders_preview"]))
        self.assertEqual(source, original, "normalization must not mutate input")

    def test_one_complete_order_is_accepted_for_preview_only(self):
        result = normalize_export(table(order_row(*CASES[-1])))
        self.assertTrue(result["accepted"])
        self.assertFalse(result["persistence_allowed"])
        self.assertEqual(result["summary"]["complete_orders"], 1)

    def test_backward_compatible_old_export_headers(self):
        row = order_row(*CASES[-1])
        old_headers = list(HEADERS)
        old_headers[0] = "ID externo"
        old_headers[7] = "Líneas del pedido/Referencia del pedido/Producto"
        del old_headers[6]
        del row[6]
        result = normalize_export(table(row, headers=old_headers))
        self.assertTrue(result["accepted"], result["errors"])
        self.assertEqual(result["summary"]["lines_with_external_id"], 0)
        self.assertTrue(any(w["code"] == "LINE_ID_NOT_EXPORTED" for w in result["warnings"]))

    def test_line_identity_duplicate_rejected(self):
        first, second = order_row(*CASES[0]), order_row(*CASES[1])
        second[6] = first[6]
        result = normalize_export(table(first, second))
        self.assertFalse(result["accepted"])
        self.assertEqual(result["orders_preview"], [])
        self.assertTrue(result["errors"])

    def test_nonzero_line_less_order_rejected(self):
        row = pending()
        row[-1] = 1
        result = normalize_export(table(row))
        self.assertFalse(result["accepted"])
        self.assertTrue(result["errors"])

    def test_partial_line_does_not_become_pending(self):
        row = pending()
        row[9] = 1
        result = normalize_export(table(row))
        self.assertFalse(result["accepted"])
        self.assertEqual(result["pending_orders"], [])
        self.assertTrue(result["errors"])

    def test_formula_is_rejected(self):
        row = order_row(*CASES[0]); row[11] = {"formula": True, "cached": 831.6}
        self.assertFalse(normalize_export(table(row))["accepted"])

    def test_wrong_subtotal_is_rejected(self):
        row = order_row(*CASES[0]); row[11] = 1
        self.assertFalse(normalize_export(table(row))["accepted"])

    def test_wrong_tax_total_is_rejected(self):
        row = order_row(*CASES[0]); row[13] = 111
        self.assertFalse(normalize_export(table(row))["accepted"])

    def test_sku_collision_is_rejected(self):
        row = order_row(*CASES[0]); row[8] = "FER-0001"
        self.assertFalse(normalize_export(table(row))["accepted"])

    def test_two_product_columns_are_ambiguous(self):
        headers = HEADERS + ["Líneas del pedido/Referencia del pedido/Producto"]
        row = order_row(*CASES[0]) + ["Producto 1"]
        errors = normalize_export(table(row, headers=headers))["errors"]
        self.assertTrue(any(x["code"] == "PRODUCT_HEADER_AMBIGUOUS" for x in errors))

    def test_missing_line_id_in_id_profile_rejected(self):
        row = order_row(*CASES[0]); row[6] = None
        self.assertFalse(normalize_export(table(row))["accepted"])

    def test_repeat_order_reference_on_other_id_rejected(self):
        first, second = order_row(*CASES[0]), order_row(*CASES[1])
        second[1] = first[1]
        self.assertFalse(normalize_export(table(first, second))["accepted"])

    def test_blank_date_is_warning_not_fabricated(self):
        result = normalize_export(table(order_row(*CASES[-1])))
        self.assertTrue(any(w["code"] == "ORDER_DATE_MISSING" for w in result["warnings"]))
        self.assertIsNone(result["orders_preview"][0]["order_date"])


if __name__ == "__main__":
    unittest.main()
