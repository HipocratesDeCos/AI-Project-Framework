# Company Financial Quality Material Preparation v0.1

New reviews v10 can prepare the existing QTG-FIN-PREP-01/v0.1 material using their exact documentary capture, required calendar/coverage and optional human findings. The user explicitly supplies criterion reference, version and UTF-8 text, actor and acknowledgment. No criterion, authorization or designation is generated or inferred. The UI accepts one criterion; the API permits up to five with 8,000 total content bytes.

The service reconstructs the canonical capture through the existing public factories and real read-only Centre ports, reproduces the required coverage and any supplied human review, and checks their fingerprints before calling build_finance_quality_preparation. Differences and negative findings remain preserved; preparing material is not quality evaluation or admission. If no human review exists it remains null, and reviewer designation always remains null.

Append-only company_finance_quality_preparation rows conserve canonical payloads and revisions. Optimistic revision and a write transaction reject changed calendar/review anchors. New reports identify an earlier preparation when its dependency fingerprints no longer match, rather than silently promoting it. Exact historical print remains unchanged and commercial drafts exclude criteria and internal preparation details.

The screen explicitly leaves reviewer designation, contextual treasury support and quality evaluation pending. Finance Basic input/evidence, Rules, QTG, operational admission and purchase viability remain unchanged. No rule/core contracts are modified.

Validation covers canonical criteria bytes, dependency binding, optional review, differences without promotion, stale revisions/anchors, history, frozen reporting, draft privacy and HTTP token checks. Full Python CI and existing SQL Server checks remain required. Local execution is available again; visual verification is recorded separately after inspection.

Local validation: 32 focused unittest checks and the full pytest suite (2,693 passed) completed. A cloud-browser attempt to reach the loopback-only fixture server returned ERR_CONNECTION_REFUSED; visual QA remains pending. No public exposure or alternate network route was introduced.
