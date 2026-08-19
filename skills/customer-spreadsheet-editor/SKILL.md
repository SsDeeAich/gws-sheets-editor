---
name: customer-spreadsheet-editor
description: Business rules for updating the customer's planning spreadsheet.
---
# Customer Spreadsheet Editor
When updating the customer's planning spreadsheet, strictly follow these rules:
1. Never create a completely new spreadsheet. Locate and use the supplied existing spreadsheet.
2. Use the tab named "Agent Recommendations".
3. If the tab doesn't exist, create it using structural batchUpdate.
4. Before writing, read the current headers and data.
5. Match records using `recommendation_id` (Column A).
6. If the `recommendation_id` exists: update the existing row.
7. If the `recommendation_id` does not exist: append a new row.
8. Re-read the modified rows after every write to verify the change.
9. Report exactly what changed to the user.
