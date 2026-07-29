# Domain Error -> HTTP Status

For implementation rules and extension workflows, see `../backend_playbook.md`.

## Standard Error Payload

Backend exception handlers return a normalized payload:

```json
{
  "detail": "Human-readable message",
  "status": 400,
  "code": "invalid_input",
  "meta": {},
  "request_id": "a3d5a4c8f1f54c2dbf4d0b7f95b29662"
}
```

Notes:

- `meta` is optional and only appears when extra context is available.
- `request_id` is always included in normalized error payloads.
- The same value is also returned in the `X-Request-ID` response header.
- Safe incoming `X-Request-ID` values are preserved. Empty, longer than 100 characters, or values
  outside letters, digits, `.`, `_`, `:`, and `-` are replaced with an opaque generated ID to
  prevent log injection.
- `401` responses include `WWW-Authenticate: Bearer`.
- Rate-limited responses use `429 rate_limited`, include `Retry-After`, and expose only numeric quota headers.
- FastAPI request validation errors are converted to `400 invalid_input`.
- API request completion logs include a consistent structured shape with `request_id`, `method`, `path`, `status_code`, and `duration_ms`.
- Authorization decisions are logged as `event=api_authorization_decision` with `request_id`, `user_id`, `permission_id`, `required_scope`, `decision`, `method`, `path`, and `route`.
- Future AI SSE provider failures use the transport-level `error` event with `code=provider_error`; provider exception details are not returned or logged.
- Provider adapters classify failures with the closed catalog in `ai_provider_errors.md`. Future
  product endpoints may expose only its stable code, constant public message, and retry decision;
  provider-controlled details remain outside the HTTP contract.
- BYOK credential validation failures use `400 invalid_input`; missing credentials use `404 not_found`.
  Corrupt or tampered AES-GCM credentials are treated as invalid input before any provider is built.

Example of normalized validation error:

```json
{
  "detail": "Request validation error",
  "status": 400,
  "code": "invalid_input",
  "request_id": "a3d5a4c8f1f54c2dbf4d0b7f95b29662",
  "meta": [
    {
      "loc": ["body", "username"],
      "msg": "Field required"
    }
  ]
}
```

For `POST /v1/token`, `username` in validation locations is the OAuth2 password-form wire field. Its
value is the account email; the product has no separate username identity.

## Domain Error Code Mapping

| Domain Error Code                | HTTP Status                 |
| -------------------------------- | --------------------------- |
| `invalid_input`                  | `400 Bad Request`           |
| `unauthorized`                   | `401 Unauthorized`          |
| `forbidden`                      | `403 Forbidden`             |
| `not_found`                      | `404 Not Found`             |
| `conflict`                       | `409 Conflict`              |
| `internal_error`                 | `500 Internal Server Error` |
| `rate_limited`                   | `429 Too Many Requests`     |
| `provider_authentication_failed` | `400 Bad Request`           |
| `provider_timeout`               | `504 Gateway Timeout`       |
| `provider_unavailable`           | `503 Service Unavailable`   |
| `provider_request_rejected`      | `400 Bad Request`           |
| `provider_invalid_response`      | `502 Bad Gateway`           |
| `provider_configuration_error`   | `500 Internal Server Error` |

The synchronous AI-assistance endpoint maps every normalized provider failure to this safe public
contract. Provider messages and response bodies are never exposed. A provider credential failure
uses `400` because it concerns the caller's configured BYOK credential rather than authentication
with this API.

Matter document uploads use `400 invalid_input` for unsupported, empty, oversized, or content-mismatched
files; `409 conflict` when the per-matter quota is reached; opaque `404 not_found` for missing or foreign
matters/documents; and `500 internal_error` for object-storage failures without provider details.
