# Standard/External modules
import boto3
import logging

# Custom/Internal Modules
import exceptions
from services import waiters

logger = logging.getLogger(__name__)

CREATE_IN_PROGRESS_STATE = "CREATE_IN_PROGRESS"


def create_cluster(hsm_type, subnet_ids):
    hsm_client = boto3.client('cloudhsmv2')
    create_cluster_resp = hsm_client.create_cluster(HsmType=hsm_type, SubnetIds=subnet_ids)

    if create_cluster_resp["Cluster"]["State"] != CREATE_IN_PROGRESS_STATE:
        raise exceptions.HsmCreateError("Error creating HSM, error is: {}"
                                        .format(create_cluster_resp["Cluster"]["StateMessage"]))

    # NOTE SecurityGroup is not returned despite what the API docs detail
    # see the api_responses examples for more information
    # returning a dict here in case we need other data from the API at a later time
    cluster_details = {"cluster_id": create_cluster_resp["Cluster"]["ClusterId"]}

    return cluster_details


def create_hsm(cluster_id, availability_zone):
    hsm_client = boto3.client('cloudhsmv2')
    create_hsm_resp = hsm_client.create_hsm(ClusterId=cluster_id, AvailabilityZone=availability_zone)

    if create_hsm_resp["Hsm"]["State"] != CREATE_IN_PROGRESS_STATE:
        raise exceptions.HsmCreateError("Error creating HSM, error is: {}"
                                        .format(create_hsm_resp["Hsm"]["StateMessage"]))

    # returning a dict here in case we need other data from the API at a later time
    hsm_details = {"hsm_id": create_hsm_resp["Hsm"]["HsmId"]}

    return hsm_details


def wait_for_cluster_create_complete():
    hsm_client = boto3.client('cloudhsmv2')
    hsm_waiter = waiters.HsmClusterCreateCompleteWaiter(hsm_client)
    hsm_waiter.wait()
    return


def get_hsm_clusters_by_vpc_id(vpc_id):
    vpc_id_filter = {"vpcIds": [vpc_id]}
    return get_hsm_clusters(vpc_id_filter)


def get_hsm_clusters(boto_filter):
    hsm_client = boto3.client('cloudhsmv2')
    hsm_clusters = hsm_client.describe_clusters(Filters=boto_filter)

    logger.debug("get_hsm_clusters() returning: {}".format(hsm_clusters))
    return hsm_clusters
