import ecs_tool.cli

from flox_aws.command import aws
from flox_aws.configure import AWSConfiguration
from flox_aws.docker import docker_credentials_provider
from flox_aws.ecs import pre_invoke
from flox_aws.kms import kms
from flox_aws.provider.session import get_session
from floxcore.context import Flox
from floxcore.plugin import Plugin


class AWSPlugin(Plugin):
    def configuration(self):
        return AWSConfiguration()

    def handle_execution_context(self, flox: Flox) -> dict:
        session = get_session(flox)

        if not session:
            return {}

        credentials = session.get_credentials()

        vars = dict(
            AWS_DEFAULT_REGION=session.region_name,
            AWS_SECRET_ACCESS_KEY=credentials.secret_key,
            AWS_ACCESS_KEY_ID=credentials.access_key,
        )

        if credentials.token:
            vars["AWS_SESSION_TOKEN"] = credentials.token

        return vars

    def add_commands(self, cli):
        cli.add_command(aws)
        cli.add_command(kms)

        ecs_tool.cli.cli.pre_invoke = pre_invoke
        cli.add_command(ecs_tool.cli.cli, name="ecs")

    def handle_docker_credentials(self, flox: Flox, repository=None):
        return docker_credentials_provider(flox=flox, repository=repository)


def plugin():
    return AWSPlugin()
