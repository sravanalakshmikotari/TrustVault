\# TrustVault – Threat Model



\## 1. Introduction



TrustVault is a secure document management and sharing application built using Python Flask and SQLite.



This document describes possible security threats, implemented protections, and accepted risks.



\## 2. Protected Assets



\- User account information

\- Password hashes

\- Uploaded documents

\- Document permissions

\- Audit logs

\- User sessions



\## 3. Threats and Mitigations



\### Threat 1: Unauthorized Access



\*\*Risk:\*\* An unauthorized user may try to access another user's documents.



\*\*Mitigation:\*\*

\- Flask-Login protects authenticated routes.

\- Document ownership is checked before allowing access.

\- Shared document permissions are checked before downloading.

\- Unauthorized download attempts return HTTP 403.



\### Threat 2: Unauthorized Document Sharing



\*\*Risk:\*\* A user may try to share documents owned by another user.



\*\*Mitigation:\*\*

\- Only document owners can grant permissions.

\- The application checks document ownership before sharing.

\- Permission changes are recorded in audit logs.



\### Threat 3: Unauthorized Permission Changes



\*\*Risk:\*\* A user may try to revoke or modify another user's document permissions.



\*\*Mitigation:\*\*

\- Only document owners can revoke access.

\- Permission changes are checked on the server.

\- Permission grant and revoke actions are recorded.



\### Threat 4: Password Theft



\*\*Risk:\*\* Attackers may try to access accounts using stored passwords.



\*\*Mitigation:\*\*

\- Passwords are stored as secure password hashes.

\- Werkzeug password hashing functions are used.

\- Plain-text passwords are not stored.



\### Threat 5: Malicious File Upload



\*\*Risk:\*\* Attackers may upload unwanted or dangerous files.



\*\*Mitigation:\*\*

\- File extensions are restricted.

\- Maximum upload size is limited to 5 MB.

\- Secure filenames and UUID-based stored filenames are used.

\- Uploaded files are stored outside the public static folder.



\### Threat 6: Cross-Site Request Forgery (CSRF)



\*\*Risk:\*\* An attacker may try to submit unauthorized actions through another website.



\*\*Mitigation:\*\*

\- Flask-WTF CSRF protection is enabled.

\- POST forms include CSRF tokens.



\### Threat 7: Audit Log Tampering or Missing Records



\*\*Risk:\*\* Important document activities may not be recorded



\## Automated Security Testing - 6 November 2026



Automated tests are implemented using pytest.



Test results:

\- 6 tests passed.

\- Unauthorized users cannot download unshared documents.

\- Owners can download their documents.

\- Non-owners cannot grant or revoke permissions.

\- Revoked users cannot download documents.

\- Non-admin users cannot access the admin page.



Test command:

python -m pytest -q



Latest test commit:

https://github.com/sravanalakshmikotari/TrustVault/commit/286029a



Limitations:

\- Deployment hardening is still pending.

\- Malware scanning and rate limiting are not implemented.

\- Edit functionality for shared documents is not yet implemented.s

