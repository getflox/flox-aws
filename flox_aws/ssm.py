import boto3
import click
from click import Abort
from humanfriendly.tables import format_smart_table

from flox_aws.kms import KMS
from flox_aws.provider.vault import Provider


class SSM(object):
    def __init__(self, ssm, kms, key='parameter_store_key'):
        self.ssm = ssm
        self.kms = kms
        self.key = key

    def write(self, name, value, encrypt=True, tags=None):
        args = {
            'Name': name,
            'Value': value,
            'Type': 'SecureString' if encrypt else 'String',
            'Overwrite': True
        }

        if encrypt:
            args['KeyId'] = self.kms.get_key_by_alias(self.key)

        self.ssm.put_parameter(**args)

        if not tags:
            return name

        self.ssm.add_tags_to_resource(
            ResourceType='Parameter',
            ResourceId=name,
            Tags=[{'Key': k, 'Value': v} for k, v in tags.items()]
        )

        return name

    def get_parameters(self, namespace):
        parameters = {}
        search_params = dict(Path=namespace, WithDecryption=True, Recursive=True)

        while search_params.get('NextToken', 0) is not None:
            results = self.ssm.get_parameters_by_path(**search_params)

            parameters.update(
                dict(map(lambda x: (x['Name'], x['Value']), results.get('Parameters')))
            )

            search_params['NextToken'] = results.get('NextToken', None)

        return parameters

    def describe_parameters(self, namespace):
        search_params = dict(
            ParameterFilters=[dict(Key='Name', Option='BeginsWith', Values=[namespace])],
            MaxResults=50
        )
        parameters = {}

        while search_params.get('NextToken', 0) is not None:
            results = self.ssm.describe_parameters(**search_params)

            parameters.update(
                dict(map(lambda x: (x['Name'], x), results.get('Parameters')))
            )

            search_params['NextToken'] = results.get('NextToken', None)

        values = self.get_parameters(namespace)

        for name, param in parameters.items():
            yield [
                name,
                values.get(name, {}),
                param.get('Type'),
                param.get('LastModifiedDate'),
                param.get('LastModifiedUser'),
            ]

    def remove(self, name):
        return self.ssm.delete_parameter(Name=name)


@click.group()
@click.pass_obj
def ssm(flox):
    """Manage SSM parameters"""
    flox.ssm = SSM(boto3.client("ssm"), KMS(boto3.client("kms")))


@ssm.command()
@click.option('--namespace', help="Namespace under which parameter should be stored, for example service:name")
@click.option('--encrypt/--no-encrypt', help="Encrypt value", default=True)
@click.argument('name')
@click.argument('value', required=False)
@click.pass_obj
def write(flox, namespace, encrypt, name, value):
    """Write parameter to SSM storage"""
    namespace = namespace or f'/service/{flox.name}'
    key = f'{namespace}/{name}'

    value = value or click.open_file('-', 'r').read()

    flox.ssm.write(key, value, encrypt)

    click.secho(f'Value: "{value}" has been stored under: "{key}"')


@ssm.command(name="list")
@click.option('--namespace', help="Namespace under which parameter should be stored, for example service:name")
@click.pass_obj
def list_parameters(flox, namespace):
    """List all service parameters for given namespace"""
    namespace = namespace or f'/service/{flox.name}'

    click.secho(
        format_smart_table(
            flox.ssm.describe_parameters(namespace),
            ['Name', 'Value', 'Type', 'Modified', 'User']
        )
    )


@ssm.command()
@click.option('--namespace', help="Namespace under which parameter should be stored, for example service:name")
@click.argument('name')
@click.pass_obj
def remove(flox, namespace, name):
    """Remove named parameter"""
    namespace = namespace or f'/service/{flox.name}'
    key = f'{namespace}/{name}'

    if not click.confirm(f'Delete "{key}"?'):
        raise Abort

    flox.ssm.remove(key)
    click.secho('Done.', fg='green')

@ssm.command()
def env():
    Provider().session('test-ecs-deploy')
