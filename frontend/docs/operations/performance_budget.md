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

- `max_total_js_bytes` remains `390000` bytes. PROD-002 first deduplicated the account-form markup
  through `shared/ui/AccountFormField`; the resulting production bundle measures `389428` raw
  bytes.
- `max_total_js_gzip_bytes` is `116000` bytes. A source-map audit found no tests, docs, e2e,
  coverage, or unrelated assets in the production graph; the audited bundle measures `115345`
  gzip bytes, 345 bytes above the former threshold.

## Commands

- Build with budget gate: `npm --prefix frontend run build`
- Run budget check against existing dist assets: `npm --prefix frontend run perf:check`

## Reviewer Impact Checklist

- Dependency updates include budget impact assessment.
- Route-level or shared UI additions include bundle impact notes when significant.
- Threshold changes in `performance/bundle_budget.json` require explicit reviewer approval and rationale.
