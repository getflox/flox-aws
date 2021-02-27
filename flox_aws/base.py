import click


class AWSCommand(click.core.Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.params.extend([
            click.core.Option(
                ["-n", "--no-session"],
                default=False,
                is_flag=True,
                help="Use root credentials, no session created"
            ),
            click.core.Option(
                ["-t", "--session-ttl"],
                default=3600 * 4,
                type=int,
                help="Expiration time for aws session"
            ),
            click.core.Option(
                ["--assume-role-ttl"],
                default=15 * 60,
                type=int,
                help="Expiration time for aws assumed role"
            ),
            click.core.Option(
                ["-t", "--session-ttl"],
                default=3600 * 4,
                type=int,
                help="The mfa token to use"
            )
        ])
