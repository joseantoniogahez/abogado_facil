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

## Commands

- Build with budget gate: `npm --prefix frontend run build`
- Run budget check against existing dist assets: `npm --prefix frontend run perf:check`

## Reviewer Impact Checklist

- Dependency updates include budget impact assessment.
- Route-level or shared UI additions include bundle impact notes when significant.
- Threshold changes in `performance/bundle_budget.json` require explicit reviewer approval and rationale.
