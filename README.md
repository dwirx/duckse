# ducksearch

CLI sederhana untuk mencari hasil web memakai `ddgs`.

## Setup

```bash
uv sync
```

## Menjalankan

```bash
uv run python main.py "open source ai"
```

Batasi jumlah hasil:

```bash
uv run python main.py "open source ai" --max-results 3
```

Output berupa JSON list, contoh field umum: `title`, `href`, `body`.

## Testing

```bash
uv run pytest -q
```

## Build Single Binary (`duckse`)

Install dev tools:

```bash
uv sync --all-groups
```

Build binary:

```bash
make build-binary
```

Hasil:
- `dist/duckse` (Linux/macOS)
- `dist/duckse.exe` (Windows, jika build di Windows)

Contoh pakai:

```bash
./dist/duckse "open source ai" --max-results 3
```
