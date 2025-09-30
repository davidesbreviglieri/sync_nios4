# Nios4 Sync (MySQL)

Python toolkit to bootstrap a **Nios4**-compatible MySQL database, handle bidirectional synchronization with the remote service, and provide common utilities (TID/UUID, safe expression evaluation, etc.).  
The project exposes three main classes:

- `database_nios4.py` — schema creation/verification, DDL/DML helpers, simple queries.
- `utility_nios4.py` — generic helpers (TID/UUID, conversions, safe math evaluator).
- `sync_nios4.py` — sync orchestrator: push/pull packets, notifications, email sending, file upload.

> Classes include **type hints** and **NumPy-style English docstrings** for IDEs and linters.

---

## Table of Contents

- [Features](#features)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [MySQL Setup](#mysql-setup)
- [Quickstart](#quickstart)
- [Common Usage](#common-usage)
  - [Application Notifications](#application-notifications)
  - [Email Sending](#email-sending)
  - [File Upload and Record Binding](#file-upload-and-record-binding)
  - [Selective Table Sync](#selective-table-sync)
- [Error Handling](#error-handling)
- [Security & Operational Notes](#security--operational-notes)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Testing](#testing)
- [License](#license)

---

## Features

- **DB Bootstrap**: automatically creates core tables (`so_tables`, `so_fields`, `so_users`, `lo_setting`, `lo_cleanbox`, `lo_syncbox`) if missing.
- **Synchronization**:
  - sends structure (tables/fields/users) and data deltas in packets,
  - handles `cleanbox` (deletions) and `syncbox` (targeted inserts/updates),
  - downloads partial batches and applies them locally.
- **Utilities**:
  - `tid()` UTC formatted as `YYYYMMDDHHMMSS` (integer),
  - `gguid()` UUID4 string,
  - `calc_expression()` safe evaluation of numeric, Python-like expressions,
  - conversions and SQL escaping helpers.
- **Email/Notifications**: send emails via the remote endpoint; create notifications in `so_notifications`.
- **File Upload**: upload to remote storage and persist metadata in your application table.

---

## Repository Structure

```
.
├── database_nios4.py
├── utility_nios4.py
├── sync_nios4.py
├── requirements.txt        # suggested (see below)
├── .env.example            # example environment variables (optional)
└── README.md               # main README (Italian)
```

---

## Prerequisites

- **Python** 3.9+ (3.11/3.12 recommended)
- **MySQL** 5.7+ / 8.0+
- Python dependencies:
  - `mysql-connector-python`
  - `requests`

Example `requirements.txt`:

```txt
mysql-connector-python>=9.0.0
requests>=2.31.0
python-dotenv>=1.0.1  # optional, to load .env
```

---

## Installation

```bash
git clone https://github.com/<org>/<repo>.git
cd <repo>
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Optionally create a `.env` from `.env.example`.

---

## MySQL Setup

Your MySQL user should have privileges for:

- `CREATE DATABASE`, `CREATE`, `ALTER`, `DROP` on the working schema,
- `SELECT`, `INSERT`, `UPDATE`, `DELETE`.

Quick example:

```sql
CREATE DATABASE nios4 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'nios4'@'%' IDENTIFIED BY '********';
GRANT ALL PRIVILEGES ON nios4.* TO 'nios4'@'%';
FLUSH PRIVILEGES;
```

> If the database does not exist, `database_nios4` can create it automatically using server credentials (standard charset/collation).

---

## Quickstart

Minimal example that initializes the DB and starts a full sync:

```python
from sync_nios4 import sync_nios4

SYNC = sync_nios4(
    username="user@example.com",   # remote service credentials
    password="password",
    token="",                      # if empty, login() is performed
    dbname="nios4",
    hostdb="127.0.0.1",
    usernamedb="nios4",
    passworddb="********"
)

# Optional: restrict involved tables
# SYNC.enabled_getdata_tables = ["my_table"]
# SYNC.enabled_setdata_tables = ["my_table"]

ok = SYNC.syncro(dbname="nios4_remote_key")  # 'db' for the remote endpoint
print("SYNC OK:", ok)
```

---

## Common Usage

### Application Notifications

```python
SYNC.send_notificationrecord(
    uta="target.user",
    title="Task reminder",
    description="Please review card #1234",
    tablename="orders",
    gguidrif="2a89c7bc-2c57-4d5e-ae9f-3c61a2d1c001"
)
```

### Email Sending

```python
SYNC.send_emailv2(
    dbname="nios4_remote_key",
    sendfrom="noreply@example.com",
    sendfromname="Nios4 Bot",
    sendto="recipient@example.com",
    subject="Order confirmation",
    replyto="support@example.com",
    body="Thanks for your order!",
    bodyhtml="<p><b>Thank you</b> for your order!</p>",
    listcc=[],
    listbcc=[],
    listdocument=[]  # attachment handling to implement if needed
)
```

Or via template:

```python
SYNC.send_templatemail(
    mail="recipient@example.com",
    idtemplate=42,
    payload={"name": "Davide", "order": "A-1002"}
)
```

### File Upload and Record Binding

```python
resp = SYNC.download_file(
    dbname="nios4_remote_key",
    pathfile="/path/invoice.pdf",
    filename="invoice.pdf",
    tablename="invoices",
    fieldname="attachment",
    gguid="6ff3a0a1-4ece-4f0e-9b5a-2f3f8b9b4c51"
)
print(resp)
```

> The record will store JSON metadata in `attachment` and the original filename in `file_attachment`. The row is added to `lo_syncbox`.

### Selective Table Sync

```python
# Receive data only for certain tables
SYNC.enabled_getdata_tables = ["invoices", "orders"]

# Send data only for certain tables
SYNC.enabled_setdata_tables = ["orders"]

# (Optional) Create only a subset of tables when applying structure
SYNC.enabled_create_tables = ["so_localusers", "orders"]
```

---

## Error Handling

All classes share an `error_n4` container:

```python
if not SYNC.syncro("nios4_remote_key"):
    print("Error:", SYNC.err.errorcode, SYNC.err.errormessage)
```

In general:

- codes `E0xx` → local errors (DB/connections/IO),
- HTTP status codes or server `KO` → remote details in `err.errormessage`.

---

## Security & Operational Notes

- Store **tokens/credentials** in environment variables or `.env`. Do not commit secrets.
- `download_file()` sends file bytes to the remote endpoint—validate **size** and **types**.
- Dynamic SQL strings rely on simplified escaping for quotes—**do not** pass unsanitized end-user input.
- Ensure your system clock is **UTC-synced**: the flow relies on `tid()` ordering.

---

## Troubleshooting

- **`Please login first to synchronize (E019)`**  
  Provide a valid `token` or `username/password` and call `login()`.

- **`None` returned from queries**  
  Check MySQL credentials, DB name and privileges; inspect `err.errormessage`.

- **Schema issues**  
  Drop/restore core tables only if necessary. `database_nios4.initializedb()` rebuilds the minimal structure.

- **Unparsable dates during `install_data`**  
  Date values must be `YYYYMMDDHHMMSS` numbers; otherwise they are ignored/logged.

---

## Development

Recommended tools:

- Linting: `ruff` or `flake8`
- Typing: `mypy`
- Formatting: `black`

Example:

```bash
pip install ruff mypy black
ruff check .
mypy .
black .
```

---

## Testing

Use `pytest` to test key flows (mock network and DB as needed):

```bash
pip install pytest pytest-mock
pytest
```

Guidelines:

- Mock `requests` and `urllib.request.urlopen` for remote calls.
- Use a **temporary database** for integration tests.

---

## License

Source files include a BSD-like disclaimer header.  
For GitHub usage, consider adding a top-level `LICENSE` file (e.g., **BSD-3-Clause**) aligned with the headers.

---

## Credits

Copyright © 2020–2024  
**Davide Sbreviglieri**

Contributions and suggestions are welcome via Pull Requests or Issues.
