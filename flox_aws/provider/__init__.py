from abc import ABC, abstractmethod

from click import ClickException


class CredentialsException(ClickException):
    """Failed to obtain credentials"""

    def __init__(self, message, exit_code):
        super().__init__(message)
        self.exit_code = exit_code


class Credentials:
    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_session_token=None, region_name=None):
        self.aws_session_token = aws_session_token
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_access_key_id = aws_access_key_id
        self.region_name = region_name

    @property
    def args(self):
        return dict(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            aws_session_token=self.aws_session_token,
            region_name=self.region_name
        )

    @property
    def env(self):
        return dict(
            AWS_ACCESS_KEY_ID=self.aws_access_key_id,
            AWS_SECRET_ACCESS_KEY=self.aws_secret_access_key,
            AWS_SESSION_TOKEN=self.aws_session_token,
            AWS_REGION=self.region_name,
            AWS_DEFAULT_REGION=self.region_name
        )


class CredentialsProvider(ABC):
    def __init__(self, profile_pattern):
        self.profile_pattern = profile_pattern

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def session(self, name):
        """Return session for named profile"""

    @abstractmethod
    def credentials(self, name) -> Credentials:
        """Return credentials for named profile"""

    def _get_profile_name(self, stage):
        return self.profile_pattern.format(stage=stage)
