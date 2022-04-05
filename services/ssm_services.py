# Standard/External modules
import boto3
import botocore
import logging

# Custom/Internal Modules
import automation_config as config
import exceptions

logger = logging.getLogger(__name__)


def get_hsm_cluster_id():
    return get_parameter(config.hsm_cluster_id_param_name)


def get_hsm_vpc_id():
    return get_parameter(config.vpc_id_ssm_param_name)


def get_parameter(param_name):
    ssm_client = boto3.client('ssm')
    try:

        logger.debug("Calling ssm.get_parameter with parameter: {}".format(param_name))

        response = ssm_client.get_parameter(Name=param_name)
    except botocore.exceptions.ClientError as err:
        # raise custom exception if necessary so we can add in details about the actual param passed
        # the standard boto ClientError does not seem to capture this
        if err.response['Error']['Code'] == 'ParameterNotFound':
            raise exceptions.SsmParameterNotFoundError("SSM parameter with name {} not found. ".
                                                       format(param_name))
        else:
            raise err

    logger.debug("get_parameter() returning: {}".format(response["Parameter"]["Value"]))

    return response["Parameter"]["Value"]


def create_hsm_cluster_id_param(hsm_cluster_id):
    put_parameter(config.hsm_cluster_id_param_name, hsm_cluster_id, "String")


def put_parameter(name, value, ssm_type):
    ssm_client = boto3.client('ssm')
    logger.debug("Calling ssm.put_parameter with name={} and value={}".format(name, value))
    ssm_client.put_parameter(Name=name, Value=value, Type=ssm_type, Overwrite=True)
    logger.debug("SSM parameter created successfully.")
