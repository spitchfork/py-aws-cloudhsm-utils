# ***** !!!READ!!! ***** #
# This module is purely for local experimentation of crypto functions.
# It does not contain any best practice and secrets are not handled appropriately.
# YOU SHOULD CONSIDER ALL OF THIS INSECURE!!!
# ***** /!!!READ!!! ***** #

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

import crypto_utils
from services import ssm_services
import automation_config as config


def create_sample_csr():
    # create entity private key
    key = rsa.generate_private_key(public_exponent=65537,
                                   key_size=2048)

    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"GB"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"London"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"London"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"mysite.com"),
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(u"www.mysite.com"),
            x509.DNSName(u"subdomain.mysite.com")
        ]),
        critical=False,
    ).sign(key, hashes.SHA256())

    return{
        "key": key,
        "csr": csr
    }


def write_key_to_disk_w_encryption(key, path, password):
    with open(path, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.BestAvailableEncryption(password),
        ))


def write_cert_to_disk(cert, path):
    with open(path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))


def read_file_from_disk(path):
    with open(path, "rb") as f:
        return f.read()


def test_local_ops():
    root_ca = crypto_utils.create_ca_self_signed_cert()
    write_key_to_disk_w_encryption(root_ca["key"], "C:\\temp\\ca_key.pem", b"secret")
    write_cert_to_disk(root_ca["certificate"], "C:\\temp\\ca_certificate.pem")

    hsm_csr = create_sample_csr()
    hsm_signed_cert = crypto_utils.sign_hsm_csr(hsm_csr["csr"], root_ca["certificate"], root_ca["key"])
    write_cert_to_disk(hsm_signed_cert, "C:\\temp\\hsm_signed_cert.pem")


def test_remote_ops():
    root_ca = crypto_utils.create_ca_self_signed_cert()

    root_cert_str = root_ca["certificate"].public_bytes(serialization.Encoding.PEM).decode("utf-8")
    ssm_services.put_parameter(config.hsm_ca_cert_param_name, root_cert_str, "String")

    hsm_csr = create_sample_csr()
    hsm_signed_cert = crypto_utils.sign_hsm_csr(hsm_csr["csr"], root_ca["certificate"], root_ca["key"])

    signed_cert_str = hsm_signed_cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")
    ssm_services.put_parameter(config.hsm_cluster_cert_param_name, signed_cert_str, "String")


if __name__ == '__main__':
    test_local_ops()
    # test_remote_ops()
