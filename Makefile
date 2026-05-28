watch:
	uv run python render.py --watch

render:
	uv run python render.py

render-local:
	uv run python render.py --local

fetch-csv:
	uv run python render.py fetch-csv

open: render-local
	@rm -rf _site
	@mkdir _site
	@cp index.html _site/
	@cp -r static/. _site/
	@(sleep 1 && open http://localhost:8000) &
	@cd _site && python3 -m http.server 8000
