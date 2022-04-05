import configparser
import validation_utils

# Read and validate external config
config_parser = configparser.ConfigParser()
config_parser.read('config.ini')
config = config_parser["DEFAULT"]
validation_utils.validate_config(config)

# SSM params
vpc_id_ssm_param_name = config["HsmVpcIdSsmParamName"]
hsm_cluster_id_param_name = config["HsmClusterIdSsmParamName"]
hsm_ca_cert_param_name = config["HsmCACertSsmParamName"]
hsm_cluster_cert_param_name = config["HsmClusterCertSsmParamName"]

hsm_type = config["HsmType"]
hsm_client_sg_tag_name = config["HsmClientSGTagName"]
hsm_client_sg_tag_value = config["HsmClientSGTagValue"]
hsm_sub_enabled_tag_name = config["HsmSubnetEnabledTagName"]
hsm_sub_enabled_tag_value = config["HsmSubnetEnabledTagValue"]
hsm_from_port = config.getint("HsmFromPort")
hsm_to_port = config.getint("HsmToPort")

ca_country = config["CACountry"]
ca_org = config["CAOrg"]
ca_common_name = config["CACommonName"]
ca_key_exponent = config.getint("CAKeyExponent")
ca_key_size = config.getint("CAKeySize")
ca_cert_expiry_days = config.getint("CACertExpiryDays")
hsm_cert_expiry_days = config.getint("HsmCertExpiryDays")
