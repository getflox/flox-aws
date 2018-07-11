from schema import Optional, And, Use

from flox_aws.extension.docker.repository import ElasticRepository
from flox_aws.provider.profile import Provider as ConfigProvider
from flox_aws.provider.vault import Provider as VaultProvider


def config():
    return {
        Optional('profile_pattern', default='{stage}'): str,
        Optional('credentials_provider', default='vault'): And(str, Use(str.lower), lambda x: x in ('vault', 'config'))
    }


def services(container, config):
    provider = container.registry(
        VaultProvider(config.profile_pattern) if config.credentials_provider == 'vault' else ConfigProvider(
            config.profile_pattern),
        ['aws-credentials-provider']
    )

    repository = container.registry(
        ElasticRepository(provider),
        ['docker-repository']
    )

    container.connect('docker-context', lambda x, profile: provider.credentials(profile).env)
