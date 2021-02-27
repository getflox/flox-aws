import json
from urllib.parse import quote_plus

import click
import requests

from flox_aws.provider.session import with_aws
from floxcore.context import Flox, EmptyContext
from floxcore.shell import execute_command


@click.group(name="aws", invoke_without_command=True, context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
@click.pass_obj
def aws(flox: Flox, args, **kwargs):
    """awscli command wrapper with session credentials provider"""
    command_name = next(iter(args), None)

    if command_name == "console":
        args = list(args)
        with EmptyContext(flox, console, args[1:], allow_interspersed_args=True, ignore_unknown_options=True) as ctx:
            return console.invoke(ctx)

    variables = flox.security_context(["aws"])
    execute_command("aws", args, variables)


@aws.command()
@click.option("--show", is_flag=True, default=False, help="Only show login URL rather than opening a browser")
@with_aws
def console(aws_session, show):
    """Generate login URL for AWS console"""
    credentials = aws_session.get_credentials()

    json_string_with_temp_credentials = json.dumps(dict(
        sessionId=credentials.access_key,
        sessionKey=credentials.secret_key,
        sessionToken=credentials.token,
    ))

    request_parameters = "?Action=getSigninToken"
    request_parameters += "&SessionDuration=43200"
    request_parameters += "&Session=" + quote_plus(json_string_with_temp_credentials)
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    r = requests.get(request_url)
    signin_token = json.loads(r.text)

    request_parameters = "?Action=login"
    request_parameters += "&Issuer=flox"
    request_parameters += "&Destination=" + quote_plus("https://console.aws.amazon.com/")
    request_parameters += "&SigninToken=" + signin_token["SigninToken"]
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    if show:
        click.echo(request_url)
    else:
        click.launch(request_url)
