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

    def text(self, keywords, max_results=None):
        self.calls.append((keywords, max_results))
        return [{"title": "Result", "href": "https://example.com"}]


def test_search_text_uses_ddgs(monkeypatch):
    fake = _FakeDDGS()
    monkeypatch.setattr(main, "DDGS", lambda: fake)

    results = main.search_text("open source", max_results=3)

    assert results == [{"title": "Result", "href": "https://example.com"}]
    assert fake.calls == [("open source", 3)]


def test_run_prints_json_results(capsys):
    captured = {}

    def fake_search(query, max_results):
        captured["query"] = query
        captured["max_results"] = max_results
        return [{"title": "Duck", "href": "https://duckduckgo.com"}]

    exit_code = main.run(["duckduckgo", "--max-results", "1"], search_fn=fake_search)

    assert exit_code == 0
    assert captured == {"query": "duckduckgo", "max_results": 1}

    output = capsys.readouterr().out
    assert json.loads(output) == [{"title": "Duck", "href": "https://duckduckgo.com"}]
