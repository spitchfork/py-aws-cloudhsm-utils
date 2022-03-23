# Standard/External modules
import boto3
import botocore
import logging

# Custom/Internal Modules
import automation_config as config
import exceptions

logger = logging.getLogger(__name__)


def get_hsm_vpc_id():
    ssm_client = boto3.client('ssm')
    try:

        logger.debug("Calling ssm.get_parameter with parameter: {}".format(config.vpc_id_ssm_param_name))

        response = ssm_client.get_parameter(Name=config.vpc_id_ssm_param_name)
    except botocore.exceptions.ClientError as err:
        # raise custom exception if necessary so we can add in details about the actual param passed
        # the standard boto ClientError does not seem to capture this
        if err.response['Error']['Code'] == 'ParameterNotFound':
            raise exceptions.SsmParameterNotFoundError("SSM parameter with name {} not found. ".
                                                       format(config.vpc_id_ssm_param_name))
        else:
            raise err

    logger.debug("get_hsm_vpc_id() returning: {}".format(response["Parameter"]["Value"]))

    return response["Parameter"]["Value"]
