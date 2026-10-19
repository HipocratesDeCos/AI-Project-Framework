"""Explicit synthetic inventory assumptions, separate from documentary facts."""
import argparse
import csv
import json
from pathlib import Path
import sqlite3

from eios.company_data import CompanyDataStore

VERSION = "SYNTHETIC-INVENTORY-01"
TABLE = """CREATE TABLE IF NOT EXISTS synthetic_planning_inventory (
    dataset_id TEXT NOT NULL, article_id TEXT NOT NULL, payload TEXT NOT NULL,
    PRIMARY KEY(dataset_id, article_id),
    FOREIGN KEY(dataset_id) REFERENCES documentary_company_snapshot(dataset_id))"""


def inventory_rows(articles, dataset, as_of):
    rows = []
    for index, record in enumerate(sorted(articles, key=lambda r: r["data"]["article_id"])):
        a = record["data"]
        if a["unit_as_documented"].lower() == "palets":
            physical, reserved = [(0, 0), (3, 1), (6, 2)][index % 3]
        else:
            physical, reserved = [(0, 0), (30, 5), (60, 10)][index % 3]
        rows.append(dict(dataset_id=dataset, article_id=a["article_id"], description=a.get("description", ""),
                         unit=a["unit_as_documented"], as_of_date=as_of, physical=physical,
                         reserved=reserved, available=physical-reserved, source=VERSION,
                         material_nature="SYNTHETIC", basis="NEW_EXPLICIT_ASSUMPTION_NOT_INFERRED_FROM_INVOICES",
                         accounting_reconciliation="NOT_RECONCILED", demand_forecast=None, safety_stock=None,
                         operational_path="FORBIDDEN", decision_authority=False))
    return rows


def read_inventory(db, dataset):
    with sqlite3.connect(db) as c:
        if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='synthetic_planning_inventory'").fetchone():
            return {}
        return {article: json.loads(raw) for article, raw in c.execute(
            "SELECT article_id,payload FROM synthetic_planning_inventory WHERE dataset_id=?", (dataset,))}


def create_inventory(db, dataset, output):
    db, output = Path(db), Path(output)
    if not db.is_file():
        raise ValueError("La base documental no existe.")
    store = CompanyDataStore(db)
    info = store.describe(dataset)
    rows = inventory_rows(store.records(dataset, "article"), dataset, info["as_of_date"])
    if not rows:
        raise ValueError("La versión no contiene artículos.")
    with sqlite3.connect(db) as c:
        c.execute("PRAGMA foreign_keys=ON")
        c.execute(TABLE)
        existing = {key: json.loads(raw) for key, raw in c.execute(
            "SELECT article_id,payload FROM synthetic_planning_inventory WHERE dataset_id=?", (dataset,))}
        expected = {r["article_id"]: r for r in rows}
        if existing and existing != expected:
            raise ValueError("Ya existe otro inventario. No se sobrescribe.")
        if not existing:
            c.executemany("INSERT INTO synthetic_planning_inventory VALUES(?,?,?)",
                          [(dataset, r["article_id"], json.dumps(r, ensure_ascii=False)) for r in rows])
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["Código", "Descripción", "Unidad", "Fecha inventario", "Stock físico", "Reservado", "Disponible", "Naturaleza", "Origen", "Conciliación contable"])
        for r in rows:
            writer.writerow([r["article_id"], r["description"], r["unit"], r["as_of_date"], r["physical"], r["reserved"], r["available"], r["material_nature"], r["source"], r["accounting_reconciliation"]])
    return dict(articles=len(rows), output=str(output.resolve()), dataset_id=dataset,
                status="UNCHANGED" if existing else "CREATED", material_nature="SYNTHETIC")


def main():
    parser = argparse.ArgumentParser(description="Crear e incorporar inventario ficticio explícito; nunca deriva stock de facturas")
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--dataset-id")
    parser.add_argument("--output", type=Path, default=Path("data/Inventario_Sintetico_30092026.csv"))
    args = parser.parse_args()
    if not args.db.is_file():
        parser.error("No existe la base documental.")
    dataset = args.dataset_id
    if dataset is None:
        with sqlite3.connect(args.db) as c:
            ids = [r[0] for r in c.execute("SELECT dataset_id FROM documentary_company_snapshot")]
        if len(ids) != 1:
            parser.error("Indica --dataset-id: debe seleccionarse una versión documental exacta.")
        dataset = ids[0]
    print(json.dumps(create_inventory(args.db, dataset, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
