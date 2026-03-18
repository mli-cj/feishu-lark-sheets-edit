---
name: feishu_lark_sheets_edit
description: "Read, write and manage Lark/Feishu Sheets (spreadsheets) and download Lark/Feishu cloud files via Lark OpenAPI. Reads Feishu app credentials (appId/appSecret) from ~/.openclaw/openclaw.json to authenticate with the Lark OpenAPI. Use when a user provides a Lark/Feishu sheet link (URL path like /sheets/TOKEN) and you need to fetch cell values, write/update cells, add/clone sheet tabs, convert to CSV/JSON, or feed the data into summaries/reports/analysis. Also use when a user provides a Lark/Feishu file link (URL path like /file/TOKEN) and needs to download the file (PDF, etc.) locally. Triggers: 'feishu sheet', 'lark sheet', 'spreadsheet', 'write to sheet', 'update sheet', 'export sheet', 'feishu file', 'lark file', 'download file', 'feishu download', 'lark download', 'cloud file'."
user-invocable: true
metadata: {"clawdbot": {"requires": {"bins": ["python3"]}, "os": ["darwin", "linux", "win32"], "files": ["scripts/sheets_export.py", "scripts/sheets_write.py", "scripts/file_download.py"]}}
---

# Lark/Feishu Sheets & File Download

Read, write and manage Lark/Feishu Sheets, and download Lark/Feishu cloud files, by calling the official OpenAPI from local scripts.

## Prerequisites

- `python3` on PATH
- Feishu/Lark app credentials configured in `~/.openclaw/openclaw.json` under `channels.feishu`:
  ```json
  {
    "channels": {
      "feishu": {
        "appId": "cli_xxx",
        "appSecret": "xxx",
        "domain": "feishu"
      }
    }
  }
  ```
- The Feishu/Lark app must have **Sheets read & write** permissions and **Drive file download** permissions enabled in the developer console.
- The target spreadsheet/file must be shared with the app/bot identity.

## Quick Start

### Get spreadsheet token from the URL

Example URL:
`https://.../sheets/YOUR_SPREADSHEET_TOKEN?sheet=SHEET_ID`

- `spreadsheet_token` = `YOUR_SPREADSHEET_TOKEN`
- `sheet` query param (often a sheetId) = `SHEET_ID`

### Read / Export

```bash
# Export a single range to CSV
python3 {baseDir}/scripts/sheets_export.py \
  --token YOUR_SPREADSHEET_TOKEN \
  --range 'SHEET_ID!A1:Z200' \
  --csv /tmp/sheet.csv

# Or export to JSON (recommended for multi-range)
python3 {baseDir}/scripts/sheets_export.py \
  --url 'https://xxx.larksuite.com/sheets/YOUR_SPREADSHEET_TOKEN?sheet=SHEET_ID' \
  --range 'SHEET_ID!A1:Z200' \
  --json /tmp/sheet.json
```

Then load `/tmp/sheet.csv` or `/tmp/sheet.json` and continue with analysis/summarization.

### Write / Update

```bash
# List all sheet tabs
python3 {baseDir}/scripts/sheets_write.py \
  --token YOUR_SPREADSHEET_TOKEN list-sheets

# Write values to a single range
python3 {baseDir}/scripts/sheets_write.py \
  --token YOUR_SPREADSHEET_TOKEN \
  write --range 'SheetId!A1:C2' --values '[["a","b","c"],["d","e","f"]]'

# Write values from a JSON file
python3 {baseDir}/scripts/sheets_write.py \
  --token YOUR_SPREADSHEET_TOKEN \
  write --range 'SheetId!A1:C2' --values-file /tmp/data.json

# Batch write multiple ranges at once
python3 {baseDir}/scripts/sheets_write.py \
  --token YOUR_SPREADSHEET_TOKEN \
  batch-write --batch '[{"range":"Sheet1!A1:B1","values":[["x","y"]]},{"range":"Sheet1!A2:B2","values":[["1","2"]]}]'

# Add a new sheet tab
python3 {baseDir}/scripts/sheets_write.py \
  --token YOUR_SPREADSHEET_TOKEN \
  add-sheet --title 'NewSheet'

# Clone an existing sheet's values into a new tab
python3 {baseDir}/scripts/sheets_write.py \
  --token YOUR_SPREADSHEET_TOKEN \
  clone-sheet --source-sheet-id abc123 --title 'ClonedSheet' --clone-range 'A1:Z200'
```

### Using a URL instead of --token

Both scripts accept `--url` to auto-extract the spreadsheet token:

```bash
python3 {baseDir}/scripts/sheets_write.py \
  --url 'https://xxx.larksuite.com/sheets/YOUR_SPREADSHEET_TOKEN?sheet=SHEET_ID' \
  write --range 'SHEET_ID!A1:B1' --values '[["hello","world"]]'
```

---

## File Download

Download cloud files (PDF, documents, etc.) from Lark/Feishu Drive.

### Get file token from the URL

Example URL:
`https://.../file/YOUR_FILE_TOKEN`

- `file_token` = `YOUR_FILE_TOKEN`

### Download a file

```bash
# Download by URL
python3 {baseDir}/scripts/file_download.py \
  --url "https://.../file/YOUR_FILE_TOKEN" \
  --out /tmp/report.pdf

# Download by file token directly
python3 {baseDir}/scripts/file_download.py \
  --file-token YOUR_FILE_TOKEN \
  --out /tmp/report.pdf
```

### Reading downloaded PDF files

After downloading, use the `Read` tool to read the PDF content directly:

```
Read file: /tmp/report.pdf
```

For large PDFs (more than 10 pages), specify a page range to avoid exceeding limits:

```
Read file: /tmp/report.pdf  pages: "1-10"
```

The typical workflow is: **download the file → read it with the Read tool → summarize/analyze the content**.

---

## Write Subcommands Reference

| Subcommand     | Description                                      | Key flags                                         |
|----------------|--------------------------------------------------|----------------------------------------------------|
| `list-sheets`  | List all sheet tabs (id, title, index)           | —                                                  |
| `write`        | Write values to a single range                   | `--range`, `--values` or `--values-file`           |
| `batch-write`  | Write values to multiple ranges in one call      | `--batch` or `--batch-file`                        |
| `add-sheet`    | Create a new empty sheet tab                     | `--title`                                          |
| `clone-sheet`  | Clone values from an existing sheet to a new tab | `--source-sheet-id`, `--title`, `--clone-range`    |

All subcommands support `--dry-run` to preview without executing.

---

## Notes / Gotchas

- **Range format:** the API accepts `"{sheetId}!A1:Z200"` or `"{sheetTitle}!A1:Z200"`.
  - If you don't know the sheet title, use `list-sheets` first, or start with the `sheet=` value from the URL.
- **Large sheets:** export only the needed columns/rows first; widen the range iteratively.
- **Values format:** must be a JSON array of arrays (rows x columns), e.g. `[["a","b"],["c","d"]]`.
- **Secrets:** the script reads `appId/appSecret` from `~/.openclaw/openclaw.json`. Do not print or paste those credentials into chat.

---

## Troubleshooting

- **403 / permission errors:**
  - Confirm the sheet/file has been shared with the app/bot identity.
  - Confirm the Lark/Feishu app has the required permissions (Sheets read & write, Drive file download) enabled in the developer console.
- **`values_batch_get failed` / `values_batch_update failed` with non-zero code:**
  - Most often a bad range string. Try a smaller range or verify the sheetId/title via `list-sheets`.
- **`addSheet failed`:**
  - The title may already exist. Sheet titles must be unique within a spreadsheet.

---

## External Endpoints

This skill makes outbound requests to the following Lark/Feishu OpenAPI endpoints only:

| URL | Purpose |
|-----|---------|
| `https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal` | Obtain tenant access token |
| `https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/*/sheets/query` | List sheet tabs |
| `https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/*/values_batch_get` | Read cell values |
| `https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/*/values_batch_update` | Write cell values |
| `https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/*/sheets_batch_update` | Add/manage sheet tabs |
| `https://open.feishu.cn/open-apis/drive/v1/files/*/download` | Download file content |

For Lark (international) users, the base URL is `https://open.larksuite.com` instead.

---

## Security & Privacy

- **Credentials are local.** `appId/appSecret` are read from `~/.openclaw/openclaw.json` and only sent to the official Feishu/Lark OpenAPI for token exchange.
- **No data leaves the Feishu ecosystem.** All read/write operations go through the official Lark OpenAPI.
- **Scripts are sandboxed.** They only access the OpenClaw config file and the target spreadsheet. No other files or environment variables are read.
