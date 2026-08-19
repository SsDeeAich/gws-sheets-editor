#!/usr/bin/env bash
set -euo pipefail

# Check for Spreadsheet ID argument
if [ -z "${1:-}" ]; then
  echo "Usage: ./demo.sh <SPREADSHEET_ID>"
  echo "Example: ./demo.sh 19SxnUWCjuJK0DVhbQwXFFYnI4TD9ad7_fM-iPlnv2zs"
  exit 1
fi

SPREADSHEET_ID="$1"
TAB_NAME="Agent Recommendations"

echo "=== 1. Checking spreadsheet metadata ==="
gws sheets spreadsheets get --params "{\"spreadsheetId\": \"${SPREADSHEET_ID}\"}" > /dev/null 2>&1 || true

echo "=== 2. Creating tab: ${TAB_NAME} ==="
gws sheets spreadsheets batchUpdate \
  --params "{\"spreadsheetId\": \"${SPREADSHEET_ID}\"}" \
  --json "{\"requests\": [{\"addSheet\": {\"properties\": {\"title\": \"${TAB_NAME}\"}}}]}" \
  || echo "Tab may already exist, proceeding..."

echo "=== 3. Initializing Column Headers ==="
gws sheets spreadsheets values update \
  --params "{\"spreadsheetId\": \"${SPREADSHEET_ID}\", \"range\": \"${TAB_NAME}!A1:D1\", \"valueInputOption\": \"USER_ENTERED\"}" \
  --json '{"values": [["recommendation_id", "status", "date", "notes"]]}'

echo "=== 4. Appending Initial Recommendations (REC-001 & REC-002) ==="
gws sheets spreadsheets values append \
  --params "{\"spreadsheetId\": \"${SPREADSHEET_ID}\", \"range\": \"${TAB_NAME}!A:D\", \"valueInputOption\": \"USER_ENTERED\"}" \
  --json '{
    "values": [
      ["REC-001", "Pending", "2026-08-19", "Needs review by Sales Ops"],
      ["REC-002", "Approved", "2026-08-19", "Ready for Q3 pipeline"]
    ]
  }'

echo "=== 5. Performing In-Place Update (REC-001 -> Approved) ==="
gws sheets spreadsheets values update \
  --params "{\"spreadsheetId\": \"${SPREADSHEET_ID}\", \"range\": \"${TAB_NAME}!A2:D2\", \"valueInputOption\": \"USER_ENTERED\"}" \
  --json '{"values": [["REC-001", "Approved", "2026-08-19", "Reviewed by Sales Ops"]]}'

echo "=== 6. Fetching Final Table State ==="
gws sheets spreadsheets values get \
  --params "{\"spreadsheetId\": \"${SPREADSHEET_ID}\", \"range\": \"${TAB_NAME}!A:D\"}" \
  --format table

echo "=== Demo completed successfully! ==="
