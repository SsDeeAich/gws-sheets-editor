# Google Workspace CLI (`gws`) — Intelligent Spreadsheet Editor POC

This repository contains a POC demonstrating how AI agents can intelligently read, create tabs, append records, and perform in-place row-level updates on existing Google Sheets using the **Google Workspace CLI (`gws`)** and agentic skill definitions.

---

## 🎯 Architecture & Business Rules

Agent behavior is governed by the custom skill defined in [`skills/customer-spreadsheet-editor/SKILL.md`](skills/customer-spreadsheet-editor/SKILL.md):

1. **Preserve Existing Files**: Never creates duplicate files; operates strictly on the targeted spreadsheet.
2. **Dedicated Tab**: Uses the tab named `"Agent Recommendations"`.
3. **Automatic Provisioning**: If the tab doesn't exist, provisions it dynamically using structural `batchUpdate`.
4. **Read Before Write**: Always fetches current headers and row data prior to mutation.
5. **Primary Key Matching**: Matches records using `recommendation_id` in **Column A**.
6. **Smart Upsert Logic**:
   - If `recommendation_id` exists $\rightarrow$ Executes an in-place **Row Update**.
   - If `recommendation_id` is new $\rightarrow$ Executes a **Row Append**.
7. **Read-After-Write Verification**: Re-reads modified ranges to guarantee persistence.
8. **Audit Trail**: Generates a clean diff report of every mutation performed.

---

## 🚀 Quickstart Guide

### 1. Prerequisites

Install the Google Workspace CLI globally:

```bash
npm install -g @googleworkspace/cli
```

Verify installation:
```bash
gws --version
```

### 2. Authentication

Authenticate `gws` with your Google Cloud project and Google account:

```bash
# Set up GCP OAuth Client (if not already configured)
gws auth setup

# Log in with required Google Sheets & Drive scopes
gws auth login --services sheets,drive
```

Check authentication status anytime:
```bash
gws auth status
```

---

## 📋 Command Reference & Workflow

### Step 1: Inspect Spreadsheet & Create Tab (if missing)

```bash
# Check existing sheets
gws sheets spreadsheets get \
  --params '{"spreadsheetId": "<SPREADSHEET_ID>"}'

# Create the "Agent Recommendations" tab
gws sheets spreadsheets batchUpdate \
  --params '{"spreadsheetId": "<SPREADSHEET_ID>"}' \
  --json '{"requests": [{"addSheet": {"properties": {"title": "Agent Recommendations"}}}]}'
```

### Step 2: Initialize Column Headers (`A1:D1`)

```bash
gws sheets spreadsheets values update \
  --params '{"spreadsheetId": "<SPREADSHEET_ID>", "range": "Agent Recommendations!A1:D1", "valueInputOption": "USER_ENTERED"}' \
  --json '{"values": [["recommendation_id", "status", "date", "notes"]]}'
```

### Step 3: Append New Records

```bash
gws sheets spreadsheets values append \
  --params '{"spreadsheetId": "<SPREADSHEET_ID>", "range": "Agent Recommendations!A:D", "valueInputOption": "USER_ENTERED"}' \
  --json '{
    "values": [
      ["REC-001", "Pending", "2026-08-19", "Needs review by Sales Ops"],
      ["REC-002", "Approved", "2026-08-19", "Ready for Q3 pipeline"]
    ]
  }'
```

### Step 4: Intelligent In-Place Update (Upsert)

```bash
# 1. Fetch current data to locate row index by recommendation_id
gws sheets spreadsheets values get \
  --params '{"spreadsheetId": "<SPREADSHEET_ID>", "range": "Agent Recommendations!A:D"}'

# 2. Update specific row (e.g. Row 2 for REC-001)
gws sheets spreadsheets values update \
  --params '{"spreadsheetId": "<SPREADSHEET_ID>", "range": "Agent Recommendations!A2:D2", "valueInputOption": "USER_ENTERED"}' \
  --json '{"values": [["REC-001", "Approved", "2026-08-19", "Reviewed by Sales Ops"]]}'
```

### Step 5: Read & Verify Final Table

```bash
gws sheets spreadsheets values get \
  --params '{"spreadsheetId": "<SPREADSHEET_ID>", "range": "Agent Recommendations!A:D"}' \
  --format table
```

---

## 📁 Repository Structure

```
.
├── README.md                                  # Customer documentation & quickstart
├── demo.sh                                    # Automated demo script
├── docs/
│   └── skills.md                              # Google Workspace skills index
└── skills/
    ├── customer-spreadsheet-editor/           # Custom business rules skill
    │   └── SKILL.md
    ├── gws-sheets/                            # Core Google Sheets skill
    ├── gws-sheets-append/                     # Append helper skill
    ├── gws-sheets-read/                       # Read helper skill
    └── ...                                    # Additional Workspace skills
```

---

## 🔒 Security & Privacy

- **No Stored Credentials**: No API keys, client secrets, or OAuth tokens are committed to this repository.
- **Role-Based Access**: Access to spreadsheets adheres strictly to standard Google Drive permissions and ACLs.
