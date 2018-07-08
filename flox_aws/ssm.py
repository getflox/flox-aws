import boto3
import click

from flox_aws.kms import KMS


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
def list_parameters():
    """List all service parameters for given namespace"""



@ssm.command()
def remove():
    """Remove named parameter"""
