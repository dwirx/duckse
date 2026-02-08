from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT_PATH = Path("skills/firecrawl/scripts/search_then_scrape.py")


def _load_module():
    spec = spec_from_file_location("search_then_scrape", SCRIPT_PATH)
    module = module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_extract_urls_deduplicates_and_supports_url_and_href():
    module = _load_module()

    urls = module.extract_urls(
        [
            {"url": "https://a.example"},
            {"href": "https://b.example"},
            {"url": "https://a.example"},
            {"title": "no url"},
        ]
    )

    assert urls == ["https://a.example", "https://b.example"]


def test_build_duckse_command_uses_json_output_and_filters():
    module = _load_module()

    cmd = module.build_duckse_command(
        query="berita indonesia hari ini",
        search_type="news",
        max_results=7,
        region="id-id",
        timelimit="d",
        backend="bing",
    )

    assert cmd[:2] == ["duckse", "berita indonesia hari ini"]
    assert "--json" in cmd
    assert "--type" in cmd and "news" in cmd
    assert "--max-results" in cmd and "7" in cmd
    assert "--region" in cmd and "id-id" in cmd
    assert "--timelimit" in cmd and "d" in cmd
    assert "--backend" in cmd and "bing" in cmd
