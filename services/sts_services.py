# Standard/External modules
import boto3
import logging

logger = logging.getLogger(__name__)


def get_aws_account_id():
    sts_client = boto3.client('sts')
    response = sts_client.get_caller_identity()

    logger.debug("get_aws_account_id() returning: {}".format(response["Account"]))

    return response["Account"]
