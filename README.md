# Google Workspace CLI (`gws`) — Intelligent Spreadsheet Editor

This repository demonstrates how AI agents and automated Python applications can intelligently read, create tabs, append records, and perform in-place row-level updates on existing Google Sheets using the **Google Workspace CLI (`gws`)** and agentic skill definitions.

---

## 🎯 Architecture & Business Rules

Both the AI Agent Skill and Python SDK enforce the following rules:

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

## 📁 Repository Structure

```
.
├── README.md                                  # Documentation & quickstart guide
├── demo.sh                                    # Bash CLI execution script
├── docs/
│   └── skills.md                              # Skills reference
├── skills/
│   ├── customer-spreadsheet-editor/           # Agent skill (rules & matching logic)
│   │   └── SKILL.md
│   └── gws-sheets/                            # Google Sheets tool definition
│       └── SKILL.md
└── src/
    └── spreadsheet_editor.py                  # Python implementation & CLI
```

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

Authenticate `gws` with your Google account:

```bash
# Log in with required Google Sheets & Drive scopes
gws auth login --services sheets,drive
```

Check authentication status:
```bash
gws auth status
```

---

## 🐍 Using the Python Implementation

You can run the Python script directly as a CLI tool or import `SpreadsheetEditor` into your Python codebase:

### Run the Full End-to-End Demo
```bash
python3 src/spreadsheet_editor.py --spreadsheet-id <YOUR_SPREADSHEET_ID> --action demo
```

### Perform an Intelligent Upsert (Update or Append)
```bash
# Updates row in-place if REC-001 exists, or appends if new:
python3 src/spreadsheet_editor.py \
  --spreadsheet-id <YOUR_SPREADSHEET_ID> \
  --action upsert \
  --id REC-001 \
  --status Approved \
  --notes "Reviewed by Sales Ops"
```

### List Current Recommendations
```bash
python3 src/spreadsheet_editor.py --spreadsheet-id <YOUR_SPREADSHEET_ID> --action list
```

### Python Code Example
```python
from src.spreadsheet_editor import SpreadsheetEditor

editor = SpreadsheetEditor(spreadsheet_id="YOUR_SPREADSHEET_ID")

# Ensure tab exists
editor.ensure_tab_exists()

# Ingest / update recommendation
editor.upsert_recommendation(
    rec_id="REC-001",
    status="Approved",
    date="2026-08-19",
    notes="Reviewed by Sales Ops"
)

# Print current state
editor.print_summary_table()
```

---

## 🤖 Using with AI Agents (Antigravity / Gemini CLI)

When this repo is opened in an agentic coding environment (e.g. Antigravity), the agent automatically reads [`skills/customer-spreadsheet-editor/SKILL.md`](skills/customer-spreadsheet-editor/SKILL.md).

You can prompt the agent directly:
> *"Add a new recommendation for account Acme Corp with ID REC-003, status Pending, and date 2026-08-20."*  
> *"Update REC-001 to Approved in the spreadsheet."*

---

## 🔒 Security & Privacy

- **Zero Stored Credentials**: No API keys, client secrets, or OAuth tokens are committed to this repository.
- **Enterprise Ready**: Access permissions are governed entirely by Google Drive ACLs and Google Cloud IAM.
