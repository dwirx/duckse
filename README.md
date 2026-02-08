# ducksearch

`ducksearch` adalah CLI metasearch berbasis `ddgs` dengan binary utama `duckse`.
Selain search (`text/images/videos/news/books`), `duckse` juga punya command native Firecrawl untuk `search`, `scrape`, `crawl`, dan alur hybrid `search-scrape`.

## Fitur Utama

- Satu binary: `duckse`
- DDGS metasearch dengan output rapi dan JSON
- Auto-intent Indonesia (`"beritakan di indonesia hari ini"` -> `news`, `id-id`, `timelimit=d`)
- Resolve final URL (`--expand-url`)
- Firecrawl native namespace: `duckse firecrawl ...`
- Build single binary untuk distribusi

## Instalasi

### 1. Install cepat dari GitHub Release

```bash
curl -sSL https://raw.githubusercontent.com/dwirx/duckse/main/scripts/install.sh | bash
```

Install versi tertentu:

```bash
curl -sSL https://raw.githubusercontent.com/dwirx/duckse/main/scripts/install.sh | bash -s -- v0.1.0
```

### 2. Verifikasi binary

```bash
duckse --help
```

Jika command belum dikenali:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Penggunaan `duckse`

### Search umum

```bash
duckse "open source ai"
duckse "beritakan di indonesia hari ini" --max-results 5
duckse "beritakan di indonesia hari ini" --json
duckse "beritakan di indonesia hari ini" --expand-url --max-results 5
```

### Tipe search dan backend valid

- `text`: `bing, brave, duckduckgo, google, grokipedia, mojeek, yandex, yahoo, wikipedia, auto`
- `images`: `duckduckgo, auto`
- `videos`: `duckduckgo, auto`
- `news`: `bing, duckduckgo, yahoo, auto`
- `books`: `annasarchive, auto`

Contoh per tipe:

```bash
duckse "open source ai" --type text --backend google --max-results 5
duckse "butterfly" --type images --backend duckduckgo --color Monochrome --max-results 10
duckse "cars" --type videos --backend duckduckgo --resolution high --duration medium
duckse "berita indonesia hari ini" --type news --backend bing --timelimit d --max-results 5
duckse "sea wolf jack london" --type books --backend annasarchive --max-results 5
```

### Opsi CLI utama

- `--type`: `text|images|videos|news|books`
- `--region`: contoh `us-en`, `id-id`
- `--safesearch`: `on|moderate|off`
- `--timelimit`: `d|w|m|y`
- `--max-results`, `--page`, `--backend`
- `--expand-url`, `--json`
- `--proxy`, `--timeout`, `--verify`

Images only:
- `--size`, `--color`, `--type-image`, `--layout`, `--license-image`

Videos only:
- `--resolution`, `--duration`, `--license-videos`

### Validasi otomatis

`duckse` akan menolak kombinasi opsi yang tidak valid.
Contoh:

```bash
duckse "butterfly" --type images --backend bing
# -> Backend 'bing' tidak valid untuk 'images'. Gunakan: auto,duckduckgo
```

## Firecrawl Native di `duckse`

Set API key dulu:

```bash
export FIRECRAWL_API_KEY=fc-xxxxxxxxxx
```

### Firecrawl search

```bash
duckse firecrawl search "ai regulation" --limit 10 --json
```

### Firecrawl scrape

```bash
duckse firecrawl scrape "https://example.com" --json
```

### Firecrawl crawl

```bash
duckse firecrawl crawl "https://example.com" --max-pages 30 --wait --json
```

### Hybrid: duckse search -> firecrawl scrape

```bash
duckse firecrawl search-scrape "berita indonesia hari ini" --type news --max-results 10 --scrape-limit 5 --region id-id --timelimit d --backend bing
```

## Development Mode (tanpa install global)

```bash
uv sync
uv run python main.py "open source ai"
uv run python main.py firecrawl search "ai regulation" --limit 10 --json
```

## Testing

```bash
uv run pytest -q
```

## Build Binary

```bash
uv sync --all-groups
make build-binary
```

Output binary:
- `dist/duckse` (Linux/macOS)
- `dist/duckse.exe` (Windows jika build di Windows)

Contoh:

```bash
./dist/duckse "open source ai" --type text --max-results 3
./dist/duckse firecrawl search "ai regulation" --limit 5 --json
```

## Release Workflow

- `.github/workflows/release.yml`: release otomatis saat push tag `v*`
- `.github/workflows/release-manual.yml`: release manual dari GitHub Actions

Contoh release tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```
