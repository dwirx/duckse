import json

import main


def test_main_uses_ddgs_package():
    assert main.DDGS.__module__.startswith("ddgs")


class _FakeDDGS:
    def __init__(self):
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def text(self, query, **kwargs):
        self.calls.append(("text", query, kwargs))
        return [{"title": "Text Result", "href": "https://example.com/text"}]

    def images(self, query, **kwargs):
        self.calls.append(("images", query, kwargs))
        return [{"title": "Image Result", "image": "https://example.com/image.jpg"}]


def test_prepare_query_defaults_indonesia_news_today():
    query, search_type, region, timelimit = main.prepare_query_defaults(
        query="beritakan di indonesia hari ini",
        search_type="text",
        region="us-en",
        timelimit=None,
    )

    assert query == "berita indonesia"
    assert search_type == "news"
    assert region == "id-id"
    assert timelimit == "d"


def test_search_dispatches_text_with_common_options(monkeypatch):
    fake = _FakeDDGS()
    monkeypatch.setattr(main, "DDGS", lambda **kwargs: fake)

    results = main.search(
        query="open source",
        search_type="text",
        region="us-en",
        safesearch="off",
        timelimit="w",
        max_results=3,
        page=2,
        backend="bing",
    )

    assert results == [{"title": "Text Result", "href": "https://example.com/text"}]
    assert fake.calls == [
        (
            "text",
            "open source",
            {
                "region": "us-en",
                "safesearch": "off",
                "timelimit": "w",
                "max_results": 3,
                "page": 2,
                "backend": "bing",
            },
        )
    ]


def test_search_dispatches_images_with_specific_options(monkeypatch):
    fake = _FakeDDGS()
    monkeypatch.setattr(main, "DDGS", lambda **kwargs: fake)

    results = main.search(
        query="butterfly",
        search_type="images",
        region="us-en",
        safesearch="moderate",
        timelimit="m",
        max_results=5,
        page=1,
        backend="duckduckgo",
        size="Large",
        color="Monochrome",
        type_image="photo",
        layout="Wide",
        license_image="Public",
    )

    assert results == [{"title": "Image Result", "image": "https://example.com/image.jpg"}]
    assert fake.calls == [
        (
            "images",
            "butterfly",
            {
                "region": "us-en",
                "safesearch": "moderate",
                "timelimit": "m",
                "max_results": 5,
                "page": 1,
                "backend": "duckduckgo",
                "size": "Large",
                "color": "Monochrome",
                "type_image": "photo",
                "layout": "Wide",
                "license_image": "Public",
            },
        )
    ]


def test_render_pretty_news_contains_full_url_and_metadata():
    text = main.render_pretty(
        [
            {
                "title": "Judul Berita",
                "url": "https://contoh.id/berita/lengkap",
                "resolved_url": "https://www.contoh.id/berita/lengkap?ref=home",
                "date": "2026-02-08T10:00:00+07:00",
                "source": "Contoh News",
                "body": "Ringkasan isi berita",
            }
        ],
        "news",
    )

    assert "1. Judul Berita" in text
    assert "URL: https://contoh.id/berita/lengkap" in text
    assert "Final URL: https://www.contoh.id/berita/lengkap?ref=home" in text
    assert "Sumber: Contoh News" in text


def test_run_supports_new_cli_options_and_pretty_output(capsys):
    captured = {}

    def fake_search(**kwargs):
        captured.update(kwargs)
        return [{"title": "Duck", "url": "https://duckduckgo.com", "body": "Mesin pencari"}]

    exit_code = main.run(
        [
            "beritakan di indonesia hari ini",
            "--max-results",
            "2",
            "--backend",
            "bing",
        ],
        search_fn=fake_search,
    )

    assert exit_code == 0
    assert captured["query"] == "berita indonesia"
    assert captured["search_type"] == "news"
    assert captured["region"] == "id-id"
    assert captured["timelimit"] == "d"

    output = capsys.readouterr().out
    assert "1. Duck" in output
    assert "URL: https://duckduckgo.com" in output


def test_run_json_output_mode(capsys):
    def fake_search(**kwargs):
        return [{"title": "Duck", "url": "https://duckduckgo.com"}]

    exit_code = main.run(["duckduckgo", "--json"], search_fn=fake_search)

    assert exit_code == 0
    output = capsys.readouterr().out
    assert json.loads(output) == [{"title": "Duck", "url": "https://duckduckgo.com"}]


def test_search_uses_ddgs_client_options(monkeypatch):
    captured = {}

    class _CtorFakeDDGS:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def text(self, query, **kwargs):
            return [{"title": "ok", "href": "https://example.com"}]

    monkeypatch.setattr(main, "DDGS", _CtorFakeDDGS)

    main.search(
        query="python",
        search_type="text",
        proxy="socks5://127.0.0.1:9150",
        timeout=15,
        verify=False,
    )

    assert captured == {
        "proxy": "socks5://127.0.0.1:9150",
        "timeout": 15,
        "verify": False,
    }


def test_search_rejects_invalid_backend_for_images():
    try:
        main.validate_search_options(search_type="images", timelimit=None, backend="bing")
    except ValueError as exc:
        assert "Backend" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid backend")


def test_search_rejects_invalid_timelimit_for_news():
    try:
        main.validate_search_options(search_type="news", timelimit="y", backend="auto")
    except ValueError as exc:
        assert "Timelimit" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid timelimit")
