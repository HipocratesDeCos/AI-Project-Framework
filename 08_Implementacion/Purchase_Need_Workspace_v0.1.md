# Purchase need workspace v0.1

Step 2 follows the supplied two-column reference: existing inputs, references,
stock/demand/receipt assumptions, declaration and short result on the left;
lettered explanation and comparison on the right. Bricolage Grotesque is reused
for headings and highlighted quantities, IBM Plex Sans for body and controls,
with tabular figures. The full width is available in this step; the separate
finance sidebar remains available in the other steps. Narrow screens stack
columns. Both appearance modes are supported.

All original controls, identifiers and event handlers are retained. Loading a
workbook or copying a saved study leaves acknowledgment unchecked. Disabled,
unacknowledged, changed or invalid assumptions clear the live calculation.
Saved-study navigation hides the complete editor; no historic result is rebuilt
from today's inputs.

The authenticated read-only `/api/purchases/stock-preview` route validates active
dataset, documentary fingerprint and synthetic material before calling the
existing stock scenario calculator. It needs neither prices nor finance-policy
activation, because it makes no financial assessment or database write.

`company_purchase_need_explanation.explain` reads the calculator's timeline,
target and fingerprint. It never changes the target. Aggregate consumption and
receipts are educational subtotals; the actual net need is the maximum safety
gap from reception to horizon end. Late receipts can make that larger than the
aggregate difference. The UI identifies this explicitly. The comparison includes
both end stock and the minimum after reception. Pre-delivery shortfall is never
repaired by adding a purchase on a later date. The engine checks closing dates
strictly before arrival; stock immediately before purchase on the arrival date
can differ (30 vs 25 in the supplied example). No intraday availability is claimed.

The reference example produces target 100, current 400, final stocks 25 and 325
and surplus quantity 300. Tests also cover late receipts, zero demand, same-day
delivery, immutable source, stale fingerprint and missing acknowledgment.
HTTP+DOM verifies book loading, retained fields and invalidation. Chromium
verification covers the reference example, desktop two columns, light/dark,
390px overflow and invalidation. The stock engine, finance criteria and purchase
authority boundaries remain unchanged.
