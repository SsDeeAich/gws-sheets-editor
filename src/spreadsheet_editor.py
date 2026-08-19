#!/usr/bin/env python3
"""
Intelligent Google Spreadsheet Editor (Python Implementation)
Implements the business logic defined in customer-spreadsheet-editor:
  1. Locates existing planning spreadsheet.
  2. Ensures "Agent Recommendations" tab exists with correct headers.
  3. Matches records using `recommendation_id` (Column A).
  4. Updates in-place if ID exists; appends if ID is new.
  5. Re-reads and verifies every change with an audit log.
"""

import argparse
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple


class SpreadsheetEditor:
    """Intelligent spreadsheet editor wrapping Google Workspace CLI (gws)."""

    def __init__(self, spreadsheet_id: str, tab_name: str = "Agent Recommendations"):
        self.spreadsheet_id = spreadsheet_id
        self.tab_name = tab_name
        self.headers = ["recommendation_id", "status", "date", "notes"]

    def _run_gws(self, cmd_args: List[str]) -> Dict[str, Any]:
        """Execute a gws CLI command and parse the JSON output."""
        full_cmd = ["gws"] + cmd_args
        try:
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout) if result.stdout.strip() else {}
        except subprocess.CalledProcessError as e:
            # Check if error output has JSON
            err_msg = e.stderr or e.stdout
            try:
                err_json = json.loads(err_msg)
                raise RuntimeError(f"GWS API Error: {err_json.get('error', {}).get('message', err_msg)}")
            except Exception:
                raise RuntimeError(f"GWS Command Failed: {err_msg.strip()}")

    def get_sheet_metadata(self) -> Dict[str, Any]:
        """Fetch spreadsheet metadata and list existing sheet tabs."""
        params = json.dumps({"spreadsheetId": self.spreadsheet_id})
        return self._run_gws(["sheets", "spreadsheets", "get", "--params", params])

    def ensure_tab_exists(self) -> bool:
        """Verify tab exists; create and initialize headers if missing."""
        meta = self.get_sheet_metadata()
        sheets = [s.get("properties", {}).get("title") for s in meta.get("sheets", [])]

        if self.tab_name not in sheets:
            print(f"[*] Tab '{self.tab_name}' not found. Creating tab via batchUpdate...")
            params = json.dumps({"spreadsheetId": self.spreadsheet_id})
            body = json.dumps({
                "requests": [
                    {"addSheet": {"properties": {"title": self.tab_name}}}
                ]
            })
            self._run_gws(["sheets", "spreadsheets", "batchUpdate", "--params", params, "--json", body])
            print(f"[+] Tab '{self.tab_name}' created successfully.")

            # Initialize Headers in Row 1
            print(f"[*] Initializing headers in Row 1 ({self.tab_name}!A1:D1)...")
            header_params = json.dumps({
                "spreadsheetId": self.spreadsheet_id,
                "range": f"{self.tab_name}!A1:D1",
                "valueInputOption": "USER_ENTERED"
            })
            header_body = json.dumps({"values": [self.headers]})
            self._run_gws(["sheets", "spreadsheets", "values", "update", "--params", header_params, "--json", header_body])
            print("[+] Headers initialized: " + ", ".join(self.headers))
            return True
        else:
            print(f"[✓] Tab '{self.tab_name}' already exists.")
            return False

    def fetch_all_records(self) -> List[List[str]]:
        """Fetch all rows from the target tab."""
        params = json.dumps({
            "spreadsheetId": self.spreadsheet_id,
            "range": f"{self.tab_name}!A:D"
        })
        res = self._run_gws(["sheets", "spreadsheets", "values", "get", "--params", params])
        return res.get("values", [])

    def find_row_by_id(self, rec_id: str) -> Optional[Tuple[int, List[str]]]:
        """Scan Column A for recommendation_id and return (1-indexed row number, row values)."""
        rows = self.fetch_all_records()
        for idx, row in enumerate(rows, start=1):
            if row and row[0].strip() == rec_id.strip():
                return idx, row
        return None

    def upsert_recommendation(self, rec_id: str, status: str, date: str, notes: str) -> Dict[str, Any]:
        """Intelligently update in-place if ID exists, or append if new."""
        existing = self.find_row_by_id(rec_id)
        record_values = [rec_id, status, date, notes]

        if existing:
            row_idx, old_values = existing
            print(f"[*] Match found for '{rec_id}' at Row {row_idx}. Executing in-place UPDATE...")
            params = json.dumps({
                "spreadsheetId": self.spreadsheet_id,
                "range": f"{self.tab_name}!A{row_idx}:D{row_idx}",
                "valueInputOption": "USER_ENTERED"
            })
            body = json.dumps({"values": [record_values]})
            self._run_gws(["sheets", "spreadsheets", "values", "update", "--params", params, "--json", body])
            
            audit = {
                "action": "UPDATE",
                "row": row_idx,
                "recommendation_id": rec_id,
                "previous_state": old_values,
                "new_state": record_values
            }
        else:
            print(f"[*] No match found for '{rec_id}'. Executing APPEND...")
            params = json.dumps({
                "spreadsheetId": self.spreadsheet_id,
                "range": f"{self.tab_name}!A:D",
                "valueInputOption": "USER_ENTERED"
            })
            body = json.dumps({"values": [record_values]})
            self._run_gws(["sheets", "spreadsheets", "values", "append", "--params", params, "--json", body])

            audit = {
                "action": "APPEND",
                "recommendation_id": rec_id,
                "new_state": record_values
            }

        # Step 8: Re-read after write to verify
        self.verify_record(rec_id)
        return audit

    def verify_record(self, rec_id: str) -> List[str]:
        """Re-read modified record from sheet to verify persistence."""
        match = self.find_row_by_id(rec_id)
        if not match:
            raise ValueError(f"Verification Failed: Record '{rec_id}' not found after mutation!")
        row_idx, values = match
        print(f"[✓] Verification successful: Row {row_idx} -> {values}")
        return values

    def print_summary_table(self):
        """Print clean summary table of all recommendations."""
        rows = self.fetch_all_records()
        if not rows:
            print("[!] No records found in sheet.")
            return

        headers = rows[0]
        data = rows[1:] if len(rows) > 1 else []

        print("\n" + "=" * 80)
        print(f"Current State: '{self.tab_name}'")
        print("=" * 80)
        row_format = "{:<20} {:<15} {:<15} {:<30}"
        print(row_format.format(*headers))
        print("-" * 80)
        for r in data:
            # Pad row if less than 4 columns
            padded = r + [""] * (4 - len(r))
            print(row_format.format(*padded[:4]))
        print("=" * 80 + "\n")


def run_full_demo(spreadsheet_id: str):
    """Executes the complete POC workflow."""
    print(f"\n🚀 Running End-to-End POC on Spreadsheet: {spreadsheet_id}\n")
    editor = SpreadsheetEditor(spreadsheet_id)

    print("--- STEP 1 & 2: Initialize Tab & Headers ---")
    editor.ensure_tab_exists()

    print("\n--- STEP 3: Append New Recommendations (REC-001 & REC-002) ---")
    editor.upsert_recommendation("REC-001", "Pending", "2026-08-19", "Needs review by Sales Ops")
    editor.upsert_recommendation("REC-002", "Approved", "2026-08-19", "Ready for Q3 pipeline")

    print("\n--- STEP 4: In-Place Update (REC-001 -> Approved) ---")
    editor.upsert_recommendation("REC-001", "Approved", "2026-08-19", "Reviewed by Sales Ops")

    print("\n--- STEP 5: Final State & Verification ---")
    editor.print_summary_table()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Intelligent Google Sheets Editor CLI & SDK")
    parser.add_argument("--spreadsheet-id", required=True, help="Target Google Spreadsheet ID")
    parser.add_argument("--tab", default="Agent Recommendations", help="Tab name (default: 'Agent Recommendations')")
    parser.add_argument("--action", choices=["init", "list", "upsert", "demo"], default="demo", help="Action to execute")
    parser.add_argument("--id", help="Recommendation ID (e.g. REC-001)")
    parser.add_argument("--status", help="Status (e.g. Approved, Pending, Rejected)")
    parser.add_argument("--date", default="2026-08-19", help="Date (YYYY-MM-DD)")
    parser.add_argument("--notes", default="", help="Notes / comments")

    args = parser.parse_args()
    ed = SpreadsheetEditor(args.spreadsheet_id, tab_name=args.tab)

    if args.action == "demo":
        run_full_demo(args.spreadsheet_id)
    elif args.action == "init":
        ed.ensure_tab_exists()
    elif args.action == "list":
        ed.print_summary_table()
    elif args.action == "upsert":
        if not args.id or not args.status:
            print("Error: --id and --status are required for upsert action.", file=sys.stderr)
            sys.exit(1)
        audit = ed.upsert_recommendation(args.id, args.status, args.date, args.notes)
        print(json.dumps(audit, indent=2))
