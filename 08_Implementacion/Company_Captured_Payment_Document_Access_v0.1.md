# Captured Payment Document Access v0.1

The proposal review now offers downloads for each document listed in its payment capture summary. The document endpoint resolves the exact saved review, then the capture in its dataset/proposal scope. It verifies the canonical capture fingerprint, embedded finance package fingerprint and input, operation identity, document association and byte SHA256 against the proposal's saved documentary context.

It reads only conserved capture bytes. Missing or damaged captures fail explicitly; current documentary_source is never used as a fallback. Replacing or deleting source files therefore cannot silently change a historical download. File names come from the saved context when available, stripped of paths and control characters, with a deterministic .bin fallback. This does not infer an original file extension.

POST /api/purchases/payments/document uses the existing local session token and Host restrictions. Responses are attachments with application/octet-stream, nosniff, no-store and byte hash. Raw documents are not rendered as active HTML in the app. The printable report lists document references and hashes; this list does not confirm document validity or complete review.

The change is additive within review v07: new summaries list document_ref, SHA256 and byte count. Existing captures and old saved reports remain unchanged. Older summaries without document lists still work through the scoped endpoint when the reference is supplied; the new download buttons appear after a new review.

Tests cover exact bytes after current-source deletion, scope, missing capture, altered payload rejection, filename hygiene and a real local HTTP download including token, attachment, cache and hash headers. Full CI includes JavaScript syntax and existing SQL Server contracts. Visual verification remains pending while the execution environment is offline.
