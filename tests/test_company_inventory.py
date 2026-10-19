import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from eios.company_inventory import create_inventory, read_inventory, inventory_rows


class InventoryTest(unittest.TestCase):
    def test_quantities_units_and_explicit_assumptions(self):
        articles = [dict(data=dict(article_id=str(i).zfill(2),unit_as_documented="palets" if i%2 else "uds.")) for i in range(18)]
        rows = inventory_rows(articles, "D", "2026-09-30")
        self.assertEqual(len(rows), 18)
        self.assertTrue(any(r["available"] == 0 for r in rows))
        for r in rows:
            self.assertEqual(r["available"], r["physical"] - r["reserved"])
            self.assertGreaterEqual(r["reserved"], 0)
            self.assertGreaterEqual(r["available"], 0)
            self.assertEqual(r["material_nature"], "SYNTHETIC")
            self.assertIsNone(r["demand_forecast"])
            self.assertFalse(r["decision_authority"])

    def test_persistence_idempotence_and_no_documentary_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/"company.db"
            with sqlite3.connect(db) as c:
                c.executescript("CREATE TABLE documentary_company_snapshot(dataset_id TEXT PRIMARY KEY,manifest_json TEXT); CREATE TABLE documentary_company_record(dataset_id TEXT,kind TEXT,record_id TEXT,record_json TEXT); CREATE TABLE documentary_source(dataset_id TEXT);")
                for ds in ("one","two"):
                    c.execute("INSERT INTO documentary_company_snapshot VALUES(?,?)",(ds,json.dumps(dict(company=dict(company_id=ds),as_of_date="2026-09-30"))))
                    c.execute("INSERT INTO documentary_company_record VALUES(?,?,?,?)",(ds,"article","A",json.dumps(dict(data=dict(article_id="A",unit_as_documented="palets",stock_quantity=None)))))
            output=Path(tmp)/"inventory.csv"
            self.assertEqual(read_inventory(db,"one"), {})
            self.assertEqual(create_inventory(db,"one",output)["status"],"CREATED")
            self.assertEqual(create_inventory(db,"one",output)["status"],"UNCHANGED")
            self.assertEqual(read_inventory(db,"two"), {})
            self.assertEqual(read_inventory(db,"one")["A"]["available"],0)
            self.assertIn("Disponible",output.read_text(encoding="utf-8-sig"))
            with sqlite3.connect(db) as c:
                original=json.loads(c.execute("SELECT record_json FROM documentary_company_record LIMIT 1").fetchone()[0])
                self.assertIsNone(original["data"]["stock_quantity"])
                c.execute("UPDATE synthetic_planning_inventory SET payload=?",(json.dumps(dict(changed=True)),))
            with self.assertRaises(ValueError):
                create_inventory(db,"one",output)
