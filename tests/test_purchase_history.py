import unittest
from eios.purchase_history import purchase_history


class Store:
    def __init__(self, records):
        self.rows = records
    def records(self, dataset, kind):
        return self.rows.get((dataset, kind), [])


class PurchaseHistoryTest(unittest.TestCase):
    def setUp(self):
        self.article = dict(article_id="A", supplier_id="S", unit_as_documented="palets")
        self.header = dict(record_id="I", data=dict(issue_date="2026-09-30", supplier_id="S", currency="EUR", invoice_number="F-1"))
        self.line = dict(data=dict(article_id="A", supplier_id="S", invoice_id="I", quantity="4", unit_price="1850", net_amount="7400", unit_as_documented="palets", currency="EUR"), source_refs=[dict(document_ref="DOC-016", page=1)])
        self.rows = {("one", "purchase_invoice"): [self.header], ("one", "purchase_invoice_line"): [self.line]}

    def history(self):
        return purchase_history(Store(self.rows), "one", self.article, "2026-09-30")

    def test_real_shape_and_discounted_comparison_basis(self):
        row = self.history()[0]
        self.assertEqual(row["effective_net_unit_price"], "1850")
        self.assertTrue(row["comparable"])
        self.assertEqual(row["source_refs"][0]["document_ref"], "DOC-016")
        self.line["data"]["net_amount"] = "6660"
        self.assertEqual(self.history()[0]["effective_net_unit_price"], "1665")
        self.assertEqual(self.line["data"]["unit_price"], "1850")

    def test_scope_article_counterparty_and_cutoff(self):
        self.assertEqual(purchase_history(Store(self.rows), "other", self.article, "2026-09-30"), [])
        for field, wrong in [("article_id", "OTHER"), ("supplier_id", "OTHER"), ("invoice_id", "MISSING")]:
            original = self.line["data"][field]
            self.line["data"][field] = wrong
            self.assertEqual(self.history(), [])
            self.line["data"][field] = original
        self.header["data"]["issue_date"] = "2026-10-01"
        self.assertEqual(self.history(), [])

    def test_incomparable_or_invalid_values(self):
        self.line["data"]["unit_as_documented"] = "uds."
        self.assertFalse(self.history()[0]["comparable"])
        self.line["data"]["unit_as_documented"] = "palets"
        for qty in ("0", "-1", "NaN", "Infinity"):
            self.line["data"]["quantity"] = qty
            self.assertFalse(self.history()[0]["comparable"])

    def test_order_and_same_day_lines_preserved(self):
        older = dict(record_id="OLD", data=dict(self.header["data"], issue_date="2026-09-01"))
        self.rows[("one", "purchase_invoice")].append(older)
        self.rows[("one", "purchase_invoice_line")].append(dict(data=dict(self.line["data"], invoice_id="OLD")))
        self.rows[("one", "purchase_invoice_line")].append(dict(self.line))
        rows = self.history()
        self.assertEqual([r["issue_date"] for r in rows], ["2026-09-30", "2026-09-30", "2026-09-01"])

    def test_rendered_javascript_syntax(self):
        import shutil
        import subprocess
        import tempfile
        from pathlib import Path
        from eios.company_app import PAGE
        node = shutil.which("node")
        if not node:
            self.skipTest("Node unavailable for JavaScript syntax check")
        script = PAGE.replace("TOKEN", '"test-token"').split("<script>")[1].split("</script>")[0]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "screen.js"
            path.write_text(script, encoding="utf-8")
            result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
