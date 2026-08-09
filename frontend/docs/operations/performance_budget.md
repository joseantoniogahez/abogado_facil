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

The gate mechanism is reusable foundation behavior, while the current byte values and their
approvals are specific to ABOGADO_FACIL. A new application must establish its own measured baseline
instead of inheriting the product's historical headroom without review.

Product-specific measurements, approvals, and delivery context remain in the implemented plans:

- [PROD-003 dashboard](../../../docs/product/plans/implemented/PROD-003_DASHBOARD_PLAN.md)
- [CORE-001 clients](../../../docs/product/plans/implemented/CORE-001_GESTION_CLIENTES_PLAN.md)
- [CORE-002 matters](../../../docs/product/plans/implemented/CORE-002_GESTION_ASUNTOS_PLAN.md)
- [CORE-003 matter notes](../../../docs/product/plans/implemented/CORE-003_NOTAS_EXPEDIENTE_PLAN.md)
- [CORE-010 matter documents](../../../docs/product/plans/implemented/CORE-010_INTERFAZ_DOCUMENTOS_EXPEDIENTE_PLAN.md)
- [UX-002 matter tabs](../../../docs/product/plans/implemented/UX-002_TABS_DETALLE_ASUNTOS_PLAN.md)
- [AI-002 AI settings](../../../docs/product/plans/implemented/AI-002_PANTALLA_CONFIGURACION_IA_PLAN.md)

The current product thresholds remain enforceable until an explicitly reviewed change updates
`performance/bundle_budget.json`, this table, and the relevant product plan together. Capacity does
not waive route-level lazy loading, dependency review, accessibility review, bundle impact
assessment, or the build gate.

## Commands

- Build with budget gate: `npm --prefix frontend run build`
- Run budget check against existing dist assets: `npm --prefix frontend run perf:check`

## Reviewer Impact Checklist

- Dependency updates include budget impact assessment.
- Route-level or shared UI additions include bundle impact notes when significant.
- Threshold changes in `performance/bundle_budget.json` require explicit reviewer approval and rationale.
