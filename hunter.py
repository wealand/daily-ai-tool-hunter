import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import subprocess
import json
import re
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

load_dotenv()
console = Console()

def fetch_future_tools():
    """Extracts AI tools from FutureTools using flexible JSON/Regex extraction."""
    url = "https://www.futuretools.io/?sort=date"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tools = []
        # Even more flexible pattern for FutureTools
        pattern = r'"name":"(?P<name>[^"]+)","description(_short)?":"(?P<desc>[^"]+)"'
        link_pattern = r'"(website_url|url)":"(?P<url>[^"]+)"'
        
        # Extract all names/descs
        matches = list(re.finditer(pattern, response.text))
        # Extract all URLs
        url_matches = list(re.finditer(link_pattern, response.text))
        
        for i in range(min(len(matches), len(url_matches))):
            try:
                name = matches[i].group('name').encode('utf-8').decode('unicode-escape')
                description = matches[i].group('desc').encode('utf-8').decode('unicode-escape')
                link = url_matches[i].group('url').replace('\\/', '/')
                
                if not link.startswith('http'):
                    link = "https://futuretools.io" + link

                tools.append({
                    "name": name,
                    "description": description,
                    "link": link,
                    "tags": ["New"],
                    "source": "FutureTools"
                })
            except:
                continue
        
        return tools
    except Exception as e:
        console.print(f"[bold red]Error parsing FutureTools:[/bold red] {e}")
        return []

def fetch_top_ai_tools():
    """Extracts AI tools from Top AI Tools using flexible HTML/JSON extraction."""
    url = "https://topaitools.com/new"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        tools = []
        # First try BeautifulSoup for the visual cards
        soup = BeautifulSoup(response.text, 'html.parser')
        # Based on typical TopAITools structure (they often use Nuxt + Tailwind)
        # We'll look for anything that looks like a title and description in a list/grid
        for card in soup.find_all(['div', 'article'], class_=re.compile(r'tool|card|item', re.I)):
            name_elem = card.find(['h2', 'h3', 'h4'])
            desc_elem = card.find('p')
            link_elem = card.find('a', href=True)
            
            if name_elem and desc_elem and len(name_elem.text.strip()) > 2:
                name = name_elem.text.strip()
                description = desc_elem.text.strip()
                link = link_elem['href']
                if not link.startswith('http'):
                    link = "https://topaitools.com" + link
                
                tools.append({
                    "name": name,
                    "description": description,
                    "link": link,
                    "tags": ["Trending"],
                    "source": "TopAITools"
                })

        # If BS4 failed, fallback to a regex for their JSON data
        if not tools:
            # Look for "name":"...","description":"..." patterns
            pattern = r'"name":"(?P<name>[^"]+)","description":"(?P<desc>[^"]+)"'
            for match in re.finditer(pattern, response.text):
                name = match.group('name')
                description = match.group('desc')
                # Try to guess link or use a placeholder
                tools.append({
                    "name": name,
                    "description": description,
                    "link": f"https://topaitools.com/search?q={name.replace(' ', '+')}",
                    "tags": ["Trending"],
                    "source": "TopAITools"
                })
        
        return tools
    except Exception as e:
        console.print(f"[bold red]Error parsing Top AI Tools:[/bold red] {e}")
        return []

def send_discord_alert(tools):
    """Sends a notification to Discord with the top tools of the day."""
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        console.print("[yellow]No DISCORD_WEBHOOK_URL found, skipping alert.[/yellow]")
        return

    # Take top 3 tools
    top_tools = tools[:3]
    embeds = []
    
    for tool in top_tools:
        embeds.append({
            "title": f"🚀 {tool['name']}",
            "description": tool['description'],
            "url": tool['link'],
            "color": 3447003, # Blue
            "fields": [
                {"name": "Source", "value": tool['source'], "inline": True},
                {"name": "Tags", "value": ", ".join(tool['tags']), "inline": True}
            ]
        })

    payload = {
        "content": "🔎 **Daily AI Tool Hunt: Top Picks!**",
        "embeds": embeds
    }
    
    try:
        requests.post(webhook_url, json=payload)
        console.print("[bold green]Discord alert sent![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error sending Discord alert:[/bold red] {e}")

def generate_html(tools):
    """Generates a complete HTML page with a rich, modern aesthetic."""
    date_str = datetime.now().strftime("%B %d, %Y")
    
    # Collect all unique tags
    all_tags = sorted(list(set(tag for tool in tools for tag in tool['tags'])))
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily AI Tool Hunter | {date_str}</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-color: #0b0f1a;
                --card-bg: rgba(30, 41, 59, 0.7);
                --text-main: #f8fafc;
                --text-muted: #94a3b8;
                --accent: #38bdf8;
                --accent-glow: rgba(56, 189, 248, 0.4);
                --border: rgba(51, 65, 85, 0.5);
                --glass-bg: rgba(15, 23, 42, 0.8);
            }}
            * {{ box-sizing: border-box; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); }}
            body {{
                font-family: 'Inter', -apple-system, sans-serif;
                background-color: var(--bg-color);
                background-image: 
                    radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.1) 0px, transparent 50%),
                    radial-gradient(at 100% 100%, rgba(129, 140, 248, 0.1) 0px, transparent 50%);
                color: var(--text-main);
                margin: 0;
                padding: 0;
                line-height: 1.5;
                min-height: 100vh;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 3rem 1.5rem;
            }}
            header {{
                text-align: center;
                margin-bottom: 4rem;
            }}
            .logo-wrapper {{
                display: inline-flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 1rem;
            }}
            h1 {{
                font-size: 3.5rem;
                font-weight: 800;
                margin: 0;
                letter-spacing: -0.025em;
                background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 10px 30px rgba(56, 189, 248, 0.2);
            }}
            .date-badge {{
                display: inline-block;
                padding: 0.5rem 1.25rem;
                background: var(--card-bg);
                border: 1px solid var(--border);
                border-radius: 9999px;
                color: var(--accent);
                font-weight: 600;
                font-size: 0.875rem;
                backdrop-filter: blur(8px);
            }}
            
            /* Search & Filters */
            .controls {{
                position: sticky;
                top: 1.5rem;
                z-index: 100;
                background: var(--glass-bg);
                backdrop-filter: blur(16px);
                padding: 1.5rem;
                border-radius: 1.25rem;
                border: 1px solid var(--border);
                margin-bottom: 3rem;
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
            }}
            .search-box {{
                width: 100%;
                padding: 0.75rem 1.25rem;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid var(--border);
                border-radius: 0.75rem;
                color: white;
                font-size: 1rem;
                margin-bottom: 1.5rem;
                outline: none;
            }}
            .search-box:focus {{
                border-color: var(--accent);
                box-shadow: 0 0 0 4px var(--accent-glow);
            }}
            .filters {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.6rem;
            }}
            .filter-btn {{
                background: transparent;
                color: var(--text-muted);
                border: 1px solid var(--border);
                border-radius: 0.5rem;
                padding: 0.5rem 1rem;
                cursor: pointer;
                font-size: 0.813rem;
                font-weight: 500;
            }}
            .filter-btn:hover {{
                border-color: var(--accent);
                color: var(--accent);
            }}
            .filter-btn.active {{
                background: var(--accent);
                color: #0b0f1a;
                border-color: var(--accent);
                font-weight: 600;
            }}

            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
                gap: 2rem;
            }}
            .card {{
                background: var(--card-bg);
                backdrop-filter: blur(12px);
                border-radius: 1.25rem;
                padding: 1.75rem;
                border: 1px solid var(--border);
                display: flex;
                flex-direction: column;
                position: relative;
                overflow: hidden;
            }}
            .card::before {{
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; height: 1px;
                background: linear-gradient(90deg, transparent, var(--accent), transparent);
                opacity: 0;
            }}
            .card:hover {{
                transform: translateY(-8px);
                border-color: var(--accent);
                box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4);
            }}
            .card:hover::before {{ opacity: 1; }}

            .source-badge {{
                position: absolute;
                top: 1.75rem;
                right: 1.75rem;
                font-size: 0.7rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                padding: 0.25rem 0.5rem;
                border-radius: 0.375rem;
                background: rgba(255, 255, 255, 0.05);
                color: var(--text-muted);
            }}
            .tool-identity {{
                display: flex;
                align-items: center;
                gap: 0.875rem;
                margin-bottom: 1rem;
            }}
            .favicon {{
                width: 32px;
                height: 32px;
                border-radius: 0.5rem;
                background: #fff;
                padding: 2px;
            }}
            .tool-name {{
                font-size: 1.375rem;
                font-weight: 700;
                color: var(--text-main);
                margin: 0;
            }}
            .tool-desc {{
                color: var(--text-muted);
                font-size: 0.938rem;
                margin-bottom: 1.5rem;
                flex-grow: 1;
                display: -webkit-box;
                -webkit-line-clamp: 3;
                -webkit-box-orient: vertical;
                overflow: hidden;
            }}
            
            .tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
                margin-bottom: 1.75rem;
            }}
            .tag {{
                font-size: 0.75rem;
                padding: 0.25rem 0.75rem;
                border-radius: 0.5rem;
                font-weight: 600;
                background: rgba(255, 255, 255, 0.05);
                color: var(--text-muted);
                border: 1px solid var(--border);
            }}

            .btn {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                background: var(--text-main);
                color: #0b0f1a;
                padding: 0.875rem;
                border-radius: 0.75rem;
                text-decoration: none;
                font-weight: 700;
                font-size: 0.938rem;
            }}
            .btn:hover {{
                background: var(--accent);
                transform: scale(1.02);
            }}
            
            footer {{
                text-align: center;
                margin-top: 6rem;
                padding-top: 3rem;
                border-top: 1px solid var(--border);
                color: var(--text-muted);
            }}
            .coffee-btn {{
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                background: #FFDD00;
                color: #000;
                padding: 0.75rem 1.5rem;
                border-radius: 0.75rem;
                text-decoration: none;
                font-weight: 800;
                margin-top: 1rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="logo-wrapper">
                    <h1>Daily AI Tool Hunter</h1>
                </div>
                <div>
                    <span class="date-badge">Discovered on {date_str}</span>
                </div>
            </header>
            
            <div class="controls">
                <input type="text" class="search-box" id="searchInput" placeholder="Search for tools, features, or categories..." onkeyup="filterTools()">
                <div class="filters" id="tagFilters">
                    <button class="filter-btn active" onclick="setCategory('all')">All Tools</button>
                    {"".join([f'<button class="filter-btn" onclick="setCategory(\'{tag}\')">{tag}</button>' for tag in all_tags])}
                </div>
            </div>
            
            <div class="grid" id="toolGrid">
    """
    
    for tool in tools:
        tags_data = " ".join(tool['tags']).lower()
        search_data = f"{tool['name']} {tool['description']} {tags_data}".lower()
        
        # Get favicon via Google S2
        domain = tool['link'].split('/')[2]
        favicon_url = f"https://www.google.com/s2/favicons?sz=64&domain={domain}"
        
        tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in tool['tags']])

        html_content += f"""
                <article class="card" data-search="{search_data}" data-tags="{tags_data}">
                    <span class="source-badge">{tool['source']}</span>
                    <div class="tool-identity">
                        <img src="{favicon_url}" class="favicon" alt="">
                        <h3 class="tool-name">{tool['name']}</h3>
                    </div>
                    <div class="tags">{tags_html}</div>
                    <p class="tool-desc">{tool['description']}</p>
                    <a href="{tool['link']}" target="_blank" class="btn">
                        Try it Out
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                    </a>
                </article>
        """
        
    html_content += """
            </div>
            
            <footer>
                <p>Curated by <b>Adam's AI Tool Hunter Bot</b></p>
                <a href="https://buymeacoffee.com/icecapades" class="coffee-btn">
                    <img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="" width="20">
                    Buy me a coffee
                </a>
            </footer>
        </div>

        <script>
            let currentCategory = 'all';

            function setCategory(cat) {
                currentCategory = cat.toLowerCase();
                const buttons = document.querySelectorAll('.filter-btn');
                buttons.forEach(btn => {
                    if (btn.innerText.toLowerCase() === currentCategory || (currentCategory === 'all' && btn.innerText === 'All Tools')) {
                        btn.classList.add('active');
                    } else {
                        btn.classList.remove('active');
                    }
                });
                filterTools();
            }

            function filterTools() {
                const searchTerm = document.getElementById('searchInput').value.toLowerCase();
                const cards = document.querySelectorAll('.card');
                
                cards.forEach(card => {
                    const searchData = card.getAttribute('data-search');
                    const tagsData = card.getAttribute('data-tags');
                    
                    const matchesSearch = searchData.includes(searchTerm);
                    const matchesCategory = currentCategory === 'all' || tagsData.includes(currentCategory);
                    
                    if (matchesSearch && matchesCategory) {
                        card.style.display = 'flex';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    } else {
                        card.style.display = 'none';
                        card.style.opacity = '0';
                        card.style.transform = 'translateY(20px)';
                    }
                });
            }
        </script>
    </body>
    </html>
    """
    return html_content

def publish_changes():
    """Commits and pushes all modified files to GitHub."""
    try:
        console.print("[blue]Commiting and pushing to GitHub...[/blue]")
        subprocess.run(["git", "add", "index.html", "hunter.py", "requirements.txt", "README.md"], check=True)
        subprocess.run(["git", "commit", "-m", f"Daily update: {datetime.now().strftime('%Y-%m-%d')}"], check=True)
        subprocess.run(["git", "push"], check=True)
        console.print("[bold green]🚀 Project updated successfully![/bold green]")
        console.print(f"[dim]View dashboard at: https://wealand.github.io/daily-ai-tool-hunter/[/dim]")
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Git Error:[/bold red] {e}")

def main():
    console.print("[bold blue]🔎 Hunting for new AI tools...[/bold blue]")
    
    # Path C: Multi-Source Hunting
    future_tools = fetch_future_tools()
    console.print(f"[dim]FutureTools: Found {len(future_tools)} tools.[/dim]")
    
    top_ai_tools = fetch_top_ai_tools()
    console.print(f"[dim]TopAITools: Found {len(top_ai_tools)} tools.[/dim]")
    
    # Combine and deduplicate (by name)
    seen_names = set()
    all_tools = []
    for tool in future_tools + top_ai_tools:
        name_lower = tool['name'].lower()
        if name_lower not in seen_names:
            all_tools.append(tool)
            seen_names.add(name_lower)
    
    console.print(f"[bold blue]Total unique tools: {len(all_tools)}[/bold blue]")
    
    if not all_tools:
        console.print("[yellow]No tools found today.[/yellow]")
        return

    # Display in terminal
    table = Table(title=f"New AI Tools - {datetime.now().strftime('%Y-%m-%d')}")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Source", style="magenta")
    table.add_column("Description", style="white")
    
    for tool in all_tools[:10]:
        table.add_row(tool['name'], tool['source'], tool['description'][:100] + "...")
    
    console.print(table)
    
    # Generate HTML
    html = generate_html(all_tools)
    with open("index.html", "w") as f:
        f.write(html)
    
    console.print(f"\n[bold green]✅ Success![/bold green] Webpage generated: [cyan]index.html[/cyan]")
    
    # Path B: Discord Alerts
    send_discord_alert(all_tools)
    
    # Push to GitHub
    if not os.environ.get("GITHUB_ACTIONS"):
        publish_changes()
    else:
        console.print("[dim]Running in GitHub Actions, skipping internal git push.[/dim]")

if __name__ == "__main__":
    main()
