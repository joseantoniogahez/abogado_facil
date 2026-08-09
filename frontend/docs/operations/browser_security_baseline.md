# Frontend Browser Security Baseline

This document defines the minimum browser-security policy contract required for frontend delivery.

## Required Baseline Policies

| Policy                        | Enforceable Mechanism                                           | Required Value/Intent                                                                                                         |
| ----------------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Content Security Policy (CSP) | CSP response header or supported CSP directives in `index.html` | Restrict sources to self plus reviewed allowances. Meta-delivered CSP cannot enforce `frame-ancestors`.                       |
| Framing protection            | CSP response header                                             | Send `frame-ancestors 'none'` (and a compatible `X-Frame-Options` fallback when required) to deny embedding.                  |
| Referrer Policy               | `meta[name="referrer"]` in `index.html` or response header      | `strict-origin-when-cross-origin`.                                                                                            |
| Permissions Policy            | `Permissions-Policy` response header                            | Disable geolocation, microphone, and camera by default. A `meta[http-equiv="Permissions-Policy"]` is not an enforcement path. |

## Current Repository Gap

- `frontend/index.html` contains a CSP meta element, but its `frame-ancestors 'none'` directive is
  ignored when CSP is delivered through `meta`; it therefore does not prove framing protection.
- `frontend/index.html` also contains `meta[http-equiv="Permissions-Policy"]`, but Permissions
  Policy is delivered by response header (or by an `iframe` `allow` attribute for embedded
  documents), not by that meta element.
- The repository production image serves static files with `serve` and contains no checked-in
  response-header configuration for either policy. An external proxy or platform may add headers,
  but no such deployment evidence exists in this repository.
- `src/contracts/browser-security.contract.test.ts` checks markup presence only. It does not prove
  that a browser receives or enforces the required response headers.

Until deployment headers and an enforcement-level check are added, framing protection and the
Permissions Policy baseline are documented security gaps, not active guarantees.

## Ownership and Enforcement

- Frontend owns supported policy markup and contract tests.
- Deployment owners must send response headers that meet or exceed this baseline.
- Route/script-loading changes must not remove or weaken this baseline without explicit review.

## Validation References

- Contract tests: `src/contracts/browser-security.contract.test.ts`
- Artifact under contract: `frontend/index.html`
- CSP meta limitations: <https://www.w3.org/TR/CSP3/#meta-element>
- Permissions Policy delivery: <https://www.w3.org/TR/permissions-policy/#permissions-policy-http-header-field>
