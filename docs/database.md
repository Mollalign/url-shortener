# Database Design

## Overview
The database stores shortened URL mappings and the metadata needed to resolve, expire, and optionally track usage of each short link.

For the MVP, user authentication is out of scope, so user ownership should be treated as optional or future-facing.

## Tables

### urls
Stores each shortened URL and its destination.

| Column | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | UUID / BIGINT | Yes | Primary key for the URL record. |
| `original_url` | TEXT | Yes | Destination URL used during redirect. |
| `short_code` | VARCHAR | Yes | Unique code used in the shortened URL. |
| `created_at` | TIMESTAMP | Yes | Time the short URL was created. |
| `expires_at` | TIMESTAMP | No | Optional expiration time. Expired links should return `410 Gone`. |
| `click_count` | BIGINT | Yes | Total redirect count, if lightweight analytics are enabled. |
| `user_id` | UUID / BIGINT | No | Optional owner reference for future authenticated users. |

### users
Reserved for future user ownership and authenticated workflows.

| Column | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | UUID / BIGINT | Yes | Primary key for a user account. |

## Relationships
- `urls.user_id` may reference `users.id` when account management is added.
- Anonymous URL creation can leave `urls.user_id` as `NULL`.

## Constraints
- `urls.id` should be the primary key.
- `urls.short_code` must be unique.
- `urls.original_url` must not be empty.
- `urls.click_count` should default to `0`.
- `urls.created_at` should default to the current timestamp.

## Indexes
- Unique index on `urls.short_code` for fast redirect lookups.
- Optional index on `urls.expires_at` for cleanup jobs that remove or deactivate expired links.
- Optional index on `urls.user_id` for future user dashboard queries.

## Notes
- Redirect reads should query by `short_code`.
- Expiration should be checked during redirect before returning the original URL.
- Click counting can be eventually consistent if high write volume makes synchronous updates expensive.
