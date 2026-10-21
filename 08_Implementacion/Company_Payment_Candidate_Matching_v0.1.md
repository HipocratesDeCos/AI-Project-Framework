# Company Payment Candidate Matching v0.1

The saved review now compares explicitly declared proposal installments with canonical PAYMENT records from the selected documentary dataset. It lists every exact amount/currency/due-date coincidence, preserves evidence states and documentary references, and flags candidates shared by more than one installment. Collections are never candidates.

This is not association, duplicate confirmation, supplier/invoice matching, reconciliation or evidence review. A unique coincidence does not prove membership; no coincidence does not establish a new payment. Candidate flows are not appended, removed, substituted or upgraded. The documentary finance execution remains unchanged.

Invalid identities, invalid canonical records, duplicate flow IDs and a mismatch with the recorded inventory count produce PARTIAL_INVENTORY with explicit issues. Duplicate identities are excluded. Even CANDIDATES_LISTED never claims inventory completeness. The report preserves the matching payload and fingerprint in COMPANY-CONTEXT-REVIEW-04, before its overall review hash is computed. Printing reads that exact saved review; previous reports are not regenerated. The commercial draft does not include this internal audit.

The next stage remains explicit documentary association with support, required calendar coverage, and reviewed duplicate controls using the existing contracts. No documentary locator, authority or confirmed finding is fabricated. Synthetic operational routes remain FORBIDDEN and decision_authority=False.

Tests cover unique, ambiguous, absent and shared candidates; wrong flow type/currency/date/amount; invalid and duplicate inventory; scope isolation; evidence preservation; immutable printing; no writes to documentary flows; no internal candidate audit in commercial drafts. Full CI includes embedded JavaScript syntax checks. Visual verification remains pending while the local environment is offline.
