"""CLI interface for the AI Event Scraper."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

from core.config import settings
from core.models import ScrapeRequest, QueryRequest
from core.database import db
from scrapers.scraper_manager import scraper_manager

# Initialize Typer app and Rich console
app = typer.Typer(help="AI Event Scraper - Find and scrape events from multiple sources")
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.command()
def scrape(
    city: str = typer.Argument(..., help="City name to search for events"),
    country: str = typer.Argument(..., help="Country name to search for events"),
    radius: int = typer.Option(100, "--radius", "-r", help="Search radius in kilometers"),
    start_date: Optional[str] = typer.Option(None, "--start-date", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end-date", "-e", help="End date (YYYY-MM-DD)"),
    categories: Optional[str] = typer.Option(None, "--categories", "-c", help="Comma-separated categories to filter"),
    save: bool = typer.Option(True, "--save/--no-save", help="Save events to database"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Scrape events from multiple sources for a given city and country."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse dates
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Invalid start date format: {start_date}. Use YYYY-MM-DD[/red]")
            raise typer.Exit(1)
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Invalid end date format: {end_date}. Use YYYY-MM-DD[/red]")
            raise typer.Exit(1)
    
    # Parse categories
    category_list = None
    if categories:
        category_list = [cat.strip() for cat in categories.split(",")]
    
    # Create scrape request
    request = ScrapeRequest(
        city=city,
        country=country,
        radius_km=radius,
        start_date=start_dt,
        end_date=end_dt,
        categories=category_list
    )
    
    # Run the scraping process
    asyncio.run(_run_scraping(request, save))


async def _run_scraping(request: ScrapeRequest, save_to_db: bool):
    """Run the scraping process with progress indicators."""
    
    # Connect to database only if saving
    if save_to_db:
        await db.connect()
    
    try:
        # Display scraping info
        console.print(Panel.fit(
            f"[bold blue]AI Event Scraper[/bold blue]\n"
            f"City: {request.city}\n"
            f"Country: {request.country}\n"
            f"Radius: {request.radius_km}km\n"
            f"Date Range: {request.start_date or 'Any'} to {request.end_date or 'Any'}",
            title="Scraping Configuration"
        ))
        
        # Check scraper status
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Checking scraper status...", total=None)
            
            status = await scraper_manager.get_scraper_status()
            
            progress.update(task, description="Scraper status checked")
        
        # Display scraper status
        status_table = Table(title="Scraper Status")
        status_table.add_column("Platform", style="cyan")
        status_table.add_column("Status", style="green")
        status_table.add_column("URL")
        
        for platform, info in status.items():
            status_color = "green" if info["status"] == "online" else "red"
            status_table.add_row(
                platform.title(),
                f"[{status_color}]{info['status']}[/{status_color}]",
                info.get("base_url", "N/A")
            )
        
        console.print(status_table)
        
        # Start scraping
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Scraping events from all sources...", total=None)
            
            events = await scraper_manager.scrape_all_events(request)
            
            progress.update(task, description=f"Found {len(events)} events")
        
        if not events:
            console.print("[yellow]No events found for the specified criteria.[/yellow]")
            return
        
        # Display results summary
        console.print(Panel.fit(
            f"[bold green]Scraping Complete![/bold green]\n"
            f"Total Events Found: {len(events)}\n"
            f"Unique Events: {len(set(event.title for event in events))}",
            title="Results Summary"
        ))
        
        # Save to database if requested
        if save_to_db:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Saving events to database...", total=None)
                
                event_ids = await scraper_manager.save_events_to_database(events)
                
                progress.update(task, description=f"Saved {len(event_ids)} events to database")
            
            console.print(f"[green]Successfully saved {len(event_ids)} events to database![/green]")
        else:
            console.print("[yellow]Events not saved to database (--no-save flag used)[/yellow]")
        
        # Display sample events
        _display_events_table(events[:10], "Sample Events (First 10)")
        
        if len(events) > 10:
            console.print(f"[dim]... and {len(events) - 10} more events[/dim]")
    
    except Exception as e:
        console.print(f"[red]Error during scraping: {e}[/red]")
        logger.error(f"Scraping error: {e}", exc_info=True)
        raise typer.Exit(1)
    
    finally:
        if save_to_db:
            await db.disconnect()


@app.command()
def query(
    city: Optional[str] = typer.Option(None, "--city", "-c", help="Filter by city"),
    country: Optional[str] = typer.Option(None, "--country", help="Filter by country"),
    start_date: Optional[str] = typer.Option(None, "--start-date", "-s", help="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end-date", "-e", help="End date (YYYY-MM-DD)"),
    category: Optional[str] = typer.Option(None, "--category", help="Filter by category"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags to filter"),
    limit: int = typer.Option(100, "--limit", "-l", help="Maximum number of events to return"),
    offset: int = typer.Option(0, "--offset", "-o", help="Number of events to skip"),
    export: Optional[str] = typer.Option(None, "--export", help="Export format (json, csv)")
):
    """Query events from the database."""
    
    # Parse dates
    start_dt = None
    end_dt = None
    
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Invalid start date format: {start_date}. Use YYYY-MM-DD[/red]")
            raise typer.Exit(1)
    
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            console.print(f"[red]Invalid end date format: {end_date}. Use YYYY-MM-DD[/red]")
            raise typer.Exit(1)
    
    # Parse tags
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
    
    # Create query request
    query_request = QueryRequest(
        city=city,
        country=country,
        start_date=start_dt,
        end_date=end_dt,
        category=category,
        tags=tag_list,
        limit=limit,
        offset=offset
    )
    
    # Run the query
    asyncio.run(_run_query(query_request, export))


async def _run_query(query_request: QueryRequest, export_format: Optional[str]):
    """Run the database query."""
    
    # Connect to database
    await db.connect()
    
    try:
        # Display query info
        filters = []
        if query_request.city:
            filters.append(f"City: {query_request.city}")
        if query_request.country:
            filters.append(f"Country: {query_request.country}")
        if query_request.start_date:
            filters.append(f"Start Date: {query_request.start_date}")
        if query_request.end_date:
            filters.append(f"End Date: {query_request.end_date}")
        if query_request.category:
            filters.append(f"Category: {query_request.category}")
        if query_request.tags:
            filters.append(f"Tags: {', '.join(query_request.tags)}")
        
        filter_text = "\n".join(filters) if filters else "No filters applied"
        
        console.print(Panel.fit(
            f"[bold blue]Database Query[/bold blue]\n{filter_text}\n"
            f"Limit: {query_request.limit}\n"
            f"Offset: {query_request.offset}",
            title="Query Configuration"
        ))
        
        # Execute query
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Querying database...", total=None)
            
            events = await db.find_events(query_request)
            total_count = await db.get_event_count(query_request)
            
            progress.update(task, description=f"Found {len(events)} events")
        
        if not events:
            console.print("[yellow]No events found matching the criteria.[/yellow]")
            return
        
        # Display results
        console.print(Panel.fit(
            f"[bold green]Query Results[/bold green]\n"
            f"Events Found: {len(events)}\n"
            f"Total in Database: {total_count}",
            title="Results Summary"
        ))
        
        # Export if requested
        if export_format:
            _export_events(events, export_format)
        else:
            _display_events_table(events, "Query Results")
    
    except Exception as e:
        console.print(f"[red]Error during query: {e}[/red]")
        logger.error(f"Query error: {e}", exc_info=True)
        raise typer.Exit(1)
    
    finally:
        await db.disconnect()


def _display_events_table(events: List, title: str):
    """Display events in a formatted table."""
    table = Table(title=title)
    table.add_column("Title", style="cyan", no_wrap=False)
    table.add_column("Date", style="green")
    table.add_column("Location", style="yellow")
    table.add_column("Category", style="magenta")
    table.add_column("Price", style="blue")
    table.add_column("Sources", style="dim")
    
    for event in events:
        # Format date
        date_str = event.start_date.strftime("%Y-%m-%d %H:%M")
        
        # Format location
        location_str = f"{event.location.city}, {event.location.country}"
        if event.location.venue_name:
            location_str = f"{event.location.venue_name}, {location_str}"
        
        # Format sources
        sources_str = ", ".join([source.platform for source in event.sources])
        
        table.add_row(
            event.title[:50] + "..." if len(event.title) > 50 else event.title,
            date_str,
            location_str[:30] + "..." if len(location_str) > 30 else location_str,
            event.category or "N/A",
            event.price or "N/A",
            sources_str
        )
    
    console.print(table)


def _export_events(events: List, format_type: str):
    """Export events to specified format."""
    if format_type.lower() == "json":
        import json
        from datetime import datetime
        
        # Convert events to JSON-serializable format
        events_data = []
        for event in events:
            event_dict = event.dict()
            # Convert datetime objects to strings
            event_dict["start_date"] = event.start_date.isoformat()
            if event.end_date:
                event_dict["end_date"] = event.end_date.isoformat()
            event_dict["created_at"] = event.created_at.isoformat()
            event_dict["updated_at"] = event.updated_at.isoformat()
            events_data.append(event_dict)
        
        filename = f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(events_data, f, indent=2)
        
        console.print(f"[green]Events exported to {filename}[/green]")
    
    elif format_type.lower() == "csv":
        import csv
        from datetime import datetime
        
        filename = f"events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                "Title", "Description", "Start Date", "End Date",
                "City", "Country", "Venue", "Address",
                "Category", "Price", "Currency", "Tags",
                "Email", "Phone", "Website", "Sources"
            ])
            
            # Write data
            for event in events:
                writer.writerow([
                    event.title,
                    event.description or "",
                    event.start_date.isoformat(),
                    event.end_date.isoformat() if event.end_date else "",
                    event.location.city,
                    event.location.country,
                    event.location.venue_name or "",
                    event.location.address,
                    event.category or "",
                    event.price or "",
                    event.currency or "",
                    ", ".join(event.tags),
                    event.contact_info.email or "",
                    event.contact_info.phone or "",
                    event.contact_info.website or "",
                    ", ".join([source.platform for source in event.sources])
                ])
        
        console.print(f"[green]Events exported to {filename}[/green]")
    
    else:
        console.print(f"[red]Unsupported export format: {format_type}[/red]")
        console.print("Supported formats: json, csv")


@app.command()
def random(
    city: str = typer.Argument(..., help="City name to search for events"),
    country: str = typer.Argument(..., help="Country name to search for events"),
    day: int = typer.Argument(..., help="Day of the month (1-31)"),
    month: int = typer.Argument(..., help="Month (1-12)"),
    year: int = typer.Argument(..., help="Year (e.g., 2024)"),
    count: int = typer.Option(10, "--count", "-n", help="Number of random events to return"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Get random events for a specific date and location."""
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate date inputs
    try:
        target_date = datetime(year, month, day)
    except ValueError as e:
        console.print(f"[red]Invalid date: {e}[/red]")
        console.print("Please provide valid day (1-31), month (1-12), and year")
        raise typer.Exit(1)
    
    # Validate count
    if count <= 0 or count > 100:
        console.print("[red]Count must be between 1 and 100[/red]")
        raise typer.Exit(1)
    
    asyncio.run(_get_random_events(city, country, target_date, count))


async def _get_random_events(city: str, country: str, target_date: datetime, count: int):
    """Get random events for a specific date and location."""
    
    # Connect to database
    await db.connect()
    
    try:
        # Display configuration
        console.print(Panel.fit(
            f"[bold blue]Random Events Query[/bold blue]\n"
            f"City: {city}\n"
            f"Country: {country}\n"
            f"Date: {target_date.strftime('%B %d, %Y')}\n"
            f"Count: {count} random events",
            title="Random Events Configuration"
        ))
        
        # Create query for the specific date
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        query_request = QueryRequest(
            city=city,
            country=country,
            start_date=start_of_day,
            end_date=end_of_day,
            limit=1000,  # Get more events to sample from
            offset=0
        )
        
        # Execute query
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Finding events for the specified date...", total=None)
            
            events = await db.find_events(query_request)
            
            progress.update(task, description=f"Found {len(events)} events for {target_date.strftime('%B %d, %Y')}")
        
        if not events:
            console.print(f"[yellow]No events found for {city}, {country} on {target_date.strftime('%B %d, %Y')}[/yellow]")
            return
        
        # Get random sample
        import random
        random_events = random.sample(events, min(count, len(events)))
        
        # Display results
        console.print(Panel.fit(
            f"[bold green]Random Events Found[/bold green]\n"
            f"Date: {target_date.strftime('%B %d, %Y')}\n"
            f"Location: {city}, {country}\n"
            f"Total events available: {len(events)}\n"
            f"Random events returned: {len(random_events)}",
            title="Results Summary"
        ))
        
        # Display events table
        _display_events_table(random_events, f"Random Events for {target_date.strftime('%B %d, %Y')}")
        
    finally:
        await db.disconnect()


@app.command()
def status():
    """Check the status of the system and database connection."""
    asyncio.run(_check_status())


async def _check_status():
    """Check system status."""
    console.print(Panel.fit(
        "[bold blue]AI Event Scraper Status[/bold blue]",
        title="System Status"
    ))
    
    # Check database connection
    try:
        await db.connect()
        console.print("[green]✓ Database connection: OK[/green]")
        
        # Get event count
        total_events = await db.get_event_count(QueryRequest())
        console.print(f"[green]✓ Total events in database: {total_events}[/green]")
        
        await db.disconnect()
    except Exception as e:
        console.print(f"[red]✗ Database connection: FAILED ({e})[/red]")
    
    # Check scraper status
    try:
        status = await scraper_manager.get_scraper_status()
        
        for platform, info in status.items():
            if info["status"] == "online":
                console.print(f"[green]✓ {platform.title()} scraper: OK[/green]")
            else:
                console.print(f"[red]✗ {platform.title()} scraper: FAILED[/red]")
    
    except Exception as e:
        console.print(f"[red]✗ Scraper status check: FAILED ({e})[/red]")
    
    # Check configuration
    console.print(f"[blue]Configuration:[/blue]")
    console.print(f"  MongoDB URL: {settings.mongodb_url}")
    console.print(f"  Database: {settings.mongodb_database}")
    console.print(f"  OpenAI API: {'✓ Configured' if settings.openai_api_key else '✗ Not configured'}")
    console.print(f"  Default Radius: {settings.default_radius_km}km")


@app.command()
def config():
    """Display current configuration."""
    console.print(Panel.fit(
        f"[bold blue]AI Event Scraper Configuration[/bold blue]\n"
        f"MongoDB URL: {settings.mongodb_url}\n"
        f"Database: {settings.mongodb_database}\n"
        f"OpenAI API Key: {'✓ Set' if settings.openai_api_key else '✗ Not set'}\n"
        f"Default Radius: {settings.default_radius_km}km\n"
        f"Max Concurrent Requests: {settings.max_concurrent_requests}\n"
        f"Request Delay: {settings.request_delay_seconds}s",
        title="Configuration"
    ))


if __name__ == "__main__":
    app()
