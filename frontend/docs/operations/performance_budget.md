# Frontend Performance Budget Contract

This document defines enforceable bundle-size budgets for the frontend foundation.

## Budget Policy Source

- Policy file: `performance/bundle_budget.json`
- Enforcement script: `scripts/performance-budget.mjs`

## Metrics

The gate evaluates production artifacts in `dist/assets`:

- Total JavaScript raw bytes
- Total JavaScript gzip bytes
- Total CSS raw bytes
- Total CSS gzip bytes

## Enforcement Rule

- `npm --prefix frontend run build` must fail when any budget threshold is exceeded.
- Build command runs `npm run perf:check` after Vite production build.

## Current Enforced Thresholds

These values must match `performance/bundle_budget.json` exactly:

| Policy key                 | Bytes    |
| -------------------------- | -------- |
| `max_total_js_bytes`       | `836000` |
| `max_total_js_gzip_bytes`  | `247000` |
| `max_total_css_bytes`      | `32100`  |
| `max_total_css_gzip_bytes` | `9000`   |

## Threshold Rationale

- The prior PROD-003 `max_total_js_bytes` was `395000` bytes. PROD-003 added the authenticated dashboard, API parser,
  route states, and global logout without adding dependencies; the approved production baseline is
  `392774` raw bytes.
- The prior PROD-003 `max_total_js_gzip_bytes` was `117000` bytes. Its approved baseline was
  `116209` gzip bytes.
- The PROD-003 limit adjustment was explicitly authorized on 2026-07-11 and retains `2226` raw
  bytes and `791` gzip bytes of headroom.
- `max_total_js_bytes` is `403000`, `max_total_js_gzip_bytes` is `119000`, and
  `max_total_css_bytes` is `20500` after CORE-001 added the protected client list, search, create,
  detail, edit, and normalized Mexico phone journeys without new dependencies. The measured
  CORE-001 baseline is `400816` raw JS bytes, `118122` gzip JS bytes, and `20244` raw CSS bytes.
- The CORE-001 adjustment was explicitly approved on 2026-07-12 and retains `2184` raw JS bytes,
  `878` gzip JS bytes, and `256` raw CSS bytes of headroom. The CSS gzip limit remains `6000`.
- CORE-002 adds the protected matter list, create, detail, edit, client-context navigation, and
  route-level lazy chunk without new dependencies. Its measured baseline is `410459` total raw JS
  bytes and `121236` total gzip JS bytes.
- The CORE-002 adjustment was explicitly approved on 2026-07-12. The JS limits are now `411000`
  raw bytes and `122000` gzip bytes, retaining `541` raw and `764` gzip bytes of headroom. CSS
  limits remain unchanged.
- The searchable client selector and reassignment confirmation added to CORE-002 measure `412622`
  raw JS bytes and `20855` raw CSS bytes. The owner explicitly approved the minimum follow-up
  adjustment on 2026-07-12: raw JS is `413000` bytes and raw CSS is `21000` bytes, retaining `378`
  and `145` bytes of headroom respectively. Gzip limits remain unchanged.
- CORE-003 adds the embedded matter-note form, deterministic list states, edit/relevance/delete
  controls, and no new dependency. Its measured baseline is `417611` raw JS bytes, `122844` gzip JS
  bytes, `21069` raw CSS bytes, and `5247` gzip CSS bytes.
- The owner explicitly approved the CORE-003 adjustment on 2026-07-12. Limits are now `418000` raw
  JS bytes, `123500` gzip JS bytes, and `21200` raw CSS bytes, retaining `389`, `656`, and `131`
  bytes of headroom respectively. The CSS gzip limit remains `6000`.
- CORE-010 adds multipart document upload, authenticated binary download, metadata listing,
  confirmed deletion, accessible states, and no new dependency. Its measured baseline is `425052`
  total raw JS bytes and `124429` total gzip JS bytes; the matters route remains lazy-loaded.
- On 2026-07-14 the owner explicitly approved doubling the JavaScript limits to provide deliberate
  capacity for the remaining product backlog. Limits are now `836000` raw bytes and `247000` gzip
  bytes. This capacity decision does not waive route-level lazy loading, dependency review, bundle
  impact assessment, or the enforced build gate. CSS limits remain unchanged.
- On 2026-07-18 the owner explicitly approved increasing the raw CSS limit from `21200` to `21400`
  bytes for UX-002. The measured build is `21333` raw CSS bytes, retaining `67` bytes of headroom;
  the CSS gzip limit remains `6000`.
- On 2026-07-24 the owner approved up to a 50% CSS capacity increase to close AI-002. The enforced
  CSS limits moved from `21400` to `32100` raw bytes and from `6000` to `9000` gzip bytes. The
  approval does not waive accessibility review, shared-style reuse, or the build gate.

## Commands

- Build with budget gate: `npm --prefix frontend run build`
- Run budget check against existing dist assets: `npm --prefix frontend run perf:check`

## Reviewer Impact Checklist

- Dependency updates include budget impact assessment.
- Route-level or shared UI additions include bundle impact notes when significant.
- Threshold changes in `performance/bundle_budget.json` require explicit reviewer approval and rationale.
