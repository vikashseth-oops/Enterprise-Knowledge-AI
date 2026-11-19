# SOC 2 Type II Security Controls and Audit Framework (CMP-STD-502)

## 1. Scope of Trust Services Criteria
Our annual SOC 2 Type II assessment audits the Security, Availability, and Confidentiality trust services criteria administered by independent AICPA-accredited auditors.

## 2. Access Management Controls
- Principle of Least Privilege: Access permissions to production AWS/GCP cloud environments are role-based (RBAC) and granted via Just-In-Time (JIT) ephemeral access expiring within 8 hours.
- Quarterly Access Reviews: Managers must review and re-certify user access lists every quarter. Any dormant accounts inactive for 60 days are automatically disabled.

## 3. Change Management and CI/CD Verification
All code changes to production systems must:
- Pass automated unit, lint, and security vulnerability scans (SAST/DAST) in GitHub Actions.
- Require at least one independent peer review and approval from a code owner.
- Direct pushes or unauthorized bypasses of protected `main` branches are cryptographically prevented.

## 4. Vulnerability Management SLAs
Critical vulnerabilities (CVSS score 9.0 - 10.0) must be remediated or mitigated within 7 business days. High vulnerabilities (CVSS score 7.0 - 8.9) must be patched within 30 calendar days.