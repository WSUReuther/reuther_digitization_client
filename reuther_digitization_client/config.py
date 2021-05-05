import configparser
import os


def load_config():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(this_dir, "conf", "config.cfg")
    config = configparser.ConfigParser()
    config.read(config_file)
    generate_derivatives = config.get("defaults", "generate_derivatives")
    if generate_derivatives.lower() in ["true", "y", "yes"]:
        generate_derivatives = True
    else:
        generate_derivatives = False
    derivative_type = config.get("defaults", "derivative_type")
    return {
        "output_dir": config.get("defaults", "output_dir"),
        "scan_storage_location": config.get("defaults", "scan_storage_location"),
        "generate_derivatives": generate_derivatives,
        "derivative_type": derivative_type
    }
