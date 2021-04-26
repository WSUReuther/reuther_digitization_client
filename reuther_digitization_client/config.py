import configparser
import os


def load_config():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(this_dir, "conf", "config.cfg")
    config = configparser.ConfigParser()
    config.read(config_file)
    return {
        "output_dir": config.get("defaults", "output_dir"),
        "scan_storage_location": config.get("defaults", "scan_storage_location")
    }
