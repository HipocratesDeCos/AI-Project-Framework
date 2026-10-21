# Local Declared Payment Coverage v0.1

New reviews v06 capture coverage of local installment association declarations: installment count, associated/pending counts and monetary totals, withdrawn declarations and cross-proposal conflicts. The summary is available on screen and in the exact saved printable report.

ALL_INSTALLMENTS_DECLARED_NOT_REVIEWED means only that each listed installment has a non-conflicting local declaration. It does not certify documents, required calendar coverage, completeness of costs, treasury reconciliation or viability. The existing required_installment_coverage contract remains NOT_EXECUTED until its complete inputs are supplied. No payment is added or removed, and no evidence state is upgraded.

The binding endpoint now rejects a flow already associated by another proposal in the same dataset and exact documentary content. The current state is derived from append-only events, with the latest event for each proposal/installment; CLEAR releases the local declaration. The check runs within the same BEGIN IMMEDIATE transaction as saving. It does not claim duplicate detection across datasets, versions, companies or documentary fingerprints.

The read projection uses one SQLite read transaction for a consistent event inventory. Association payload schema is COMPANY-PAYMENT-DECLARED-ASSOCIATIONS-02; historical events remain unchanged. Current reports include the summary within their normal content fingerprint.

Tests cover pending/full/withdrawn coverage and amounts, cross-proposal rejection and release, scoped lookup and frozen printing, along with existing association validation and evidence-preservation tests. CI includes Python, embedded JavaScript syntax and SQL Server contracts. Visual verification remains pending while the local execution environment is disconnected.
