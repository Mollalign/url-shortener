# API Design

Base URL: https://api.short.ly (example)

Content-Type: application/json

## Endpoints

### POST /urls
Create a shortened URL.

Request body:

```json
{
  "long_url": "https://www.example.com/some/very/long/url",
  "custom_alias": "optional_custom_alias",        // optional, alphanumeric + -/_ allowed
  "expiration_date": "2026-12-31T23:59:59Z"      // optional, ISO 8601 UTC
}
```

Responses:

- 201 Created

```json
{
  "short_url": "https://short.ly/abc123",
  "alias": "abc123",
  "expires_at": "2026-12-31T23:59:59Z"  // null if none
}
```

- 400 Bad Request — invalid URL format, missing `long_url`, or invalid `expiration_date`.
- 409 Conflict — requested `custom_alias` already in use.

Notes:

- If `custom_alias` is omitted, server generates a unique short code.
- Requests should be idempotent per `long_url` + `custom_alias` combination when appropriate.

### GET /{short_code}
Redirect to the original URL.

- 302 Found (or 307 Temporary Redirect) with `Location` header set to the original URL.
- 404 Not Found — short code does not exist.
- 410 Gone — short code existed but has expired or been deleted.

### GET /urls/{short_code}
Retrieve metadata about a short URL (non-redirecting).

Response 200:

```json
{
  "short_url": "https://short.ly/abc123",
  "long_url": "https://www.example.com/some/very/long/url",
  "created_at": "2026-01-01T12:00:00Z",
  "expires_at": null,
  "clicks": 12345   // optional, if analytics available
}
```

### DELETE /urls/{short_code}
Delete or deactivate a short URL. (Typically requires authorization; out of scope for MVP.)

Responses: 204 No Content, 404 Not Found.

### GET /health
Health check endpoint. Responds 200 OK when service is healthy.

## Validation and error format

Errors return a JSON body:

```json
{
  "error": "invalid_request",
  "message": "`long_url` is required and must be a valid URL"
}
```

## Behavioural notes

- Rate limiting: apply per-IP or per-API-key limits to prevent abuse.
- Short-code generation: use a sufficiently large alphabet and length to avoid collisions. Consider collision-resistant IDs (e.g., base62 + time or monotonic counter backed by DB or key-value store).
- TTL / expiration: enforce expiration on redirect and optionally surface `410 Gone`.
- Security: validate `long_url` scheme (allow http/https), and optionally block private IPs.
- Idempotency: creating the same `long_url` without `custom_alias` may return the same short code depending on policy.

## Examples

Create (example):

Request

```http
POST /urls
Content-Type: application/json

{
  "long_url": "https://www.example.com/some/very/long/url",
  "custom_alias": "my-link",
  "expiration_date": "2026-12-31T23:59:59Z"
}
```

Response (201)

```json
{
  "short_url": "https://short.ly/my-link",
  "alias": "my-link",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

Redirect (example):

Request: `GET /my-link`

Response: 302 Found, Location: `https://www.example.com/some/very/long/url`

## Open questions

- Authorization model for deletion or private links.
- Analytics endpoint design (if needed later).

