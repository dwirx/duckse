import argparse
import json
from collections.abc import Callable

from ddgs import DDGS


SearchFn = Callable[[str, int | None], list[dict[str, str]]]


def search_text(query: str, max_results: int | None = 5) -> list[dict[str, str]]:
    with DDGS() as ddgs:
        return ddgs.text(query, max_results=max_results)


def run(argv: list[str] | None = None, search_fn: SearchFn = search_text) -> int:
    parser = argparse.ArgumentParser(description="Search DuckDuckGo from CLI")
    parser.add_argument("query", help="Kata kunci pencarian")
    parser.add_argument("--max-results", type=int, default=5, help="Jumlah hasil")
    args = parser.parse_args(argv)

    results = search_fn(args.query, args.max_results)
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
