from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_route53 as r53,
)
from constructs import Construct

class CloudResumeInfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a S3 bucket to host static website.
        resume_bucket = s3.Bucket(
            self, 
            "cri", 
            bucket_name="static-resume-20224", 
            website_index_document="index.html", 
            website_error_document="error.html",
            block_public_access=s3.BlockPublicAccess(restrict_public_buckets=False)
        )

        # Attach a bucket policy to allow public access.
        resume_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                actions=['s3:GetObject'],
                principals=[iam.StarPrincipal()],
                resources=[f'{resume_bucket.bucket_arn}/*'],
            )
        )

        # Create a hosted zone for domain.
        r53.PublicHostedZone(
            self, 
            "static-resume-hz", 
            zone_name="lekhadenihar.dev",
        )