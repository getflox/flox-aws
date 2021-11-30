import json
from functools import wraps

import boto3
import click
from boto3 import Session
from botocore.exceptions import ClientError

from floxcore.context import Flox
from floxcore.exceptions import InvalidFunctionCallException, MissingConfigurationValue


def with_aws(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        flox = click.get_current_context().obj

        if not isinstance(flox, Flox):
            raise InvalidFunctionCallException("Decorator `with_aws_session` requires a function to be called with "
                                               "named flox paramter, or flox instance to be first argument")

        session_name = f"aws_session_{flox.name}@{flox.profile}"
        session_data = flox.secrets.getone(session_name)
        session = None

        if session_data:
            session_data = json.loads(session_data)
            session = boto3.Session(
                aws_access_key_id=session_data.get("access_key"),
                aws_secret_access_key=session_data.get("secret_key"),
                aws_session_token=session_data.get("token"),
                region_name=flox.settings.aws.region,
            )
            try:
                session.caller = session.client("sts").get_caller_identity()
            except ClientError as e:
                session_data = None

        if not session_data:
            session = create_session(flox, session_name)
            if not session.get_credentials():
                raise MissingConfigurationValue("access_key, aws_key_secret")
            session.caller = session.client("sts").get_caller_identity()
            flox.secrets.put(session_name, json.dumps(session.get_credentials().__dict__))

        return f(*args, aws_session=session, **kwargs)

    return wrapper


def assume_role(flox: Flox, client, session_name="flox"):
    params = dict(
        RoleArn=flox.settings.aws.role_arn,
        RoleSessionName=session_name,
    )

    if flox.settings.aws.mfa_arn:
        params["SerialNumber"] = flox.settings.aws.mfa_arn
        params["TokenCode"] = click.prompt(f"Enter MFA code for {flox.settings.aws.mfa_arn}")

    try:
        return client.assume_role(**params)
    except ClientError as e:
        raise ConnectionError(e.response)


def create_session(flox: Flox, session_name) -> Session:
    secrets = dict(
        aws_access_key_id=flox.secrets.getone("aws_key_id"),
        aws_secret_access_key=flox.secrets.getone("aws_key_secret")
    )
    client = boto3.client("sts", **secrets)

    if flox.settings.aws.role_arn:
        role = assume_role(flox, client, session_name).get("Credentials")
        credentials = dict(
            aws_access_key_id=role.get("AccessKeyId"),
            aws_secret_access_key=role.get("SecretAccessKey"),
            aws_session_token=role.get("SessionToken"),
        )
    else:
        token = client.get_federation_token(Name=flox.id)
        credentials = dict(
            aws_access_key_id=token.get("Credentials").get("AccessKeyId"),
            aws_secret_access_key=token.get("Credentials").get("SecretAccessKey"),
            aws_session_token=token.get("Credentials").get("SessionToken"),
        )

    return boto3.Session(**credentials)


@with_aws
def get_session(flox: Flox, aws_session):
    return aws_session
