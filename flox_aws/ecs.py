from os import getenv, environ

from flox_aws.provider.session import with_aws
from floxcore.context import Flox


@with_aws
def pre_invoke(flox: Flox, aws_session):
    aws_vars = dict(
        AWS_DEFAULT_REGION=getenv("AWS_DEFAULT_REGION"),
        AWS_SECRET_ACCESS_KEY=getenv("AWS_SECRET_ACCESS_KEY"),
        AWS_ACCESS_KEY_ID=getenv("AWS_ACCESS_KEY_ID"),
        AWS_SESSION_TOKEN=getenv("AWS_SESSION_TOKEN"),
    )

    credentials = aws_session.get_credentials()
    environ["AWS_DEFAULT_REGION"] = aws_session.region_name
    environ["AWS_SECRET_ACCESS_KEY"] = credentials.secret_key
    environ["AWS_ACCESS_KEY_ID"] = credentials.access_key

    if hasattr(credentials, "token") and credentials.token:
        environ["AWS_SESSION_TOKEN"] = credentials.token

    return aws_vars


def post_invoke(flox: Flox, pre_invoke_state):
    environ.update(pre_invoke_state)
