import json
from pathlib import Path

QUERIES_FILE = Path(__file__).resolve().parent / "dataset" / "queries.jsonl"

RAW_QUERIES = [
    # 1 - 20: HR Remote Work & Leave Policies
    (
        "What is the home office equipment stipend amount for remote employees?",
        "hr_remote_work_policy.md",
        ["stipend", "$1,000", "ergonomic", "office"],
        "factual",
    ),
    (
        "How much can remote workers get reimbursed monthly for internet bills?",
        "hr_remote_work_policy.md",
        ["$75", "internet", "subsidy", "50 Mbps"],
        "factual",
    ),
    (
        "What are the mandatory core working hours for hybrid and remote staff?",
        "hr_remote_work_policy.md",
        ["10:00 AM", "4:00 PM", "core business hours"],
        "factual",
    ),
    (
        "Who is eligible to request full remote work status?",
        "hr_remote_work_policy.md",
        ["90-day", "probationary", "Meets Expectations"],
        "factual",
    ),
    (
        "What are the minimum internet speed requirements for remote team members?",
        "hr_remote_work_policy.md",
        ["50 Mbps", "10 Mbps upload", "video conferencing"],
        "factual",
    ),
    (
        "How many PTO days does an employee with 4 years of tenure accrue annually?",
        "hr_leave_and_vacation_policy.md",
        ["22 days", "3 to 5 years", "1.83 days per month"],
        "factual",
    ),
    (
        "How many unused PTO days are allowed to roll over into the next calendar year?",
        "hr_leave_and_vacation_policy.md",
        ["5 unused PTO days", "March 31st"],
        "factual",
    ),
    (
        "How many weeks of paid parental leave does the company provide?",
        "hr_leave_and_vacation_policy.md",
        ["16 consecutive weeks", "fully paid", "regardless of gender"],
        "factual",
    ),
    (
        "When do rolled over PTO days expire if not taken?",
        "hr_leave_and_vacation_policy.md",
        ["March 31st", "expire"],
        "factual",
    ),
    (
        "How many paid sick days do employees receive each year?",
        "hr_leave_and_vacation_policy.md",
        ["10 paid sick days", "front-loaded", "January 1st"],
        "factual",
    ),
    (
        "What documentation is required if an employee is absent on sick leave for 4 days?",
        "hr_leave_and_vacation_policy.md",
        ["licensed physician note", "exceeding three consecutive"],
        "factual",
    ),
    (
        "How many days of bereavement leave are granted for the loss of a sibling?",
        "hr_leave_and_vacation_policy.md",
        ["5 paid days", "immediate family", "sibling"],
        "factual",
    ),
    (
        "Can an employee roll over 8 unused PTO days into the following year?",
        "hr_leave_and_vacation_policy.md",
        ["maximum of 5", "unused days beyond 5 expire"],
        "paraphrased",
    ),
    (
        "Is paternity leave separate from maternity leave or are both eligible for 16 weeks?",
        "hr_leave_and_vacation_policy.md",
        ["16 consecutive weeks", "regardless of gender", "all new parents"],
        "paraphrased",
    ),
    (
        "What is the deadline for submitting receipts for the remote office setup grant?",
        "hr_remote_work_policy.md",
        ["60 calendar days", "Expensify portal"],
        "factual",
    ),
    (
        "How often must remote workers complete their ergonomic workspace self-certification?",
        "hr_remote_work_policy.md",
        ["Annual", "November", "Workday"],
        "factual",
    ),
    (
        "How much advance notice is required before taking a midday break during core hours?",
        "hr_remote_work_policy.md",
        ["30-minute advance notice", "team channel"],
        "factual",
    ),
    (
        "What are the paid leave provisions for employees called for jury service?",
        "hr_leave_and_vacation_policy.md",
        ["Up to 10 business days", "jury duty", "court attendance"],
        "factual",
    ),
    (
        "Does tenure increase sick leave accrual after 5 years?",
        "hr_leave_and_vacation_policy.md",
        ["10 paid sick days", "front-loaded"],
        "paraphrased",
    ),
    (
        "What tenure level is required to receive 26 days of annual vacation?",
        "hr_leave_and_vacation_policy.md",
        ["5+ years", "26 days annually"],
        "factual",
    ),
    # 21 - 40: IT Security, Passwords, Devices & Incidents
    (
        "What are the minimum password complexity rules for enterprise accounts?",
        "it_password_and_auth_policy.md",
        ["14 characters", "uppercase", "lowercase", "digit", "special symbol"],
        "factual",
    ),
    (
        "Is SMS-based two-factor authentication permitted for production infrastructure access?",
        "it_password_and_auth_policy.md",
        ["SMS-based 2FA is prohibited", "SIM-swapping"],
        "factual",
    ),
    (
        "How many failed login attempts will cause an account lockout?",
        "it_password_and_auth_policy.md",
        ["5 consecutive failed", "lockout"],
        "factual",
    ),
    (
        "After how many minutes of inactivity does an employee screen lock?",
        "it_password_and_auth_policy.md",
        ["15 minutes", "inactivity", "lock"],
        "factual",
    ),
    (
        "How frequently must service account API keys be rotated?",
        "it_password_and_auth_policy.md",
        ["90 days", "rotated", "Vault"],
        "factual",
    ),
    (
        "What is the response SLA for a Sev-1 critical cybersecurity incident?",
        "it_incident_response_plan.md",
        ["15-minute response", "Sev-1", "Critical"],
        "factual",
    ),
    (
        "What is the response SLA for a Sev-2 security incident?",
        "it_incident_response_plan.md",
        ["1-hour response", "Sev-2", "High"],
        "factual",
    ),
    (
        "What framework does the IT Security incident response team follow?",
        "it_incident_response_plan.md",
        ["NIST SP 800-61", "Preparation", "Detection", "Containment"],
        "factual",
    ),
    (
        "Within how many days must a post-incident root cause analysis be published?",
        "it_incident_response_plan.md",
        ["5 business days", "root cause analysis", "RCA"],
        "factual",
    ),
    (
        "Which Slack channel is designated as the war room for Sev-1 incidents?",
        "it_incident_response_plan.md",
        ["#incident-war-room", "War room"],
        "factual",
    ),
    (
        "What disk encryption algorithm is enforced on Windows laptops?",
        "it_device_and_encryption_standards.md",
        ["BitLocker", "XTS-AES 256-bit", "Intune"],
        "factual",
    ),
    (
        "What tool manages macOS device enrollment and encryption key escrow?",
        "it_device_and_encryption_standards.md",
        ["Jamf Pro", "FileVault 2", "MDM"],
        "factual",
    ),
    (
        "Can employees write company data onto personal unencrypted USB flash drives?",
        "it_device_and_encryption_standards.md",
        ["blocked at the OS kernel level", "unencrypted USB"],
        "factual",
    ),
    (
        "What hardware encrypted brand of USB drive is approved by IT?",
        "it_device_and_encryption_standards.md",
        ["Kingston IronKey", "hardware-encrypted"],
        "factual",
    ),
    (
        "How quickly must an employee notify the SOC if their company laptop is lost or stolen?",
        "it_device_and_encryption_standards.md",
        ["within 2 hours", "soc@enterprise.com", "remote cryptographic wipe"],
        "factual",
    ),
    (
        "What happens to production network access if an employee disables FileVault on their Mac?",
        "it_device_and_encryption_standards.md",
        ["Disabling encryption immediately revokes network access", "non-compliant"],
        "factual",
    ),
    (
        "What approved MFA methods are permitted instead of SMS?",
        "it_password_and_auth_policy.md",
        ["FIDO2 security keys", "YubiKey", "Okta Verify", "Google Authenticator"],
        "paraphrased",
    ),
    (
        "How many previous passwords does the directory remember to prevent reuse?",
        "it_password_and_auth_policy.md",
        ["last 10 previously used passwords"],
        "factual",
    ),
    (
        "Where must service credentials and API tokens be securely stored?",
        "it_password_and_auth_policy.md",
        ["HashiCorp Vault", "OAuth2"],
        "factual",
    ),
    (
        "Who is authorized to speak to the media during a major data breach incident?",
        "it_incident_response_plan.md",
        ["Legal and Corporate Communications", "exclusively coordinated"],
        "factual",
    ),
    # 41 - 60: Product Architecture, SLA, & Cloud Infrastructure
    (
        "What is the rate limit for Enterprise tier customers on the API?",
        "product_api_architecture_and_rate_limits.md",
        ["10,000 requests per minute", "RPM", "burst capacity of 15,000"],
        "factual",
    ),
    (
        "What is the rate limit for Starter tier API customers?",
        "product_api_architecture_and_rate_limits.md",
        ["100 requests per minute", "RPM", "burst capacity of 150"],
        "factual",
    ),
    (
        "What is the maximum payload size for standard JSON requests on the API gateway?",
        "product_api_architecture_and_rate_limits.md",
        ["25 MB", "standard JSON", "payload size"],
        "factual",
    ),
    (
        "What is the gateway timeout for synchronous REST API calls?",
        "product_api_architecture_and_rate_limits.md",
        ["30 seconds", "synchronous REST"],
        "factual",
    ),
    (
        "How long is the required deprecation notice for breaking API changes?",
        "product_api_architecture_and_rate_limits.md",
        ["12-month deprecation notice period", "breaking changes"],
        "factual",
    ),
    (
        "What is the guaranteed monthly uptime percentage for Enterprise customers?",
        "product_sla_and_uptime_guarantees.md",
        ["99.95% monthly uptime", "less than 21.9 minutes"],
        "factual",
    ),
    (
        "When does the company conduct scheduled maintenance windows?",
        "product_sla_and_uptime_guarantees.md",
        ["Sundays between 02:00 UTC and 06:00 UTC"],
        "factual",
    ),
    (
        "How much advance notice is required for scheduled maintenance?",
        "product_sla_and_uptime_guarantees.md",
        ["at least 7 calendar days in advance", "status.enterprise.com"],
        "factual",
    ),
    (
        "What service credit percentage is issued if uptime drops to 98% in a month?",
        "product_sla_and_uptime_guarantees.md",
        ["25% monthly service credit", "95.0% to < 99.0%"],
        "factual",
    ),
    (
        "What service credit is provided if monthly uptime falls below 95%?",
        "product_sla_and_uptime_guarantees.md",
        ["50% monthly service credit", "< 95.0%"],
        "factual",
    ),
    (
        "What is the primary cloud provider used for containerized microservices and AI workloads?",
        "it_cloud_infrastructure_governance.md",
        ["Google Cloud Platform", "GCP", "Cloud Run"],
        "factual",
    ),
    (
        "What cloud provider is used for cold storage disaster recovery?",
        "it_cloud_infrastructure_governance.md",
        ["Amazon Web Services", "AWS", "cold storage"],
        "factual",
    ),
    (
        "What metadata tags are mandatory on all cloud resources?",
        "it_cloud_infrastructure_governance.md",
        ["environment", "owner", "cost-center", "service"],
        "factual",
    ),
    (
        "What happens to unlabeled cloud resources in development environments?",
        "it_cloud_infrastructure_governance.md",
        ["automatically deleted after 48 hours", "unlabeled"],
        "factual",
    ),
    (
        "During what hours are non-production development environments automatically shut down?",
        "it_cloud_infrastructure_governance.md",
        ["8:00 PM and 7:00 AM", "weekdays and all weekend"],
        "factual",
    ),
    (
        "How many times do failed outgoing webhooks retry?",
        "product_api_architecture_and_rate_limits.md",
        ["retry 5 times", "exponential backoff over 24 hours"],
        "factual",
    ),
    (
        "Within how many days must SLA outage credit claims be submitted?",
        "product_sla_and_uptime_guarantees.md",
        ["within 30 days", "sla-claims@enterprise.com"],
        "factual",
    ),
    (
        "What is the Business tier monthly uptime SLA commitment?",
        "product_sla_and_uptime_guarantees.md",
        ["99.9% monthly uptime", "43.8 minutes"],
        "factual",
    ),
    (
        "Can a customer request SLA credits if downtime occurred during Sunday 03:00 UTC maintenance?",
        "product_sla_and_uptime_guarantees.md",
        ["excluded from SLA calculations", "Sunday"],
        "paraphrased",
    ),
    (
        "What TLS version is mandatory for API connections?",
        "product_api_architecture_and_rate_limits.md",
        ["TLS 1.3 encryption", "Bearer JWT"],
        "factual",
    ),
    # 61 - 80: Finance, Procurement, Budgeting & Benefits
    (
        "What is the maximum nightly hotel allowance for business travel in New York City?",
        "finance_travel_and_expense_policy.md",
        ["$350 USD per night", "Tier 1 Cities", "New York"],
        "factual",
    ),
    (
        "What is the daily meal per diem cap for employees traveling on business?",
        "finance_travel_and_expense_policy.md",
        ["$85 USD per full travel day", "Breakfast", "Lunch", "Dinner"],
        "factual",
    ),
    (
        "When is business class air travel permitted for company employees?",
        "finance_travel_and_expense_policy.md",
        ["continuous international flights exceeding 6 hours", "VP approval"],
        "factual",
    ),
    (
        "Within how many days must travel expense reports be submitted in Expensify?",
        "finance_travel_and_expense_policy.md",
        ["within 30 calendar days", "30 days", "Expensify"],
        "factual",
    ),
    (
        "Are alcoholic drinks reimbursable on ordinary solo travel days?",
        "finance_travel_and_expense_policy.md",
        [
            "only during approved client entertainment dinners",
            "external client present",
        ],
        "paraphrased",
    ),
    (
        "Who must approve a purchase requisition between $25,001 and $100,000?",
        "finance_procurement_and_vendor_approval.md",
        ["VP and Finance Controller approval", "$25,001 to $100,000"],
        "factual",
    ),
    (
        "What spending threshold mandates a competitive RFP with three vendor bids?",
        "finance_procurement_and_vendor_approval.md",
        ["exceeding $50,000 USD", "RFP", "three competitive vendor bids"],
        "factual",
    ),
    (
        "What security documentation is required before onboarding a new SaaS vendor?",
        "finance_procurement_and_vendor_approval.md",
        ["SOC 2 Type II or ISO 27001", "SIG questionnaire", "DPA"],
        "factual",
    ),
    (
        "What is the standard payment term for corporate vendor invoices?",
        "finance_procurement_and_vendor_approval.md",
        ["Net 45 days", "undisputed, valid invoice"],
        "factual",
    ),
    (
        "What is the dollar threshold for capitalizing purchases as CapEx?",
        "finance_budget_allocation_and_capex.md",
        ["$5,000 USD or greater", "useful life exceeding one year"],
        "factual",
    ),
    (
        "When must department heads submit next year's OpEx and headcount budget forecasts?",
        "finance_budget_allocation_and_capex.md",
        ["October 15th", "headcount and operating expense"],
        "factual",
    ),
    (
        "Who must sign an Emergency Expenditure Request exceeding $20,000?",
        "finance_budget_allocation_and_capex.md",
        ["Department VP and CFO", "Emergency Expenditure Request"],
        "factual",
    ),
    (
        "What is the maximum 401(k) company matching percentage?",
        "hr_benefits_and_wellness_guide.md",
        ["maximum company match of 5%", "100% of employee contributions up to 4%"],
        "factual",
    ),
    (
        "Are company 401(k) matching funds subject to a multi-year vesting schedule?",
        "hr_benefits_and_wellness_guide.md",
        ["100% vested immediately", "matching contributions"],
        "paraphrased",
    ),
    (
        "How much does the company contribute annually to employee HSAs for individuals?",
        "hr_benefits_and_wellness_guide.md",
        ["$1,200 annually for individuals", "HDHP"],
        "factual",
    ),
    (
        "What is the monthly wellness stipend amount available to employees?",
        "hr_benefits_and_wellness_guide.md",
        ["$80 USD monthly wellness stipend", "gym memberships"],
        "factual",
    ),
    (
        "What percentage of medical premiums does the company cover for employees?",
        "hr_benefits_and_wellness_guide.md",
        ["covers 90% of medical premiums for employees", "75% for dependents"],
        "factual",
    ),
    (
        "Can wellness stipends be used for mental health therapy copays?",
        "hr_benefits_and_wellness_guide.md",
        ["mental health therapy co-pays", "mindfulness apps"],
        "paraphrased",
    ),
    (
        "What is the hotel allowance cap for Tier 2 cities like Austin or Berlin?",
        "finance_travel_and_expense_policy.md",
        ["Up to $250 USD per night", "Tier 2 Cities"],
        "factual",
    ),
    (
        "What happens to expenses submitted past 60 days from incurrence?",
        "finance_travel_and_expense_policy.md",
        ["rejected and ineligible for reimbursement", "after 60 days"],
        "factual",
    ),
    # 81 - 95: Compliance, Engineering Standards & Support SLAs
    (
        "Within how many calendar days must a GDPR Data Subject Access Request be fulfilled?",
        "compliance_gdpr_and_privacy_sop.md",
        ["within 30 calendar days", "DSAR", "Article 12"],
        "factual",
    ),
    (
        "How long is customer data retained following contract termination?",
        "compliance_gdpr_and_privacy_sop.md",
        ["90 calendar days following termination", "automated cryptographic purging"],
        "factual",
    ),
    (
        "How long must statutory financial records and tax filings be kept?",
        "compliance_gdpr_and_privacy_sop.md",
        ["7 years", "statutory tax obligations"],
        "factual",
    ),
    (
        "How long can ephemeral JIT production cloud access sessions last before expiration?",
        "compliance_soc2_controls_and_auditing.md",
        ["expiring within 8 hours", "Just-In-Time", "JIT"],
        "factual",
    ),
    (
        "What is the remediation SLA for critical CVSS 9.0+ security vulnerabilities?",
        "compliance_soc2_controls_and_auditing.md",
        ["within 7 business days", "Critical vulnerabilities", "CVSS"],
        "factual",
    ),
    (
        "What is the remediation deadline for high CVSS vulnerabilities under SOC 2 controls?",
        "compliance_soc2_controls_and_auditing.md",
        ["within 30 calendar days", "High vulnerabilities", "CVSS"],
        "factual",
    ),
    (
        "What is the minimum unit test coverage required on core engineering repositories?",
        "onboarding_engineering_handbook.md",
        ["minimum test coverage of 80%", "core business logic"],
        "factual",
    ),
    (
        "What are the target milestones for an engineer's first 5 days?",
        "onboarding_engineering_handbook.md",
        [
            "Day 1: Laptop setup",
            "Day 3: First pull request",
            "Day 5: First production deployment",
        ],
        "multi_hop",
    ),
    (
        "What framework must sales account executives use to qualify enterprise opportunities?",
        "onboarding_sales_playbook.md",
        ["MEDDPICC", "Metrics", "Economic Buyer", "Champion"],
        "factual",
    ),
    (
        "What is the standard list price per user for the enterprise product?",
        "onboarding_sales_playbook.md",
        ["$48 per user per month", "annual billing"],
        "factual",
    ),
    (
        "What is the initial response SLA for a P1 critical customer support ticket?",
        "customer_support_escalation_matrix.md",
        ["Initial response: 15 minutes", "Critical (P1)"],
        "factual",
    ),
    (
        "How often must customer support post updates on an active P2 incident?",
        "customer_support_escalation_matrix.md",
        ["Update frequency: every 2 hours", "High (P2)"],
        "factual",
    ),
    (
        "What is the hotline phone number for reporting ethical violations anonymously?",
        "compliance_whistleblower_and_ethics.md",
        ["1-800-555-ETHO", "EthicsPoint", "Hotline"],
        "factual",
    ),
    (
        "What protection is guaranteed to employees reporting misconduct in good faith?",
        "compliance_whistleblower_and_ethics.md",
        ["prohibits any form of retaliation", "anti-retaliation guarantee"],
        "factual",
    ),
    (
        "How long must operational system logs be retained for audit forensics?",
        "product_data_retention_and_destruction.md",
        ["Retained for 365 days", "encrypted cold storage"],
        "factual",
    ),
    # 96 - 100: Unanswerable / Negative queries (to test negative retrieval guard)
    (
        "What is the company policy regarding cryptocurrency compensation and bitcoin bonuses?",
        "None",
        ["could not find sufficient information", "not found"],
        "unanswerable",
    ),
    (
        "How many company stock options are awarded for getting a private pilot license?",
        "None",
        ["could not find sufficient information", "not found"],
        "unanswerable",
    ),
    (
        "What is the corporate discount rate for purchasing a Tesla electric vehicle?",
        "None",
        ["could not find sufficient information", "not found"],
        "unanswerable",
    ),
    (
        "What brand of espresso beans is provided in the London office cafeteria?",
        "None",
        ["could not find sufficient information", "not found"],
        "unanswerable",
    ),
    (
        "What is the company policy on wearing scuba gear during client Zoom calls?",
        "None",
        ["could not find sufficient information", "not found"],
        "unanswerable",
    ),
]


def generate():
    QUERIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    print(f"Generating {len(RAW_QUERIES)} labeled evaluation queries...")
    with open(QUERIES_FILE, "w", encoding="utf-8") as f:
        for idx, (query, gold_doc, keywords, qtype) in enumerate(RAW_QUERIES, start=1):
            record = {
                "query_id": f"q{idx:03d}",
                "query": query,
                "gold_doc": gold_doc,
                "gold_keywords": keywords,
                "query_type": qtype,
            }
            f.write(json.dumps(record) + "\n")
    print(f"Saved queries to {QUERIES_FILE}")


if __name__ == "__main__":
    generate()
