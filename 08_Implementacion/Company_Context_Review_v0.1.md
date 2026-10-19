# Saved-proposal context review v0.1

`PurchaseDesk.review(dataset_id, proposal_id)` adds a dated descriptive review to an existing saved proposal. It is not an assessment from Rules, CRC, PRICE or the Decisor, and does not admit operational evidence. The UI action is **Revisar**, with the visible conclusion **REVISIÓN PARCIAL · EVALUACIÓN COMPLETA PENDIENTE** and an explanation immediately below it.

The server loads the proposal from the selected dataset; the client cannot submit replacement amounts or historical facts. Price comparison uses the unique latest documented invoice line no later than both the documentary cutoff and the proposed order date. Ties and incompatible currency/unit/net price remain unavailable. The net unit delta and percentage are descriptive and apply no purchasing thresholds.

Inventory is shown as dated synthetic context, never current stock. A future inventory snapshot is excluded for a past order. Existing canonical STK coverage is reused from `company_planning`, retaining its date and forecast horizon. An order beyond that horizon is explicitly flagged; no projected inventory or recommended purchase quantity is calculated.

The review freezes the original proposal, selected invoice and source references, inventory and coverage context, version and pending checks. A deterministic SHA-256 `review_id` identifies the content. `manual_purchase_context_review` stores immutable review payloads; repeating identical inputs returns the original report and timestamp. A changed context creates a different review. The proposal remains pending evaluation. No purchase, stock movement or cash movement is generated.

`POST /api/purchases/review` uses the existing session token and request-size protections. The lookup is scoped by dataset and proposal ID. All report data is rendered with `textContent`. Navigation/dataset changes invalidate in-flight review display to avoid showing a result under a different context.

Financial evaluation, freight/other costs, full payment conditions, stock freshness, pending receipts and Decisor integration remain pending. `decision_authority=false`, material `SYNTHETIC` and operational path `FORBIDDEN` are retained.

Validation covers exact arithmetic, tied/incompatible references, future-evidence exclusion, expired forecast indication, version isolation, idempotent persistence, original-proposal preservation, JavaScript syntax, and DOM interaction with the real HTTP endpoint on a disposable company database. Pixel-level rendering is not established by DOM tests.
