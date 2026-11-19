# Corporate Device and Data Encryption Standards (SEC-STD-310)

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