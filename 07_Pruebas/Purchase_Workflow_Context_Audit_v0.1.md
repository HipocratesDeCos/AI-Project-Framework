# Purchase workflow: context audit

## Scope

Audit of saved-study review, explicit study-to-draft copying, negotiation,
installments, agreement records and printable reports. Synthetic fixtures only.

## Reproduced defects and corrections

1. A delayed review response replaced the visible draft after the user edited
   quantity. Reviews now require the same company, request and edit generation
   before rendering. Older failed reviews cannot overwrite a newer notice.
2. Selecting another study during either animation-frame pause in draft copying
   let the old copy resume and replace that selection. Every asynchronous copying
   boundary now checks ownership of the company, study and edit generation.
   Hydration cleanup belongs to its own request; real user edits invalidate it.

Both failures were reproduced in a real browser before correction. No saved
proposal was changed by these failures or by the corrections.

## Validation

- `tests/browser/purchase_context_audit.cjs`: delayed review plus both copy
  hydration phases pass; selected study and edited quantity remain intact,
  no copied lineage leaks and only one alternatives block remains visible.
- `tests/browser/purchase_study_to_draft.cjs`: complete copy, fresh stock
  acknowledgment, alternative recalculation, installments and real save pass;
  lineage is recorded and the original remains unchanged.
- 46 unittest cases pass across scope audit, draft, agreement, cash preview,
  negotiation, payment plan and proposal report modules.
- New scope tests use identical supplier, article and reference identifiers in
  two companies: foreign review, draft source, cash context and report access
  are rejected, without adding proposals.

These checks verify the tested flows and isolation rules. They do not authorize
a purchase, verify supplier acceptance or post a payment. The changes remain on
the draft pull request; production/main is unchanged.
