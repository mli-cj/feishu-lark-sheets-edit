#!/usr/bin/env python3
"""Download a Lark/Feishu file by file link using the OpenClaw Feishu app credentials.

- Reads appId/appSecret from ~/.openclaw/openclaw.json (OpenClaw config)
- Fetches tenant_access_token
- Calls Feishu/Lark Drive OpenAPI to download the file content

Usage examples:
  python3 file_download.py --url "https://.../file/YOUR_FILE_TOKEN" --out /tmp/file.bin
  python3 file_download.py --file-token YOUR_FILE_TOKEN --out report.pdf

Notes:
- This script targets the Drive File Download API endpoint:
  GET /open-apis/drive/v1/files/:file_token/download
- The caller must ensure the app/bot has permission to access the file (shared to the app).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request

OPENCLAW_CONFIG = os.environ.get(
    "OPENCLAW_CONFIG",
    os.path.join(os.path.expanduser("~"), ".openclaw", "openclaw.json"),
)


def _read_openclaw_feishu_config(path: str = OPENCLAW_CONFIG) -> tuple[str, str, str]:
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    feishu = (cfg.get("channels") or {}).get("feishu") or {}
    app_id = feishu.get("appId")
    app_secret = feishu.get("appSecret")
    domain = feishu.get("domain") or "feishu"  # "lark" or "feishu"

    if not app_id or not app_secret:
        raise RuntimeError(
            f"Missing channels.feishu.appId/appSecret in {path}. "
            "Run `openclaw configure` or set OPENCLAW_CONFIG."
        )

    return app_id, app_secret, domain


def _base_url(domain: str) -> str:
    domain = (domain or "").lower().strip()
    if domain == "lark":
        return "https://open.larksuite.com"
    return "https://open.feishu.cn"


def _http_json(method: str, url: str, headers: dict[str, str] | None = None, body: dict | None = None, timeout: int = 30):
    import json as _json

    data = None
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)

    if body is not None:
        data = _json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=req_headers, method=method.upper())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    try:
        return _json.loads(raw)
    except _json.JSONDecodeError:
        raise RuntimeError(f"Non-JSON response from {url}: {raw[:2000]}")


def _get_tenant_access_token(app_id: str, app_secret: str, base: str) -> str:
    url = base + "/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}
    j = _http_json("POST", url, body=payload)

    if j.get("code") != 0:
        raise RuntimeError(f"Failed to get tenant_access_token: code={j.get('code')} msg={j.get('msg')}")

    token = (j.get("tenant_access_token") or "").strip()
    if not token:
        raise RuntimeError("tenant_access_token missing in response")
    return token


def _extract_file_token(url: str) -> str | None:
    """Extract file token from a Lark/Feishu file URL.

    Example:
      https://xxx.larksuite.com/file/YOUR_FILE_TOKEN
      -> file_token = YOUR_FILE_TOKEN
    """

    m = re.search(r"/file/([A-Za-z0-9]+)", url)
    return m.group(1) if m else None


def _download_file(file_token: str, access_token: str, base: str, out_path: str, timeout: int = 300):
    """Download file content via Feishu Drive API and save to out_path.

    API: GET /open-apis/drive/v1/files/:file_token/download
    The response is binary file content (not JSON).
    """

    endpoint = f"{base}/open-apis/drive/v1/files/{file_token}/download"
    headers = {"Authorization": f"Bearer {access_token}"}

    req = urllib.request.Request(endpoint, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()

    with open(out_path, "wb") as f:
        f.write(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", help="Lark/Feishu file URL")
    ap.add_argument("--file-token", help="File token (the part after /file/)")
    ap.add_argument("--out", required=True, help="Output path for downloaded file")
    args = ap.parse_args()

    file_token = args.file_token
    if not file_token and args.url:
        file_token = _extract_file_token(args.url)

    if not file_token:
        raise SystemExit("Missing file token. Provide --file-token or --url containing /file/<token>.")

    app_id, app_secret, domain = _read_openclaw_feishu_config()
    base = _base_url(domain)
    access_token = _get_tenant_access_token(app_id, app_secret, base)

    _download_file(file_token, access_token, base, args.out)

    print(f"OK: downloaded file_token={file_token} to {args.out}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
