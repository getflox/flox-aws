from flox_aws.provider import CredentialsProvider


class Provider(CredentialsProvider):
    @property
    def name(self):
        return 'aws-config'

    def session(self, name):
        pass

    def credentials(self, name):
        pass
