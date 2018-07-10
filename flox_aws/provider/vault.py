import subprocess

import boto3
import click
from flox_aws.provider import CredentialsProvider, Credentials, CredentialsException


class Provider(CredentialsProvider):
    """Execute AWS related commands using aws-vault"""

    def __init__(self, profile_pattern):
        super().__init__(profile_pattern)
        self.sessions = {}

    @property
    def name(self):
        return 'aws-vault'

    def session(self, name):
        if name in self.sessions:
            return self.sessions[name]

        self.sessions[name] = boto3.Session(
            **self.credentials(name).args
        )

        return self.sessions[name]

    def credentials(self, name) -> Credentials:
        p = subprocess.Popen(
            ['aws-vault', 'exec', self._get_profile_name(name), '--', 'env'],
            stdin=click.get_text_stream('stdin'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )

        stdout, stderr = p.communicate()

        if p.returncode != 0:
            raise CredentialsException(p.stderr, p.returncode)

        env = dict(filter(
            lambda x: x[0].startswith('AWS_'),
            map(lambda x: x.strip().split("=", 1), stdout.splitlines()))
        )

        return Credentials(
            aws_access_key_id=env.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=env.get('AWS_SECRET_ACCESS_KEY'),
            aws_session_token=env.get('AWS_SESSION_TOKEN'),
            region_name=env.get('AWS_REGION')
        )
