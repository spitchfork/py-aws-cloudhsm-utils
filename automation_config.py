import configparser
import validation_utils

# Read and validate external config
config_parser = configparser.ConfigParser()
config_parser.read('config.ini')
config = config_parser["DEFAULT"]
validation_utils.validate_config(config)

vpc_id_ssm_param_name = config["HsmVpcIdSsmParamName"]
hsm_type = config["HsmType"]
hsm_client_sg_tag_name = config["HsmClientSGTagName"]
hsm_client_sg_tag_value = config["HsmClientSGTagValue"]
hsm_sub_enabled_tag_name = config["HsmSubnetEnabledTagName"]
hsm_sub_enabled_tag_value = config["HsmSubnetEnabledTagValue"]
hsm_from_port = config.getint("HsmFromPort")
hsm_to_port = config.getint("HsmToPort")

