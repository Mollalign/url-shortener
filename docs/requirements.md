# Requirements

## Overview
This document lists the functional and non-functional requirements for the URL shortener service.

## Functional requirements
- Users can submit a long URL and receive a shortened URL.
- Users can resolve a shortened URL and be redirected to the original long URL.
- Optional: Users may provide a custom alias for their shortened URL (e.g. "www.short.ly/my-custom-alias").
- Optional: Users may set an expiration date for a shortened URL.

## Non-functional requirements
- Uniqueness: The system must ensure short codes are unique (one-to-one mapping between short code and long URL).
- Performance: Redirection latency should be low (target: < 100 ms for the redirect operation, p95).
- Reliability & availability: Target availability of 99.99%.
- Scalability: The system must scale to support ~1 billion stored shortened URLs and ~100 million daily active users (DAU).

## Out of scope
- User authentication and account management.
- Click analytics and real-time analytics (e.g., click counts, geographic data) are not required for the MVP.
- Advanced security features such as spam detection or malicious URL filtering.
- Real-time consistency guarantees for analytics pipelines.

## Definitions
- DAU: Daily Active Users.

## Notes
- Where practicality requires, prioritize availability and low-latency redirects over strong consistency for analytics.
