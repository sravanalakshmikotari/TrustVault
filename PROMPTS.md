\# TrustVault – AI Prompt Log



\*\*Project:\*\* TrustVault  

\*\*Developer:\*\* Sravana Lakshmi  

\*\*Development period:\*\* November 4–6, 2026



> Note: The prompts below are concise summaries of the AI-assisted development discussions, not verbatim transcripts.



\## Entry 1 – November 4, 2026: Authentication



\*\*Prompt summary:\*\* Help me create user registration and login functionality using Flask and Flask-Login.



\*\*AI Output:\*\* Provided Flask authentication code, user model, password hashing, and login/register routes.



\*\*Flaw identified:\*\* Public registration should not allow users to select an administrator role.



\*\*Fix:\*\* Registration assigns the viewer role by default. Administrator access is assigned separately.



\*\*Commit:\*\* \[Initial application commit](https://github.com/sravanalakshmikotari/TrustVault/commit/e46b8ac)



\## Entry 2 – November 4, 2026: Document Database Models



\*\*Prompt summary:\*\* Help me create database models for documents, document permissions, and audit logs.



\*\*AI Output:\*\* Provided SQLAlchemy models for Document, DocumentPermission, and AuditLog.



\*\*Flaw identified:\*\* Document access needs to be associated with individual users and documents.



\*\*Fix:\*\* Added document ownership, user-specific permissions, read/edit flags, and a unique constraint for document-user permissions.



\*\*Commit:\*\* \[Initial application commit](https://github.com/sravanalakshmikotari/TrustVault/commit/e46b8ac)



\## Entry 3 – November 5, 2026: Secure Document Upload



\*\*Prompt summary:\*\* Help me implement secure document uploads and downloads in Flask.



\*\*AI Output:\*\* Provided file upload and download functionality.



\*\*Flaw identified:\*\* Uploaded files should not be directly accessible through a public static folder, and unrestricted file uploads are risky.



\*\*Fix:\*\* Added allowed file extensions, a 5 MB upload limit, secure filenames, UUID-based stored filenames, and protected download routes.



\*\*Commit:\*\* \[Initial application commit](https://github.com/sravanalakshmikotari/TrustVault/commit/e46b8ac)



\## Entry 4 – November 5, 2026: Authorization and Access Control



\*\*Prompt summary:\*\* Help me implement per-document read/edit permissions, document sharing, and access revocation.



\*\*AI Output:\*\* Provided server-side permission checks for document sharing, downloading, and revocation.



\*\*Flaw identified:\*\* A user without permission must not be able to download another user's document by directly entering its URL.



\*\*Fix:\*\* Added ownership and permission checks on the server. Tested access after revocation and confirmed that an unauthorized download returns HTTP 403.



\*\*Verification:\*\* Manually tested with two user accounts.



\*\*Commit:\*\* \[Initial application commit](https://github.com/sravanalakshmikotari/TrustVault/commit/e46b8ac)



\## Entry 5 – November 6, 2026: Audit Logging and Admin Dashboard



\*\*Prompt summary:\*\* Help me record document activities and display audit logs in an administrator dashboard.



\*\*AI Output:\*\* Provided audit logging and administrator activity-view functionality.



\*\*Flaw identified:\*\* Unauthorized download attempts and permission changes must also be recorded, not just successful downloads.



\*\*Fix:\*\* Added audit records for uploads, downloads, denied downloads, permission grants, and permission revocations. Verified the records in the admin dashboard.



\*\*Verification:\*\* Manually checked activity logs using two accounts.



\*\*Commit:\*\* \[Initial application commit](https://github.com/sravanalakshmikotari/TrustVault/commit/e46b8ac)



\## Current Testing Limitations



\- Manual authorization checks have been performed.

\- Automated security tests are still pending.

\- Additional testing is required for edit/delete operations and other security threats.

\- Production deployment hardening is pending.



\## Conclusion



AI assistance was used during development for implementation guidance, debugging, and security improvements. The generated code was reviewed and tested manually during development.



\## 6 November 2026 - Search, Delete and Automated Testing



\*\*Prompt:\*\* Add document search and owner-only document deletion. Verify security using automated tests.



\*\*AI Output:\*\* Added document search filters for name, category, owner and date. Added an owner-only delete route with audit logging. Created pytest access-control tests.



\*\*Flaw identified:\*\* Search and delete needed server-side authorization checks to prevent unauthorized access.



\*\*Fix:\*\* Search results are restricted to documents owned by or shared with the logged-in user. Delete is restricted to the document owner.



\*\*Test Result:\*\* 6 automated tests passed.



\*\*Commit:\*\* https://github.com/sravanalakshmikotari/TrustVault/commit/286029a

