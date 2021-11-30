import re
from base64 import b64decode

from flox_aws.provider.session import with_aws

from floxcore.context import Flox


@with_aws
def docker_credentials_provider(flox: Flox, repository: str, aws_session, **kwargs):
    if not re.match(r".*\.dkr\.ecr\..*?\.amazonaws\.com", repository.lower()) and repository != "aws":
        return None

    ecr = aws_session.client("ecr")
    token = ecr.get_authorization_token(registryIds=[aws_session.caller.get("Account")])
    token = token.get("authorizationData", [dict()])[0]
    auth = b64decode(token.get("authorizationToken").encode()).decode("utf-8").split(":")

    return auth[0], auth[1], token.get("proxyEndpoint")
