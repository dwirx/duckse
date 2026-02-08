#!/usr/bin/env python3
"""Run duckse search first, then scrape resulting URLs with Firecrawl."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from urllib.error import HTTPError, URLError


def build_duckse_command(
    *,
    query: str,
    search_type: str = "text",
    max_results: int = 10,
    region: str = "us-en",
    timelimit: str | None = None,
    backend: str = "auto",
) -> list[str]:
    cmd = [
        "duckse",
        query,
        "--json",
        "--type",
        search_type,
        "--max-results",
        str(max_results),
        "--region",
        region,
        "--backend",
        backend,
    ]
    if timelimit:
        cmd.extend(["--timelimit", timelimit])
    return cmd


def run_duckse_search(command: list[str]) -> list[dict]:
    try:
        proc = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        print("Error: command 'duckse' tidak ditemukan.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as exc:
        print("Error: duckse search gagal.", file=sys.stderr)
        if exc.stderr:
            print(exc.stderr.strip(), file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print("Error: output duckse bukan JSON valid.", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print("Error: format output duckse tidak didukung (harus list).", file=sys.stderr)
        sys.exit(1)
    return data


def extract_urls(results: list[dict]) -> list[str]:
    seen: set[str] = set()
    urls: list[str] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        url = item.get("url") or item.get("href")
        if isinstance(url, str) and url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def firecrawl_scrape(url: str, api_key: str, formats: list[str]) -> dict:
    req_url = "https://api.firecrawl.dev/v1/scrape"
    payload = {
        "url": url,
        "formats": formats,
        "onlyMainContent": True,
    }
    data = json.dumps(payload).encode()

    req = urllib.request.Request(
        req_url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
            return json.loads(resp.read().decode())
    except HTTPError as exc:
        body = exc.read().decode(errors="ignore")
        return {
            "success": False,
            "url": url,
            "error": f"HTTP {exc.code}",
            "details": body,
        }
    except URLError as exc:
        return {
            "success": False,
            "url": url,
            "error": "URL error",
            "details": str(exc),
        }


def parse_formats(args: argparse.Namespace) -> list[str]:
    formats: list[str] = []
    if args.markdown:
        formats.append("markdown")
    if args.html:
        formats.append("html")
    if args.screenshot:
        formats.append("screenshot")
    return formats or ["markdown"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cari dengan duckse lalu scrape URL hasilnya via Firecrawl"
    )
    parser.add_argument("query", help="Search query")
    parser.add_argument("--type", default="text", choices=["text", "news"], help="Tipe search duckse")
    parser.add_argument("--max-results", type=int, default=10, help="Jumlah hasil dari duckse")
    parser.add_argument("--scrape-limit", type=int, default=5, help="Maks URL yang di-scrape")
    parser.add_argument("--region", default="us-en", help="Region duckse")
    parser.add_argument("--timelimit", choices=["d", "w", "m", "y"], help="Filter waktu duckse")
    parser.add_argument("--backend", default="auto", help="Backend duckse")

    parser.add_argument("--markdown", action="store_true", default=True, help="Include markdown")
    parser.add_argument("--html", action="store_true", help="Include html")
    parser.add_argument("--screenshot", action="store_true", help="Include screenshot")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("Error: FIRECRAWL_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    duckse_cmd = build_duckse_command(
        query=args.query,
        search_type=args.type,
        max_results=args.max_results,
        region=args.region,
        timelimit=args.timelimit,
        backend=args.backend,
    )
    search_results = run_duckse_search(duckse_cmd)
    urls = extract_urls(search_results)[: args.scrape_limit]

    if not urls:
        print("Tidak ada URL dari hasil duckse.", file=sys.stderr)
        sys.exit(1)

    formats = parse_formats(args)
    scraped = [firecrawl_scrape(url, api_key, formats) for url in urls]

    output = {
        "query": args.query,
        "duckse_command": duckse_cmd,
        "urls": urls,
        "scraped": scraped,
    }

    if args.json:
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    print(f"Query: {args.query}")
    print(f"URLs selected: {len(urls)}")
    for idx, entry in enumerate(scraped, start=1):
        if entry.get("success") and "data" in entry:
            metadata = entry["data"].get("metadata", {})
            print(f"\n{idx}. {metadata.get('title', 'N/A')}")
            print(f"   URL: {metadata.get('sourceURL', urls[idx - 1])}")
            if "markdown" in entry["data"]:
                snippet = entry["data"]["markdown"][:300].replace("\n", " ")
                print(f"   Preview: {snippet}...")
        else:
            print(f"\n{idx}. Gagal scrape")
            print(f"   URL: {entry.get('url', urls[idx - 1])}")
            print(f"   Error: {entry.get('error', 'unknown')}")


if __name__ == "__main__":
    main()
