# Standard/External modules
import boto3
import logging

# Custom/Internal Modules
from services import ssm_services
import automation_config as config
import exceptions

logger = logging.getLogger(__name__)


def get_sg_id_by_name(sg_name):
    name_filter = [{"Name": "group-name", "Values": [sg_name]}]
    return get_sg_id(name_filter)


def get_sg_id_by_tag(tag_name, tag_value):
    tag_filter = [{"Name": "tag:" + tag_name, "Values": [tag_value]}]
    return get_sg_id(tag_filter)


def get_sg_id(boto_filter):
    ec2_client = boto3.client('ec2')
    sg = ec2_client.describe_security_groups(Filters=boto_filter)
    # throw exception if no security group can be found e.g. cfn template not run yet
    # or more than one exists with the given name or tag
    if len(sg["SecurityGroups"]) != 1:
        raise exceptions.SecurityGroupNotFoundError("No security group id found for the given filter.")

    logger.debug("Returning security group Id: {}".format(sg["SecurityGroups"][0]["GroupId"]))
    sg_id = sg["SecurityGroups"][0]["GroupId"]
    return sg_id


def add_source_sg_ingress_rule_to_sg(source_sg_id, target_sg_id, aws_account_id, from_port, to_port):
    ec2 = boto3.resource('ec2')
    security_group = ec2.SecurityGroup(target_sg_id)
    security_group.authorize_ingress(IpPermissions=[{"FromPort": from_port,
                                                     "IpProtocol": 'tcp',
                                                     "ToPort": to_port,
                                                     "UserIdGroupPairs": [{"GroupId": source_sg_id,
                                                                           "UserId": aws_account_id}]}])


def get_hsm_enabled_subnets():
    ec2_client = boto3.client('ec2')
    # Get subnet details for the given VPC and where they are tagged as hsm enabled
    response = ec2_client.describe_subnets(Filters=[{"Name": "vpc-id",
                                                     "Values": [ssm_services.get_hsm_vpc_id()]},
                                                    {"Name": "tag:" + config.hsm_sub_enabled_tag_name,
                                                     "Values": [config.hsm_sub_enabled_tag_value]}])
    subnet_ids = []
    az_ids = []
    azs = []

    # Check we have subnets defined in the VPC
    if len(response["Subnets"]) == 0:
        raise exceptions.HsmSubnetsNotFoundError("No HSM enabled subnets found.")

    for subnet in response["Subnets"]:
        subnet_ids.append(subnet["SubnetId"])
        az_ids.append(subnet["AvailabilityZoneId"])
        azs.append(subnet["AvailabilityZone"])

    # Check we dont have multiple subnets defined in a single AZ
    # Convert to 'Set' to remove any duplicates and compare to the original list
    az_ids_set = set(az_ids)
    if len(az_ids) != len(az_ids_set):
        # TODO this could be improved to provide details of exactly which AZs have multiple subnets defined
        raise exceptions.MultiSubnetsInAzError("Multiple HSM enabled subnets found in single AZ. " +
                                               "Only one HSM subnet supported per AZ.")

    logger.debug("get_hsm_enabled_subnets() returning: {}".format(subnet_ids))

    return {"subnet_ids": subnet_ids, "az_ids": az_ids, "azs": azs}
