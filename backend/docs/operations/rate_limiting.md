# Rate limiting

Rate limiting protects sensitive and cost-bearing surfaces without limiting health checks or
ordinary authenticated reads.

## Policy

- `POST /v1/token`: 10 requests per client IP per 60 seconds.
- `POST /v1/users/register`: 5 requests per client IP per 60 seconds.
- `POST /v1/matters/{matter_id}/documents`: 30 requests per client IP per 60 seconds.
- Limits and the window are configurable with `RATE_LIMIT_*` settings.
- Direct backend execution without `RATE_LIMIT_*` variables defaults to disabled and uses an
  application-local memory counter when enabled.
- The repository Compose profile and `.env_examples` enable rate limiting with shared Redis by
  default, including local Docker development. Backend unit tests keep it disabled unless a test
  opts in explicitly.
- Production requires `RATE_LIMIT_STORAGE=redis` when rate limiting is enabled. Redis uses an atomic
  increment/expiry script, so counters are shared across workers.

## Response contract

An exceeded limit returns the normalized error payload with `status=429` and `code=rate_limited`.
The response includes `Retry-After`, `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and
`X-RateLimit-Reset`. No credentials, emails, request bodies, or document data are used in keys or
logs.
