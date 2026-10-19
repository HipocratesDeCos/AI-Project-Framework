import json
from decimal import Decimal
from pathlib import Path
import sqlite3
import tempfile
import unittest
from eios.company_planning import coverage_for_article, create_planning, read_planning, VERSION


class PlanningTest(unittest.TestCase):
    def values(self, physical=3, reserved=1, demand="0.1"):
        inventory=dict(dataset_id="snapshot",article_id="A",unit="palets",as_of_date="2026-09-30",
            physical=physical,reserved=reserved,material_nature="SYNTHETIC",source="SYNTHETIC-INVENTORY-01")
        plan=dict(dataset_id="snapshot",article_id="A",unit="palets",as_of_date="2026-09-30",
            daily_demand=demand,lead_time_days=14,safety_stock="1",valid_to="2026-10-30",
            material_nature="SYNTHETIC",source=VERSION,pending_receipts_state="UNKNOWN")
        return inventory,plan

    def test_canonical_coverage_and_no_authority(self):
        stock,plan=self.values()
        result=coverage_for_article("C","snapshot",stock,plan)
        self.assertEqual(Decimal(result["coverage_days"]),Decimal("20"))
        self.assertEqual(result["stock_available"],"2")
        self.assertEqual(result["pending_receipts_state"],"UNKNOWN")
        self.assertFalse(result["decision_authority"])
        self.assertEqual(result["operational_path"],"FORBIDDEN")

    def test_zero_stock_zero_demand_missing_and_mismatch(self):
        stock,plan=self.values(physical=0,reserved=0)
        self.assertEqual(Decimal(coverage_for_article("C","snapshot",stock,plan)["coverage_days"]),Decimal("0"))
        stock,plan=self.values(demand="0")
        self.assertEqual(coverage_for_article("C","snapshot",stock,plan)["status"],"UNBOUNDED")
        self.assertEqual(coverage_for_article("C","snapshot",None,plan)["status"],"MISSING_DATA")
        stock["unit"]="uds."
        with self.assertRaises(ValueError):
            coverage_for_article("C","snapshot",stock,plan)

    def test_persistence_scope_and_idempotence(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"company.db"
            with sqlite3.connect(db) as c:
                c.executescript("CREATE TABLE documentary_company_snapshot(dataset_id TEXT PRIMARY KEY,manifest_json TEXT); CREATE TABLE documentary_company_record(dataset_id TEXT,kind TEXT,record_id TEXT,record_json TEXT); CREATE TABLE documentary_source(dataset_id TEXT);")
                for ds in ("one","two"):
                    c.execute("INSERT INTO documentary_company_snapshot VALUES(?,?)",(ds,json.dumps(dict(company=dict(company_id=ds),as_of_date="2026-09-30"))))
                    for index in range(18):
                        data=dict(article_id="A"+str(index),unit_as_documented="palets" if index%2 else "uds.",demand_forecast=None)
                        c.execute("INSERT INTO documentary_company_record VALUES(?,?,?,?)",(ds,"article",data["article_id"],json.dumps(dict(data=data))))
            self.assertEqual(read_planning(db,"one"),{})
            self.assertEqual(create_planning(db,"one")["status"],"CREATED")
            self.assertEqual(create_planning(db,"one")["status"],"UNCHANGED")
            self.assertEqual(len(read_planning(db,"one")),18)
            self.assertEqual(read_planning(db,"two"),{})
            with sqlite3.connect(db) as c:
                c.execute("UPDATE synthetic_article_planning SET payload=?",(json.dumps(dict(changed=True)),))
            with self.assertRaises(ValueError):
                create_planning(db,"one")
