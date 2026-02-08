---
name: web-search
description: Use when users need web search, current news lookup, image/video discovery, or web extraction workflows. Uses duckse for DDGS metasearch and native Firecrawl commands for scraping/crawling.
---

# Web Search (duckse + Firecrawl)

## Overview

Skill ini memakai `duckse` sebagai satu pintu untuk:
- metasearch DDGS (`text`, `images`, `videos`, `news`, `books`)
- output human-readable atau JSON
- resolusi URL final (`--expand-url`)
- scraping/crawling via Firecrawl native command (`duckse firecrawl ...`)

Gunakan skill ini untuk riset, fact-checking, monitoring berita, atau pengambilan konten web.

## Prerequisites

Pastikan binary tersedia:

```bash
duckse --help
```

Install cepat (Linux/macOS):

```bash
curl -sSL https://raw.githubusercontent.com/dwirx/duckse/main/scripts/install.sh | bash
```

Untuk fitur Firecrawl, set API key:

```bash
export FIRECRAWL_API_KEY=fc-xxxxxxxxxx
```

## DDGS Search (duckse)

### Basic

```bash
duckse "python asyncio tutorial"
```

### News + Time Filter

```bash
duckse "artificial intelligence" --type news --timelimit w --max-results 15
```

### Images

```bash
duckse "butterfly" --type images --color Monochrome --layout Wide --max-results 10
```

### Videos

```bash
duckse "python tutorial" --type videos --resolution high --duration medium
```

### Books

```bash
duckse "sea wolf jack london" --type books --backend annasarchive
```

### JSON + Final URL

```bash
duckse "beritakan di indonesia hari ini" --json
duckse "beritakan di indonesia hari ini" --expand-url --max-results 5
```

## Firecrawl Native (duckse)

### Search

```bash
duckse firecrawl search "ai regulation" --limit 10 --json
```

### Scrape Single Page

```bash
duckse firecrawl scrape "https://example.com" --json
```

### Crawl Site

```bash
duckse firecrawl crawl "https://example.com" --max-pages 30 --wait --json
```

### Hybrid: duckse search -> firecrawl scrape

```bash
duckse firecrawl search-scrape "berita indonesia hari ini" --type news --max-results 10 --scrape-limit 5 --region id-id --timelimit d --backend bing
```

## Valid Backends by Type

- `text`: `bing, brave, duckduckgo, google, grokipedia, mojeek, yandex, yahoo, wikipedia, auto`
- `images`: `duckduckgo, auto`
- `videos`: `duckduckgo, auto`
- `news`: `bing, duckduckgo, yahoo, auto`
- `books`: `annasarchive, auto`

## Quick Reference

Command format:

```bash
duckse "<query>" [options]
```

Essential options:
- `--type` (`text|images|videos|news|books`)
- `--max-results`, `--timelimit`, `--region`, `--backend`
- `--json`, `--expand-url`
- `--proxy`, `--timeout`, `--verify`

Firecrawl namespace:

```bash
duckse firecrawl <search|scrape|crawl|search-scrape> [options]
```

## Best Practices

1. Pakai query spesifik
2. Gunakan `--timelimit` untuk data terbaru
3. Pakai `--json` untuk otomasi
4. Pakai `--expand-url` jika butuh URL final
5. Cek validasi backend sesuai tipe

## Troubleshooting

- `duckse: command not found`
  - tambahkan PATH: `export PATH="$HOME/.local/bin:$PATH"`
- `FIRECRAWL_API_KEY belum diset`
  - export API key sebelum `duckse firecrawl ...`
- backend tidak valid
  - sesuaikan dengan daftar backend per tipe
- hasil kosong/timeout
  - longgarkan query, ubah filter waktu, tambah `--timeout`, atau pakai `--proxy`

## Development Fallback

Jika binary belum diinstall global:

```bash
uv run python main.py "<query>" [opsi]
uv run python main.py firecrawl <subcommand> [opsi]
```
