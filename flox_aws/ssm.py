import click


@click.group()
def cli():
    """SubCommandline interface for yourpackage."""
    click.echo("test")

