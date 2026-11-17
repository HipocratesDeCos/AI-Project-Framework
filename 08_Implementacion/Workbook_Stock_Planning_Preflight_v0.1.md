# Workbook stock planning preflight v0.1

Status: connected to workbook reception and exclusive activation.

`eios.company_workbook_stock_planning.preview(content, filename, cutoff)` reads
the article/inventory sheets mapped in `97_Guia_Carga`, the continuous scenario
block beginning at row 27 of `013_Planificacion_Stock`, and the row-1 table in
`014_Recepciones_Pendientes`. This is an explicit template adapter, not an
automatic mapping for arbitrary worksheets.

It returns `VALIDATED_NOT_ACTIVE`, the exact workbook SHA-256, and synthetic
planning assumptions. It never writes to a database, confirms stock, activates
policy, records supplier acceptance, or authorizes a purchase. Unknown receipts
remain unknown, including when the detail list is empty. Consumers must not
silently turn that state into an acknowledged empty collection.

Inputs must match the SKU, unit, observed inventory date and cutoff from the
same workbook bytes. Fixed scenario inputs are required: formula caches are not
accepted as declared demand. Historical worksheet formulas remain informational.
Validity must span delivery plus target coverage. Receipts are positive, dated
after cutoff and within validity, uniquely referenced and consistent with the
per-article state. Template blocks end at the first physical blank row; additional
multi-cell records beyond that boundary are rejected.

Verification: `python -m unittest tests.test_company_workbook_stock_planning
tests.test_company_purchase_stock_scenario tests.test_company_workbook_reception
-q` (single command, 20 tests). The v03 synthetic workbook was additionally read
by the adapter and exercised through the existing stock scenario calculator.

Integration validates before reception/activation commits and binds the
immutable planning to the selected workbook snapshot, avoid synthetic-plan
fallback for received inventory, preserve saved snapshots and require explicit
acknowledgment before populating purchase stock scenarios. The active route now consumes only planning embedded in that immutable workbook manifest. Legacy books without these sheets keep their previous behavior.


## Integrated behavior

Supplemental sheets are optional as a pair, only for SYNTHETIC material. Invalid
planning produces no reception ticket. Activation re-reads the same immutable
bytes before making any live database change and embeds the validated draft in
its source-bound manifest. Received plans never fall back to older synthetic
planning. A different selected inventory source cannot reuse this plan.

Coverage uses the existing STK engine. The purchase stock panel offers an explicit
“Usar planificación del libro” action only at the inventory cutoff. It copies
assumptions and the applicable receipts, leaves acknowledgment unchecked and
requires review. Other order dates require current stock to be declared. Unknown
receipts cannot be silently copied as a known empty list. Saved study snapshots
and existing purchase records are not updated.

Verification: 37 targeted unittest cases (including inherited workbook regression
cases), plus end-to-end activation of the v03 workbook in an isolated temporary
database (10 FINITE coverages and all 3 receipts). JavaScript syntax checked.
Integration tests cover invalid receipt units, idempotent activation, historical
snapshot preservation, and a subsequent workbook without planning. No local
Microsoft Excel or Chromium execution was available for this change.
