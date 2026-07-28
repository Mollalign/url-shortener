# Architecture

## Overview
The URL shortener service accepts long URLs, generates unique short codes, and redirects users from short links to the original destinations.

The architecture prioritizes low-latency redirects, high availability, and horizontal scalability. For the MVP, user accounts, advanced abuse detection, and real-time analytics are out of scope.

## High-Level Components

```text
Client
  |
  v
Load Balancer / API Gateway
  |
  v
Application Service
  |
  +--> Cache
  |
  +--> Primary Database
  |
  +--> Async Queue / Analytics Worker
```

## Components

### Client
Sends API requests to create short URLs and follows redirects from short codes.

### Load Balancer / API Gateway
- Routes traffic across application instances.
- Applies rate limiting and request size limits.
- Terminates TLS.

### Application Service
- Validates incoming URLs.
- Generates unique short codes.
- Stores URL mappings.
- Resolves short codes during redirect requests.
- Enforces expiration rules.

### Cache
- Stores hot `short_code` to `original_url` mappings.
- Reduces database reads for high-traffic redirects.
- Uses TTLs so expired links are not cached indefinitely.

### Primary Database
- Stores durable URL mappings and metadata.
- Enforces uniqueness for `short_code`.
- Supports lookup by `short_code` for redirects.

### Async Queue / Analytics Worker
- Optional for MVP.
- Handles click counting or analytics updates without slowing redirect responses.
- Can batch writes to reduce database pressure.

## Core Flows

### Create Short URL
1. Client sends `POST /urls` with `long_url`, optional `custom_alias`, and optional `expiration_date`.
2. Application validates the URL and expiration date.
3. If a custom alias is provided, the application checks uniqueness.
4. If no alias is provided, the application generates a unique short code.
5. Application stores the mapping in the database.
6. Application returns the full short URL to the client.

### Redirect Short URL
1. Client requests `GET /{short_code}`.
2. Application checks the cache for the short code.
3. On cache miss, application reads from the database.
4. Application checks whether the URL exists and has not expired.
5. Application returns a redirect response with the original URL.
6. Click counting can be sent to an async queue.

### Expiration
- Expiration is enforced during redirect.
- Expired links should return `410 Gone`.
- A background cleanup job can remove or deactivate expired rows later.

## Data Model
The primary table is `urls`, which stores:

- `id`
- `original_url`
- `short_code`
- `created_at`
- `expires_at`
- `click_count`
- `user_id`

See [Database Design](database.md) for the full schema.

## Short Code Generation
- Use a large alphabet such as Base62.
- Keep generated codes long enough to avoid collisions at the expected scale.
- Enforce uniqueness with a database constraint.
- On collision, generate a new code and retry.

Possible approaches:

- Random Base62 codes.
- Monotonic ID encoded as Base62.
- Distributed ID generator encoded as Base62.

## Scaling Strategy

### Application Layer
- Run multiple stateless application instances.
- Scale horizontally behind a load balancer.

### Cache Layer
- Cache popular redirects.
- Use cache-aside reads: check cache first, then database, then populate cache.
- Keep cache TTL aligned with URL expiration.

### Database Layer
- Index `short_code` for fast lookup.
- Partition or shard by `short_code` if data grows beyond a single database.
- Use read replicas for metadata reads if needed.

## Consistency
- Short-code uniqueness requires strong consistency at write time.
- Redirects should favor availability and low latency.
- Click counts and analytics can be eventually consistent.

## Reliability
- Health checks should be exposed through `GET /health`.
- Application instances should be stateless and replaceable.
- Database backups and replication are required for durable URL mappings.
- Cache loss should not break redirects because the database remains the source of truth.

## Security
- Allow only safe URL schemes such as `http` and `https`.
- Rate limit URL creation and redirect traffic.
- Consider blocking private IP ranges and internal hostnames to reduce SSRF risk.
- Validate custom aliases to prevent unsafe characters.

## Open Questions
- Should generated short codes be random or derived from a distributed ID?
- Should anonymous duplicate long URLs return the same short code or create new mappings?
- What analytics data should be captured beyond basic click counts?
- When user accounts are added, what authorization rules apply to updates and deletion?
