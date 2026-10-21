# Company Proposal Payment Calendar v0.1

## Result
Proposals can explicitly declare up to twenty payments, separating merchandise and buyer freight, with amounts including the supplied VAT and individual due dates. The server requires exact agreement with each declared component total and its final maturity. Dates must be on or after the order, strictly increasing within each component. Pending freight prevents a complete calendar. Discounts and totals reuse company_commercial_terms.

The optional editor does not infer a single payment when omitted. New proposals store NOT_DECLARED or DECLARED_UNVERIFIED. Historical proposals are not backfilled. Payment candidates use the existing CashFlow model with NOT_EVIDENCED, due_date_evidenced=False and no invented source. Their identifiers belong to the proposal and are not company documentary flow identities.

## Boundary
This is capture and validation of the declared costs only. Other costs and schedule completeness are not established. These candidates are not added to the documentary projection, and no finance core, evidence, parameter centre, QTG or operational admission is modified. Matching existing documentary cash flows, documentary support, and the existing documentary capture/review and required calendar contracts remain the next connection. RequiredInstallmentCalendar is not fabricated: its document locators and authority references must be supplied.

No payment is upgraded by user entry or successful arithmetic. No purchase viability, scenario comparison or three alternatives is claimed. Synthetic routes remain FORBIDDEN and decision_authority=False.

## Presentation
The proposal review and printable report show the captured schedule. The commercial draft lists proposed commercial maturities without internal evidence or candidate identifiers. Sending and acceptance remain absent. Dates use DD/MM/YYYY and monetary presentation follows Spanish formatting.

## Validation
Tests cover exact component sums including freight VAT, duplicate or unordered dates, missing costs, invalid values, evidence preservation, persistence, report/draft export and absence of writes to company cash flows. Existing CI checks the full suite and embedded JavaScript syntax. Visual verification remains pending while the local environment is offline.
