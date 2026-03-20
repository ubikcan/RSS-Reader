import hashlib
import json
import os
from datetime import datetime

import feedparser
import requests
from bs4 import BeautifulSoup

CONFIG_FILE = "config.json"
OUTPUT_FILE = "feeds.json"


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_existing_items():
    if not os.path.exists(OUTPUT_FILE):
        return {}
    with open(OUTPUT_FILE) as f:
        items = json.load(f)
    return {item["link"]: item for item in items}


def fetch_rss(url):
    feed = feedparser.parse(url)
    items = []
    for entry in feed.entries:
        link = entry.get("link", "")
        if not link:
            continue
        published = entry.get("published", entry.get("updated", ""))
        items.append({
            "title": entry.get("title", ""),
            "link": link,
            "source": url,
            "published": published,
            "hash": None,
        })
    return items


def fetch_scrape(url):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    content_hash = hashlib.sha256(soup.get_text().encode()).hexdigest()

    # Attempt to extract a meaningful title and canonical link
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url

    canonical = soup.find("link", rel="canonical")
    link = canonical["href"] if canonical and canonical.get("href") else url

    return [{
        "title": title,
        "link": link,
        "source": url,
        "published": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hash": content_hash,
    }]


def main():
    config = load_config()
    existing = load_existing_items()

    for feed in config["feeds"]:
        url = feed["url"]
        feed_type = feed["type"]
        try:
            if feed_type == "rss":
                items = fetch_rss(url)
            elif feed_type == "scrape":
                items = fetch_scrape(url)
            else:
                print(f"Unknown type '{feed_type}' for {url}, skipping.")
                continue
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

        for item in items:
            link = item["link"]
            if link not in existing:
                existing[link] = item
            elif feed_type == "scrape" and item["hash"] != existing[link].get("hash"):
                # Content changed — update hash and timestamp
                existing[link]["hash"] = item["hash"]
                existing[link]["published"] = item["published"]

    output = list(existing.values())
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Wrote {len(output)} items to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
