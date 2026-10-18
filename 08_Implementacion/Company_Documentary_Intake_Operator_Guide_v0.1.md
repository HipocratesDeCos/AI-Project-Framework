# Company documentary intake adapter v0.1

This adapter provides persistent, source-bound intake of **synthetic company
documents**, before a user creates a purchase. It does not construct decisions,
run QTG, approve source quality, authenticate a company, or change analytical
engines. It is a local SQLite documentary store, separate from the existing
SQL Server C0 and parameter schemas. No company-management UI is added.

## Package and command

The ZIP contains `company_manifest.json`, its hash-bound `company_records.json`,
and every source document declared in the manifest. Paths and ZIP membership
are checked; duplicate record/document identities, content corruption, missing
references, mismatched company/cutoff and unknown record kinds fail before a
write transaction. The schema is adapter-specific:
`EIOS-COMPANY-DOCUMENT-DATASET-01/v0.1`. It does not replace any core input
contract or the per-decision 13-component synthetic fixture schema.

From the repository root:

```powershell
python -m eios.company_data load --package "C:\ruta\A_Monkey_Datos_Documentados.zip" --db "C:\ruta\a_monkey_documentary.sqlite3"
python -m eios.company_data inspect --db "C:\ruta\a_monkey_documentary.sqlite3" --dataset-id "<dataset_id returned by load>"
```

The same content produces `UNCHANGED` and no duplicate rows. Changed content
creates another immutable dataset snapshot; the old one is retained. Every read
uses an exact dataset ID. Decimal money is stored as JSON decimal strings and
dates as ISO values, rather than binary SQL floats.

`CompanyDataStore.cash_flows(dataset_id)` reconstructs canonical `CashFlow`
objects. `financial_snapshot(dataset_id)` reconstructs `FinancialSnapshot`.
`records(dataset_id, kind)` retrieves sourced counterparties, invoices, articles,
historical documents and missing-data records. `document(dataset_id, ref)`
retrieves the original bytes. No unreviewed flow is promoted to demonstrated.

## Source and semantic limits

Historical orders are documentary records, not new `PurchaseOperation` objects.
Article catalogue quantities from invoice lines are not stock on hand. Stock
and demand stay null in this version of documentary intake; a later dedicated
source-backed stock intake can extend the adapter explicitly. Unknown
availability, treasury minimum, current offers and sales-SKU mappings stay
unknown. A policy candidate is not a configuration activated in the parameter
centre. Spreadsheet rows retain formulas and existing caches; they are not
silently recalculated by this adapter.

The A Monkey extraction additionally checks line/invoice arithmetic, forecast
totals and documentary references. It preserves different company addresses and
sales descriptions lacking supplier SKU codes instead of choosing fuzzy matches.
Prior stock simulations, proposed purchases and negative authority fixtures are
not part of the company dataset.

## Validation

```powershell
python -m unittest discover -s tests -p test_company_documentary_intake.py -v
```

The tests cover persisted roundtrip and nulls, exact money, repeat-load
idempotence, rejected duplicate identities and corrupt bytes, cross-company
rejection, prevention of prior simulated stock/evidence promotion, and retained
old snapshots. These tests use only standard-library unittest plus existing
Pydantic; no new dependency is required. The full pytest suite is a separate CI
check. Loading documents alone is not operational admission or authority to buy.
