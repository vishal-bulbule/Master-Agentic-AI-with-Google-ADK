#!/usr/bin/env bash
# Author: Vishal Bulbule
# Date: 2026-09-22

# Create the demo folder that the filesystem MCP server is allowed to access.
#
# macOS / Linux:  bash setup_demo_folder.sh
# Other folder:   MCP_DEMO_DIR="$HOME/mcp-demo" bash setup_demo_folder.sh
# Windows:        create a folder such as C:\Users\<you>\mcp-demo and add
#                 three .txt files to it by hand.

set -euo pipefail

DEMO_DIR="${MCP_DEMO_DIR:-/tmp/mcp-demo}"

echo "Creating $DEMO_DIR"
mkdir -p "$DEMO_DIR"

cat > "$DEMO_DIR/readme.txt" <<'EOF'
# Demo folder

This folder is exposed to an MCP host through the filesystem MCP server.

Files here:
- readme.txt        (this file)
- pricing.txt       (sample SaaS pricing tiers)
- meeting_notes.txt (sample planning meeting notes)

Questions to try:
  "Summarize what is in this folder."
  "Compare the pricing tiers in pricing.txt."
  "What action items came out of the meeting?"
EOF

cat > "$DEMO_DIR/pricing.txt" <<'EOF'
Example Cloud Monitoring SaaS - Pricing (sample data)

STARTER         USD 29 / month
  - 5 monitored services
  - 7-day metric retention
  - Email alerts

TEAM            USD 99 / month
  - Everything in Starter
  - 50 monitored services
  - 30-day metric retention
  - Slack and PagerDuty alerts

ENTERPRISE      USD 499 / month (annual contract)
  - Everything in Team
  - Unlimited services
  - 13-month retention
  - SSO and audit logs
EOF

cat > "$DEMO_DIR/meeting_notes.txt" <<'EOF'
Q3 Planning - 14 July (sample data)
Attendees: Priya, Karan, Anjali, Sam

Decisions
---------
1. Ship the alerting API v2 by end of September.
2. Move all integration tests into the main repository.
3. Use MCP for the new AI assistant integrations instead of custom adapters.

Action items
------------
- [Priya]   Draft the alerting API v2 spec by 21 July.
- [Karan]   Set up the Cloud Run deploy pipeline for the MCP server.
- [Anjali]  Write the migration guide for v1 API users.
- [Sam]     Load-test the new ingestion path.

Risks
-----
- The v1 API has undocumented behavior that some customers rely on.
- Deploy pipeline depends on a shared service account that needs review.
EOF

echo "Done. Files in $DEMO_DIR:"
ls -1 "$DEMO_DIR"
