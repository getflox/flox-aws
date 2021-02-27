import base64

import click
from click import Abort

from floxcore.console import warning, success, error
from floxcore.context import Flox


@click.group()
def kms():
    """AWS KMS encryption/decryption support commands"""
    pass


@kms.command()
@click.option("--key-id", help="Key ARN to be used for encryption (overwrite default one)", default="alias/flox")
@click.option("--stdin", help="Read value from stdin", default=False, is_flag=True)
@click.option("--with-strip/--without-strip", help="Strip new lines from input", default=True, is_flag=True)
@click.argument("plaintext", required=False)
@click.pass_obj
def encrypt(flox: Flox, with_strip, key_id, stdin, plaintext, **kwargs):
    """Encrypt given value with KMS"""
    from flox_aws import get_session

    if stdin:
        plaintext = click.get_text_stream('stdin').read()

    if not plaintext:
        error("Empty plaintext value, you need to either provide argument or stdin value")
        raise Abort

    if with_strip:
        plaintext = plaintext.strip()

    session = get_session(flox)
    kms = session.client("kms")

    key_id = flox.settings.aws.kms or key_id

    if key_id == "alias/flox":
        aliases = kms.list_aliases()
        create = False
        if len(list(filter(lambda x: x["AliasName"] == key_id, aliases.get("Aliases")))) == 0:
            warning(f"Requested encryption with default flox key: {key_id}, which doesn't exist.")
            create = click.prompt(click.style("Would you like to create it?", fg="yellow"))

        if create:
            key = kms.create_key()
            alias = kms.create_alias(
                AliasName=key_id,
                TargetKeyId=key.get("KeyMetadata").get("KeyId")
            )
            success(f"Created Key with ARN: {key.get('KeyMetadata').get('Arn')}")

    encrypted = kms.encrypt(KeyId=key_id, Plaintext=plaintext)

    click.echo(base64.b64encode(encrypted.get("CiphertextBlob")))


@kms.command()
@click.option("--with-base64-decode/--without-base64-decode", help="Input is base64 encoded, decode before decrypting",
              is_flag=True, default=True)
@click.option("--stdin", help="Read value from stdin", default=False, is_flag=True)
@click.argument("encrypted", required=False)
@click.pass_obj
def decrypt(flox: Flox, with_base64_decode, stdin, encrypted):
    """Decrypt given value with KMS"""

    if stdin:
        encrypted = click.get_text_stream('stdin').read()

    if with_base64_decode:
        encrypted = base64.b64decode(encrypted)

    from flox_aws import get_session
    session = get_session(flox)
    kms = session.client("kms")
    decrypted = kms.decrypt(CiphertextBlob=encrypted)

    click.echo(decrypted.get("Plaintext"))
