# ducksearch

`ducksearch` adalah CLI metasearch berbasis [`ddgs`](https://pypi.org/project/ddgs/) untuk mencari `text`, `images`, `videos`, `news`, dan `books` dari beberapa backend.

## Fitur Utama

- Satu CLI untuk 5 tipe pencarian: `text`, `images`, `videos`, `news`, `books`
- Output default yang rapi untuk dibaca manusia
- Mode JSON mentah dengan `--json`
- Opsi URL final (setelah redirect) dengan `--expand-url`
- Auto-intent Indonesia: query seperti `"beritakan di indonesia hari ini"` otomatis diarahkan ke `news` + `region id-id` + `timelimit d`
- Build single binary `duckse`

## Prasyarat

- Python `>= 3.10` (sesuai `pyproject.toml`)
- [`uv`](https://docs.astral.sh/uv/)

## Instalasi

```bash
uv sync
```

Untuk tooling dev (mis. PyInstaller):

```bash
uv sync --all-groups
```

### Install Cepat dari GitHub Release

Install versi terbaru (Linux/macOS):

```bash
curl -sSL https://raw.githubusercontent.com/dwirx/duckse/main/scripts/install.sh | bash
```

Install versi tertentu:

```bash
curl -sSL https://raw.githubusercontent.com/dwirx/duckse/main/scripts/install.sh | bash -s -- v0.1.0
```

## Penggunaan Dasar

Text search (default):

```bash
uv run python main.py "open source ai"
```

Berita Indonesia hari ini (auto-intent):

```bash
uv run python main.py "beritakan di indonesia hari ini" --max-results 5
```

Output JSON mentah:

```bash
uv run python main.py "beritakan di indonesia hari ini" --json
```

## Tipe Search dan Backend

- `text`: `bing, brave, duckduckgo, google, grokipedia, mojeek, yandex, yahoo, wikipedia, auto`
- `images`: `duckduckgo, auto`
- `videos`: `duckduckgo, auto`
- `news`: `bing, duckduckgo, yahoo, auto`
- `books`: `annasarchive, auto`

## Opsi CLI

Opsi umum:

- `--type`: `text|images|videos|news|books`
- `--region`: contoh `us-en`, `id-id`
- `--safesearch`: `on|moderate|off`
- `--timelimit`: `d|w|m|y`
- `--max-results`: jumlah hasil
- `--page`: halaman
- `--backend`: backend tunggal atau dipisah koma
- `--expand-url`: tampilkan URL final hasil redirect
- `--json`: output JSON mentah
- `--proxy`: proxy `http/https/socks5`
- `--timeout`: timeout request (detik, default `5`)
- `--verify`: `true`, `false`, atau path file PEM

Khusus images:

- `--size`, `--color`, `--type-image`, `--layout`, `--license-image`

Khusus videos:

- `--resolution`, `--duration`, `--license-videos`

## Validasi Otomatis

CLI akan menolak kombinasi opsi yang tidak sesuai:

- `images/videos` hanya backend `duckduckgo` atau `auto`
- `news` backend: `bing|duckduckgo|yahoo|auto`
- `books` backend: `annasarchive|auto`
- `timelimit=y` valid untuk `text/images`, tidak valid untuk `news/videos`

Contoh error validasi:

```bash
uv run python main.py "butterfly" --type images --backend bing
```

## Contoh Lanjutan

Image search:

```bash
uv run python main.py "butterfly" --type images --color Monochrome --layout Wide --max-results 10
```

Video search:

```bash
uv run python main.py "cars" --type videos --resolution high --duration medium --timelimit w
```

Books search:

```bash
uv run python main.py "sea wolf jack london" --type books --backend annasarchive
```

Berita Indonesia + URL final:

```bash
uv run python main.py "beritakan di indonesia hari ini" --expand-url --max-results 5
```

Pakai proxy:

```bash
uv run python main.py "berita indonesia" --type news --proxy socks5://127.0.0.1:9150 --timeout 10
```

## Testing

```bash
uv run pytest -q
```

## Build Single Binary (`duckse`)

Build:

```bash
make build-binary
```

Output:

- `dist/duckse` (Linux/macOS)
- `dist/duckse.exe` (Windows, jika build di Windows)

Contoh pakai binary:

```bash
./dist/duckse "open source ai" --type text --max-results 3
```

## Rilis Otomatis

Workflow GitHub Actions ada di:
- `.github/workflows/release.yml` (otomatis via tag + bisa manual)
- `.github/workflows/release-manual.yml` (manual-only, tombol Run workflow)
Rilis dibuat otomatis saat push tag dengan prefix `v`, contoh:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Atau jalankan manual dari tab **Actions**:

- pilih workflow **Release Manual**
- isi `tag` (contoh `v0.1.1`)
- set `prerelease=true` jika ingin rilis pre-release

Asset release yang dihasilkan:
- `duckse-linux-x86_64.tar.gz`
- `duckse-macos-x86_64.tar.gz`
- `duckse-windows-x86_64.zip`
