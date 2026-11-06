\# TrustVault – Secure Document Sharing System



\## Overview

TrustVault is a Flask-based web application designed to securely upload, manage, share, and access documents with role-based permissions and audit logging.



\## Features

\- User registration and login

\- Password hashing

\- Admin and viewer roles

\- Secure document upload with file validation

\- Document sharing with read/edit permission settings

\- Access revocation

\- Protected document downloads

\- Document search by name, owner, category, and date

\- Owner-only document deletion

\- Audit logs for document activities

\- Admin activity dashboard



\## Technologies Used

\- Python

\- Flask

\- Flask-Login

\- Flask-SQLAlchemy

\- SQLite

\- HTML

\- Pytest



\## Installation and Setup



1\. Clone the repository:



&#x20;  `git clone https://github.com/sravanalakshmikotari/TrustVault.git`



2\. Open the project folder:



&#x20;  `cd TrustVault`



3\. Create and activate a virtual environment:



&#x20;  `python -m venv venv`



&#x20;  Windows:



&#x20;  `venv\\Scripts\\activate`



4\. Install dependencies:



&#x20;  `pip install -r requirements.txt`



5\. Run the application:



&#x20;  `python app.py`



6\. Open in your browser:



&#x20;  `http://127.0.0.1:5000`



\## Run Automated Tests



`python -m pytest -q`



Latest result: \*\*6 tests passed\*\*.



\## Security

\- Server-side authentication and authorization checks

\- Owner and permission-based document access

\- CSRF protection

\- Secure filenames and UUID-based storage

\- Upload type and size validation

\- Audit logging of important activities



See \[THREATS.md](THREATS.md) for the threat model and accepted risks.



\## AI Usage

AI assistance was used for development guidance, debugging, and security improvements. See \[PROMPTS.md](PROMPTS.md) for the development prompt log.



\## Current Limitations

\- Shared-document editing is not implemented yet.

\- Malware scanning and rate limiting are not implemented.

\- Production deployment hardening is pending.

\- The application has not yet been deployed to a public live URL.



\## Repository

https://github.com/sravanalakshmikotari/TrustVault

