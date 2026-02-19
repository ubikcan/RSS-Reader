GitHub-Hosted RSS Feed Aggregator

This repository scaffolds an automated RSS aggregator that fetches public RSS feeds and (later) scrapes sites without feeds. Use `scripts/generate_feeds.py` to fetch RSS sources defined in `feeds.yaml` and write output XML files to `output/`.

Quick start

1. Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
# on Windows:
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the generator:

```bash
python scripts/generate_feeds.py
```

Next steps: add site scraping logic, a GitHub Actions workflow, and a GitHub Pages landing page.

Manual scraping

You can configure manual scraping for sources that do not publish RSS. In
`feeds.yaml` set `scrape: true` for the source and provide `selectors` (CSS
selectors) to locate items. See the commented example at the bottom of
`feeds.yaml`.

Selectors example keys:
- `list`: CSS selector matching each article container (required)
- `title`: selector for title within the container
- `link`: selector for link element (href will be joined to the source URL)
- `content`: selector for content/teaser text
- `date`: selector for published date text

When scraping is enabled the generator will use `requests` + `BeautifulSoup`
to extract items and emit an RSS XML file for that source.
