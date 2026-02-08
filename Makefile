PYINSTALLER = uv run pyinstaller

.PHONY: test build-binary clean-binary

test:
	uv run pytest -q

build-binary:
	$(PYINSTALLER) --onefile --name duckse main.py

clean-binary:
	rm -rf build dist duckse.spec
