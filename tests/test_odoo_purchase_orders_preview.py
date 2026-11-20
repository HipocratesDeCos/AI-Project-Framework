import unittest
from decimal import Decimal
from integrations.odoo.purchase_orders import normalize_table

HEADERS = [
    "ID externo", "Referencia del pedido", "Proveedor", "Fecha del pedido",
    "Estado", "Moneda/Nombre", "Líneas del pedido/Referencia del pedido/Producto",
    "Producto/Referencia interna", "Líneas del pedido/Cantidad",
    "Líneas del pedido/Precio unitario", "Impuestos", "Líneas del pedido/Subtotal", "Total"
]
ROW = ["__export__.purchase_order_108_94658254", "EIOS-DEMO-PO-2026-001",
       "Adjust-A-Wings Ltd", None, "SdP", "Euro",
       "[ILU-0012] Reflector Adjust-A-Wings Enforcer Medium", "ILU-0012",
       6, 28, 35.28, 168, 203.28]


def data(*rows, headers=HEADERS):
    return {"headers": list(headers), "rows":
            [{"row": i+2, "values": list(r)} for i, r in enumerate(rows)]}


class OdooOrdersReadOnlyTests(unittest.TestCase):
    def test_valid_quotation_no_admission(self):
        result = normalize_table(data(ROW))
        self.assertTrue(result["accepted"])
        self.assertEqual(result["orders"][0]["base"], "168.00")
        self.assertEqual(result["orders"][0]["total"], "203.28")
        self.assertEqual(result["orders"][0]["lines"][0]["sku"], "ILU-0012")
        self.assertEqual(result["orders"][0]["currency"], "EUR")
        self.assertFalse(result["decision_authority"])
        self.assertEqual(result["operational_path"], "FORBIDDEN")
        self.assertEqual(result["admission_status"], "PENDING")

    def test_missing_identity_fails(self):
        row = list(ROW)
        row[0] = ""
        self.assertFalse(normalize_table(data(row))["accepted"])

    def test_sku_mismatch_fails(self):
        row = list(ROW)
        row[7] = "FER-0001"
        self.assertFalse(normalize_table(data(row))["accepted"])

    def test_imported_subtotal_inconsistent_fails(self):
        row = list(ROW)
        row[11] = 167
        self.assertFalse(normalize_table(data(row))["accepted"])

    def test_formula_rejected(self):
        row = list(ROW)
        row[11] = {"formula": True, "cached": 168}
        self.assertFalse(normalize_table(data(row))["accepted"])

    def test_duplicate_line_ambiguous_fails(self):
        self.assertFalse(normalize_table(data(ROW, ROW))["accepted"])

    def test_missing_header_fails_closed(self):
        self.assertFalse(normalize_table(data(ROW, headers=HEADERS[:-1]))["accepted"])

    def test_order_total_inconsistent_fails(self):
        row = list(ROW)
        row[12] = 202
        self.assertFalse(normalize_table(data(row))["accepted"])

    def test_three_orders_matching_sample_export(self):
        r003 = list(ROW)
        r003[0], r003[1], r003[2] = "__export__.purchase_order_110_ae882146", "EIOS-DEMO-PO-2026-003", "AgroSoportes S.L."
        r003[6], r003[7] = "[TUT-0001] Tutor de Bambú Natural 90cm", "TUT-0001"
        r003[8:13] = [240, .35, 17.64, 84, 101.64]
        r010 = list(ROW)
        r010[0], r010[1], r010[2] = "__export__.purchase_order_117_cecbea2a", "EIOS-DEMO-PO-2026-010", "Lumatek Europe B.V."
        r010[6], r010[7] = "[ILU-0001] Lumatek Zeus 600W Pro 2.9 1 Ud", "ILU-0001"
        r010[8:13] = [2, 415.8, 174.64, 831.6, 1006.24]
        result = normalize_table(data(r010, r003, ROW))
        self.assertTrue(result["accepted"], result["errors"])
        self.assertEqual(len(result["orders"]), 3)
        self.assertEqual(sum(Decimal(o["base"]) for o in result["orders"]), Decimal("1083.60"))
        self.assertEqual(sum(Decimal(o["total"]) for o in result["orders"]), Decimal("1311.16"))

    def test_multiple_distinct_lines_supported(self):
        row = list(ROW)
        row[6], row[7] = "[SUS-0012] Sustrato", "SUS-0012"
        row[8:13] = [3, 10, 41.58, 30, 239.58]
        original = list(ROW)
        original[10], original[12] = 41.58, 239.58
        result = normalize_table(data(original, row))
        self.assertTrue(result["accepted"], result["errors"])
        self.assertEqual(result["orders"][0]["base"], "198.00")


if __name__ == "__main__":
    unittest.main()
