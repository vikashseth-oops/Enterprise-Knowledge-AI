# IT Security Password and Multi-Factor Authentication Policy (SEC-POL-101)

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