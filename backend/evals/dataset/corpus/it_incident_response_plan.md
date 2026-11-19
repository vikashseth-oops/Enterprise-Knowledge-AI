# Cybersecurity Incident Response Standard Operating Procedure (SEC-SOP-205)

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