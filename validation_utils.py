import logging.config

logger = logging.getLogger(__name__)


def validate_config(config_dict):
    for key, val in config_dict.items():
        logger.debug("Config dict key/val: {}:{}".format(key, val))
        if len(val) == 0:
            raise ValueError("Config.ini key '{}' does not have a value.".format(key))
