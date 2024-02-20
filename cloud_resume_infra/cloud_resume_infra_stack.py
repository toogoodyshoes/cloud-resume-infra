from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct

class CloudResumeInfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        resume_bucket = s3.Bucket(
            self, 
            "cri", 
            bucket_name="static-resume-20224", 
            website_index_document="index.html", 
            website_error_document="error.html",
            block_public_access=s3.BlockPublicAccess(restrict_public_buckets=False)
        )

        resume_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                actions=['s3:GetObject'],
                principals=[iam.StarPrincipal()],
                resources=[f'{resume_bucket.bucket_arn}/*'],
            )
        )