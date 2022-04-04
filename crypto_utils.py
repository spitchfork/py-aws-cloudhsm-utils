# Standard/External modules
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

# Custom/Internal Modules
import automation_config as config


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

    # build the certificate
    cert = x509.CertificateBuilder().subject_name(subject) \
        .issuer_name(issuer) \
        .public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=config.ca_cert_expiry_days)
    ).sign(key, hashes.SHA256())

    return {
        "key": key,
        "cert": cert
    }


def create_csr():
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


def test_sign_csr():
    self_signed_resp = create_ca_self_signed_cert()
    csr_resp = create_csr()


if __name__ == '__main__':
    test_sign_csr()
