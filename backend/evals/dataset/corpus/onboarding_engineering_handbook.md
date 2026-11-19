# Software Engineering Onboarding and Standards Handbook (ENG-HDB-001)

## 1. First Week Milestones
- Day 1: Laptop setup, Okta SSO provisioning, 1Password vault invite, Slack setup.
- Day 2: Development environment configuration using Docker Compose and local dev containers.
- Day 3: First pull request (PR) submitted to staging environment (typically documentation or test improvement).
- Day 5: First production deployment completed with assigned engineering buddy shadowing.

## 2. Git Workflow and Branching Strategy
We practice trunk-based development with short-lived feature branches (`feat/JIRA-123-description`, `fix/JIRA-456-bug`). Feature flags (LaunchDarkly) must be utilized for any significant feature rollout to enable dark launches and instant rollbacks.

## 3. Testing Standards and Coverage
Every service must maintain a minimum test coverage of 80% on core business logic modules. Automated PR checks will fail if coverage decreases by more than 1% or if any unit/integration test fails.

## 4. Code Review Etiquette
Pull requests should remain small (<400 lines of code changed). Reviewers are expected to review assigned PRs within 4 business hours. Comments should be categorized using standard conventional prefixes: `[blocking]`, `[suggestion]`, or `[nit]`.