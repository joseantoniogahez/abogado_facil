# Clients Frontend Scaffold Checklist

- [ ] Read `AGENTS.md`.
- [ ] Read `frontend/docs/frontend_playbook.md`.
- [ ] Confirm route, API, auth, state, UX, a11y, observability, performance, and validation impact.
- [ ] Import `ClientsPage` in `frontend/src/app/routes.tsx` when the route is ready.
- [ ] Add route path `/clients` in `frontend/src/app/routes.tsx` with the right guard.
- [ ] Add user-facing text keys to `frontend/src/shared/i18n/ui-text.ts`.
- [ ] Update `frontend/docs/operations/route_inventory.md` when route behavior changes.
- [ ] Update `frontend/docs/operations/api_consumer_matrix.md` when API consumers change.
- [ ] Update `frontend/docs/operations/e2e_smoke_suite.md` when auth/routing/error journeys change.
- [ ] Add page, route guard, API consumer, a11y, and e2e tests as applicable.
- [ ] Run `npm --prefix frontend run check`.
- [ ] Run `npm --prefix frontend run test:e2e:ci` when auth, routing, or error journeys change.
- [ ] Run `npm --prefix frontend run build`.

Suggested route import:

```tsx
import { ClientsPage } from "@/features/clients/ClientsPage";
```
