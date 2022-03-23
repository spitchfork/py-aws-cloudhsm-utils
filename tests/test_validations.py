# Standard/External modules
import unittest

# Custom/Internal Modules
import validation_utils


class TestValidateConfig(unittest.TestCase):
    def test_empty_value(self):
        # Test that an empty config value returns an exception.
        config = {"HsmVpcIdSsmParamName": ""}
        self.assertRaises(ValueError, validation_utils.validate_config, config)


if __name__ == '__main__':
    unittest.main()
