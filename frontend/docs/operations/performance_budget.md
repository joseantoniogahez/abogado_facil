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

- `max_total_js_bytes` is `395000` bytes. PROD-003 adds the authenticated dashboard, API parser,
  route states, and global logout without adding dependencies; the approved production baseline is
  `392774` raw bytes.
- `max_total_js_gzip_bytes` is `117000` bytes. The corresponding approved PROD-003 baseline is
  `116209` gzip bytes.
- The PROD-003 limit adjustment was explicitly authorized on 2026-07-11 and retains `2226` raw
  bytes and `791` gzip bytes of headroom.

## Commands

- Build with budget gate: `npm --prefix frontend run build`
- Run budget check against existing dist assets: `npm --prefix frontend run perf:check`

## Reviewer Impact Checklist

- Dependency updates include budget impact assessment.
- Route-level or shared UI additions include bundle impact notes when significant.
- Threshold changes in `performance/bundle_budget.json` require explicit reviewer approval and rationale.
