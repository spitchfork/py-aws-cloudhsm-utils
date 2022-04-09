# Standard/External modules
import logging.config
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

# Custom/Internal Modules
import automation_config as config
from services import ssm_services, hsm_services

logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def create_ca_self_signed_cert():
    # create private key
    key = rsa.generate_private_key(public_exponent=config.ca_key_exponent,
                                   key_size=config.ca_key_size)

    # set subject = issuer since this is a root CA cert
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, config.ca_country),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, config.ca_org),
        x509.NameAttribute(NameOID.COMMON_NAME, config.ca_common_name)
    ])

    # build the CA certificate
    certificate = x509.CertificateBuilder()\
        .subject_name(subject) \
        .issuer_name(issuer) \
        .public_key(key.public_key())\
        .serial_number(x509.random_serial_number())\
        .not_valid_before(datetime.datetime.utcnow())\
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=config.ca_cert_expiry_days))\
        .add_extension(x509.BasicConstraints(True, 0), critical=True)\
        .sign(key, hashes.SHA256())

    return {
        "key": key,
        "certificate": certificate
    }


def sign_hsm_csr(csr, ca_certificate, ca_key):
    # build the end entity certificate
    signed_certificate = x509.CertificateBuilder()\
        .subject_name(csr.subject) \
        .issuer_name(ca_certificate.issuer) \
        .public_key(csr.public_key())\
        .serial_number(x509.random_serial_number())\
        .not_valid_before(datetime.datetime.utcnow())\
        .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=config.hsm_cert_expiry_days))\
        .sign(ca_key, hashes.SHA256())

    return signed_certificate


def create_hsm_pki():
    # get the hsm csr into memory
    logger.info("Getting HSM cluster CSR.")
    hsm_csr_pem = hsm_services.get_hsm_csr_pem(ssm_services.get_hsm_cluster_id())
    csr = x509.load_pem_x509_csr(hsm_csr_pem)

    # create the root CA
    logger.info("Creating Root CA.")
    root_ca = create_ca_self_signed_cert()
    # TODO store the CA key in Secrets Manager

    # store the CA cert in SSM
    root_cert_str = root_ca["certificate"].public_bytes(serialization.Encoding.PEM).decode("utf-8")
    logger.info("Storing Root CA in SSM.")
    ssm_services.put_parameter(config.hsm_ca_cert_param_name, root_cert_str, "String")

    # sign the HSM CSR
    logger.info("Signing HSM cluster CSR with generated Root CA.")
    hsm_signed_cert = sign_hsm_csr(csr, root_ca["certificate"], root_ca["key"])

    # store the HSM cert in SSM
    signed_cert_str = hsm_signed_cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    logger.info("Storing signed HSM cluster certificate in SSM.")
    ssm_services.put_parameter(config.hsm_cluster_cert_param_name, signed_cert_str, "String")

    return {
        "signed_cert": signed_cert_str,
        "trust_anchor": root_cert_str
    }


if __name__ == '__main__':
    create_hsm_pki()
