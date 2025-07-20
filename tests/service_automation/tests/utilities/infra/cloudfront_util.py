import boto3
from loguru import logger


class CloudFrontWrapper:
    """Encapsulates Amazon CloudFront operations."""

    def __init__(self):
        """
        :param cloudfront_client: A Boto3 CloudFront client
        """
        self.cloudfront_client = boto3.client("cloudfront")

    def list_distributions(self,cloudfront_s3 ):
        cloudfront_s3 = cloudfront_s3 + ".s3.eu-west-2.amazonaws.com"
        distributions = self.cloudfront_client.list_distributions()
        if distributions["DistributionList"]["Quantity"] > 0:
            for distribution in distributions['DistributionList']['Items']:
                if distribution['Origins']['Items'][1]['DomainName'] == cloudfront_s3:
                    logger.info(f"Found CloudFront distribution for S3 bucket: {cloudfront_s3}")
                    cloudfront_url = f"https://{distribution['DomainName']}"
                    return cloudfront_url
        else:
            logger.info("No CloudFront distributions detected.")


