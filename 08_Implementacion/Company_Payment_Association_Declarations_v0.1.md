# Local Payment Association Declarations v0.1

## Behaviour
The proposal review allows a local user to declare a binding between an installment and an exact documentary payment candidate, with actor, reason and a document/page/section locator. A binding requires one uniquely conserved source with stored-byte SHA256 and that source must already be linked to the selected documentary flow. The existing DocumentaryLocator and DocumentaryPaymentBinding models validate the declaration. A local statement does not certify the content at that location or the person's identity.

Bindings can be withdrawn using CLEAR. Append-only SQLite company_payment_association_event records revisions, predecessor state through revision ordering, original review, proposal/dataset, matching and documentary fingerprints, actor/reason/time and immutable event fingerprint. Optimistic revision and BEGIN IMMEDIATE prevent lost updates. The same flow cannot be bound to two installments in the same captured proposal context. Cross-proposal duplication remains pending. Changed documents and partial candidate inventories block saving.

## Reporting and boundaries
New reviews v05 capture the current declarations; existing reports remain exact and unchanged. A declaration alone never adds/removes flows or upgrades evidence, performs documentary review, proves inventory/calendar completeness or purchase viability. It does not construct the full documentary payment capture, human review or required installment coverage because their required material/controls have not yet been supplied. Those existing contracts remain the integration boundary; no confirmed findings or authority references are invented.

The commercial draft excludes the internal declarations. The UI describes the scope and blocked prerequisites. Local declaration is not enterprise authentication. Operational path remains FORBIDDEN and decision_authority=False.

## Validation
Tests cover declaration persistence, stale revision, withdrawal/history, source and candidate rejection, scope, changed content, one-flow reuse, unchanged historical printing, HTML escaping, evidence preservation and draft privacy. The HTTP endpoint uses the existing local token and Host restrictions. CI validates Python, embedded JavaScript syntax and existing SQL Server contracts. Visual verification remains pending while the local execution environment is offline.
