import click
from humanfriendly.tables import format_smart_table


@click.group()
@click.pass_obj
def aws(flox):
    """AWS integration for flox"""


@aws.command()
@click.pass_obj
def credentials(flox):
    """Display AWS session credentials"""
    click.secho(
        format_smart_table(
            flox.container.get('aws-credentials-provider').credentials(flox.profile).env.items(),
            ['Name', 'Value']
        )
    )
