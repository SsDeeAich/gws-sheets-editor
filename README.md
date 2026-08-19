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

## 🔑 Permissions & GCP Setup (One-Time Setup)

To allow the CLI or AI agent to interact with Google Sheets, your Google Cloud environment requires the following standard setup:

1. **Google Cloud Project**:
   - Enable the **Google Sheets API** and **Google Drive API** in your GCP project.
2. **OAuth Consent Screen & Credentials**:
   - In GCP Console $\rightarrow$ **APIs & Services** $\rightarrow$ **Credentials**, create an **OAuth 2.0 Client ID** with Application type **Desktop app**.
   - Download the client secret JSON and place it at:
     ```bash
     mkdir -p ~/.config/gws
     cp <YOUR_DOWNLOADED_SECRET>.json ~/.config/gws/client_secret.json
     ```
3. **Google Sheet Permissions**:
   - The Google account logging in must have **Editor** access to the target Google Sheet.
   - *(Enterprise Workspace)*: Ensure third-party app access for your OAuth Client ID is marked as **Trusted** in Google Workspace Admin Console (**Security $\rightarrow$ API Controls $\rightarrow$ App Access Control**).

---

## 🚀 Quickstart Guide

### 1. Install Google Workspace CLI

```bash
npm install -g @googleworkspace/cli
```

Verify installation:
```bash
gws --version
```

### 2. Authenticate

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

You can run the Python script directly as a CLI tool or import `SpreadsheetEditor` into your codebase:

### Run the Full End-to-End Demo
```bash
python3 src/spreadsheet_editor.py --spreadsheet-id <YOUR_SPREADSHEET_ID> --action demo
```

### Perform an Intelligent Upsert (Update or Append)
```bash
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
