# SEC-004 - Proteccion contra prompt injection documental

## Tracking Status

- ID: `SEC-004`
- Type: `Backend`
- Priority: `P0-IA`
- Plan status: `Complete`
- Implementation status: `Hecho`
- Last updated: `2026-07-26`
- Backlog source: `docs/product/BACKLOG_ABOGADO_FACIL.md`

## Objective

Impedir que texto recuperado de documentos pueda confundirse con instrucciones confiables o
habilitar acciones: los proveedores deben recibir instrucciones y datos no confiables en canales
separados, con delimitacion explicita y sin herramientas.

## Starting Point

El contexto minimizado esta sellado y delimitado, pero `render()` concatena la instruccion y los
datos en un unico mensaje de usuario. Los adaptadores no ofrecen herramientas hoy, aunque esa
restriccion todavia no forma parte del contrato verificable.

## Scope

### Included

- Separacion estructural entre instruccion confiable y datos documentales no confiables.
- Sobre delimitado comun que declara el contenido como datos y neutraliza instrucciones embebidas.
- Payloads de OpenAI y Gemini sin definiciones de herramientas ni seleccion automatica.
- Gate comun aplicado tambien al proveedor Mock.
- Pruebas negativas con texto documental adversarial y contratos documentales.

### Excluded

- Deteccion heuristica o clasificacion semantica de ataques.
- Agentes, tool calling, navegacion o ejecucion de acciones.
- Funciones IA concretas y revision humana (`LEGAL-002A`).

## Dependencies and Decisions

- Dependencies: `AI-008`, `DOCS-AI-002`.
- Decisions closed: defensa por separacion de canales y ausencia de capacidades, no por listas
  fragiles de frases prohibidas.
- Open questions: none.

## Acceptance Criteria

- [x] Ningun valor de `source_context` se serializa como instruccion confiable.
- [x] OpenAI y Gemini reciben instrucciones y datos no confiables en campos separados.
- [x] Los adaptadores no habilitan herramientas ni aceptan una definicion de herramientas.
- [x] Un documento adversarial permanece escapado dentro del sobre de datos no confiables.
- [x] Logs, metricas y errores siguen sin contener instrucciones o documentos.
- [x] Required documentation is synchronized with delivered behavior.
- [x] Required validation gates pass and are recorded below.
- [x] Mandatory human approvals are recorded, or explicitly not applicable.

## Affected Contracts and Files

| Surface | Expected files or contracts                         | Change required |
| ------- | --------------------------------------------------- | --------------- |
| Runtime | `app/integrations/ai_context.py`, `ai_providers.py` | yes             |
| Tests   | context, provider, provider matrix and docs suites  | yes             |
| Docs    | AI context, threat model, architecture, foundation  | yes             |

## Work Plan

### Implementation

- [x] Separar render de instruccion y datos documentales.
- [x] Adaptar payloads OpenAI/Gemini y mantener herramientas ausentes/deshabilitadas.
- [x] Mantener un unico gate sellado para todos los proveedores.

### Tests and Documentation

- [x] Add or update tests with the behavior change.
- [x] Review all documentation surfaces required by `AGENTS.md`.
- [x] Update canonical documents affected by the code diff.

### Validation

- [x] Targeted AI integration and documentation tests.
- [x] Full backend suite with 100% coverage.
- [x] Pre-commit on all files.

## Progress Log

| Date       | State       | Completed                         | Pending / next safe action |
| ---------- | ----------- | --------------------------------- | -------------------------- |
| 2026-07-26 | En progreso | Alcance y decisiones establecidos | Implementar runtime        |
| 2026-07-26 | Hecho       | Runtime, pruebas y docs validados | Continuar con LEGAL-002A   |

## Validation Results

| Date       | Command                                         | Result | Notes        |
| ---------- | ----------------------------------------------- | ------ | ------------ |
| 2026-07-26 | pruebas focalizadas de integracion y documentos | Passed | 90 passed    |
| 2026-07-26 | `python -m pytest backend/tests`                | Passed | 549 passed   |
| 2026-07-26 | suite completa con `--cov-fail-under=100`       | Passed | 549; 100%    |
| 2026-07-26 | `pre-commit run --all-files`                    | Passed | segundo pase |

## Pause / Handoff Record

- Current state: gate implementado, documentado y validado.
- Changed files and contracts: contexto, payloads de proveedores, pruebas, documentos y tracking.
- Pending work: none.
- Blockers or approvals: none.
- Residual risks: el modelo sigue siendo probabilistico; el control evita autoridad y capacidades,
  no garantiza que todo contenido adversarial sea ignorado semantically.
- Next safe action: continuar con `LEGAL-002A`.

## Completion Documentation Review

- [x] Root and service READMEs reviewed.
- [x] Backend operation and architecture docs reviewed.
- [x] Frontend operation docs and inventories reviewed.
- [x] Foundation status files reviewed and changed only if a foundation contract moved.
- [x] AI governance docs, templates, and checklists reviewed.
- [x] Item plan and summary backlog synchronized.

Record documents intentionally unchanged and why:

- Root/backend README: no setup or public API changed; backend docs index was updated.
- Frontend docs: no frontend route, API consumer or runtime behavior changed.
- AI governance templates: backlog lifecycle and request shapes did not change.

## Completion Summary

- Delivered: trusted/untrusted provider-channel separation, escaped document envelope and no tool
  capability across OpenAI, Gemini and Mock.
- Validation: 90 focused tests; 549 backend tests; 100% application coverage; all pre-commit hooks.
- Skipped validation: none.
- Human approvals: not applicable.
- Residual risk: model output remains probabilistic; `LEGAL-002A` remains required before a
  user-facing document workflow.
