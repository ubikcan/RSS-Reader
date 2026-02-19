GitHub-Hosted RSS Feed Aggregator
Project Planning Summary

Project Overview
A fully automated RSS feed aggregator hosted on GitHub, combining existing RSS feeds with scraped content from sites that do not provide feeds. The system will organize content by topic and source, and present it through a clean landing page hosted on GitHub Pages.

Architecture
• GitHub Pages: Hosts the landing page and all output XML feed files (static hosting, free).
• GitHub Actions: Runs automated feed fetching and scraping on a schedule (e.g., every 6 hours).
• Python Scripts: Handle RSS feed fetching (feedparser) and site scraping (BeautifulSoup).
• XML Output Files: Generated feed files organized by topic and source.

Content Sources
Two types of sources will be supported:

• RSS Feeds: Direct feed ingestion from sources that publish RSS.
• Scraped Sites: Web scraping for public sites that do not provide RSS feeds.
All sources are publicly accessible (no authentication required).

Content Organization
Content will be organized hierarchically by topic, then by source within each topic. Example structure:

• Topic: Labs
        – Oak Ridge National Laboratory
        – Argonne National Laboratory
        – (additional sources...)

Landing Page
A GitHub Pages-hosted landing page will list all topics and their sources, with subscribe links to the individual XML feed files. The UI will be clean and efficient, suitable for direct use by end users.

Git Operations Reference
After initial setup, most automation runs on GitHub’s servers. The primary Git commands needed locally are:

• git clone <repo-url> – Download the repository to your local machine.
• git add . – Stage all changed files for commit.
• git commit -m "message" – Save a labeled snapshot of your changes.
• git push – Upload your committed changes to GitHub.

Next Steps
• Provide the full topic/source list to configure feed targets.
• Clarify scraping approach for sites without RSS (auto-detect vs. manual selectors).
• Generate Python fetch/scrape scripts and GitHub Actions workflow.
• Build the landing page UI.
• Deploy to GitHub Pages and verify scheduled runs.
