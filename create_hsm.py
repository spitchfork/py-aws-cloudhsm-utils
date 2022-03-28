# Standard/External modules
import sys
import logging.config

# Custom/Internal Modules
from services import ec2_services
from services import hsm_services
from services import ssm_services


logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def create_hsm():

    try:
        # Get details about an existing HSM cluster - we need the Cluster Id to create a HSM
        cluster_details = hsm_services.get_hsm_clusters_by_vpc_id(ssm_services.get_hsm_vpc_id())
        # Get details about existing HSM enabled subnets - we need an AZ to create a HSM
        subnet_details = ec2_services.get_hsm_enabled_subnets()

        # Create a HSM in the cluster and in the first AZ
        # This can take up to 5 minutes..
        hsm_services.create_hsm(cluster_details["Clusters"][0]["ClusterId"],
                                subnet_details["azs"][0])

    except Exception as err:
        logger.error(err)
        sys.exit(1)


if __name__ == '__main__':
    create_hsm()
