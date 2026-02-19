#!/usr/bin/env python3
"""Generate per-source RSS XML files from sources listed in feeds.yaml.

This script currently supports ingesting existing RSS feeds. Scraping for sites
without RSS will be added later.
"""
import os
import sys
import yaml
import feedparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from feedgen.feed import FeedGenerator


def slugify(s: str) -> str:
    return (
        s.lower()
        .replace(" ", "-")
        .replace("/", "-")
        .replace(".", "-")
    )


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_config(path="feeds.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_feed_from_parsed(source_name, source_url, parsed):
    fg = FeedGenerator()
    fg.title(source_name)
    fg.link(href=source_url, rel="alternate")
    fg.id(source_url)
    fg.description(parsed.feed.get("description", f"Feed generated for {source_name}"))

    for entry in parsed.entries:
        fe = fg.add_entry()
        fe.id(entry.get("id", entry.get("link", None)))
        fe.title(entry.get("title", "(no title)"))
        fe.link(href=entry.get("link", ""))
        # Prefer summary/content where available
        content = entry.get("summary", "")
        if not content and "content" in entry and entry["content"]:
            content = entry["content"][0].get("value", "")
        fe.description(content)
        if entry.get("published"):
            fe.pubDate(entry.get("published"))

    return fg


def scrape_url(source_url: str, selectors: dict):
    """Scrape a page and return a list of item dicts using the provided CSS selectors.

    selectors should include: list, title, link, content (optional), date (optional).
    """
    items = []
    try:
        resp = requests.get(source_url, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  Error fetching for scrape {source_url}: {e}")
        return items

    soup = BeautifulSoup(resp.text, "html.parser")
    list_sel = selectors.get("list")
    if not list_sel:
        print("  No 'list' selector provided for scraping; returning no items.")
        return items

    for node in soup.select(list_sel):
        try:
            title_node = node.select_one(selectors.get("title")) if selectors.get("title") else None
            link_node = node.select_one(selectors.get("link")) if selectors.get("link") else None
            content_node = node.select_one(selectors.get("content")) if selectors.get("content") else None
            date_node = node.select_one(selectors.get("date")) if selectors.get("date") else None

            title = title_node.get_text(strip=True) if title_node else node.get_text(strip=True)
            href = None
            if link_node and link_node.has_attr("href"):
                href = urljoin(source_url, link_node.get("href"))
            elif link_node:
                href = link_node.get_text(strip=True)

            content = content_node.get_text(strip=True) if content_node else ""
            published = date_node.get_text(strip=True) if date_node else None

            items.append({"title": title, "link": href, "content": content, "published": published})
        except Exception:
            continue

    return items


def build_feed_from_scraped(source_name, source_url, items):
    fg = FeedGenerator()
    fg.title(source_name)
    fg.link(href=source_url, rel="alternate")
    fg.id(source_url)
    fg.description(f"Scraped feed for {source_name}")

    for entry in items:
        fe = fg.add_entry()
        fe.id(entry.get("link") or entry.get("title"))
        fe.title(entry.get("title", "(no title)"))
        if entry.get("link"):
            fe.link(href=entry.get("link"))
        fe.description(entry.get("content", ""))
        if entry.get("published"):
            fe.pubDate(entry.get("published"))

    return fg


def main():
    cfg = load_config()
    out_root = os.path.join(os.getcwd(), "feeds")
    ensure_dir(out_root)

    for topic, sources in cfg.items():
        topic_slug = slugify(topic)
        topic_dir = os.path.join(out_root, topic_slug)
        ensure_dir(topic_dir)

        for src in sources:
            name = src.get("name")
            url = src.get("url")
            # If 'scrape' is true, perform manual scraping using selectors
            if src.get("scrape"):
                selectors = src.get("selectors", {})
                print(f"Scraping {name}: {url} using selectors {selectors}")
                items = scrape_url(url, selectors)
                if not items:
                    print(f"  No items scraped for {name}; skipping.")
                    continue
                fg = build_feed_from_scraped(name, url, items)
                out_path = os.path.join(topic_dir, f"{slugify(name)}.xml")
                fg.rss_file(out_path)
                print(f"  Wrote {out_path}")
                continue
            print(f"Fetching {name}: {url}")
            parsed = feedparser.parse(url)

            if parsed.bozo:
                print(f"  Warning: feedparser flagged a problem for {url}: {parsed.bozo_exception}")

            fg = build_feed_from_parsed(name, url, parsed)

            out_path = os.path.join(topic_dir, f"{slugify(name)}.xml")
            fg.rss_file(out_path)
            print(f"  Wrote {out_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e, file=sys.stderr)
        sys.exit(1)
