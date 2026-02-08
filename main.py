import argparse
import json
import os
import re
import sys
import time
from collections.abc import Callable
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from ddgs import DDGS


SearchFn = Callable[..., list[dict[str, Any]]]
FirecrawlRunFn = Callable[[list[str]], int]
SEARCH_BACKENDS: dict[str, set[str]] = {
    "text": {
        "auto",
        "bing",
        "brave",
        "duckduckgo",
        "google",
        "grokipedia",
        "mojeek",
        "wikipedia",
        "yahoo",
        "yandex",
    },
    "images": {"auto", "duckduckgo"},
    "videos": {"auto", "duckduckgo"},
    "news": {"auto", "bing", "duckduckgo", "yahoo"},
    "books": {"auto", "annasarchive"},
}
TIMELIMIT_BY_TYPE: dict[str, set[str]] = {
    "text": {"d", "w", "m", "y"},
    "images": {"d", "w", "m", "y"},
    "videos": {"d", "w", "m"},
    "news": {"d", "w", "m"},
}


def prepare_query_defaults(
    *, query: str, search_type: str, region: str, timelimit: str | None
) -> tuple[str, str, str, str | None]:
    normalized = re.sub(r"\s+", " ", query.lower()).strip()
    if search_type == "text" and "indonesia" in normalized:
        has_berita = "berita" in normalized or "beritakan" in normalized
        has_today = "hari ini" in normalized or "today" in normalized
        if has_berita and has_today:
            return "berita indonesia", "news", "id-id", "d"
    return query, search_type, region, timelimit


def get_result_url(item: dict[str, Any]) -> str | None:
    for key in ("url", "href"):
        value = item.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def resolve_url(url: str, timeout: int = 6) -> str | None:
    try:
        request = Request(url, method="GET", headers={"User-Agent": "duckse/1.0"})
        with urlopen(request, timeout=timeout) as response:  # noqa: S310
            final_url = response.geturl()
    except (URLError, ValueError):
        return None

    parsed = urlparse(final_url)
    if parsed.scheme and parsed.netloc:
        return final_url
    return None


def with_resolved_urls(
    results: list[dict[str, Any]], resolver: Callable[[str], str | None] = resolve_url
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for item in results:
        record = dict(item)
        url = get_result_url(record)
        if url:
            resolved = resolver(url)
            if resolved and resolved != url:
                record["resolved_url"] = resolved
        output.append(record)
    return output


def render_pretty(results: list[dict[str, Any]], search_type: str) -> str:
    if not results:
        return "Tidak ada hasil."

    lines: list[str] = []
    for idx, item in enumerate(results, start=1):
        lines.append(f"{idx}. {item.get('title', '(tanpa judul)')}")

        source = item.get("source") or item.get("publisher")
        if source:
            lines.append(f"   Sumber: {source}")

        date = item.get("date") or item.get("published")
        if date:
            lines.append(f"   Tanggal: {date}")

        url = get_result_url(item)
        if url:
            lines.append(f"   URL: {url}")

        resolved_url = item.get("resolved_url")
        if isinstance(resolved_url, str) and resolved_url:
            lines.append(f"   Final URL: {resolved_url}")

        body = item.get("body") or item.get("description")
        if isinstance(body, str) and body:
            lines.append(f"   Ringkasan: {body}")

        if search_type == "images" and item.get("image"):
            lines.append(f"   Image: {item.get('image')}")

        lines.append("")
    return "\n".join(lines).rstrip()


def validate_search_options(*, search_type: str, timelimit: str | None, backend: str) -> None:
    if timelimit is not None:
        allowed_timelimits = TIMELIMIT_BY_TYPE.get(search_type)
        if allowed_timelimits is not None and timelimit not in allowed_timelimits:
            values = ",".join(sorted(allowed_timelimits))
            raise ValueError(f"Timelimit '{timelimit}' tidak valid untuk '{search_type}'. Gunakan: {values}")

    allowed_backends = SEARCH_BACKENDS.get(search_type, {"auto"})
    for value in (item.strip() for item in backend.split(",")):
        if value and value not in allowed_backends:
            options = ",".join(sorted(allowed_backends))
            raise ValueError(f"Backend '{value}' tidak valid untuk '{search_type}'. Gunakan: {options}")


def search(
    *,
    query: str,
    search_type: str = "text",
    region: str = "us-en",
    safesearch: str = "moderate",
    timelimit: str | None = None,
    max_results: int | None = 10,
    page: int = 1,
    backend: str = "auto",
    size: str | None = None,
    color: str | None = None,
    type_image: str | None = None,
    layout: str | None = None,
    license_image: str | None = None,
    resolution: str | None = None,
    duration: str | None = None,
    license_videos: str | None = None,
    proxy: str | None = None,
    timeout: int = 5,
    verify: bool | str = True,
) -> list[dict[str, Any]]:
    validate_search_options(search_type=search_type, timelimit=timelimit, backend=backend)

    with DDGS(proxy=proxy, timeout=timeout, verify=verify) as ddgs:
        if search_type == "text":
            return ddgs.text(
                query,
                region=region,
                safesearch=safesearch,
                timelimit=timelimit,
                max_results=max_results,
                page=page,
                backend=backend,
            )

        if search_type == "images":
            return ddgs.images(
                query,
                region=region,
                safesearch=safesearch,
                timelimit=timelimit,
                max_results=max_results,
                page=page,
                backend=backend,
                size=size,
                color=color,
                type_image=type_image,
                layout=layout,
                license_image=license_image,
            )

        if search_type == "videos":
            return ddgs.videos(
                query,
                region=region,
                safesearch=safesearch,
                timelimit=timelimit,
                max_results=max_results,
                page=page,
                backend=backend,
                resolution=resolution,
                duration=duration,
                license_videos=license_videos,
            )

        if search_type == "news":
            return ddgs.news(
                query,
                region=region,
                safesearch=safesearch,
                timelimit=timelimit,
                max_results=max_results,
                page=page,
                backend=backend,
            )

        if search_type == "books":
            return ddgs.books(
                query,
                max_results=max_results,
                page=page,
                backend=backend,
            )

    raise ValueError(f"Unsupported search type: {search_type}")


def _firecrawl_api_key() -> str:
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY belum diset")
    return api_key


def _firecrawl_request(
    *,
    method: str,
    path: str,
    api_key: str,
    payload: dict[str, Any] | None = None,
    timeout: int = 60,
) -> dict[str, Any]:
    base_url = "https://api.firecrawl.dev/v1"
    url = f"{base_url}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return json.loads(resp.read().decode())
    except HTTPError as exc:
        body = exc.read().decode(errors="ignore")
        raise ValueError(f"Firecrawl API error {exc.code}: {body or exc.reason}") from exc
    except URLError as exc:
        raise ValueError(f"Firecrawl API network error: {exc}") from exc


def firecrawl_search(query: str, limit: int, lang: str, country: str, api_key: str) -> dict[str, Any]:
    payload = {"query": query, "limit": limit, "lang": lang, "country": country}
    return _firecrawl_request(method="POST", path="/search", payload=payload, api_key=api_key)


def firecrawl_scrape(url: str, formats: list[str], only_main: bool, api_key: str) -> dict[str, Any]:
    payload = {"url": url, "formats": formats, "onlyMainContent": only_main}
    return _firecrawl_request(method="POST", path="/scrape", payload=payload, api_key=api_key)


def firecrawl_start_crawl(url: str, limit: int, api_key: str) -> dict[str, Any]:
    payload = {
        "url": url,
        "limit": limit,
        "scrapeOptions": {"formats": ["markdown"], "onlyMainContent": True},
    }
    return _firecrawl_request(method="POST", path="/crawl", payload=payload, api_key=api_key)


def firecrawl_check_crawl(job_id: str, api_key: str) -> dict[str, Any]:
    return _firecrawl_request(method="GET", path=f"/crawl/{job_id}", api_key=api_key)


def run_firecrawl(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Firecrawl native commands di duckse")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    search_parser = subparsers.add_parser("search", help="Firecrawl web search")
    search_parser.add_argument("query")
    search_parser.add_argument("--limit", type=int, default=10)
    search_parser.add_argument("--lang", default="en")
    search_parser.add_argument("--country", default="us")
    search_parser.add_argument("--json", action="store_true")

    scrape_parser = subparsers.add_parser("scrape", help="Firecrawl scrape single URL")
    scrape_parser.add_argument("url")
    scrape_parser.add_argument("--markdown", action="store_true", default=True)
    scrape_parser.add_argument("--html", action="store_true")
    scrape_parser.add_argument("--screenshot", action="store_true")
    scrape_parser.add_argument("--json", action="store_true")
    scrape_parser.add_argument("--only-main", action="store_true", default=True)

    crawl_parser = subparsers.add_parser("crawl", help="Firecrawl crawl site")
    crawl_parser.add_argument("url")
    crawl_parser.add_argument("--max-pages", type=int, default=50)
    crawl_parser.add_argument("--wait", action="store_true")
    crawl_parser.add_argument("--json", action="store_true")
    crawl_parser.add_argument("--poll-seconds", type=int, default=2)

    search_scrape = subparsers.add_parser(
        "search-scrape",
        help="Cari dengan duckse lalu scrape top URL via Firecrawl",
    )
    search_scrape.add_argument("query")
    search_scrape.add_argument("--type", dest="search_type", choices=["text", "news"], default="text")
    search_scrape.add_argument("--max-results", type=int, default=10)
    search_scrape.add_argument("--scrape-limit", type=int, default=5)
    search_scrape.add_argument("--region", default="us-en")
    search_scrape.add_argument("--timelimit", choices=["d", "w", "m", "y"])
    search_scrape.add_argument("--backend", default="auto")
    search_scrape.add_argument("--markdown", action="store_true", default=True)
    search_scrape.add_argument("--html", action="store_true")
    search_scrape.add_argument("--screenshot", action="store_true")
    search_scrape.add_argument("--json", action="store_true")

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code)

    try:
        api_key = _firecrawl_api_key()
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    try:
        if args.subcommand == "search":
            result = firecrawl_search(args.query, args.limit, args.lang, args.country, api_key)
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                data = result.get("data", [])
                for idx, item in enumerate(data, start=1):
                    print(f"{idx}. {item.get('title', 'N/A')}")
                    print(f"   URL: {item.get('url', 'N/A')}")
                    print(f"   Description: {item.get('description', 'N/A')}")
            return 0

        if args.subcommand == "scrape":
            formats: list[str] = []
            if args.markdown:
                formats.append("markdown")
            if args.html:
                formats.append("html")
            if args.screenshot:
                formats.append("screenshot")
            result = firecrawl_scrape(args.url, formats or ["markdown"], args.only_main, api_key)
            if args.json:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                data = result.get("data", {})
                metadata = data.get("metadata", {})
                print(f"Title: {metadata.get('title', 'N/A')}")
                print(f"URL: {metadata.get('sourceURL', args.url)}")
                if "markdown" in data:
                    print(data["markdown"])
            return 0

        if args.subcommand == "crawl":
            result = firecrawl_start_crawl(args.url, args.max_pages, api_key)
            if not args.wait:
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return 0

            job_id = result.get("id")
            if not isinstance(job_id, str) or not job_id:
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return 0

            status = result
            while status.get("status") not in {"completed", "failed", "cancelled"}:
                time.sleep(max(1, args.poll_seconds))
                status = firecrawl_check_crawl(job_id, api_key)

            print(json.dumps(status, indent=2, ensure_ascii=False))
            return 0

        if args.subcommand == "search-scrape":
            results = search(
                query=args.query,
                search_type=args.search_type,
                region=args.region,
                timelimit=args.timelimit,
                backend=args.backend,
                max_results=args.max_results,
            )
            urls = []
            for item in results:
                url = get_result_url(item)
                if url and url not in urls:
                    urls.append(url)
            urls = urls[: args.scrape_limit]

            formats: list[str] = []
            if args.markdown:
                formats.append("markdown")
            if args.html:
                formats.append("html")
            if args.screenshot:
                formats.append("screenshot")
            formats = formats or ["markdown"]

            scraped = [firecrawl_scrape(url, formats, True, api_key) for url in urls]
            output = {"query": args.query, "urls": urls, "scraped": scraped}
            print(json.dumps(output, indent=2, ensure_ascii=False))
            return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 2


def run(
    argv: list[str] | None = None,
    search_fn: SearchFn = search,
    firecrawl_run_fn: FirecrawlRunFn = run_firecrawl,
) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] == "firecrawl":
        return firecrawl_run_fn(argv[1:])

    parser = argparse.ArgumentParser(description="DDGS metasearch CLI")
    parser.add_argument("query", help="Kata kunci pencarian")
    parser.add_argument(
        "--type",
        dest="search_type",
        default="text",
        choices=["text", "images", "videos", "news", "books"],
        help="Tipe pencarian",
    )
    parser.add_argument("--region", default="us-en", help="Region, contoh: us-en")
    parser.add_argument(
        "--safesearch",
        default="moderate",
        choices=["on", "moderate", "off"],
        help="Filter safe search",
    )
    parser.add_argument("--timelimit", choices=["d", "w", "m", "y"], help="Batas waktu")
    parser.add_argument("--max-results", type=int, default=10, help="Jumlah hasil")
    parser.add_argument("--page", type=int, default=1, help="Halaman hasil")
    parser.add_argument("--backend", default="auto", help="Backend tunggal atau koma")

    parser.add_argument("--size", help="Filter image size")
    parser.add_argument("--color", help="Filter image color")
    parser.add_argument("--type-image", help="Filter image type")
    parser.add_argument("--layout", help="Filter image layout")
    parser.add_argument("--license-image", help="Filter image license")

    parser.add_argument("--resolution", help="Filter video resolution")
    parser.add_argument("--duration", help="Filter video duration")
    parser.add_argument("--license-videos", help="Filter video license")
    parser.add_argument("--expand-url", action="store_true", help="Resolve URL final")
    parser.add_argument("--json", action="store_true", help="Output JSON mentah")
    parser.add_argument("--proxy", help="Proxy http/https/socks5")
    parser.add_argument("--timeout", type=int, default=5, help="HTTP timeout dalam detik")
    parser.add_argument(
        "--verify",
        default="true",
        help="TLS verify: true, false, atau path PEM",
    )

    args = parser.parse_args(argv)
    query, search_type, region, timelimit = prepare_query_defaults(
        query=args.query,
        search_type=args.search_type,
        region=args.region,
        timelimit=args.timelimit,
    )

    verify: bool | str
    verify_raw = args.verify.strip().lower()
    if verify_raw == "true":
        verify = True
    elif verify_raw == "false":
        verify = False
    else:
        verify = args.verify

    try:
        results = search_fn(
            query=query,
            search_type=search_type,
            region=region,
            safesearch=args.safesearch,
            timelimit=timelimit,
            max_results=args.max_results,
            page=args.page,
            backend=args.backend,
            size=args.size,
            color=args.color,
            type_image=args.type_image,
            layout=args.layout,
            license_image=args.license_image,
            resolution=args.resolution,
            duration=args.duration,
            license_videos=args.license_videos,
            proxy=args.proxy,
            timeout=args.timeout,
            verify=verify,
        )
    except ValueError as exc:
        parser.error(str(exc))
    if args.expand_url:
        results = with_resolved_urls(results)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(render_pretty(results, search_type))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
