# Company Required Calendar Coverage v0.1

New proposals can explicitly conserve order reference, order version and confirmation reference as an optional complete group. They pass unchanged to DOC-PAY-CAP-01; old proposals are not backfilled. These references name supplied documents and do not establish authenticity or authority.

With a captured payment package and explicit references, the user can declare a required calendar, supplying declaration/authority references, actor, total and affirmative acknowledgment after checking the shown installments/supports. The server builds RequiredInstallmentCalendar and calls the existing check_required_installment_coverage. It conserves canonical DOC-PAY-COVER-01 payloads and revision history. The declaration is not an operational mandate or verified authority.

STRUCTURAL_MATCH only means the supplied calendar matches captured associations in the contract's structural scope. Differences remain explicit observations; the original amounts and dates are never rewritten. Required supports must be conserved in the capture and declared total must match the proposal's declared cost total. No evidence upgrade, flow duplication, financial execution, QTG or viability inference occurs on calendar submission.

The UI route uses the proposal's listed schedule and requires supported associations for every displayed installment. The unchanged core contract requires strictly increasing dates across the calendar. Simultaneous maturities are rejected with an explanation; users must not falsify dates to pass. Supporting simultaneous or consolidated maturities is a future contract decision, not silently introduced.

New company reviews v09 and saved reports include the latest coverage for their exact capture, with immutable older reports. Local human findings now label calendar checking as a separate scope instead of asserting NOT_SUPPLIED after a separate calendar declaration exists.

Tests cover explicit reference conservation, canonical structural match, date mismatch, no evidence promotion, missing reference/ack/authority/support/total rejection, stale revision, simultaneous-date rejection, frozen printing and append-only history. HTTP checks use existing token/Host restrictions; CI checks JavaScript syntax, Python and existing SQL Server contracts. Visual verification remains pending while the local environment is offline.
