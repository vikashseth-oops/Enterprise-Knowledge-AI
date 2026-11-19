from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parent / "dataset" / "corpus"
QUERIES_FILE = Path(__file__).resolve().parent / "dataset" / "queries.jsonl"

DOCUMENTS = {
    "hr_remote_work_policy.md": """# Enterprise Remote Work Policy (HR-POL-042)

## 1. Overview and Eligibility
Enterprise Knowledge Corp supports flexible and hybrid working environments. Full-time employees who have completed their 90-day probationary period and maintain a 'Meets Expectations' or higher performance rating are eligible to request hybrid or full remote arrangements with managerial and HR approval.

## 2. Core Working Hours and Availability
All remote employees must be accessible on official communication channels (Slack, Microsoft Teams, Email) during core business hours from 10:00 AM to 4:00 PM in their designated primary time zone. A minimum 30-minute advance notice in the team channel is required for planned temporary midday absences.

## 3. Home Office Equipment Stipend
Eligible remote employees receive a one-time home office setup stipend of $1,000 USD upon hire or transition to full remote status. This stipend covers ergonomic chairs, external monitors, docking stations, and standing desks. Receipts must be submitted through the Expensify portal within 60 calendar days of expense occurrence.

## 4. Internet and Utility Reimbursement
Remote team members are eligible for a monthly internet connectivity subsidy of up to $75 USD. To qualify, internet service must provide minimum speeds of 50 Mbps download and 10 Mbps upload to ensure seamless video conferencing.

## 5. Ergonomic and Workspace Safety Requirements
Employees must maintain a designated, secure workspace compliant with company ergonomic guidelines. Annual self-certification of workspace safety is mandatory via the Workday HR portal each November.
""",
    "hr_leave_and_vacation_policy.md": """# Comprehensive Employee Leave and Time-Off Policy (HR-POL-018)

## 1. Paid Time Off (PTO) Accrual
Full-time permanent employees accrue Paid Time Off based on tenure:
- 0 to 2 years: 18 days annually (1.5 days per month)
- 3 to 5 years: 22 days annually (1.83 days per month)
- 5+ years: 26 days annually (2.16 days per month)
PTO accrual runs on the 1st of each calendar month. A maximum of 5 unused PTO days may roll over into the following calendar year; unused days beyond 5 expire on March 31st.

## 2. Sick and Wellness Leave
Employees receive 10 paid sick days per calendar year, front-loaded on January 1st. Sick leave covers personal illness, medical appointments, and caring for immediate family members. Absences exceeding three consecutive business days require a licensed physician note submitted to HR.

## 3. Parental and Family Bonding Leave
Enterprise Knowledge Corp provides 16 consecutive weeks of fully paid Parental Leave for all new parents (birth, adoption, or foster placement) regardless of gender. Parental leave must be taken within 12 months following the child's birth or arrival.

## 4. Bereavement Leave
Employees are entitled to 5 paid days for immediate family members (spouse, child, parent, sibling) and 3 paid days for extended family members (grandparents, in-laws). Additional unpaid leave may be requested.

## 5. Jury Duty and Civic Leave
Up to 10 business days of paid leave are granted for employees summoned to jury duty. Court attendance verification documentation must be presented to People Operations.
""",
    "it_password_and_auth_policy.md": """# IT Security Password and Multi-Factor Authentication Policy (SEC-POL-101)

## 1. Password Complexity Requirements
All corporate directory passwords must contain:
- Minimum of 14 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one numeric digit (0-9)
- At least one approved special symbol (!@#$%^&*()_+-=)
Passwords cannot match any of the last 10 previously used passwords or include the user's name or username.

## 2. Mandatory Multi-Factor Authentication (MFA)
MFA is strictly enforced on all enterprise accounts, Single Sign-On (SSO), and VPN gateways. Approved MFA factors include hardware FIDO2 security keys (YubiKey) and authorized authenticator applications (Okta Verify, Google Authenticator). SMS-based 2FA is prohibited for all internal production and infrastructure access due to SIM-swapping vulnerabilities.

## 3. Session Expiration and Lockouts
Enterprise sessions automatically lock after 15 minutes of inactivity on all employee workstations. Account lockout triggers after 5 consecutive failed authentication attempts, requiring self-service unlock via authenticated push notification or IT Helpdesk verification.

## 4. API Keys and Service Account Management
Service accounts must use machine-to-machine OAuth2 or API keys stored in HashiCorp Vault. API keys must be rotated at least every 90 days. Hardcoding credentials in source code repositories is an immediate critical security violation.
""",
    "it_incident_response_plan.md": """# Cybersecurity Incident Response Standard Operating Procedure (SEC-SOP-205)

## 1. Incident Classification Severities
Security incidents are categorized into four severity tiers:
- Sev-1 (Critical): Active data exfiltration, widespread ransomware, unauthorized root compromise of production infrastructure. SLA: 15-minute response.
- Sev-2 (High): Compromise of non-critical server, credential leak of privileged account without confirmed access. SLA: 1-hour response.
- Sev-3 (Medium): Phishing email reported with user interaction, malware quarantined by EDR. SLA: 4-hour response.
- Sev-4 (Low): Suspicious scan activity, non-exploitable vulnerability reports. SLA: 24-hour response.

## 2. Incident Response Phases
The IT Security team executes the NIST SP 800-61 framework:
1. Preparation: Maintaining tools, runbooks, and logging pipelines.
2. Detection & Analysis: SIEM alert correlation, triage, and scoping.
3. Containment: Network isolation, credential revocation, session termination.
4. Eradication: Malware removal, vulnerability patching, clean image re-deployment.
5. Recovery: Phased restoration, monitoring for recurrence.
6. Post-Incident Review: Root cause analysis (RCA) published within 5 business days.

## 3. Internal and External Communication Protocols
For Sev-1 and Sev-2 incidents, the Incident Commander (IC) establishes a dedicated war room channel `#incident-war-room`. External communications to customers, regulators, or media must be exclusively coordinated through Legal and Corporate Communications.
""",
    "it_device_and_encryption_standards.md": """# Corporate Device and Data Encryption Standards (SEC-STD-310)

## 1. Device Fleet Management
All company-owned laptops (macOS and Windows) must be enrolled in Mobile Device Management (MDM) via Jamf Pro or Microsoft Intune prior to user handover. Personal devices (BYOD) are strictly limited to mobile email and chat via secure MDM sandboxes.

## 2. Full-Disk Encryption (FDE)
Full-disk encryption is mandatory across 100% of the fleet:
- macOS: FileVault 2 with institutional recovery keys escrowed in Jamf.
- Windows: BitLocker with XTS-AES 256-bit encryption escrowed in Microsoft Intune.
Disabling encryption immediately revokes network access and flags the device as non-compliant.

## 3. Removable Media and USB Policy
Writing data to unencrypted USB thumb drives or external storage drives is blocked at the OS kernel level via endpoint protection agents. When business necessity requires external data transfer, IT-provisioned hardware-encrypted Kingston IronKey drives must be checked out.

## 4. Lost or Stolen Device Procedure
In the event of a lost or stolen laptop, the employee must report the incident to the Security Operations Center (soc@enterprise.com) within 2 hours. The SOC issues an immediate remote cryptographic wipe command.
""",
    "product_api_architecture_and_rate_limits.md": """# Enterprise API Platform Architecture and Rate Limits (ENG-DOC-501)

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
""",
    "product_sla_and_uptime_guarantees.md": """# Service Level Agreement (SLA) and Uptime Guarantees (LEG-DOC-802)

## 1. Uptime Commitments
Enterprise Knowledge Corp guarantees monthly service uptime of:
- Enterprise Tier Customers: 99.95% monthly uptime (less than 21.9 minutes of unscheduled downtime per month).
- Business Tier Customers: 99.9% monthly uptime (less than 43.8 minutes of unscheduled downtime per month).

## 2. Scheduled Maintenance Windows
Scheduled maintenance occurs exclusively on Sundays between 02:00 UTC and 06:00 UTC. Maintenance notices must be posted to status.enterprise.com at least 7 calendar days in advance. Maintenance downtime during this designated window is excluded from SLA calculations.

## 3. Service Credit Tiers for Outages
If monthly availability falls below the guaranteed commitment, customers are eligible for service credits applied to subsequent billing cycles:
- 99.0% to < 99.95%: 10% monthly service credit
- 95.0% to < 99.0%: 25% monthly service credit
- < 95.0%: 50% monthly service credit
Claims must be submitted in writing to sla-claims@enterprise.com within 30 days of the impacted calendar month.
""",
    "finance_travel_and_expense_policy.md": """# Corporate Travel and Business Expense Policy (FIN-POL-202)

## 1. Travel Booking and Airfare Class
All business travel must be booked through the corporate TravelPerk portal. Economy class is required for domestic flights and international flights under 6 hours duration. Business class is permitted for continuous international flights exceeding 6 hours duration, subject to VP approval.

## 2. Hotel Lodging Allowances
Standard hotel nightly rate caps (excluding taxes):
- Tier 1 Cities (New York, San Francisco, London, Tokyo): Up to $350 USD per night.
- Tier 2 Cities (Chicago, Austin, Berlin, Singapore): Up to $250 USD per night.
- Tier 3 Cities (All other destinations): Up to $180 USD per night.

## 3. Meals and Per Diem Guidelines
Employees traveling on company business are reimbursed for meals up to a daily limit of $85 USD per full travel day (Breakfast: $20, Lunch: $25, Dinner: $40). Alcoholic beverages are reimbursable only during approved client entertainment dinners with at least one external client present.

## 4. Expense Submission Deadlines
All expense reports and itemized receipts must be submitted in Expensify within 30 calendar days of expense incurrence or travel completion. Expenses submitted after 60 days will be rejected and ineligible for reimbursement.
""",
    "finance_procurement_and_vendor_approval.md": """# Procurement and Vendor Management Standard Operating Procedure (FIN-SOP-110)

## 1. Spending Authorization Thresholds
Purchase requisitions must be approved according to the following matrix:
- Up to $5,000 USD: Direct Manager approval.
- $5,001 to $25,000 USD: Department Director approval.
- $25,001 to $100,000 USD: VP and Finance Controller approval.
- Above $100,000 USD: CFO and CEO approval.

## 2. Competitive Bidding Requirements
Any procurement engagement exceeding $50,000 USD requires a formal Request for Proposal (RFP) process with at least three competitive vendor bids evaluated on pricing, security compliance, and vendor stability.

## 3. Vendor Security and Risk Assessment
Before signing contracts with third-party software (SaaS) or data processing vendors, the IT Security team must conduct a vendor security review. Vendors must provide:
- Current SOC 2 Type II or ISO 27001 audit report
- Standard Information Gathering (SIG) questionnaire
- Data Processing Addendum (DPA) incorporating Standard Contractual Clauses (SCCs).

## 4. Payment Terms
The standard enterprise payment term is Net 45 days from receipt of an undisputed, valid invoice. Early payment discount terms (e.g., 2% 10 Net 30) may be accepted upon Treasury approval.
""",
    "compliance_gdpr_and_privacy_sop.md": """# Data Privacy and GDPR Compliance Standard Operating Procedure (CMP-SOP-401)

## 1. Principles of Data Processing
Enterprise Knowledge Corp adheres to the European Union General Data Protection Regulation (GDPR) and California Consumer Privacy Act (CCPA). Personal data must be processed lawfully, fairly, and transparently, collected solely for specified, explicit, and legitimate business purposes.

## 2. Data Subject Access Requests (DSAR)
Individuals have the right to request access to, rectification of, or erasure of their personal data. DSARs must be routed immediately to privacy@enterprise.com and fulfilled within 30 calendar days as mandated by GDPR Article 12.

## 3. Data Retention and Disposal Schedules
Customer data is retained for the active duration of the subscription agreement plus 90 calendar days following termination, after which automated cryptographic purging is executed across all production and backup stores. Financial records must be retained for 7 years to satisfy statutory tax obligations.

## 4. Data Protection Impact Assessments (DPIA)
A DPIA is mandatory before initiating any new processing activity involving high-risk personal data, AI profiling, or large-scale processing of biometric or sensitive personal information.
""",
    "compliance_soc2_controls_and_auditing.md": """# SOC 2 Type II Security Controls and Audit Framework (CMP-STD-502)

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
""",
    "onboarding_engineering_handbook.md": """# Software Engineering Onboarding and Standards Handbook (ENG-HDB-001)

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
""",
    "onboarding_sales_playbook.md": """# Enterprise Sales Playbook and Qualification Methodology (SLS-HDB-105)

## 1. MEDDPICC Qualification Framework
Account Executives must qualify all prospective enterprise pipeline opportunities using the MEDDPICC criteria:
- Metrics: Quantifiable economic impact and ROI expected by the prospect.
- Economic Buyer: Person with discretionary budget release authority.
- Decision Criteria: Technical, architectural, and commercial evaluation matrix.
- Decision Process: Steps, stakeholders, and timeline to signature.
- Paper Process: Legal, procurement, and security review milestones.
- Identify Pain: Core business problem causing measurable revenue or productivity loss.
- Champion: Internal influential advocate selling on our behalf.
- Competitors: Alternative options or internal build initiatives.

## 2. Standard Pricing and Discount Authorization
- Standard Enterprise List Price: $48 per user per month (annual billing).
- Up to 10% discount: Account Executive discretion.
- 11% to 20% discount: Regional Sales Director approval required.
- Above 20% discount: VP of Sales and CFO approval required.

## 3. Proof of Concept (POC) Guidelines
POCs are reserved for qualified Tier 1 prospects (>250 target seats). Standard POC duration is strictly 14 calendar days with clearly agreed success metrics signed before sandbox provisioning.
""",
    "customer_support_escalation_matrix.md": """# Customer Support Tiering and Escalation Matrix (CS-SOP-301)

## 1. Support Tier Levels
- Tier 1: General inquiries, password resets, product navigation, documentation references.
- Tier 2: Configuration issues, API troubleshooting, webhook verification, reproducible bugs.
- Tier 3: Engineering escalations, database query analysis, infrastructure outages, deep code fixes.

## 2. Priority SLAs and Response Times
- Critical (P1): Core service completely unavailable for multiple users. Initial response: 15 minutes. Update frequency: every 30 minutes.
- High (P2): Significant degradation of major functionality with no viable workaround. Initial response: 1 hour. Update frequency: every 2 hours.
- Medium (P3): Partial functionality impairment with an available workaround. Initial response: 4 hours. Update frequency: daily.
- Low (P4): Minor cosmetic issues or general questions. Initial response: 24 hours.

## 3. Escalation Pathways
If a P1 issue cannot be diagnosed within 45 minutes, Tier 2 must escalate to the On-Call Engineering Incident Commander via PagerDuty rotation.
""",
    "hr_performance_and_promotions.md": """# Performance Management and Career Progression Framework (HR-POL-055)

## 1. Bi-Annual Review Cycles
Enterprise Knowledge Corp conducts two formal performance appraisal cycles per year:
- Mid-Year Check-in: June (focus on goal alignment and feedback).
- Year-End Comprehensive Review: November-December (performance rating, compensation calibration, and promotion decisions).

## 2. Five-Point Rating Scale
Employees are evaluated across core competencies and OKRs:
1 - Needs Immediate Improvement
2 - Developing Towards Expectations
3 - Consistently Meets Expectations
4 - Exceeds Expectations
5 - Significantly Outperforms

## 3. Promotion Eligibility Criteria
To be eligible for promotion to the next career band, an employee must have spent at least 12 continuous months in their current role and demonstrated sustained performance at the next level for at least two consecutive review cycles.
""",
    "it_cloud_infrastructure_governance.md": """# Cloud Infrastructure Governance and Cost Management (ENG-POL-602)

## 1. Multi-Cloud Architecture
Our primary infrastructure runs on Google Cloud Platform (GCP) for containerized microservices and AI workloads, with Amazon Web Services (AWS) providing disaster recovery cold storage.

## 2. Mandatory Resource Tagging
All provisioned cloud resources (VMs, Cloud Run services, buckets, databases) must include the following metadata labels:
- `environment`: `production`, `staging`, or `development`
- `owner`: team email alias (e.g., `team-rag@enterprise.com`)
- `cost-center`: financial department allocation code
- `service`: microservice name
Unlabeled resources in non-production environments are automatically deleted after 48 hours.

## 3. Idle Resource Auto-Shutdown
Non-production development clusters and sandbox environments are automatically stopped between 8:00 PM and 7:00 AM local time on weekdays and all weekend to minimize unnecessary cloud computing expenditure.
""",
    "finance_budget_allocation_and_capex.md": """# Budget Planning, Capital Expenditure, and Cash Management (FIN-POL-304)

## 1. Annual Budget Planning Cycle
The corporate budgeting cycle commences annually in September for the following fiscal year. Department heads must submit initial headcount and operating expense (OpEx) forecasts by October 15th. Final board approval of the consolidated budget occurs by December 10th.

## 2. Capital Expenditure (CapEx) Threshold
Purchases of tangible or intangible assets with a useful life exceeding one year and an acquisition cost of $5,000 USD or greater must be capitalized rather than expensed as OpEx. CapEx requires sign-off from the Corporate Controller.

## 3. Emergency Budget Contingency
Unbudgeted emergency spending exceeding $20,000 USD requires submission of an Emergency Expenditure Request (EER) signed by the Department VP and CFO detailing financial impact, mitigation steps, and business justification.
""",
    "compliance_whistleblower_and_ethics.md": """# Corporate Ethics and Whistleblower Protection Policy (CMP-POL-701)

## 1. Commitment to Ethical Conduct
Enterprise Knowledge Corp is committed to maintaining the highest standards of integrity, transparency, and compliance with all applicable securities, labor, and anti-corruption regulations.

## 2. Reporting Suspected Misconduct
Employees who observe or suspect financial fraud, insider trading, harassment, discrimination, or security violations are urged to report through:
- Direct notification to the Chief Legal Officer
- The anonymous, confidential 24/7 Ethics Hotline (operated independently by EthicsPoint at 1-800-555-ETHO)
- Secure web portal: ethics.enterprise.com

## 3. Strict Anti-Retaliation Guarantee
The company strictly prohibits any form of retaliation (demotion, termination, harassment, discrimination) against an employee who reports a concern in good faith. Any manager engaging in retaliatory behavior is subject to immediate termination.
""",
    "product_data_retention_and_destruction.md": """# Data Retention and Cryptographic Destruction Policy (SEC-POL-415)

## 1. Retention Classification Schedules
- Operational system logs: Retained for 365 days in encrypted cold storage for compliance forensics.
- Customer application data: Retained for the contract duration + 90 days grace period.
- Employee personnel files: Retained for 7 years post-termination.
- Financial invoices and tax filings: Retained for 7 years.

## 2. Secure Cryptographic Sanitization
When data reaches the end of its mandated retention schedule, automated pipelines execute secure cryptographic erasure conforming to NIST SP 800-88 Revision 1 (Guidelines for Media Sanitization). Physical hard drives retired from data centers are shredded off-site with issued destruction certificates.
""",
    "hr_benefits_and_wellness_guide.md": """# Employee Benefits, Health Insurance, and Wellness Guide (HR-GDE-012)

## 1. Medical, Dental, and Vision Coverage
Enterprise Knowledge Corp covers 90% of medical premiums for employees and 75% for dependents. We offer PPO and HDHP health plan options paired with a Health Savings Account (HSA). The company contributes $1,200 annually for individuals and $2,400 for families enrolled in the HDHP plan.

## 2. 401(k) Retirement Savings Match
Employees can enroll in the 401(k) retirement plan immediately upon hire. The company matches 100% of employee contributions up to 4% of base salary, plus 50% on the next 2% of salary (maximum company match of 5%). Company matching contributions are 100% vested immediately.

## 3. Monthly Wellness Reimbursement
All full-time employees are eligible for an $80 USD monthly wellness stipend. This subsidy reimburses gym memberships, fitness classes, mindfulness apps, mental health therapy co-pays, and sports equipment.
""",
}


def generate():
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating {len(DOCUMENTS)} enterprise documents into {CORPUS_DIR}...")
    for filename, content in DOCUMENTS.items():
        (CORPUS_DIR / filename).write_text(content.strip(), encoding="utf-8")
    print("Corpus generated successfully.")


if __name__ == "__main__":
    generate()
