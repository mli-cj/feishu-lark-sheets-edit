# feishu-lark-sheets-edit

> OpenClaw skill — Read, write and manage Lark/Feishu Sheets via OpenAPI.

## What it does

- **Read/export** cell values from Lark/Feishu Sheets to CSV or JSON
- **Write/update** cell values (single range or batch)
- **Add** new sheet tabs to a spreadsheet
- **Clone** an existing sheet tab's values into a new tab
- **List** all sheet tabs in a spreadsheet

## Installation

```bash
clawhub install feishu-lark-sheets-edit
```

Or search and install from within OpenClaw:

```bash
clawhub search feishu-lark-sheets-edit
```

Once installed, use `/feishu-lark-sheets-edit` in any OpenClaw session.

## Quick start

```
# Read a sheet range to CSV
/feishu-lark-sheets-edit export --token TOKEN --range 'SheetId!A1:Z200' --csv /tmp/out.csv

# Write values to a range
/feishu-lark-sheets-edit write --token TOKEN --range 'SheetId!A1:C2' --values '[["a","b","c"]]'

# List all sheet tabs
/feishu-lark-sheets-edit list-sheets --token TOKEN

# Add a new sheet tab
/feishu-lark-sheets-edit add-sheet --token TOKEN --title 'NewSheet'

# Clone a sheet
/feishu-lark-sheets-edit clone-sheet --token TOKEN --source-sheet-id abc123 --title 'Copy'
```

## Requirements

- `python3` on PATH
- Feishu/Lark app credentials in `~/.openclaw/openclaw.json` (under `channels.feishu`)
- The app must have Sheets read & write permissions enabled

## Files

| File | Purpose |
|------|---------|
| `scripts/sheets_export.py` | Read/export ranges to CSV or JSON |
| `scripts/sheets_write.py` | Write cells, add/clone sheet tabs |
| `references/lark-sheets-api.md` | Lark Sheets OpenAPI reference |
