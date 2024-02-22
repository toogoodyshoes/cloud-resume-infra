from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_route53 as r53,
    aws_certificatemanager as acm,
    aws_cloudfront as cf,
    aws_cloudfront_origins as origins,
    aws_route53_targets as targets,
)
from constructs import Construct
from certificate import *

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

        # SSL/TLS Certificate
        certificate_arn = CERTIFICATE_ARN
        certificate = acm.Certificate.from_certificate_arn(self, "domain-cert", certificate_arn=certificate_arn)
        
        # Create a hosted zone for domain.
        resume_hz = r53.PublicHostedZone(
            self, 
            "static-resume-hz", 
            zone_name="lekhadenihar.dev",
        )

        # Create a CNAME record for certificate
        r53.CnameRecord(
            self,
            "cert-cname",
            zone=resume_hz,
            domain_name=DOMAIN_NAME,
            record_name=RECORD_NAME,
        )

        # CloudFront Distribution
        resume_distribution = cf.Distribution(
            self,
            "resume-distribution",
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3Origin(resume_bucket),
                viewer_protocol_policy=cf.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=["lekhadenihar.dev"],
            certificate=certificate,
        )

        # Add A record to hosted zone for CloudFront distribution
        r53.ARecord(
            self,
            'alias',
            zone=resume_hz,
            target=r53.RecordTarget.from_alias(
                targets.CloudFrontTarget(resume_distribution)
            ),
        )

        # Add AAAA Record to hosted zone for CloudFront distribution
        r53.AaaaRecord(
            self,
            'alias-ipv6',
            zone=resume_hz,
            target=r53.RecordTarget.from_alias(
                targets.CloudFrontTarget(resume_distribution)
            ),
        )

        
