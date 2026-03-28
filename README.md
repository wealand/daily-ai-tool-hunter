# Daily AI Tool Hunter 🔎

A Python-powered scraper that hunts for the newest AI tools across multiple sources and generates a high-aesthetic, filterable dashboard.

## Features
- **Multi-Source Hunting**: Scrapes **FutureTools.io** and **Product Hunt** (AI topic) for the freshest tools.
- **Automated Discord Alerts**: Sends the top 3 tools of the day directly to your Discord channel.
- **Rich Aesthetic Dashboard**: Modern, glassmorphism-inspired UI with:
    - Real-time search and category filtering.
    - Automatic tool favicons.
    - Responsive grid design.
    - Dark mode by default.
- **Easy Deployment**: Hosted for free on GitHub Pages with daily updates via GitHub Actions.

## How it works
1. `hunter.py` fetches data from multiple AI tool directories.
2. Deduplicates results and generates a static `index.html`.
3. Sends a summary to Discord via Webhook.
4. GitHub Actions runs the hunt daily and redeploys the site.

## Setup
1. Fork or clone this repository.
2. **Discord Notifications**: 
   - Create a Discord Webhook (Server Settings > Integrations > Webhooks).
   - Add the URL as a GitHub Secret named `DISCORD_WEBHOOK_URL` or create a `.env` file locally.
3. **GitHub Pages**:
   - Enable in **Settings > Pages** (Source: Deploy from a branch, Branch: main).
4. The dashboard will be live at `https://YOUR_USERNAME.github.io/daily-ai-tool-hunter/`.

---
*Created by Adam Wealand. Support my work by [buying me a coffee](https://buymeacoffee.com/icecapades).*
