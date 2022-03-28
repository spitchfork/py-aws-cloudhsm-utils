# Standard/External modules
import sys
import logging.config

# Custom/Internal Modules
from services import ec2_services
from services import hsm_services
from services import ssm_services
from services import sts_services
import automation_config as config


logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def configure_security_groups():

    try:
        aws_account_id = sts_services.get_aws_account_id()

        # get the Id of the ec2 security group created by cloudformation
        hsm_client_sg_id = ec2_services.get_sg_id_by_tag(config.hsm_client_sg_tag_name, config.hsm_client_sg_tag_value)

        # get the Id of the security group auto created by CloudHSM
        cluster_details = hsm_services.get_hsm_clusters_by_vpc_id(ssm_services.get_hsm_vpc_id())
        hsm_cluster_sg_id = cluster_details["Clusters"][0]["SecurityGroup"]

        # add inbound rule TO THE EC2 CLIENT SG allowing inbound connectivity FROM THE HSM CLUSTER SG
        ec2_services.add_source_sg_ingress_rule_to_sg(hsm_cluster_sg_id, hsm_client_sg_id, aws_account_id,
                                                      config.hsm_from_port, config.hsm_to_port)

        logger.info("Ingress rule added to security group: {}".format(hsm_client_sg_id))

        # add inbound rule TO THE HSM CLUSTER SG allowing inbound connectivity FROM THE EC2 CLIENT SG
        ec2_services.add_source_sg_ingress_rule_to_sg(hsm_client_sg_id, hsm_cluster_sg_id, aws_account_id,
                                                      config.hsm_from_port, config.hsm_to_port)

        logger.info("Ingress rule added to security group: {}".format(hsm_cluster_sg_id))

    except Exception as err:
        logger.error(err)
        sys.exit(1)


if __name__ == '__main__':
    configure_security_groups()
