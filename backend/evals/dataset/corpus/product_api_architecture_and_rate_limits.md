# Enterprise API Platform Architecture and Rate Limits (ENG-DOC-501)

## 1. Architecture Overview
The Enterprise API is built on RESTful OpenAPI 3.1 specifications and gRPC microservices deployed on Google Cloud Run and Kubernetes. All endpoints require TLS 1.3 encryption and Bearer JWT authentication tokens issued by our auth server.

## 2. Global Rate Limiting Tiers
Rate limiting is enforced at the Cloud Armor edge and Envoy API Gateway:
- Starter Tier: 100 requests per minute (RPM), burst capacity of 150.
- Business Tier: 1,000 requests per minute (RPM), burst capacity of 1,500.
- Enterprise Tier: 10,000 requests per minute (RPM), burst capacity of 15,000.
When limits are exceeded, the API returns HTTP 429 Too Many Requests along with `Retry-After` and `X-RateLimit-Reset` headers.

## 3. Payload and Timeout Constraints
- Maximum request payload size: 25 MB for standard JSON, 100 MB for multipart upload endpoints.
- Gateway timeout: 30 seconds for synchronous REST calls, 300 seconds for streaming or long-polling endpoints.
- Webhook callbacks must respond with HTTP 2xx within 5 seconds; failing webhooks retry 5 times with exponential backoff over 24 hours.

## 4. Versioning and Deprecation Strategy
API changes follow semantic versioning in URL paths (`/v1/`, `/v2/`). Breaking changes require a minimum 12-month deprecation notice period published in the developer release portal.