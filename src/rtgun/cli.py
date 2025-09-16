import click
from .sync_timebase import sync_window

@click.group()
def main():
    """audio-sync-triangulation CLI"""
    pass

@main.command()
@click.option("--trigger", required=True, help="ISO time, e.g. 2025-09-16T11:00:00Z")
def sync(trigger):
    """Cut time-aligned window around trigger and save to data/synced/"""
    data, fs = sync_window(trigger)
    click.echo(f"Synced {len(data)} channels at {fs} Hz")

if __name__ == "__main__":
    main()