# Standard/External modules
import logging.config

# Custom/Internal Modules
import crypto_utils
from services import hsm_services
from services import ssm_services


logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def init_hsm_cluster():
    logger.info("Auto creating HSM PKI.")
    certs = crypto_utils.create_hsm_pki()

    logger.info("Initialising HSM cluster.")
    hsm_services.initialize_cluster(ssm_services.get_hsm_cluster_id(),
                                    certs["signed_cert"],
                                    certs["trust_anchor"])

    logger.info("HSM cluster initialised successfully.")


if __name__ == '__main__':
    init_hsm_cluster()
