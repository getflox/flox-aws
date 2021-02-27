from floxcore.config import Configuration, ParamDefinition


class AWSConfiguration(Configuration):
    def parameters(self):
        return (
            ParamDefinition("region", "AWS Default region"),
            ParamDefinition("role_arn", "Role (ARN) to be assumed", default="", filter_empty=False),
            ParamDefinition("mfa_arn", "Multi factor authentication device ARN", default="", filter_empty=False),
            ParamDefinition("kms", "Default KMS key to be used for encryption", default=""),
        )

    def secrets(self):
        return (
            ParamDefinition("key_id", "AWS Key Id", secret=True, default=""),
            ParamDefinition("key_secret", "AWS Secret Key", secret=True, default=""),
        )

    def schema(self):
        pass
