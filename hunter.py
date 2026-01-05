import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
from rich.console import Console
from rich.table import Table

console = Console()

def fetch_new_tools():
    """Scrapes FutureTools for recently added AI tools."""
    url = "https://www.futuretools.io/?sort=date"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tools = []
        # Find tool cards - the selector might need updates if the site structure changes
        tool_cards = soup.select('.tool-card-style')
        
        for card in tool_cards:
            name_elem = card.select_one('.tool-name')
            desc_elem = card.select_one('.tool-description')
            link_elem = card.select_one('a')
            
            if name_elem and desc_elem:
                name = name_elem.text.strip()
                description = desc_elem.text.strip()
                link = "https://www.futuretools.io" + link_elem['href'] if link_elem else "N/A"
                
                tools.append({
                    "name": name,
                    "description": description,
                    "link": link
                })
        
        return tools
    except Exception as e:
        console.print(f"[bold red]Error scraping FutureTools:[/bold red] {e}")
        return []

def save_report(tools):
    """Saves the found tools to a daily Markdown report."""
    if not tools:
        return None
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    
    file_path = os.path.join(report_dir, f"{date_str}.md")
    
    with open(file_path, "w") as f:
        f.write(f"# New AI Tools - {date_str}\n\n")
        for tool in tools:
            f.write(f"### {tool['name']}\n")
            f.write(f"- **Description:** {tool['description']}\n")
            f.write(f"- **Link:** [View on FutureTools]({tool['link']})\n\n")
            
    return file_path

def main():
    console.print(f"[bold blue]🔎 Hunting for new AI tools...[/bold blue]")
    
    tools = fetch_new_tools()
    
    if not tools:
        console.print("[yellow]No tools found today.[/yellow]")
        return

    # Display in terminal
    table = Table(title=f"New AI Tools - {datetime.now().strftime('%Y-%m-%d')}")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    
    for tool in tools[:10]: # Show top 10 in terminal
        table.add_row(tool['name'], tool['description'][:100] + "...")
    
    console.print(table)
    
    # Save report
    report_path = save_report(tools)
    if report_path:
        console.print(f"\n[bold green]✅ Success![/bold green] Full report saved to: [cyan]{report_path}[/cyan]")

if __name__ == "__main__":
    main()
