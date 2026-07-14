# Frontend Accessibility Gate Baseline

This document defines the automated accessibility quality gate for foundation routes.

## Scope

- Landing route (`/`)
- Login route (`/login`)
- Dashboard (`/dashboard`) and protected error state for session validation failure.
- Selected admin routes, including users, assignments, permissions, and audit log.
- Matter document empty/form/list states through the focused component axe test.

## Automation Contract

- Baseline test file: `src/app/accessibility.routes.test.tsx`.
- Shared AI notice test: `src/shared/ui/AiGeneratedContentNotice.test.tsx`.
- Matter documents test: `src/features/matters/matter-documents/MatterDocuments.test.tsx`.
- Engine: `axe-core` running inside the frontend Vitest workflow.
- Violations fail the test suite and therefore fail `npm --prefix frontend run check`.

## Commands

- Focused run: `npm --prefix frontend run test:a11y`
- Standard workflow run: `npm --prefix frontend run check`

## Reviewer Validation Checklist

- Any UI change on baseline routes keeps `test:a11y` green.
- New UI states include semantic labels/headings and keyboard-safe controls.
- AI-generated result views use `AiGeneratedContentNotice`, associate the result and its actions
  with the notice ID when implemented, and keep the complete contextual warning visible.
- If accepted violations are temporarily allowed, they require explicit reviewer notes and follow-up task ID.

## Maintenance Rule

- When auth/routing error states change, update this gate coverage in the same pull request.
