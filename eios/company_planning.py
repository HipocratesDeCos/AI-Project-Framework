"""Synthetic planning assumptions and coverage through the existing STK engine."""
import argparse
from datetime import date, timedelta
from decimal import Decimal
import json
from pathlib import Path
import sqlite3

from eios.company_data import CompanyDataStore
from eios.company_inventory import read_inventory
from eios.core.models import DecisionContext
from eios.stock.models import (
    StockScope, StockComputationContext, DemandMethodSelection, AuthorizedForecastRate,
    NormalizedQuantity, StockAvailabilityInput, CollectionEnvelope, StockCommitmentComponent)
from eios.stock.engine import calculate_stock_availability, use_authorized_forecast, calculate_coverage

VERSION = "SYNTHETIC-PLANNING-01"


def read_planning(db, dataset):
    with sqlite3.connect(db) as c:
        if not c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='synthetic_article_planning'").fetchone():
            return {}
        return {key: json.loads(raw) for key,raw in c.execute("SELECT article_id,payload FROM synthetic_article_planning WHERE dataset_id=?", (dataset,))}


def create_planning(db, dataset):
    store = CompanyDataStore(Path(db))
    info = store.describe(dataset)
    rows = []
    for record in store.records(dataset,"article"):
        a = record["data"]
        pallet = a["unit_as_documented"].lower() == "palets"
        rows.append(dict(dataset_id=dataset,article_id=a["article_id"],unit=a["unit_as_documented"],
                         as_of_date=info["as_of_date"],daily_demand="0.1" if pallet else "1",
                         lead_time_days=14 if pallet else 7,safety_stock="1" if pallet else "10",
                         valid_to=(date.fromisoformat(info["as_of_date"])+timedelta(days=30)).isoformat(),
                         demand_basis="ADDITIONAL_DEMAND_EXCLUDES_EXISTING_RESERVATIONS",
                         pending_receipts_state="UNKNOWN",material_nature="SYNTHETIC",source=VERSION,
                         operational_path="FORBIDDEN",decision_authority=False))
    if not rows:
        raise ValueError("No hay artículos.")
    with sqlite3.connect(db) as c:
        c.execute("PRAGMA foreign_keys=ON")
        c.execute("""CREATE TABLE IF NOT EXISTS synthetic_article_planning (
            dataset_id TEXT NOT NULL REFERENCES documentary_company_snapshot(dataset_id),
            article_id TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(dataset_id,article_id))""")
        existing = {key:json.loads(raw) for key,raw in c.execute("SELECT article_id,payload FROM synthetic_article_planning WHERE dataset_id=?",(dataset,))}
        if existing and existing != {r["article_id"]:r for r in rows}:
            raise ValueError("Ya existe otra planificación; no se sobrescribe.")
        if not existing:
            c.executemany("INSERT INTO synthetic_article_planning VALUES(?,?,?)",[(dataset,r["article_id"],json.dumps(r)) for r in rows])
    return dict(status="UNCHANGED" if existing else "CREATED",articles=len(rows),source=VERSION)


def coverage_for_article(company, dataset, inventory, planning):
    if inventory is None or planning is None:
        return dict(status="MISSING_DATA",message="Falta inventario o planificación sintética.")
    for field in ("article_id","unit","as_of_date","dataset_id"):
        if inventory[field] != planning[field]:
            raise ValueError("Inventario y planificación incompatibles: "+field)
    if inventory["dataset_id"] != dataset or inventory["material_nature"] != "SYNTHETIC" or planning["material_nature"] != "SYNTHETIC":
        raise ValueError("Contexto sintético incompatible.")
    if inventory["source"] != "SYNTHETIC-INVENTORY-01" or planning["source"] != VERSION:
        raise ValueError("Versión de supuestos no soportada.")
    when=date.fromisoformat(planning["as_of_date"])
    scope=StockScope(company_id=company,operational_scope_id="SYNTHETIC-PLANNING")
    article=planning["article_id"]
    ref=VERSION+":"+dataset+":"+article
    inventory_ref=inventory["source"]+":"+dataset+":"+article
    selection=DemandMethodSelection(method="AUTHORIZED_FORECAST",state="KNOWN",policy_ref=VERSION,policy_version="1",applicable_reference_date=when,source_ref=ref)
    context=StockComputationContext(
        decision_context=DecisionContext(decision_id="SYNTHETIC-COVERAGE",scenario_id="DOCUMENTARY-PLANNING",
            rules_version="STK-v0.1",parameters_version=VERSION,data_snapshot_id=dataset),
        scope=scope,article_id=article,evaluation_date=when,base_unit=planning["unit"],
        methodology_version="STK-v0.1",demand_selection=selection,forecast_version=VERSION)
    def quantity(value):
        return NormalizedQuantity(scope=scope,article_id=article,value=Decimal(str(value)),unit=planning["unit"],
            source_unit=planning["unit"],state="KNOWN",source_ref=inventory_ref,effective_date=when)
    committed=Decimal(str(inventory["reserved"]))
    components=() if committed == 0 else (StockCommitmentComponent(
        commitment_id="SYNTHETIC-RESERVATION",scope=scope,article_id=article,quantity=committed,
        unit=planning["unit"],effective_date=when,source_ref=inventory_ref),)
    availability=calculate_stock_availability(StockAvailabilityInput(context=context,
        stock_on_hand=quantity(inventory["physical"]),stock_committed=quantity(committed),
        committed_components=CollectionEnvelope[StockCommitmentComponent](state="KNOWN",items=components,source_ref=inventory_ref)))
    forecast=AuthorizedForecastRate(scope=scope,article_id=article,daily_demand=Decimal(planning["daily_demand"]),
        unit=planning["unit"],state="KNOWN",forecast_version=VERSION,reference_date=when,
        applicable_from=when,applicable_to=date.fromisoformat(planning["valid_to"]),horizon_ref=ref,source_ref=ref)
    coverage=calculate_coverage(availability,use_authorized_forecast(context,forecast))
    # Coverage only: no parallel purchasing rule, QTG admission or final purchase authority.
    return dict(status=coverage.state,coverage_days=str(coverage.coverage_days) if coverage.coverage_days is not None else None,
                stock_available=str(availability.stock_available),daily_demand=planning["daily_demand"],
                lead_time_days=planning["lead_time_days"],safety_stock=planning["safety_stock"],
                unit=planning["unit"],as_of_date=planning["as_of_date"],valid_to=planning["valid_to"],
                pending_receipts_state=planning["pending_receipts_state"],engine="eios.stock.engine.calculate_coverage",
                material_nature="SYNTHETIC",operational_path="FORBIDDEN",decision_authority=False)


def planning_context(db,dataset,company,articles):
    inventory=read_inventory(db,dataset)
    plans=read_planning(db,dataset)
    return {r["data"]["article_id"]:coverage_for_article(company,dataset,
        inventory.get(r["data"]["article_id"]),plans.get(r["data"]["article_id"])) for r in articles}


def main():
    parser=argparse.ArgumentParser(description="Crear supuestos sintéticos de demanda, entrega y seguridad")
    parser.add_argument("--db",type=Path,required=True)
    parser.add_argument("--dataset-id")
    args=parser.parse_args()
    if not args.db.is_file():
        parser.error("No existe la base documental.")
    dataset=args.dataset_id
    if dataset is None:
        with sqlite3.connect(args.db) as c:
            ids=[r[0] for r in c.execute("SELECT dataset_id FROM documentary_company_snapshot")]
        if len(ids)!=1:
            parser.error("Indica --dataset-id.")
        dataset=ids[0]
    print(json.dumps(create_planning(args.db,dataset),ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
