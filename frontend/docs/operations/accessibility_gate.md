# Frontend Accessibility Gate Baseline

This document defines the automated accessibility quality gate for foundation routes.

## Scope

- Landing route (`/`)
- Login route (`/login`)
- Protected error state for session validation failure.
- Selected admin routes, including users, assignments, permissions, and audit log.
- Matter document empty state through a focused component axe test.

## Automation Contract

- Baseline test file: `src/app/accessibility.routes.test.tsx`.
- AI settings initial guided state axe check:
  `src/features/ai-settings/AiSettingsPage.test.tsx`.
- Shared AI notice axe check: `src/shared/ui/AiGeneratedContentNotice.test.tsx`.
- Matter documents empty-state axe check:
  `src/features/matters/matter-documents/MatterDocuments.test.tsx`.
- Engine: `axe-core` running inside the frontend Vitest workflow.
- Violations fail the test suite and therefore fail `npm --prefix frontend run check`.

The AI settings and matter document files also contain behavioral tests for additional states, but
those behavioral assertions are not equivalent to running axe against each state.

## Known Coverage Limits

- `npm --prefix frontend run test:a11y` runs only
  `src/app/accessibility.routes.test.tsx`; the component axe checks above run as part of the full
  Vitest workflow and `npm --prefix frontend run check`.
- The route baseline does not currently run axe against a successfully loaded `/dashboard`.
- The matter document form and populated-list states are behavior-tested, but only the empty state
  receives a focused axe run.
- The AI settings connection success/error, demo, and delete states are behavior-tested, but the
  focused axe run covers the initial guided state only.
- The jsdom axe runs disable the `color-contrast` rule where indicated in their test options. Color
  contrast therefore still requires review in a rendered browser.

## Action Hierarchy Contract

- Shared action variants live in `src/shared/ui/actionStyles.ts` and preserve native link/button
  semantics at each call site.
- Primary, accent, secondary, quiet, destructive, compact, and navigation variants have a
  persistent border, background, or underline cue in addition to color.
- `INLINE_ACTION_CLASS_NAME` is reserved for contextual text links, such as login/registration and
  matter titles, that need the persistent underline cue without the boxed `landing-link` treatment;
  `QUIET_ACTION_CLASS_NAME` retains that base treatment for standalone contextual actions.
- Shared focus, pressed, and disabled rules live in `src/app/styles.css`; disabled controls retain a
  legible label and use background, border, inset shadow, and cursor cues instead of opacity alone.
- RBAC/admin action constants delegate to the shared variants rather than defining a parallel
  visual system.

## Commands

- Focused route-baseline run: `npm --prefix frontend run test:a11y`
- Full workflow, including component axe tests: `npm --prefix frontend run check`

## Reviewer Validation Checklist

- Any UI change on baseline routes keeps `test:a11y` green.
- New UI states include semantic labels/headings and keyboard-safe controls.
- AI-generated result views use `AiGeneratedContentNotice`, associate the result and its actions
  with the notice ID when implemented, and keep the complete contextual warning visible.
- If accepted violations are temporarily allowed, they require explicit reviewer notes and follow-up task ID.

## Maintenance Rule

- When auth/routing error states change, update this gate coverage in the same pull request.
